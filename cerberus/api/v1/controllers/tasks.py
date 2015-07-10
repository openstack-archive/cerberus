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
import threading

import eventlet
import json
import pecan
from webob import exc
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from oslo.config import cfg
from oslo import messaging
from oslo.messaging import rpc

from cerberus.api.v1.controllers import base
from cerberus.api.v1.datamodels import task as task_models
from cerberus import coordination
from cerberus.openstack.common import log
from cerberus.openstack.common import service


LOG = log.getLogger(__name__)


action_kind = ["stop", "start", "force_delete"]
action_kind_enum = wtypes.Enum(str, *action_kind)


class ActionController(base.BaseController):
    _custom_actions = {
        'stop': ['POST'],
        'force_delete': ['POST'],
        'start': ['POST'],
    }

    @wsme_pecan.wsexpose(None, wtypes.text)
    def stop(self, task_id):
        """Stop task

        :raises:
            HTTPBadRequest: task not found or impossible to stop it
        """
        try:
            self.stop_task(task_id)
        except rpc.RemoteError:
            raise exc.HTTPBadRequest(
                explanation="Task can not be stopped")

    @wsme_pecan.wsexpose(None, wtypes.text)
    def force_delete(self, task_id):
        """Force delete task

        :raises:
            HTTPNotFound: task is not found
        """
        try:
            self.force_delete_task(task_id)
        except rpc.RemoteError as e:
            raise exc.HTTPNotFound(explanation=e.value)

    @wsme_pecan.wsexpose(None, wtypes.text)
    def start(self, task_id):
        """Start task

        :raises:
            HTTPBadRequest: task not found or impossible to start it
        """
        try:
            self.start_task(task_id)
        except rpc.RemoteError as e:
            raise exc.HTTPBadRequest(explanation=e.value)

    def stop_task(self, task_id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx, 'stop_task', task_id=task_id)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

    def force_delete_task(self, task_id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx,
                             'force_delete_recurrent_task',
                             task_id=task_id)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

    def start_task(self, task_id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx,
                             'start_recurrent_task',
                             task_id=task_id)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise


class TasksController(base.BaseController, service.Service):

    action = ActionController()

    def __init__(self):
        super(TasksController, self).__init__()
        self.tasks = []
        self.responses = 0
        self.partition_coordinator = coordination.PartitionCoordinator()
        self.event = threading.Event()
        self.start()

    def start(self):
        transport = messaging.get_transport(cfg.CONF)
        server_rpc_target = messaging.Target(topic='api_agent_rpc',
                                             server='api')
        self.rpc_server = messaging.get_rpc_server(transport,
                                                   server_rpc_target,
                                                   [self],
                                                   executor='eventlet')
        self.rpc_server.start()
        self.partition_coordinator.start()

    # todo(rza): this method must be protected by a lock
    def _tasks(self, ctx, **kwargs):
        LOG.debug(kwargs)
        agent_tasks = kwargs.get('response', [])
        for task in agent_tasks:
            self.tasks.append(task)
        self.responses += 1
        self.event.set()
        self.event.clear()

    def list_tasks(self):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.prepare(fanout=True).cast(ctx, 'get_tasks')
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise
        tasks_resource = []
        LOG.debug("responses before loop: " + str(self.responses))
        LOG.debug("Number of active agents: " + str(
            len(self.partition_coordinator._get_members(
                'cerberus-agents'))))

        # TODO(rza): != instead of <=    and  add a timeout
        # we don't manage to use zake driver and agents are alone in their
        # groups
        i = 0
        while ((self.responses <= len(self.partition_coordinator._get_members(
                'cerberus-agents'))) and (i <= 2)):
            i += 1
            LOG.debug("responses in loop: " + str(self.responses))
            self.event.wait(5)

        LOG.info("tasks: " + str(self.tasks))
        for task in self.tasks:
            tasks_resource.append(
                task_models.TaskResource(json.loads(task)))

        self.responses = 0
        self.tasks = []

        return task_models.TaskResourceCollection(tasks=tasks_resource)

    @wsme_pecan.wsexpose(task_models.TaskResourceCollection)
    def get_all(self):
        """ List tasks handled by Cerberus Manager.

        :return: list of tasks
        :raises:
            HTTPServiceUnavailable: an error occurred in Cerberus Manager or
            the service is unavailable
        """
        try:
            tasks = self.list_tasks()
        except rpc.RemoteError:
            raise exc.HTTPServiceUnavailable()
        return tasks

    def get_task(self, task_id):
        ctx = pecan.request.context.to_dict()
        try:
            task = self.client.call(ctx, 'get_task', task_id=task_id)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise
        return json.loads(task)

    @wsme_pecan.wsexpose(task_models.TaskResource,
                         wtypes.text)
    def get(self, task_id):
        """ Get details of a task

        :return: task details
        :raises:
            HTTPNotFound: task is not found
        """
        try:
            task = self.get_task(task_id)
        except rpc.RemoteError:
            raise exc.HTTPNotFound()
        except Exception as e:
            LOG.exception(e)
            raise exc.HTTPNotFound()
        return task_models.TaskResource(initial_data=task)

    def create_task(self, task):
        ctx = pecan.request.context.to_dict()
        try:
            if task.period is wsme.Unset:
                task.period = None
            task.id = self.client.call(
                ctx,
                'create_task',
                plugin_id=task.plugin_id,
                method_=task.method,
                task_period=task.period,
                task_name=task.name,
                task_type=task.type,
                persistent=task.persistent
            )
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

        return task

    @wsme_pecan.wsexpose(task_models.TaskResource,
                         body=task_models.TaskResource)
    def post(self, task):
        """Create a task

        :return: task details
        :raises:
            HTTPBadRequest
        """

        try:
            task = self.create_task(task)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise exc.HTTPBadRequest(explanation=e.value)
        except Exception as e:
            LOG.exception(e)
            raise exc.HTTPBadRequest()
        return task

    @wsme_pecan.wsexpose(None, wtypes.text)
    def delete(self, task_id):
        """Delete a task

        :raises:
            HTTPNotFound: task does not exist
        """
        try:
            self.delete_task(task_id)
        except rpc.RemoteError as e:
            raise exc.HTTPNotFound(explanation=e.value)
        except Exception as e:
            LOG.exception(e)
            raise

    def delete_task(self, task_id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx, 'delete_recurrent_task', task_id=task_id)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise
