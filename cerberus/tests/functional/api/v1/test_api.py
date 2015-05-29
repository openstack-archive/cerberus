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

    def test_create_recurrent_task_not_persistent(self):
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


class PluginTestsV1(base.TestCase):

    _service = 'security'

    def test_list_plugins(self):
        resp, body = self.security_client.get(
            self.security_client._version + '/plugins')
        self.assertEqual(200, resp.status)
