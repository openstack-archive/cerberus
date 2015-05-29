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

from cerberus.tests.functional import base


class AlarmTestsV1(base.TestCase):

    _service = 'security'

    def test_list_alarms(self):
        resp, body = self.security_client.get("v1/security_alarms")
        self.assertEqual(200, resp.status)


class ReportTestsV1(base.TestCase):

    _service = 'security'

    def test_list_reports(self):
        resp, body = self.security_client.get("v1/security_reports")
        self.assertEqual(200, resp.status)


class TaskTestsV1(base.TestCase):

    _service = 'security'

    def test_list_tasks(self):
        resp, body = self.security_client.get("v1/tasks")
        self.assertEqual(200, resp.status)


class PluginTestsV1(base.TestCase):

    _service = 'security'

    def test_list_plugins(self):
        resp, body = self.security_client.get("v1/plugins")
        self.assertEqual(200, resp.status)
