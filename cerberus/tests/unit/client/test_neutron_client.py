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

from cerberus.client import neutron_client
from cerberus.tests.unit import base

cfg.CONF.import_group('service_credentials', 'cerberus.service')


class TestNeutronClient(base.TestCase):

    def setUp(self):
        super(TestNeutronClient, self).setUp()

    @staticmethod
    def fake_networks_list():
        return {'networks':
                [{'admin_state_up': True,
                  'id': '298a3088-a446-4d5a-bad8-f92ecacd786b',
                  'name': 'public',
                  'provider:network_type': 'gre',
                  'provider:physical_network': None,
                  'provider:segmentation_id': 2,
                  'router:external': True,
                  'shared': False,
                  'status': 'ACTIVE',
                  'subnets': [u'c4b6f5b8-3508-4896-b238-a441f25fb492'],
                  'tenant_id': '62d6f08bbd3a44f6ad6f00ca15cce4e5'},
                 ]}

    @staticmethod
    def fake_network_get():
        return {"network": {
            "status": "ACTIVE",
            "subnets": [
                "54d6f61d-db07-451c-9ab3-b9609b6b6f0b"],
            "name": "private-network",
            "provider:physical_network": None,
            "admin_state_up": True,
            "tenant_id": "4fd44f30292945e481c7b8a0c8908869",
            "provider:network_type": "local",
            "router:external": True,
            "shared": True,
            "id": "d32019d3-bc6e-4319-9c1d-6722fc136a22",
            "provider:segmentation_id": None
        }
        }

    @staticmethod
    def fake_subnets_list():
        return {"subnets": [
            {
                "name": "private-subnet",
                "enable_dhcp": True,
                "network_id": "db193ab3-96e3-4cb3-8fc5-05f4296d0324",
                "tenant_id": "26a7980765d0414dbc1fc1f88cdb7e6e",
                "dns_nameservers": [],
                "allocation_pools": [
                    {
                        "start": "10.0.0.2",
                        "end": "10.0.0.254"
                    }
                ],
                "host_routes": [],
                "ip_version": 4,
                "gateway_ip": "10.0.0.1",
                "cidr": "10.0.0.0/24",
                "id": "08eae331-0402-425a-923c-34f7cfe39c1b"},
            {
                "name": "my_subnet",
                "enable_dhcp": True,
                "network_id": "d32019d3-bc6e-4319-9c1d-6722fc136a22",
                "tenant_id": "4fd44f30292945e481c7b8a0c8908869",
                "dns_nameservers": [],
                "allocation_pools": [
                    {
                        "start": "192.0.0.2",
                        "end": "192.255.255.254"
                    }
                ],
                "host_routes": [],
                "ip_version": 4,
                "gateway_ip": "192.0.0.1",
                "cidr": "192.0.0.0/8",
                "id": "54d6f61d-db07-451c-9ab3-b9609b6b6f0b"
            }
        ]
        }

    @staticmethod
    def fake_subnet_get():
        return {"subnet": {
            "name": "my_subnet",
            "enable_dhcp": True,
            "network_id": "d32019d3-bc6e-4319-9c1d-6722fc136a22",
            "tenant_id": "4fd44f30292945e481c7b8a0c8908869",
            "dns_nameservers": [],
            "allocation_pools": [
                {
                    "start": "192.0.0.2",
                    "end": "192.255.255.254"
                }],
            "host_routes": [],
            "ip_version": 4,
            "gateway_ip": "192.0.0.1",
            "cidr": "192.0.0.0/8",
            "id": "54d6f61d-db07-451c-9ab3-b9609b6b6f0b"
        }
        }

    @staticmethod
    def fake_floating_ips_list():
        return {'floatingips': [
            {
                'router_id': 'd23abc8d-2991-4a55-ba98-2aaea84cc72f',
                'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                'floating_network_id': '376da547-b977-4cfe-9cba-275c80debf57',
                'fixed_ip_address': '10.0.0.3',
                'floating_ip_address': '172.24.4.228',
                'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ab',
                'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7'},
            {
                'router_id': None,
                'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                'floating_network_id': '376da547-b977-4cfe-9cba-275c80debf57',
                'fixed_ip_address': None,
                'floating_ip_address': '172.24.4.227',
                'port_id': None,
                'id': '61cea855-49cb-4846-997d-801b70c71bdd'
            }
        ]}

    @mock.patch('neutronclient.v2_0.client.Client')
    def test_list_networks(self, mock_client):
        nc = neutron_client.Client()
        nc.neutronClient.list_networks = mock.MagicMock(
            return_value=self.fake_networks_list())
        networks = nc.list_networks('tenant')
        self.assertTrue(len(networks) == 1)
        self.assertEqual('298a3088-a446-4d5a-bad8-f92ecacd786b',
                         networks[0].get('id'))

    @mock.patch('neutronclient.v2_0.client.Client')
    def test_list_floatingips(self, mock_client):
        nc = neutron_client.Client()
        nc.neutronClient.list_floatingips = mock.MagicMock(
            return_value=self.fake_floating_ips_list())
        floating_ips = nc.list_floatingips('tenant')
        self.assertTrue(len(floating_ips) == 2)
        self.assertEqual('2f245a7b-796b-4f26-9cf9-9e82d248fda7',
                         floating_ips[0].get('id'))
        self.assertEqual('61cea855-49cb-4846-997d-801b70c71bdd',
                         floating_ips[1].get('id'))

    @mock.patch('neutronclient.v2_0.client.Client')
    def test_list_associated_floatingips(self, mock_client):
        nc = neutron_client.Client()
        nc.neutronClient.list_floatingips = mock.MagicMock(
            return_value=self.fake_floating_ips_list())
        floating_ips = nc.list_associated_floatingips()
        self.assertTrue(len(floating_ips) == 1)
        self.assertEqual('2f245a7b-796b-4f26-9cf9-9e82d248fda7',
                         floating_ips[0].get('id'))

    @mock.patch('neutronclient.v2_0.client.Client')
    def test_subnet_ips_get(self, mock_client):
        nc = neutron_client.Client()
        nc.neutronClient.show_subnet = mock.MagicMock(
            return_value=self.fake_subnet_get())
        subnet_ips = nc.subnet_ips_get("d32019d3-bc6e-4319-9c1d-6722fc136a22")
        self.assertTrue(len(subnet_ips) == 1)
        self.assertEqual("192.0.0.2", subnet_ips[0].get("start", None))
        self.assertEqual("192.255.255.254", subnet_ips[0].get("end", None))

    @mock.patch('neutronclient.v2_0.client.Client')
    def test_net_ips_get(self, mock_client):
        nc = neutron_client.Client()
        nc.neutronClient.show_network = mock.MagicMock(
            return_value=self.fake_network_get())
        nc.neutronClient.show_subnet = mock.MagicMock(
            return_value=self.fake_subnet_get())
        ips = nc.net_ips_get("d32019d3-bc6e-4319-9c1d-6722fc136a22")
        self.assertTrue(len(ips) == 1)
        self.assertTrue(len(ips[0]) == 1)
        self.assertEqual("192.0.0.2", ips[0][0].get("start", None))
        self.assertEqual("192.255.255.254", ips[0][0].get("end", None))

    @mock.patch('neutronclient.v2_0.client.Client')
    def test_get_net_of_subnet(self, mock_client):
        nc = neutron_client.Client()
        nc.neutronClient.show_subnet = mock.MagicMock(
            return_value=self.fake_subnet_get())
        network_id = nc.get_net_of_subnet(
            "54d6f61d-db07-451c-9ab3-b9609b6b6f0b")
        self.assertEqual("d32019d3-bc6e-4319-9c1d-6722fc136a22", network_id)
