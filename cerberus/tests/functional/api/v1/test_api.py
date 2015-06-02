#
# Copyright (c) 2015 EUROGICIEL
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

from cerberus.tests.functional import base


class AlarmTestsV1(base.TestCase):

    _service = 'security'

    def test_list_alarms(self):
        resp, body = self.security_client.get(
            self.security_client._version + '/security_alarms')
        self.assertEqual(200, resp.status)


class ReportTestsV1(base.TestCase):

    _service = 'security'

    def test_list_reports(self):
        resp, body = self.security_client.get(
            self.security_client._version + '/security_reports')
        self.assertEqual(200, resp.status)

    def test_create_get_delete_report(self):

        # Create a task to get security report from test_plugin
        plugin_id = None
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins',
        )
        plugins = json.loads(body).get('plugins', None)
        if plugins is not None:
            for plugin in plugins:
                if (plugin.get('name', None) ==
                        'cerberus.plugins.test_plugin.TestPlugin'):
                    plugin_id = plugin.get('uuid', None)

        self.assertIsNotNone(plugin_id,
                             message='cerberus.plugins.test_plugin.TestPlugin '
                                     'must exist and have an id')
        task = {
            "name": "test_create_get_delete_report",
            "method": "get_security_reports",
            "plugin_id": plugin_id,
            "type": "unique"
        }
        headers = {'content-type': 'application/json'}
        resp, body = self.security_client.post(
            self.security_client._version + '/tasks', json.dumps(task),
            headers=headers)
        self.assertEqual(200, resp.status)

        # Check if security report has been stored in db and delete it
        report_id = 'test_plugin_report_id'
        resp, body = self.security_client.get(
            self.security_client._version + '/security_reports/' + report_id)
        report = json.loads(body)
        self.assertEqual('a1d869a1-6ab0-4f02-9e56-f83034bacfcb',
                         report['component_id'])
        self.assertEqual(200, resp.status)

        # Delete security report
        resp, body = self.security_client.delete(
            self.security_client._version + '/security_reports/' + report_id)

        self.assertEqual(204, resp.status)


class TaskTestsV1(base.TestCase):

    _service = 'security'

    def test_list_tasks(self):
        resp, body = self.security_client.get(
            self.security_client._version + '/tasks')
        self.assertEqual(200, resp.status)

    def test_create_unique_task_not_persistent(self):
        plugin_id = None
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins',
        )
        plugins = json.loads(body).get('plugins', None)
        if plugins is not None:
            for plugin in plugins:
                if (plugin.get('name', None) ==
                        'cerberus.plugins.test_plugin.TestPlugin'):
                    plugin_id = plugin.get('uuid', None)

        self.assertIsNotNone(plugin_id,
                             message='cerberus.plugins.test_plugin.TestPlugin '
                                     'must exist and have an id')

        task = {
            "name": "unique_task_np",
            "method": "act_short",
            "plugin_id": plugin_id,
            "type": "unique"
        }
        headers = {'content-type': 'application/json'}
        resp, body = self.security_client.post(
            self.security_client._version + '/tasks', json.dumps(task),
            headers=headers)
        self.assertEqual(200, resp.status)

    def test_create_get_delete_recurrent_task_not_persistent(self):
        plugin_id = None
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins',
        )
        plugins = json.loads(body).get('plugins', None)
        if plugins is not None:
            for plugin in plugins:
                if (plugin.get('name', None) ==
                        'cerberus.plugins.test_plugin.TestPlugin'):
                    plugin_id = plugin.get('uuid', None)

        self.assertIsNotNone(plugin_id,
                             message='cerberus.plugins.test_plugin.TestPlugin '
                                     'must exist and have an id')

        task = {
            "name": "recurrent_task_np",
            "method": "act_short",
            "plugin_id": plugin_id,
            "type": "recurrent",
            "period": 3
        }
        headers = {'content-type': 'application/json'}
        resp, body = self.security_client.post(
            self.security_client._version + '/tasks', json.dumps(task),
            headers=headers)
        task_id = json.loads(body).get('id', None)
        self.assertEqual(200, resp.status)
        self.assertIsNotNone(task_id)
        resp, body = self.security_client.delete(
            self.security_client._version + '/tasks/' + task_id,
        )
        self.assertEqual(204, resp.status)

    def test_create_get_stop_delete_recurrent_task_persistent(self):

        # Get test_plugin
        plugin_id = None
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins',
        )
        plugins = json.loads(body).get('plugins', None)
        if plugins is not None:
            for plugin in plugins:
                if (plugin.get('name', None) ==
                        'cerberus.plugins.test_plugin.TestPlugin'):
                    plugin_id = plugin.get('uuid', None)

        self.assertIsNotNone(plugin_id,
                             message='cerberus.plugins.test_plugin.TestPlugin '
                                     'must exist and have an id')

        # create the task
        task = {
            'name': 'recurrent_persistent_task',
            'method': 'act_short',
            'plugin_id': plugin_id,
            'type': 'recurrent',
            'period': 3,
            'persistent': 'True'
        }
        headers = {'content-type': 'application/json'}
        resp, body = self.security_client.post(
            self.security_client._version + '/tasks', json.dumps(task),
            headers=headers)
        task_id = json.loads(body).get('id', None)
        self.assertEqual(200, resp.status)
        self.assertIsNotNone(task_id)

        # Get the task through API
        resp, body = self.security_client.get(
            self.security_client._version + '/tasks/' + task_id,
            headers=headers)
        self.assertEqual(200, resp.status)
        self.assertEqual(task_id, json.loads(body)['id'])
        self.assertEqual('True', json.loads(body)['persistent'])
        self.assertEqual('recurrent', json.loads(body)['type'])
        self.assertEqual('running', json.loads(body)['state'])
        self.assertEqual(3, json.loads(body)['period'])

        # Stop the task
        resp, body = self.security_client.post(
            self.security_client._version + '/tasks/' + task_id +
            '/action/stop', json.dumps({}), headers=headers)
        self.assertEqual(204, resp.status)

        resp, body = self.security_client.get(
            self.security_client._version + '/tasks/' + task_id,
            headers=headers)
        self.assertEqual(200, resp.status)
        self.assertEqual(task_id, json.loads(body)['id'])
        self.assertEqual('True', json.loads(body)['persistent'])
        self.assertEqual('recurrent', json.loads(body)['type'])
        self.assertEqual('stopped', json.loads(body)['state'])
        self.assertEqual(3, json.loads(body)['period'])

        # Delete the task
        resp, body = self.security_client.delete(
            self.security_client._version + '/tasks/' + task_id,
        )
        self.assertEqual(204, resp.status)


class PluginTestsV1(base.TestCase):

    _service = 'security'

    def test_list_plugins(self):
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins')
        self.assertEqual(200, resp.status)

    def test_get_plugin(self):
        # Get test_plugin
        plugin_id = None
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins',
        )
        plugins = json.loads(body).get('plugins', None)
        if plugins is not None:
            for plugin in plugins:
                if (plugin.get('name', None) ==
                        'cerberus.plugins.test_plugin.TestPlugin'):
                    plugin_id = plugin.get('uuid', None)

        self.assertIsNotNone(plugin_id,
                             message='cerberus.plugins.test_plugin.TestPlugin '
                                     'must exist and have an id')
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins/' + plugin_id,
        )
        self.assertEqual(200, resp.status)
        self.assertEqual('cerberus.plugins.test_plugin.TestPlugin',
                         json.loads(body)['name'])
