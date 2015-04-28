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

from novaclient.v3 import client as nova_client
from oslo.config import cfg

from cerberus.openstack.common import log


OPTS = [
    cfg.BoolOpt('nova_http_log_debug',
                default=False,
                help='Allow novaclient\'s debug log output.'),
]

SERVICE_OPTS = [
    cfg.StrOpt('nova',
               default='compute',
               help='Nova service type.'),
]

cfg.CONF.register_opts(OPTS)
cfg.CONF.register_opts(SERVICE_OPTS, group='service_types')
# cfg.CONF.import_opt('http_timeout', 'cerberus.service')
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
    """A client which gets information via python-novaclient."""
    def __init__(self, bypass_url=None, auth_token=None):
        """Initialize a nova client object."""
        conf = cfg.CONF.service_credentials
        tenant = conf.os_tenant_id or conf.os_tenant_name
        self.nova_client = nova_client.Client(
            username=conf.os_username,
            project_id=tenant,
            auth_url=conf.os_auth_url,
            password=conf.os_password,
            region_name=conf.os_region_name,
            endpoint_type=conf.os_endpoint_type,
            service_type=cfg.CONF.service_types.nova,
            bypass_url=bypass_url,
            cacert=conf.os_cacert,
            insecure=conf.insecure,
            http_log_debug=cfg.CONF.nova_http_log_debug,
            no_cache=True)

    @logged
    def instance_get_all(self):
        """Returns list of all instances."""
        search_opts = {'all_tenants': True}
        return self.nova_client.servers.list(
            detailed=True,
            search_opts=search_opts)

    @logged
    def get_instance_details_from_floating_ip(self, ip):
        """
        Get instance_id which is associated to the floating ip "ip"
        :param ip: the floating ip that should belong to an instance
        :return instance_id if ip is found, else None
        """
        instances = self.instance_get_all()

        try:
            for instance in instances:
                # An instance can belong to many networks. An instance can
                # have two ips in a network:
                # at least a private ip and potentially a floating ip
                addresses_in_networks = instance.addresses.values()
                for addresses_in_network in addresses_in_networks:
                    for address_in_network in addresses_in_network:
                        if ((address_in_network.get('OS-EXT-IPS:type', None)
                                == 'floating')
                                and (address_in_network['addr'] == ip)):
                            return instance
        except Exception as e:
            LOG.exception(e)
            raise
        return None
