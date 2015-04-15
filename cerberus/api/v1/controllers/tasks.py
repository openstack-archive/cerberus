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
from wsme import types as wtypes

from oslo.messaging import rpc

from cerberus.api.v1.controllers import base
from cerberus.common import errors
from cerberus.openstack.common import log


LOG = log.getLogger(__name__)


action_kind = ["stop", "restart", "force_delete"]
action_kind_enum = wtypes.Enum(str, *action_kind)


class Task(wtypes.Base):
    """ Representation of a task.
    """
    name = wtypes.text
    period = wtypes.IntegerType()
    method = wtypes.text
    plugin_id = wtypes.text
    type = wtypes.text


class TasksController(base.BaseController):

    @pecan.expose()
    def _lookup(self, task_id, *remainder):
        return TaskController(task_id), remainder

    def list_tasks(self):
        ctx = pecan.request.context.to_dict()
        try:
            tasks = self.client.call(ctx, 'get_tasks')
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise
        tasks_ = []
        for task in tasks:
            task_ = json.loads(task)
            tasks_.append(task_)
        return tasks_

    @pecan.expose("json")
    def get(self):
        """ List tasks
        :return: list of tasks
        :raises:
            HTTPBadRequest
        """
        try:
            tasks = self.list_tasks()
        except rpc.RemoteError:
            raise exc.HTTPServiceUnavailable()
        return {'tasks': tasks}

    def create_task(self, body):

        ctx = pecan.request.context.to_dict()

        task = body.get('task', None)
        if task is None:
            LOG.exception("Task object not provided in request")
            raise errors.TaskObjectNotProvided()

        plugin_id = task.get('plugin_id', None)
        if plugin_id is None:
            LOG.exception("Plugin id not provided in request")
            raise errors.PluginIdNotProvided()

        method_ = task.get('method', None)
        if method_ is None:
            LOG.exception("Method not provided in request")
            raise errors.MethodNotProvided()

        try:
            task['id'] = self.client.call(
                ctx,
                'add_task',
                uuid=plugin_id,
                method_=method_,
                task_period=task.get('period', None),
                task_name=task.get('name', "unknown"),
                task_type=task.get('type', "unique")
            )
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

        return task

    @pecan.expose("json")
    def post(self):
        """Ask Cerberus Manager to call a function of a plugin whose identifier
        is uuid, either once or periodically.
        :return:
        :raises:
            HTTPBadRequest: the request is not correct
        """
        body_ = pecan.request.body
        try:
            body = json.loads(body_.decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            LOG.exception(e)
            raise exc.HTTPBadRequest()
        try:
            task = self.create_task(body)
        except errors.TaskObjectNotProvided:
            raise exc.HTTPBadRequest(
                explanation='The task object is required.')
        except errors.PluginIdNotProvided:
            raise exc.HTTPBadRequest(
                explanation='Plugin id must be provided as a string')
        except errors.MethodNotProvided:
            raise exc.HTTPBadRequest(
                explanation='Method must be provided as a string')
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise exc.HTTPBadRequest(explanation=e.value)
        except Exception as e:
            LOG.exception(e)
            raise exc.HTTPBadRequest()
        return {'task': task}


class TaskController(base.BaseController):
    """Manages operation on a single task."""

    _custom_actions = {
        'action': ['POST']
    }

    def __init__(self, task_id):
        super(TaskController, self).__init__()
        pecan.request.context['task_id'] = task_id
        try:
            self._id = int(task_id)
        except ValueError:
            raise exc.HTTPBadRequest(
                explanation='Task id must be an integer')

    def get_task(self, id):
        ctx = pecan.request.context.to_dict()
        try:
            task = self.client.call(ctx, 'get_task', id=int(id))
        except ValueError as e:
            LOG.exception(e)
            raise
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise
        return json.loads(task)

    @pecan.expose("json")
    def get(self):
        """ Get details of a task whose id is id
        :param id: the id of the task
        :return:
        :raises:
            HTTPBadRequest
        """
        try:
            task = self.get_task(self._id)
        except ValueError:
            raise exc.HTTPBadRequest(
                explanation='Task id must be an integer')
        except rpc.RemoteError:
            raise exc.HTTPNotFound()
        except Exception as e:
            LOG.exception(e)
            raise
        return {'task': task}

    @pecan.expose("json")
    def post(self):
        """
        Enable to perform certain actions on a specific task (e.g; stop it)
        :param req: the HTTP request, including the action to perform
        :param resp: the HTTP response, including a description and the task id
        :param id: the identifier of the task on which an action has to be
         performed
        :return:
        :raises:
            HTTPError: Incorrect JSON or not UTF-8 encoded
            HTTPBadRequest: id not integer or task does not exist
        """
        body_ = pecan.request.body
        try:
            body = json.loads(body_.decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            LOG.exception(e)
            raise exc.HTTPBadRequest()

        if 'stop' in body:
            try:
                self.stop_task(self._id)
            except ValueError:
                raise exc.HTTPBadRequest(
                    explanation="Task id must be an integer")
            except rpc.RemoteError:
                raise exc.HTTPBadRequest(
                    explanation="Task can not be stopped")
        elif 'forceDelete' in body:
            try:
                self.force_delete(self._id)
            except ValueError:
                raise exc.HTTPBadRequest(
                    explanation="Task id must be an integer")
            except rpc.RemoteError as e:
                raise exc.HTTPBadRequest(explanation=e.value)

        elif 'restart' in body:
            try:
                self.restart(self._id)
            except ValueError:
                raise exc.HTTPBadRequest(
                    explanation="Task id must be an integer")
            except rpc.RemoteError as e:
                raise exc.HTTPBadRequest(explanation=e.value)
        else:
            raise exc.HTTPBadRequest()

    def stop_task(self, id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx, 'stop_task', id=int(id))
        except ValueError as e:
            LOG.exception(e)
            raise
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

    def force_delete(self, id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx,
                             'force_delete_recurrent_task',
                             id=int(id))
        except ValueError as e:
            LOG.exception(e)
            raise
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

    def restart(self, id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx,
                             'restart_recurrent_task',
                             id=int(id))
        except ValueError as e:
            LOG.exception(e)
            raise
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

    def delete_task(self, id):
        ctx = pecan.request.context.to_dict()
        try:
            self.client.call(ctx, 'delete_recurrent_task', id=int(id))
        except ValueError as e:
            LOG.exception(e)
            raise
        except rpc.RemoteError as e:
            LOG.exception(e)
            raise

    @pecan.expose("json")
    def delete(self):
        """
        Delete a task specified by its identifier. If the task is running, it
         has to be stopped.
        :param req: the HTTP request
        :param resp: the HTTP response, including a description and the task id
        :param id: the identifier of the task to be deleted
        :return:
        :raises:
            HTTPBadRequest: id not an integer or task can't be deleted
        """
        try:
            self.delete_task(self._id)
        except ValueError:
            raise exc.HTTPBadRequest(explanation="Task id must be an integer")
        except rpc.RemoteError as e:
            raise exc.HTTPBadRequest(explanation=e.value)
        except Exception as e:
            LOG.exception(e)
            raise
