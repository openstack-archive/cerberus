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

from sqlalchemy import exc as sql_exc

import mock

from cerberus import db
from cerberus.tests.unit.api import base
from cerberus.tests.unit.db import utils as db_utils


SECURITY_REPORT_ID = 'abc123'
SECURITY_REPORT_ID_2 = 'xyz789'


class TestSecurityReports(base.TestApiCase):

    def setUp(self):
        super(TestSecurityReports, self).setUp()
        self.fake_security_report = db_utils.get_test_security_report(
            uuid=SECURITY_REPORT_ID
        )
        self.fake_security_reports = []
        self.fake_security_reports.append(self.fake_security_report)
        self.fake_security_reports.append(db_utils.get_test_security_report(
            uuid=SECURITY_REPORT_ID_2
        ))
        self.fake_security_report_model = db_utils.get_security_report_model(
            uuid=SECURITY_REPORT_ID
        )
        self.fake_security_reports_model = []
        self.fake_security_reports_model.append(
            self.fake_security_report_model)
        self.fake_security_reports_model.append(
            db_utils.get_security_report_model(
                uuid=SECURITY_REPORT_ID_2
            )
        )
        self.security_reports_path = '/security_reports'
        self.security_report_path = '/security_reports/%s' \
                                    % self.fake_security_report['uuid']

    def test_get(self):

        db.security_report_get = mock.MagicMock(
            return_value=self.fake_security_report_model)
        security_report = self.get_json(self.security_report_path)
        self.assertEqual(self.fake_security_report,
                         security_report)

    def test_list(self):

        db.security_report_get_all = mock.MagicMock(
            return_value=self.fake_security_reports_model)

        security_reports = self.get_json(self.security_reports_path)

        self.assertEqual({'security_reports': self.fake_security_reports},
                         security_reports)

    def test_update_sr_ticket_id(self):
        db.security_report_update_ticket_id = mock.MagicMock()
        res = self.put_json(self.security_report_path + '/tickets/1', None)
        self.assertEqual(200, res.status_code)

    def test_get_sreports_db_error(self):
        db.security_report_get_all = mock.MagicMock(
            side_effect=sql_exc.NoSuchTableError)

        res = self.get_json(self.security_reports_path, expect_errors=True)
        self.assertEqual(404, res.status_code)

    def test_get_sreport_db_error(self):
        db.security_report_get = mock.MagicMock(
            side_effect=sql_exc.OperationalError)
        res = self.get_json(self.security_report_path, expect_errors=True)
        self.assertEqual(404, res.status_code)
