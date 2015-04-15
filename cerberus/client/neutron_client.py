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

import functools

from neutronclient.v2_0 import client as neutron_client
from oslo.config import cfg

from cerberus.openstack.common import log


cfg.CONF.import_group('service_credentials', 'cerberus.service')

LOG = log.getLogger(__name__)


def logged(func):

    @functools.wraps(func)
    def with_logging(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            LOG.exception(e)
            raise

    return with_logging


class Client(object):
    """A client which gets information via python-neutronclient."""

    def __init__(self):
        """Initialize a neutron client object."""
        conf = cfg.CONF.service_credentials
        self.neutronClient = neutron_client.Client(
            username=conf.os_username,
            password=conf.os_password,
            tenant_name=conf.os_tenant_name,
            auth_url=conf.os_auth_url,
        )

    @logged
    def list_networks(self, tenant_id):
        """Returns the list of networks of a given tenant"""
        return self.neutronClient.list_networks(
            tenant_id=tenant_id).get("networks", None)

    @logged
    def list_floatingips(self, tenant_id):
        """Returns the list of networks of a given tenant"""
        return self.neutronClient.list_floatingips(
            tenant_id=tenant_id).get("floatingips", None)

    @logged
    def list_associated_floatingips(self, **params):
        """Returns the list of associated floating ips  of a given tenant"""
        floating_ips = self.neutronClient.list_floatingips(
            **params).get("floatingips", None)
        # A floating IP is an IP address on an external network, which is
        # associated with a specific port, and optionally a specific IP
        # address, on a private OpenStack Networking network. Therefore a
        # floating IP allows access to an instance on a private network from an
        # external network. Floating IPs can only be defined on networks for
        # which the attribute router:external (by the external network
        # extension) has been set to True.
        associated_floating_ips = []
        for floating_ip in floating_ips:
            if floating_ip.get("port_id") is not None:
                associated_floating_ips.append(floating_ip)
        return associated_floating_ips

    @logged
    def net_ips_get(self, network_id):
        """
        Return ip pools used in all subnets of a network
        :param network_id:
        :return: list of pools
        """
        subnets = self.neutronClient.show_network(
            network_id)["network"]["subnets"]
        ips = []
        for subnet in subnets:
            ips.append(self.subnet_ips_get(subnet))
        return ips

    @logged
    def get_net_of_subnet(self, subnet_id):
        return self.neutronClient.show_subnet(
            subnet_id)["subnet"]["network_id"]

    @logged
    def subnet_ips_get(self, network_id):
        """Returns ip pool of a subnet."""
        return self.neutronClient.show_subnet(
            network_id)["subnet"]["allocation_pools"]
