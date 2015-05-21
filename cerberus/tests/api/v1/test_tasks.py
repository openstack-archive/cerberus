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
import mock

from oslo import messaging

from cerberus.api.v1.datamodels import task as task_model
from cerberus.tests.api import base
from cerberus.tests.db import utils as db_utils


class MockTask(object):
    name = None
    id = None
    period = None
    plugin_id = None
    type = None

    def __init__(self, name, period, plugin_id, type, method):
        self.name = name
        self.period = period
        self.plugin_id = plugin_id
        self.type = type
        self.method = method


class TestTasks(base.TestApiBase):

    def setUp(self):
        super(TestTasks, self).setUp()
        self.fake_task = db_utils.get_test_task()
        self.fake_tasks = []
        self.fake_tasks.append(self.fake_task)
        self.fake_tasks.append(db_utils.get_test_task(
            id=2,
            type='reccurent',
            name='recurrent_task',
            period=20
        ))
        self.tasks_path = '/tasks'
        self.task_path = '/tasks/%s' % self.fake_task['id']

    def test_list(self):
        rpc_tasks = []
        for task in self.fake_tasks:
            rpc_tasks.append(json.dumps(task))

        messaging.RPCClient.call = mock.MagicMock(return_value=rpc_tasks)
        tasks = self.get_json(self.tasks_path)
        self.assertEqual({'tasks': self.fake_tasks}, tasks)

    def test_create(self):
        task_id = 1
        task = task_model.TaskResource(
            initial_data={
                'method': "act_long",
                'name': "task1",
                'type': "recurrent",
                'period': 60,
                'plugin_id': "test"})

        expected_task = task
        expected_task.id = task_id
        messaging.RPCClient.call = mock.MagicMock(return_value=task_id)
        task = self.post_json(self.tasks_path, task.as_dict())
        self.assertEqual(expected_task.as_dict(), task.json_body)

    def test_get(self):
        rpc_task = json.dumps(self.fake_task)
        messaging.RPCClient.call = mock.MagicMock(
            return_value=rpc_task)
        task = self.get_json(self.task_path,)
        self.assertEqual(self.fake_task, task)

    def test_stop(self):
        messaging.RPCClient.call = mock.MagicMock(return_value=1)
        response = self.post_json(self.task_path + '/action/stop', {})
        self.assertEqual(204, response.status_code)

    def test_delete(self):
        messaging.RPCClient.call = mock.MagicMock(return_value=1)
        response = self.delete(self.task_path)
        self.assertEqual(204, response.status_code)

    def test_list_tasks_remote_error(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        response = self.get_json(self.task_path, expect_errors=True)
        self.assertEqual(404, response.status_code)

    def test_create_task_incorrect_json(self):
        request_body = "INCORRECT JSON"
        response = self.post_json(self.tasks_path,
                                  request_body,
                                  expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_create_recurrent_task_without_task_object(self):
        task_id = 1
        messaging.RPCClient.call = mock.MagicMock(return_value=task_id)
        response = self.post_json(self.tasks_path, None,
                                  expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_create_recurrent_task_without_plugin_id(self):
        task_id = 1
        task = task_model.TaskResource(
            initial_data={
                "method": "act_long",
                "name": "task1",
                "type": "recurrent",
                "period": 60,
            })
        messaging.RPCClient.call = mock.MagicMock(return_value=task_id)
        response = self.post_json(self.tasks_path,
                                  task.as_dict(),
                                  expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_create_recurrent_task_without_method(self):
        task_id = 1
        task = task_model.TaskResource(
            initial_data={
                "name": "task1",
                "type": "recurrent",
                "period": 60,
                "plugin_id": "plugin-test"
            })
        messaging.RPCClient.call = mock.MagicMock(return_value=task_id)
        response = self.post_json(self.tasks_path,
                                  task.as_dict(),
                                  expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_create_recurrent_task_remote_error(self):
        task = task_model.TaskResource(
            initial_data={
                "method": "act_long",
                "name": "task1",
                "type": "recurrent",
                "period": 60,
                "plugin_id": "plugin-test"
            })

        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError(value="dummy"))
        response = self.post_json(self.tasks_path,
                                  task.as_dict(),
                                  expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_get_task_remote_error(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        response = self.get_json(self.task_path, expect_errors=True)
        self.assertEqual(404, response.status_code)

    def test_stop_task_wrong_id(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        response = self.post_json(self.task_path + '/action/stop', {},
                                  expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('Task can not be stopped',
                         response.json.get('faultstring', None))

    def test_force_delete_task_wrong_id(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        response = self.post_json(self.task_path + 'action/force_delete', {},
                                  expect_errors=True)
        self.assertEqual(404, response.status_code)

    def test_force_delete_task_id_not_integer(self):
        response = self.post_json('/tasks/toto' + 'action/force_delete', {},
                                  expect_errors=True)
        self.assertEqual(404, response.status_code)

    def test_delete_task_not_existing(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError(value="dummy"))
        response = self.delete(self.task_path, expect_errors=True)
        self.assertEqual(404, response.status_code)
