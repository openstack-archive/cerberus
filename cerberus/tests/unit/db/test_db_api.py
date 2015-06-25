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

"""
Tests for `db api` module.
"""

import mock

from cerberus.db.sqlalchemy import api as db_api
from cerberus.openstack.common.db.sqlalchemy import models as db_models
from cerberus.tests.unit.db import base


class DbApiTestCase(base.DbTestCase):

    def setUp(self):
        super(DbApiTestCase, self).setUp()
        self.db_api = db_api.get_instance()

    def test_security_report_create(self):
        db_models.ModelBase.save = mock.MagicMock()
        report = self.db_api.security_report_create(
            {'title': 'TitleSecurityReport',
             'plugin_id': '123456789',
             'description': 'The first',
             'component_id': '1234'})

        self.assertEqual('TitleSecurityReport', report.title)
        self.assertEqual('123456789', report.plugin_id)
        self.assertEqual('The first', report.description)
        self.assertEqual('1234', report.component_id)

    def test_plugin_info_create(self):
        pi = self.db_api.plugin_info_create(
            {'name': 'NameOfPlugin',
             'uuid': '0000-aaaa-1111-bbbb'})
        self.assertTrue(pi.id >= 0)

    def test_plugin_info_get(self):
        self.db_api.plugin_info_create(
            {'name': 'NameOfPluginToGet',
             'uuid': '3333-aaaa-1111-bbbb'})

        pi = self.db_api.plugin_info_get('NameOfPluginToGet')
        self.assertEqual('NameOfPluginToGet', pi.name)
