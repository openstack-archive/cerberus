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
import uuid

from oslo.config import cfg

from cerberus import notifications
from cerberus.openstack.common.fixture import moxstubout
from cerberus.tests import base


EXP_RESOURCE_TYPE = uuid.uuid4().hex


class NotificationsTestCase(base.TestBase):
    def setUp(self):
        super(NotificationsTestCase, self).setUp()
        fixture = self.useFixture(moxstubout.MoxStubout())
        self.stubs = fixture.stubs

        # these should use self.config_fixture.config(), but they haven't
        # been registered yet
        cfg.CONF.rpc_backend = 'fake'
        cfg.CONF.notification_driver = ['fake']

    def test_send_notification(self):
        """Test the private method _send_notification to ensure event_type,
           payload, and context are built and passed properly.
        """
        resource = uuid.uuid4().hex
        payload = {'resource_info': resource}
        resource_type = EXP_RESOURCE_TYPE
        operation = 'created'

        # NOTE(ldbragst): Even though notifications._send_notification doesn't
        # contain logic that creates cases, this is suppose to test that
        # context is always empty and that we ensure the resource ID of the
        # resource in the notification is contained in the payload. It was
        # agreed that context should be empty in Keystone's case, which is
        # also noted in the /keystone/notifications.py module. This test
        # ensures and maintains these conditions.
        expected_args = [
            {},  # empty context
            'security.%s.created' % resource_type,  # event_type
            {'resource_info': resource},  # payload
            'INFO',  # priority is always INFO...
        ]

        with mock.patch.object(notifications._get_notifier(),
                               '_notify') as mocked:
            notifications.send_notification(operation, resource_type,
                                            payload)
            mocked.assert_called_once_with(*expected_args)

        notifications.send_notification(operation, resource_type, payload)
