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
import pecan
from webob import exc
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from oslo.messaging import rpc

from cerberus.api.v1.controllers import base
from cerberus.api.v1.datamodels import task as task_models
from cerberus.openstack.common import log


LOG = log.getLogger(__name__)


action_kind = ["stop", "restart", "force_delete"]
action_kind_enum = wtypes.Enum(str, *action_kind)


class ActionController(base.BaseController):
    _custom_actions = {
        'stop': ['POST'],
        'force_delete': ['POST'],
        'restart': ['POST'],
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
    def restart(self, task_id):
        """Restart delete task

        :raises:
            HTTPBadRequest: task not found or impossible to restart it
        """
        try:
            self.restart_task(task_id)
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

    def restart_task(self, task_id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx,
                             'restart_recurrent_task',
                             task_id=task_id)
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise


class TasksController(base.BaseController):

    action = ActionController()

    def __init__(self):
        super(TasksController, self).__init__()

    def list_tasks(self):
        ctx = pecan.request.context.to_dict()
        try:
            tasks = self.client.call(ctx, 'get_tasks')
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise
        tasks_resource = []
        for task in tasks:
            tasks_resource.append(
                task_models.TaskResource(json.loads(task)))

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
