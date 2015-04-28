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
from oslo import messaging
from stevedore import extension

from cerberus.common import errors
from cerberus.db.sqlalchemy import api
from cerberus.openstack.common import log
from cerberus.openstack.common import loopingcall
from cerberus.openstack.common import service
from cerberus.openstack.common import threadgroup
from plugins import base


LOG = log.getLogger(__name__)

OPTS = [

    cfg.MultiStrOpt('messaging_urls',
                    default=[],
                    help="Messaging URLs to listen for notifications. "
                         "Example: transport://user:pass@host1:port"
                         "[,hostN:portN]/virtual_host "
                         "(DEFAULT/transport_url is used if empty)"),
    cfg.ListOpt('notification-topics', default=['designate']),
    cfg.ListOpt('cerberus_control_exchange', default=['cerberus']),
]

cfg.CONF.register_opts(OPTS)


class CerberusManager(service.Service):

    TASK_NAMESPACE = 'cerberus.plugins'

    @classmethod
    def _get_cerberus_manager(cls):
        return extension.ExtensionManager(
            namespace=cls.TASK_NAMESPACE,
            invoke_on_load=True,
        )

    def __init__(self):
        self.task_id = 0
        super(CerberusManager, self).__init__()

    def _register_plugin(self, extension):
        # Record plugin in database
        version = extension.entry_point.dist.version
        plugin = extension.obj
        db_plugin_info = api.plugin_info_get(plugin._name)
        if db_plugin_info is None:
            db_plugin_info = api.plugin_info_create({'name': plugin._name,
                                                     'uuid': uuid.uuid4(),
                                                     'version': version,
                                                     'provider':
                                                     plugin.PROVIDER,
                                                     'type': plugin.TYPE,
                                                     'description':
                                                     plugin.DESCRIPTION,
                                                     'tool_name':
                                                     plugin.TOOL_NAME
                                                     })
        else:
            api.plugin_version_update(db_plugin_info.id, version)

        plugin._uuid = db_plugin_info.uuid

    def start(self):

        self.rpc_server = None
        self.notification_server = None
        super(CerberusManager, self).start()

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

        transport = messaging.get_transport(cfg.CONF)

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

    def _get_unique_task(self, id):

        try:
            unique_task = next(
                thread for thread in self.tg.threads
                if (thread.kw.get('task_id', None) == id))
        except StopIteration:
            return None
        return unique_task

    def _get_recurrent_task(self, id):
        try:
            recurrent_task = next(timer for timer in self.tg.timers if
                                  (timer.kw.get('task_id', None) == id))
        except StopIteration:
            return None
        return recurrent_task

    def _add_unique_task(self, callback, *args, **kwargs):
        """
        Add a simple task executing only once without delay
        :param callback: Callable function to call when it's necessary
        :param args: list of positional arguments to call the callback with
        :param kwargs: dict of keyword arguments to call the callback with
        :return the thread object that is created
        """
        self.tg.add_thread(callback, *args, **kwargs)

    def _add_recurrent_task(self, callback, period, initial_delay=None, *args,
                            **kwargs):
        """
        Add a recurrent task executing periodically with or without an initial
         delay
        :param callback: Callable function to call when it's necessary
        :param period: the time in seconds during two executions of the task
        :param initial_delay: the time after the first execution of the task
         occurs
        :param args: list of positional arguments to call the callback with
        :param kwargs: dict of keyword arguments to call the callback with
        """
        self.tg.add_timer(period, callback, initial_delay, *args, **kwargs)

    def get_plugins(self, ctx):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        It is used to get information about plugins
        '''
        json_plugins = []
        for extension in self.cerberus_manager:
            plugin = extension.obj
            res = json.dumps(plugin, cls=base.PluginEncoder)
            json_plugins.append(res)
        return json_plugins

    def _get_plugin_from_uuid(self, uuid):
        for extension in self.cerberus_manager:
            plugin = extension.obj
            if (plugin._uuid == uuid):
                return plugin
        return None

    def get_plugin_from_uuid(self, ctx, uuid):
        plugin = self._get_plugin_from_uuid(uuid)
        if plugin is not None:
            return json.dumps(plugin, cls=base.PluginEncoder)
        else:
            return None

    def add_task(self, ctx, uuid, method_, *args, **kwargs):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        It is used to call a method of a plugin back
        :param ctx: a request context dict supplied by client
        :param uuid: the uuid of the plugin to call method onto
        :param method_: the method to call back
        :param task_type: the type of task to create
        :param args: some extra arguments
        :param kwargs: some extra keyworded arguments
        '''
        self.task_id += 1
        kwargs['task_id'] = self.task_id
        kwargs['plugin_id'] = uuid
        task_type = kwargs.get('task_type', "unique")
        plugin = self._get_plugin_from_uuid(uuid)

        if plugin is None:
            raise errors.PluginNotFound(uuid)

        if (task_type.lower() == 'recurrent'):
            try:
                task_period = int(kwargs.get('task_period', None))
            except (TypeError, ValueError) as e:
                LOG.exception(e)
                raise errors.TaskPeriodNotInteger()
            try:
                self._add_recurrent_task(getattr(plugin, method_),
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
                self._add_unique_task(
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
        return self.task_id

    def _stop_recurrent_task(self, id):
        """
        Stop the recurrent task but does not remove it from the ThreadGroup.
        I.e, the task still exists and could be restarted
        Plus, if the task is running, wait for the end of its execution
        :param id: the id of the recurrent task to stop
        :return:
        :raises:
            StopIteration: the task is not found
        """
        recurrent_task = self._get_recurrent_task(id)
        if recurrent_task is None:
            raise errors.TaskNotFound(id)
        recurrent_task.stop()

    def _stop_unique_task(self, id):
        unique_task = self._get_unique_task(id)
        if unique_task is None:
            raise errors.TaskNotFound(id)
        unique_task.stop()

    def _stop_task(self, id):
        task = self._get_task(id)
        if isinstance(task, loopingcall.FixedIntervalLoopingCall):
            try:
                self._stop_recurrent_task(id)
            except errors.InvalidOperation:
                raise
        elif isinstance(task, threadgroup.Thread):
            try:
                self._stop_unique_task(id)
            except errors.InvalidOperation:
                raise

    def stop_task(self, ctx, id):
        try:
            self._stop_task(id)
        except errors.InvalidOperation:
            raise
        return id

    def _delete_recurrent_task(self, id):
        """
        Stop the task and delete the recurrent task from the ThreadGroup.
        If the task is running, wait for the end of its execution
        :param id: the identifier of the task to delete
        :return:
        """
        recurrent_task = self._get_recurrent_task(id)
        if (recurrent_task is None):
            raise errors.TaskDeletionNotAllowed(id)
        recurrent_task.stop()
        try:
            self.tg.timers.remove(recurrent_task)
        except ValueError:
            raise

    def delete_recurrent_task(self, ctx, id):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        Stop the task and delete the recurrent task from the ThreadGroup.
        If the task is running, wait for the end of its execution
        :param ctx: a request context dict supplied by client
        :param id: the identifier of the task to delete
        '''
        try:
            self._delete_recurrent_task(id)
        except errors.InvalidOperation:
            raise
        return id

    def _force_delete_recurrent_task(self, id):
        """
        Stop the task even if it is running and delete the recurrent task from
        the ThreadGroup.
        :param id: the identifier of the task to force delete
        :return:
        """
        recurrent_task = self._get_recurrent_task(id)
        if (recurrent_task is None):
            raise errors.TaskDeletionNotAllowed(id)
        recurrent_task.stop()
        recurrent_task.gt.kill()
        try:
            self.tg.timers.remove(recurrent_task)
        except ValueError:
            raise

    def force_delete_recurrent_task(self, ctx, id):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        Stop the task even if it is running and delete the recurrent task
        from the ThreadGroup.
        :param ctx: a request context dict supplied by client
        :param id: the identifier of the task to force delete
        '''
        try:
            self._force_delete_recurrent_task(id)
        except errors.InvalidOperation:
            raise
        return id

    def _get_tasks(self):
        tasks = []
        for timer in self.tg.timers:
            tasks.append(timer)
        for thread in self.tg.threads:
            tasks.append(thread)
        return tasks

    def _get_task(self, id):
        task = self._get_unique_task(id)
        task_ = self._get_recurrent_task(id)
        if (task is None and task_ is None):
            raise errors.TaskNotFound(id)
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

    def get_task(self, ctx, id):
        try:
            task = self._get_task(id)
        except errors.InvalidOperation:
            raise
        if isinstance(task, loopingcall.FixedIntervalLoopingCall):
            return json.dumps(task,
                              cls=base.FixedIntervalLoopingCallEncoder)
        elif isinstance(task, threadgroup.Thread):
            return json.dumps(task,
                              cls=base.ThreadEncoder)

    def _restart_recurrent_task(self, id):
        """
        Restart the task
        :param id: the identifier of the task to restart
        :return:
        """
        recurrent_task = self._get_recurrent_task(id)
        if (recurrent_task is None):
            raise errors.TaskRestartNotAllowed(str(id))
        period = recurrent_task.kw.get("task_period", None)
        if recurrent_task._running is True:
            raise errors.TaskRestartNotPossible(str(id))
        else:
            try:
                recurrent_task.start(int(period))
            except ValueError as e:
                LOG.exception(e)

    def restart_recurrent_task(self, ctx, id):
        '''
        This method is designed to be called by an rpc client.
        E.g: Cerberus-api
        Restart a recurrent task after it's being stopped
        :param ctx: a request context dict supplied by client
        :param id: the identifier of the task to restart
        '''
        try:
            self._restart_recurrent_task(id)
        except errors.InvalidOperation:
            raise
        return id
