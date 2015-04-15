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

from cerberus.client import nova_client
from cerberus.tests import base

cfg.CONF.import_group('service_credentials', 'cerberus.service')


class TestNovaClient(base.TestBase):

    @staticmethod
    def fake_servers_list(*args, **kwargs):
        a = mock.MagicMock()
        a.id = 42
        a.flavor = {'id': 1}
        a.image = {'id': 1}
        a_addresses = []
        a_addresses.append({"addr": "10.0.0.1", "version": 4,
                            'OS-EXT-IPS:type': 'floating'})
        a.addresses = {'private': a_addresses}
        b = mock.MagicMock()
        b.id = 43
        b.flavor = {'id': 2}
        b.image = {'id': 2}
        return [a, b]

    @staticmethod
    def fake_detailed_servers_list():
        return \
            {"servers": [
                {
                    "accessIPv4": "",
                    "accessIPv6": "",
                    "addresses": {
                        "private": [
                            {
                                "addr": "192.168.0.3",
                                "version": 4
                            }
                        ]
                    },
                    "created": "2012-09-07T16:56:37Z",
                    "flavor": {
                        "id": "1",
                        "links": [
                            {
                                "href": "http://openstack.example.com/"
                                        "openstack/flavors/1",
                                "rel": "bookmark"
                            }
                        ]
                    },
                    "hostId": "16d193736a5cfdb60c697ca27ad071d6126fa13baeb670f"
                              "c9d10645e",
                    "id": "05184ba3-00ba-4fbc-b7a2-03b62b884931",
                    "image": {
                        "id": "70a599e0-31e7-49b7-b260-868f441e862b",
                        "links": [
                            {
                                "href": "http://openstack.example.com/"
                                        "openstack/images/70a599e0-31e7-49b7-"
                                        "b260-868f441e862b",
                                "rel": "bookmark"
                            }
                        ]
                    },
                    "links": [
                        {
                            "href": "http://openstack.example.com/v2/"
                                    "openstack/servers/05184ba3-00ba-4fbc-"
                                    "b7a2-03b62b884931",
                            "rel": "self"
                        },
                        {
                            "href": "http://openstack.example.com/openstack/"
                                    "servers/05184ba3-00ba-4fbc-b7a2-"
                                    "03b62b884931",
                            "rel": "bookmark"
                        }
                    ],
                    "metadata": {
                        "My Server Name": "Apache1"
                    },
                    "name": "new-server-test",
                    "progress": 0,
                    "status": "ACTIVE",
                    "tenant_id": "openstack",
                    "updated": "2012-09-07T16:56:37Z",
                    "user_id": "fake"
                }
            ]
            }

    def setUp(self):
        super(TestNovaClient, self).setUp()
        self.nova_client = nova_client.Client()

    def test_instance_get_all(self):
        self.nova_client.nova_client.servers.list = mock.MagicMock(
            return_value=self.fake_servers_list())
        instances = self.nova_client.instance_get_all()
        self.assertTrue(instances is not None)

    def test_get_instance_details_from_floating_ip(self):
        self.nova_client.nova_client.servers.list = mock.MagicMock(
            return_value=self.fake_servers_list())
        instance_1 = self.nova_client.get_instance_details_from_floating_ip(
            "10.0.0.1")
        instance_2 = self.nova_client.get_instance_details_from_floating_ip(
            "10.0.0.2")
        self.assertTrue(instance_1 is not None)
        self.assertTrue(instance_2 is None)
