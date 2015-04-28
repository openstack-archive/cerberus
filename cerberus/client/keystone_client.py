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

from keystoneclient.v2_0 import client as keystone_client_v2_0
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
    """A client which gets information via python-keystoneclient."""

    def __init__(self):
        """Initialize a keystone client object."""
        conf = cfg.CONF.service_credentials
        self.keystone_client_v2_0 = keystone_client_v2_0.Client(
            username=conf.os_username,
            password=conf.os_password,
            tenant_name=conf.os_tenant_name,
            auth_url=conf.os_auth_url,
            region_name=conf.os_region_name,
        )

    @logged
    def user_detail_get(self, user):
        """Returns details for a user."""
        return self.keystone_client_v2_0.users.get(user)

    @logged
    def roles_for_user(self, user, tenant=None):
        """Returns role for a given id."""
        return self.keystone_client_v2_0.roles.roles_for_user(user, tenant)
