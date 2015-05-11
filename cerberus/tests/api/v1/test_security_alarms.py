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
from sqlalchemy import exc as sql_exc

from cerberus import db
from cerberus.tests.api import base
from cerberus.tests.db import utils as db_utils

SECURITY_ALARM_ID = 'abc123'
SECURITY_ALARM_ID_2 = 'xyz789'


class TestSecurityReports(base.TestApiBase):

    def setUp(self):
        super(TestSecurityReports, self).setUp()
        self.fake_security_alarm = db_utils.get_test_security_alarm(
            id=SECURITY_ALARM_ID
        )
        self.fake_security_alarms = []
        self.fake_security_alarms.append(self.fake_security_alarm)
        self.fake_security_alarms.append(db_utils.get_test_security_alarm(
            id=SECURITY_ALARM_ID_2
        ))
        self.fake_security_alarm_model = db_utils.get_security_alarm_model(
            id=SECURITY_ALARM_ID
        )
        self.fake_security_alarms_model = []
        self.fake_security_alarms_model.append(
            self.fake_security_alarm_model)
        self.fake_security_alarms_model.append(
            db_utils.get_security_alarm_model(
                id=SECURITY_ALARM_ID_2
            )
        )
        self.security_alarms_path = '/security_alarms'
        self.security_alarm_path = '/security_alarms/%s' \
                                   % self.fake_security_alarm['alarm_id']

    def test_get(self):

        db.security_alarm_get = mock.MagicMock(
            return_value=self.fake_security_alarm_model)
        security_alarm = self.get_json(self.security_alarm_path)
        self.assertEqual(self.fake_security_alarm,
                         security_alarm)

    def test_list(self):

        db.security_alarm_get_all = mock.MagicMock(
            return_value=self.fake_security_alarms_model)

        security_alarms = self.get_json(self.security_alarms_path)

        self.assertEqual({'security_alarms': self.fake_security_alarms},
                         security_alarms)

    def test_get_salarms_db_error(self):
        db.security_alarm_get_all = mock.MagicMock(
            side_effect=sql_exc.NoSuchTableError)

        res = self.get_json(self.security_alarms_path, expect_errors=True)
        self.assertEqual(404, res.status_code)

    def test_get_salarm_db_error(self):
        db.security_alarm_get = mock.MagicMock(
            side_effect=sql_exc.OperationalError)
        res = self.get_json(self.security_alarm_path, expect_errors=True)
        self.assertEqual(404, res.status_code)
