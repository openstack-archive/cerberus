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

import json
from sqlalchemy import exc

import mock
from oslo import messaging

from cerberus import db
from cerberus.tests.unit.api import base
from cerberus.tests.unit.db import utils as db_utils


PLUGIN_ID_1 = 1
PLUGIN_ID_2 = 2
PLUGIN_NAME_2 = 'toolyx'


class TestPlugins(base.TestApiBase):

    def setUp(self):
        super(TestPlugins, self).setUp()
        self.fake_plugin = db_utils.get_test_plugin(
            id=PLUGIN_ID_1
        )
        self.fake_plugins = []
        self.fake_plugins.append(self.fake_plugin)
        self.fake_plugins.append(db_utils.get_test_plugin(
            id=PLUGIN_ID_2,
            name=PLUGIN_NAME_2
        ))
        self.fake_plugin_model = db_utils.get_plugin_model(
            id=PLUGIN_ID_1
        )
        self.fake_plugins_model = []
        self.fake_plugins_model.append(
            self.fake_plugin_model)
        self.fake_plugins_model.append(
            db_utils.get_plugin_model(
                id=PLUGIN_ID_2,
                name=PLUGIN_NAME_2
            )
        )
        self.fake_rpc_plugin = db_utils.get_rpc_plugin()
        self.fake_rpc_plugins = []
        self.fake_rpc_plugins.append(self.fake_rpc_plugin)
        self.fake_rpc_plugins.append(db_utils.get_rpc_plugin(
            name=PLUGIN_NAME_2
        ))
        self.plugins_path = '/plugins'
        self.plugin_path = '/plugins/%s' % self.fake_plugin['uuid']

    def test_list(self):

        rpc_plugins = []
        for plugin in self.fake_rpc_plugins:
            rpc_plugins.append(json.dumps(plugin))

        messaging.RPCClient.call = mock.MagicMock(
            return_value=rpc_plugins)
        db.plugins_info_get = mock.MagicMock(
            return_value=self.fake_plugins_model)

        plugins = self.get_json(self.plugins_path)
        expecting_sorted = sorted({'plugins': self.fake_plugins}['plugins'],
                                  key=lambda k: k['name'])
        actual_sorted = sorted(plugins['plugins'], key=lambda k: k['name'])
        self.assertEqual(expecting_sorted,
                         actual_sorted)

    def test_get(self):
        rpc_plugin = json.dumps(self.fake_rpc_plugin)
        messaging.RPCClient.call = mock.MagicMock(return_value=rpc_plugin)
        db.plugin_info_get_from_uuid = mock.MagicMock(
            return_value=self.fake_plugin_model)
        plugin = self.get_json(self.plugin_path)
        self.assertEqual(self.fake_plugin, plugin)

    def test_list_plugins_remote_error(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        res = self.get_json(self.plugins_path, expect_errors=True)
        self.assertEqual(503, res.status_code)

    def test_get_plugin_not_existing(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        res = self.get_json(self.plugin_path, expect_errors=True)
        self.assertEqual(503, res.status_code)

    def test_list_plugins_db_error(self):
        messaging.RPCClient.call = mock.MagicMock(return_value=None)
        db.plugins_info_get = mock.MagicMock(side_effect=exc.OperationalError)
        res = self.get_json(self.plugins_path, expect_errors=True)
        self.assertEqual(404, res.status_code)

    def test_get_plugin_remote_error(self):
        messaging.RPCClient.call = mock.MagicMock(
            side_effect=messaging.RemoteError)
        res = self.get_json(self.plugin_path, expect_errors=True)
        self.assertEqual(503, res.status_code)
