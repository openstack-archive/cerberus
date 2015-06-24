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
import time

from tempest import test
from tempest_lib.common.utils import data_utils

from cerberus.tests.functional import base


class NotificationTests(base.TestCase):

    _service = 'security'

    @test.attr(type='gate')
    @test.services("image")
    def test_notification_image(self):

        # Create image
        image_name = data_utils.rand_name('image')
        glance_resp = self.mgr.image_client.create_image(image_name,
                                                         'bare',
                                                         'iso',
                                                         visibility='private')
        self.assertEqual('queued', glance_resp['status'])
        image_id = glance_resp['id']

        # Remove image at the end
        self.addCleanup(self.mgr.image_client.delete_image, glance_resp['id'])

        # Check how many tasks there are at the beginning
        resp, task_list_0 = self.security_client.get("v1/tasks")
        task_list_0 = json.loads(task_list_0)

        # Update Image
        self.mgr.image_client.update_image(image_id, 'START')

        # Verifying task has been created
        resp, task_list_1 = self.security_client.get("v1/tasks")
        task_list_1 = json.loads(task_list_1)
        self.assertEqual(len(task_list_0.get('tasks', 0)) + 1,
                         len(task_list_1.get('tasks', 0)))

        # Update Image
        self.mgr.image_client.update_image(image_id, 'STOP')

        # Verify task has been created
        resp, task_list_2 = self.security_client.get("v1/tasks")
        task_list_2 = json.loads(task_list_2)
        self.assertEqual(len(task_list_1.get('tasks', 0)) - 1,
                         len(task_list_2.get('tasks', 0)))

    @test.services("telemetry")
    def test_notifier(self):

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

        # Count the number of security.security_report sample
        # todo(rza): delete the sample at the end if possible
        resp = self.mgr.telemetry_client.list_samples(
            'security.security_report.store')
        samples_number = len(resp)

        task = {
            "name": "test_notifier",
            "method": "get_security_reports",
            "plugin_id": plugin_id,
            "type": "unique"
        }
        headers = {'content-type': 'application/json'}
        resp, body = self.security_client.post(
            self.security_client._version + '/tasks', json.dumps(task),
            headers=headers)
        self.assertEqual(200, resp.status)

        # Check if secu[rity report has been stored in db and delete it
        report_id = 'test_plugin_report_id'
        resp, body = self.security_client.get(
            self.security_client._version + '/security_reports/')

        i = 0
        security_reports = json.loads(body)['security_reports']
        while security_reports[i].get('report_id', None) != report_id:
            i += 1
        report_uuid = security_reports[i].get('uuid', None)
        resp, body = self.security_client.get(
            self.security_client._version + '/security_reports/' + report_uuid)
        report = json.loads(body)
        self.assertEqual('a1d869a1-6ab0-4f02-9e56-f83034bacfcb',
                         report['component_id'])
        self.assertEqual(200, resp.status)

        # Delete security report
        resp, body = self.security_client.delete(
            self.security_client._version + '/security_reports/' + report_uuid)

        self.assertEqual(204, resp.status)

        # Check if a sample has been created in Ceilometer
        time.sleep(10)
        resp = self.mgr.telemetry_client.list_samples(
            'security.security_report.store')
        self.assertEqual(samples_number + 1, len(resp))
