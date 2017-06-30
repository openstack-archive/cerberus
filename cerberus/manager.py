#
#   Copyright (c) 2014 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

import json
import uuid

from oslo.config import cfg
from oslo_messaging import messaging
from stevedore import extension

from cerberus.common import errors
from cerberus.common import exception as cerberus_exception
from cerberus.common import service
from cerberus.db.sqlalchemy import api as db_api
from cerberus import notifications
from cerberus.openstack.common import log
from cerberus.openstack.common import loopingcall
from cerberus.openstack.common import threadgroup
from plugins import base


OPTS = [
    cfg.StrOpt('notifier_topic',
               default='notifications',
               help='The topic that Cerberus uses for generating '
                    'notifications')
]

cfg.CONF.register_opts(OPTS)

LOG = log.getLogger(__name__)


_SECURITY_REPORT = 'security_report'


def store_report_and_notify(title, plugin_id, report_id, component_id,
                            component_name, component_type, project_id,
                            description, security_rating, vulnerabilities,
                            vulnerabilities_number, last_report_date):
    report_uuid = uuid.uuid4()
    report = {'title': title,
              'plugin_id': plugin_id,
              'uuid': str(report_uuid),
              'report_id': report_id,
              'component_id': component_id,
              'component_type': component_type,
              'component_name': component_name,
              'project_id': project_id,
              'description': description,
              'security_rating': security_rating,
              'vulnerabilities': vulnerabilities,
              'vulnerabilities_number': vulnerabilities_number}
    try:
        db_api.security_report_create(report)
        db_api.security_report_update_last_report_date(
            report_uuid, last_report_date)
        notifications.send_notification('store', 'security_report', report)
    except cerberus_exception.DBException:
        raise


def store_alarm_and_notify(plugin_id, alarm_id, timestamp, status, severity,
                           component_id, description, summary):
    alarm = {'plugin_id': plugin_id,
             'alarm_id': alarm_id,
             'timestamp': timestamp,
             'status': status,
             'severity': severity,
             'component_id': component_id,
             'description': description,
             'summary': summary}
    try:
        db_api.security_alarm_create(alarm)
        notifications.send_notification('store', 'security_alarm', alarm)
    except cerberus_exception.DBException:
        raise


class CerberusManager(service.CerberusService):

    TASK_NAMESPACE = 'cerberus.plugins'

    @classmethod
    def _get_cerberus_manager(cls):
        return extension.ExtensionManager(
            namespace=cls.TASK_NAMESPACE,
            invoke_on_load=True,
        )

    def __init__(self):
        super(CerberusManager, self).__init__()
        self.notifier = None

    def _register_plugin(self, extension):
        """Register plugin in database

        :param extension: stevedore extension containing the plugin to register
        :return:
        """

        version = extension.entry_point.dist.version
        plugin = extension.obj
        db_plugin_info = db_api.plugin_info_get(plugin._name)
        if db_plugin_info is None:
            db_plugin_info = db_api.plugin_info_create({'name': plugin._name,
                                                        'uuid': uuid.uuid4(),
                                                        'version': version,
                                                        'provider':
                                                        plugin.PROVIDER,
                                                        'type': plugin.TYPE,
                                                        'description':
                                                        plugin.DESCRIPTION,
                                                        'tool_name':
                                                        plugin.TOOL_NAME})
        else:
            db_api.plugin_version_update(db_plugin_info.id, version)

        plugin._uuid = db_plugin_info.uuid

    def add_stored_tasks(self):
        """Add stored tasks when Cerberus starts"""
        tasks = db_api.get_all_tasks()
        for task in tasks:
            kwargs = {}
            kwargs['task_name'] = task.name
            kwargs['task_type'] = task.type
            kwargs['task_period'] = task.period
            kwargs['task_id'] = task.uuid
            kwargs['running'] = task.running
            kwargs['persistent'] = True
            self._add_task(task.plugin_id, task.method, **kwargs)

    def start(self):
        """Start Cerberus Manager"""

        self.rpc_server = None
        self.notification_server = None
        super(CerberusManager, self).start()

        transport = messaging.get_rpc_transport(cfg.CONF)
        self.notifier = notifications._get_notifier()
        targets = []
        plugins = []
        self.cerberus_manager = self._get_cerberus_manager()
        if not list(self.cerberus_manager):
            LOG.warning('Failed to load any task handlers for %s',
                        self.TASK_NAMESPACE)

        for extension in self.cerberus_manager:
            handler = extension.obj
            LOG.debug('Plugin loaded: ' + extension.name)
            LOG.debug(('Event types from %(name)s: %(type)s')
                      % {'name': extension.name,
                         'type': ', '.join(handler._subscribedEvents)})

            self._register_plugin(extension)
            handler.register_manager(self)
            targets.extend(handler.get_targets(cfg.CONF))
            plugins.append(handler)

        self.add_stored_tasks()

        if transport:
            rpc_target = messaging.Target(topic='test_rpc', server='server1')
            self.rpc_server = messaging.get_rpc_server(transport, rpc_target,
                                                       [self],
                                                       executor='eventlet')

            self.notification_server = messaging.get_notification_listener(
                transport, targets, plugins, executor='eventlet')

            LOG.info("RPC Server starting...")
            self.rpc_server.start()
            self.notification_server.start()

    def _get_unique_task(self, task_id):
        """Get unique task (executed once) thanks to its identifier

        :param task_id: the uique identifier of the task
        :return: the task or None if there is not any task with this id
        """

        try:
            unique_task = next(
                thread for thread in self.tg.threads
                if (thread.kw.get('task_id', None) == task_id))
        except StopIteration:
            return None
        return unique_task

    def _get_recurrent_task(self, task_id):
        """Get recurrent task thanks to its identifier

        :param task_id: the uique identifier of the task
        :return: the task or None if there is not any task with this id
        """
        try:
            recurrent_task = next(timer for timer in self.tg.timers if
                                  (timer.kw.get('task_id', None) == task_id))
        except StopIteration:
            return None
        return recurrent_task

    def _add_unique_task(self, callback, *args, **kwargs):
        """Add an unique task (executed once) without delay

        :param callback: Callable function to call when it's necessary
        :param args: list of positional arguments to call the callback with
        :param kwargs: dict of keyword arguments to call the callback with
        :return the thread object that is created
        """
        return self.tg.add_thread(callback, *args, **kwargs)

    def _add_stopped_reccurent_task(self, callback, period, initial_delay=None,
                                    *args, **kwargs):
        """Add a recurrent task (executed periodically) without starting it

        :param callback: Callable function to call when it's necessary
        :param period: the time in seconds during two executions of the task
        :param initial_delay: the time after the first execution of the task
         occurs
        :param args: list of positional arguments to call the callback with
        :param kwargs: dict of keyword arguments to call the callback with
        """
        return self.tg.add_stopped_timer(callback, initial_delay,
                                         *args, **kwargs)

    def _add_recurrent_task(self, callback, period, initial_delay=None, *args,
                            **kwargs):
        """Add a recurrent task (executed periodically)

        :param callback: Callable function to call when it's necessary
        :param period: the time in seconds during two executions of the task
        :param initial_delay: the time after the first execution of the task
         occurs
        :param args: list of positional arguments to call the callback with
        :param kwargs: dict of keyword arguments to call the callback with
        """
        return self.tg.add_timer(period, callback, initial_delay, *args,
                                 **kwargs)

    def get_plugins(self, ctx):
        '''List plugins loaded by Cerberus manager

        This method is called by the Cerberus-api rpc client
        '''
        json_plugins = []
        for extension in self.cerberus_manager:
            plugin = extension.obj
            res = json.dumps(plugin, cls=base.PluginEncoder)
            json_plugins.append(res)
        return json_plugins

    def _get_plugin_from_uuid(self, plugin_id):
        for extension in self.cerberus_manager:
            plugin = extension.obj
            if plugin._uuid == plugin_id:
                return plugin
        return None

    def get_plugin_from_uuid(self, ctx, uuid):
        plugin = self._get_plugin_from_uuid(uuid)
        if plugin is not None:
            return json.dumps(plugin, cls=base.PluginEncoder)
        else:
            return None

    def _add_task(self, plugin_id, method_, *args, **kwargs):
        '''Add a task in the Cerberus manager

        :param plugin_id: the uuid of the plugin to call method onto
        :param method_: the method to call back
        :param task_type: the type of task to create
        :param args: some extra arguments
        :param kwargs: some extra keyworded arguments
        '''
        kwargs['plugin_id'] = plugin_id
        task_type = kwargs.get('task_type', "unique")
        plugin = self._get_plugin_from_uuid(plugin_id)

        if plugin is None:
            raise errors.PluginNotFound(plugin_id)

        if (task_type.lower() == 'recurrent'):
            try:
                task_period = int(kwargs.get('task_period', None))
            except (TypeError, ValueError) as e:
                LOG.exception(e)
                raise errors.TaskPeriodNotInteger()
            try:
                if kwargs.get('running', True) is True:
                    task = self._add_recurrent_task(getattr(plugin, method_),
                                                    task_period,
                                                    *args,
                                                    **kwargs)
                else:
                    task = self._add_stopped_reccurent_task(
                        getattr(plugin, method_),
                        task_period,
                        *args,
                        **kwargs)
            except TypeError as e:
                LOG.exception(e)
                raise errors.MethodNotString()

            except AttributeError as e:
                LOG.exception(e)
                raise errors.MethodNotCallable(method_,
                                               plugin.__class__.__name__)
        else:
            try:
                task = self._add_unique_task(
                    getattr(plugin, method_),
                    *args,
                    **kwargs)
            except TypeError as e:
                LOG.exception(e)
                raise errors.MethodNotString()
            except AttributeError as e:
                LOG.exception(e)
                raise errors.MethodNotCallable(method_,
                                               plugin.__class__.__name__)

        return task

    def _store_task(self, task, method_):
        try:
            task_period_ = task.kw.get('task_period', None)
            if task_period_ is not None:
                task_period = int(task_period_)
            else:
                task_period = task_period_

            db_api.create_task({'name': task.kw.get('task_name',
                                                    'Unknown'),
                                'method': str(method_),
                                'type': task.kw['task_type'],
                                'period': task_period,
                                'plugin_id': task.kw['plugin_id'],
                                'running': True,
                                'uuid': task.kw['task_id']})

        except Exception as e:
            LOG.exception(e)
            pass

    def create_task(self, ctx, plugin_id, method_, *args, **kwargs):
        """Create a task

        This method is called by a rpc client. It adds a task in the manager
        and stores it if the task is persistent

        :param ctx: a request context dict supplied by client
        :param plugin_id: the uuid of the plugin to call method onto
        :param method_: the method to call back
        :param args: some extra arguments
        :param kwargs: some extra keyworded arguments
        """
        task_id = uuid.uuid4()
        try:
            task = self._add_task(plugin_id, method_, *args,
                                  task_id=str(task_id), **kwargs)
        except Exception:
            raise
        if kwargs.get('persistent', False) is True:
            try:
                self._store_task(task, method_)
            except Exception as e:
                LOG.exception(e)
                pass
        return str(task_id)

    def _stop_recurrent_task(self, task_id):
        """Stop the recurrent task but does not remove it from the ThreadGroup.

        The task still exists and could be started. Plus, if the task is
         running, wait for the end of its execution
        :param task_id: the id of the recurrent task to stop
        :return:
        :raises:
            StopIteration: the task is not found
        """
        recurrent_task = self._get_recurrent_task(task_id)
        if recurrent_task is None:
            raise errors.TaskNotFound(task_id)
        recurrent_task.stop()
        if recurrent_task.kw.get('persistent', False) is True:
            try:
                db_api.update_state_task(task_id, False)
            except Exception as e:
                LOG.exception(e)
                raise e

    def _stop_unique_task(self, task_id):
        """Stop the task. This task is automatically deleted as it's not
        recurrent
        """
        unique_task = self._get_unique_task(task_id)
        if unique_task is None:
            raise errors.TaskNotFound(task_id)
        unique_task.stop()
        if unique_task.kw.get('persistent', False) is True:
            try:
                db_api.delete_task(task_id)
            except Exception as e:
                LOG.exception(e)
                raise e

    def _stop_task(self, task_id):
        task = self._get_task(task_id)
        if isinstance(task, loopingcall.FixedIntervalLoopingCall):
            try:
                self._stop_recurrent_task(task_id)
            except errors.InvalidOperation:
                raise
        elif isinstance(task, threadgroup.Thread):
            try:
                self._stop_unique_task(task_id)
            except errors.InvalidOperation:
                raise

    def stop_task(self, ctx, task_id):
        try:
            self._stop_task(task_id)
        except errors.InvalidOperation:
            raise
        return task_id

    def _delete_recurrent_task(self, task_id):
        """
        Stop the task and delete the recurrent task from the ThreadGroup.
        If the task is running, wait for the end of its execution
        :param task_id: the identifier of the task to delete
        :return:
        """
        recurrent_task = self._get_recurrent_task(task_id)
        if (recurrent_task is None):
            raise errors.TaskDeletionNotAllowed(task_id)
        recurrent_task.stop()
        try:
            self.tg.timers.remove(recurrent_task)
        except ValueError:
            raise
        if recurrent_task.kw.get('persistent', False) is True:
            try:
                db_api.delete_task(task_id)
            except Exception as e:
                LOG.exception(e)
                raise e

    def delete_recurrent_task(self, ctx, task_id):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        Stop the task and delete the recurrent task from the ThreadGroup.
        If the task is running, wait for the end of its execution
        :param ctx: a request context dict supplied by client
        :param task_id: the identifier of the task to delete
        '''
        try:
            self._delete_recurrent_task(task_id)
        except errors.InvalidOperation:
            raise
        return task_id

    def _force_delete_recurrent_task(self, task_id):
        """
        Stop the task even if it is running and delete the recurrent task from
        the ThreadGroup.
        :param task_id: the identifier of the task to force delete
        :return:
        """
        recurrent_task = self._get_recurrent_task(task_id)
        if (recurrent_task is None):
            raise errors.TaskDeletionNotAllowed(task_id)
        recurrent_task.stop()
        recurrent_task.gt.kill()
        try:
            self.tg.timers.remove(recurrent_task)
        except ValueError:
            raise
        if recurrent_task.kw.get('persistent', False) is True:
            try:
                db_api.delete_task(task_id)
            except Exception as e:
                LOG.exception(e)
                raise e

    def force_delete_recurrent_task(self, ctx, task_id):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        Stop the task even if it is running and delete the recurrent task
        from the ThreadGroup.
        :param ctx: a request context dict supplied by client
        :param task_id: the identifier of the task to force delete
        '''
        try:
            self._force_delete_recurrent_task(task_id)
        except errors.InvalidOperation:
            raise
        return task_id

    def _get_tasks(self):
        tasks = []
        for timer in self.tg.timers:
            tasks.append(timer)
        for thread in self.tg.threads:
            tasks.append(thread)
        return tasks

    def _get_task(self, task_id):
        task = self._get_unique_task(task_id)
        task_ = self._get_recurrent_task(task_id)
        if (task is None and task_ is None):
            raise errors.TaskNotFound(task_id)
        return task if task is not None else task_

    def get_tasks(self, ctx):
        tasks_ = []
        tasks = self._get_tasks()
        for task in tasks:
            if (isinstance(task, loopingcall.FixedIntervalLoopingCall)):
                tasks_.append(
                    json.dumps(task,
                               cls=base.FixedIntervalLoopingCallEncoder))
            elif (isinstance(task, threadgroup.Thread)):
                tasks_.append(
                    json.dumps(task,
                               cls=base.ThreadEncoder))
        return tasks_

    def get_task(self, ctx, task_id):
        try:
            task = self._get_task(task_id)
        except errors.InvalidOperation:
            raise
        if isinstance(task, loopingcall.FixedIntervalLoopingCall):
            return json.dumps(task,
                              cls=base.FixedIntervalLoopingCallEncoder)
        elif isinstance(task, threadgroup.Thread):
            return json.dumps(task,
                              cls=base.ThreadEncoder)

    def _start_recurrent_task(self, task_id):
        """
        Start the task
        :param task_id: the identifier of the task to start
        :return:
        """
        recurrent_task = self._get_recurrent_task(task_id)
        if (recurrent_task is None):
            raise errors.TaskStartNotAllowed(str(task_id))
        period = recurrent_task.kw.get("task_period", None)
        if recurrent_task._running is True:
            raise errors.TaskStartNotPossible(str(task_id))
        else:
            try:
                recurrent_task.start(int(period))
                if recurrent_task.kw.get('persistent', False) is True:
                    db_api.update_state_task(task_id, True)
            except Exception as e:
                LOG.exception(e)
                raise e

    def start_recurrent_task(self, ctx, task_id):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        Start a recurrent task after it's being stopped
        :param ctx: a request context dict supplied by client
        :param task_id: the identifier of the task to start
        '''
        try:
            self._start_recurrent_task(task_id)
        except errors.InvalidOperation:
            raise
        return task_id
