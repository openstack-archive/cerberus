#
#   Copyright (c) 2015 EUROGICIEL
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

import mock
from oslo.config import cfg

from cerberus.client import keystone_client
from cerberus.tests.unit import base

cfg.CONF.import_group('service_credentials', 'cerberus.service')


class TestKeystoneClient(base.TestCase):

    def setUp(self):
        super(TestKeystoneClient, self).setUp()

    @staticmethod
    def fake_get_user():
        return {
            'user': {
                "id": "u1000",
                "name": "jqsmith",
                "email": "john.smith@example.org",
                "enabled": True
            }
        }

    @mock.patch('keystoneclient.v2_0.client.Client')
    def test_get_user(self, mock_client):
        kc = keystone_client.Client()
        user = self.fake_get_user()
        kc.keystone_client_v2_0.users.get = mock.MagicMock(
            return_value=user)
        user = kc.user_detail_get("user")
        self.assertEqual("u1000", user['user'].get('id'))

    @mock.patch('keystoneclient.v2_0.client.Client')
    def test_roles_for_user(self, mock_client):
        kc = keystone_client.Client()
        kc.keystone_client_v2_0.roles.roles_for_user = mock.MagicMock(
            return_value="role"
        )
        role = kc.roles_for_user("user", "tenant")
        self.assertEqual("role", role)
