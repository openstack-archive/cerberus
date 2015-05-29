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

from tempest import test
from tempest_lib.common.utils import data_utils

from cerberus.tests.functional import base


class NotificationTests(base.TestCase):

    _service = 'security'

    @test.attr(type='gate')
    def test_notification_image(self):

        # Create image
        image_name = data_utils.rand_name('image')
        glance_resp = self.mgr.image_client.create_image(image_name,
                                                         'bare',
                                                         'iso',
                                                         visibility='private')

        # Remove image at the end
        self.addCleanup(self.mgr.image_client.delete_image, glance_resp['id'])
        self.assertEqual('queued', glance_resp['status'])
        image_id = glance_resp['id']

        resp, task_list_0 = self.security_client.get("v1/tasks")
        task_list_0 = json.loads(task_list_0)

        # Update Image
        self.mgr.image_client.update_image(image_id,
                                           'START')

        # Verifying task has been created
        resp, task_list_1 = self.security_client.get("v1/tasks")
        task_list_1 = json.loads(task_list_1)

        import pdb
        pdb.set_trace()

        self.assertEqual(len(task_list_0.get('tasks', 0)) + 1,
                         len(task_list_1.get('tasks', 0)))

        # Update Image
        self.mgr.image_client.update_image(image_id,
                                           'STOP')

        # Verifying task has been created
        resp, task_list_2 = self.security_client.get("v1/tasks")
        task_list_2 = json.loads(task_list_2)

        self.assertEqual(len(task_list_1.get('tasks', 0)) - 1,
                         len(task_list_2.get('tasks', 0)))
