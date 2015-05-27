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

import mock
import os

from tempest import clients
from tempest import config
from tempest_lib import auth
from tempest_lib import base
from tempest_lib.common import rest_client
from tempest_lib import exceptions


CONF = config.CONF


def get_resource(path):
    main_package = 'cerberus/tests'
    dir_path = __file__[0:__file__.find(main_package) + len(main_package) + 1]

    return open(dir_path + 'resources/' + path).read()


def find_items(items, **props):
    def _matches(item, **props):
        for prop_name, prop_val in props.iteritems():
            if item[prop_name] != prop_val:
                return False

        return True

    filtered = filter(lambda item: _matches(item, **props), items)

    if len(filtered) == 1:
        return filtered[0]

    return filtered


class CerberusClientBase(rest_client.RestClient):

    def __init__(self, auth_provider, service_type):
        super(CerberusClientBase, self).__init__(
            auth_provider=auth_provider,
            service=service_type,
            region=CONF.identity.region)

        if service_type not in ('security'):
            msg = ("Invalid parameter 'service_type'. ")
            raise exceptions.UnprocessableEntity(msg)

        self.endpoint_url = 'publicURL'

        self.workbooks = []
        self.executions = []
        self.workflows = []
        self.triggers = []
        self.actions = []


class CerberusClientV1(CerberusClientBase):

    def list(self):
        self.get("http://127.0.0.1:8300/v1")


class AuthProv(auth.KeystoneV2AuthProvider):

    def __init__(self):
        self.alt_part = None

    def auth_request(self, method, url, *args, **kwargs):
        req_url, headers, body = super(AuthProv, self).auth_request(
            method, url, *args, **kwargs)
        return 'http://localhost:8300/{0}/{1}'.format(
            'v1', url), headers, body

    def get_auth(self):
        return 'mock_str', 'mock_str'

    def base_url(self, *args, **kwargs):
        return ''


class TestCase(base.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        """This method allows to initialize authentication before
        each test case and define parameters of Mistral API Service.
        """
        super(TestCase, cls).setUpClass()

        if 'WITHOUT_AUTH' in os.environ:
            cls.mgr = mock.MagicMock()
            cls.mgr.auth_provider = AuthProv()
        else:
            cls.mgr = clients.Manager()

        cls.client = CerberusClientV1(
            cls.mgr.auth_provider, cls._service)

    def setUp(self):
        super(TestCase, self).setUp()

    def tearDown(self):
        super(TestCase, self).tearDown()
