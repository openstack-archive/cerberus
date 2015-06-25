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
test_cerberus manager
----------------------------------

Tests for `cerberus` module.
"""

from eventlet import greenpool
import json
import mock
import pkg_resources
from stevedore import extension
import uuid

from oslo import messaging

from cerberus.common import errors
from cerberus.common import loopingcall
from cerberus.common import threadgroup
from cerberus.db.sqlalchemy import api as db_api
from cerberus import manager
from cerberus.plugins import base as base_plugin
from cerberus.tests.unit import base
from cerberus.tests.unit.db import utils as db_utils


PLUGIN_UUID = 'UUID'


class FakePlugin(base_plugin.PluginBase):

    def __init__(self):
        super(FakePlugin, self).__init__()
        self._uuid = PLUGIN_UUID

    def fake_function(self, *args, **kwargs):
        return(args, kwargs)

    @base_plugin.PluginBase.webmethod
    def another_fake_but_web_method(self):
        pass

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):
        pass


class DbPluginInfo(object):
    def __init__(self, id, uuid):
        self.id = id
        self.uuid = uuid


class EntryPoint(object):
    def __init__(self):
        self.dist = pkg_resources.Distribution.from_filename(
            "FooPkg-1.2-py2.4.egg")


class TestCerberusManager(base.WithDbTestCase):

    def setUp(self):
        super(TestCerberusManager, self).setUp()
        self.plugin = FakePlugin()
        self.extension_mgr = extension.ExtensionManager.make_test_instance(
            [
                extension.Extension(
                    'plugin',
                    EntryPoint(),
                    None,
                    self.plugin, ),
            ]
        )
        self.db_plugin_info = DbPluginInfo(1, PLUGIN_UUID)
        self.manager = manager.CerberusManager()
        self.manager.cerberus_manager = self.extension_mgr
        self.fake_db_task = db_utils.get_recurrent_task_model(
            plugin_id=PLUGIN_UUID
        )

    def test_register_plugin(self):
        with mock.patch('cerberus.db.sqlalchemy.api.plugin_info_create') \
                as MockClass:
            MockClass.return_value = DbPluginInfo(1, PLUGIN_UUID)
            self.manager._register_plugin(self.manager.
                                          cerberus_manager['plugin'])
            self.assertEqual(self.db_plugin_info.uuid,
                             self.manager.cerberus_manager['plugin'].obj._uuid)

    def test_register_plugin_new_version(self):
        with mock.patch('cerberus.db.sqlalchemy.api.plugin_info_get') \
                as MockClass:
            MockClass.return_value = DbPluginInfo(1, PLUGIN_UUID)
            db_api.plugin_version_update = mock.MagicMock()
            self.manager._register_plugin(
                self.manager.cerberus_manager['plugin'])
            self.assertEqual(self.db_plugin_info.uuid,
                             self.manager.cerberus_manager['plugin'].obj._uuid)

    @mock.patch.object(messaging.MessageHandlingServer, 'start')
    def test_start(self, rpc_start):
        manager.CerberusManager._register_plugin = mock.MagicMock()
        manager.CerberusManager.add_stored_tasks = mock.MagicMock()
        mgr = manager.CerberusManager()
        mgr.start()
        rpc_start.assert_called_with()
        assert(rpc_start.call_count == 2)

    @mock.patch.object(greenpool.GreenPool, "spawn")
    def test_add_task_without_args(self, mock):
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function)
        assert(len(self.manager.tg.threads) == 1)
        mock.assert_called_with(
            self.manager.cerberus_manager['plugin'].obj.fake_function)

    @mock.patch.object(greenpool.GreenPool, "spawn")
    def test_add_task_with_args(self, mock):
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            name="fake")
        assert(len(self.manager.tg.threads) == 1)
        mock.assert_called_with(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            name="fake")

    @mock.patch.object(loopingcall.CerberusFixedIntervalLoopingCall, "start")
    def test_add_recurrent_task_without_delay(self, mock):
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            15)
        assert(len(self.manager.tg.timers) == 1)
        mock.assert_called_with(initial_delay=None, interval=15)

    @mock.patch.object(loopingcall.CerberusFixedIntervalLoopingCall, "start")
    def test_add_recurrent_task_with_delay(self, mock):
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            15,
            200)
        assert(len(self.manager.tg.timers) == 1)
        mock.assert_called_with(initial_delay=200, interval=15)

    @mock.patch.object(db_api, "create_task")
    def test_store_task(self, db_mock):
        task = db_utils.get_recurrent_task_object(
            persistent='True', task_name='task_name', task_type='recurrent',
            task_period=5, plugin_id='490cc562-9e60-46a7-9b5f-c7619aca2e07',
            task_id='500cc562-5c50-89t4-5fc8-c7619aca3n29')
        self.manager._store_task(task, 'method_')
        db_mock.assert_called_with(
            {'name': 'task_name',
             'method': 'method_',
             'type': 'recurrent',
             'period': 5,
             'plugin_id': '490cc562-9e60-46a7-9b5f-c7619aca2e07',
             'running': True,
             'uuid': '500cc562-5c50-89t4-5fc8-c7619aca3n29'})

    @mock.patch.object(greenpool.GreenPool, "spawn")
    @mock.patch.object(uuid, "uuid4", return_value=1)
    def test_create_task(self, uuid_mock, th_mock):
        ctx = {"some": "context"}
        db_api.create_task = mock.MagicMock(return_value=self.fake_db_task)
        self.manager.create_task(ctx, PLUGIN_UUID, 'fake_function')
        assert(len(self.manager.tg.threads) == 1)
        th_mock.assert_called_with(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            plugin_id=PLUGIN_UUID,
            task_id='1')

    @mock.patch.object(greenpool.GreenPool, "spawn")
    @mock.patch.object(uuid, "uuid4", return_value=1)
    def test_create_task_incorrect_task_type(self, uuid_mock, th_mock):
        ctx = {"some": "context"}
        db_api.create_task = mock.MagicMock(return_value=self.fake_db_task)
        self.manager.create_task(ctx, PLUGIN_UUID, 'fake_function',
                                 task_type='INCORRECT')
        assert(len(self.manager.tg.threads) == 1)
        th_mock.assert_called_with(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            plugin_id=PLUGIN_UUID,
            task_type='INCORRECT',
            task_id='1')

    @mock.patch.object(loopingcall.CerberusFixedIntervalLoopingCall, "start")
    def test_create_recurrent_task_with_interval(self, mock):
        ctx = {"some": "context"}
        db_api.create_task = mock.MagicMock(return_value=self.fake_db_task)
        self.manager.create_task(ctx, PLUGIN_UUID, 'fake_function',
                                 task_type='recurrent', task_period=5)
        assert(len(self.manager.tg.timers) == 1)
        mock.assert_called_with(initial_delay=None, interval=5)

    def test_get_recurrent_task(self):
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            15,
            task_id=1)
        recurrent_task = self.manager._get_recurrent_task(1)
        assert(isinstance(recurrent_task,
                          loopingcall.CerberusFixedIntervalLoopingCall))

    def test_get_recurrent_task_wrong_id(self):
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            15,
            task_id=task_id)
        self.assertTrue(self.manager._get_recurrent_task(task_id + 1) is None)

    def test_get_plugins(self):
        ctx = {"some": "context"}
        json_plugin1 = {
            "name": "cerberus.tests.unit.test_cerberus_manager.FakePlugin",
            "subscribed_events":
            [
            ],
            "methods":
            [
                "another_fake_but_web_method"
            ]
        }
        expected_json_plugins = []
        jplugin1 = json.dumps(json_plugin1)
        expected_json_plugins.append(jplugin1)
        json_plugins = self.manager.get_plugins(ctx)
        self.assertEqual(json_plugins, expected_json_plugins)

    def test_get_plugin(self):
        ctx = {"some": "context"}
        c_manager = manager.CerberusManager()
        c_manager.cerberus_manager = self.extension_mgr

        json_plugin1 = {
            "name": "cerberus.tests.unit.test_cerberus_manager.FakePlugin",
            "subscribed_events":
            [
            ],
            "methods":
            [
                "another_fake_but_web_method"
            ]
        }
        jplugin1 = json.dumps(json_plugin1)
        json_plugin = c_manager.get_plugin_from_uuid(ctx, PLUGIN_UUID)
        self.assertEqual(json_plugin, jplugin1)

    def test_get_plugin_wrong_id(self):
        ctx = {"some": "context"}
        self.assertEqual(self.manager.get_plugin_from_uuid(ctx, 'wrong_test'),
                         None)

    def test_get_tasks(self):
        recurrent_task_id = 1
        unique_task_id = 2
        task_period = 5
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_period,
            task_id=recurrent_task_id)
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=unique_task_id)
        tasks = self.manager._get_tasks()
        self.assertTrue(len(tasks) == 2)
        self.assertTrue(
            isinstance(tasks[0],
                       loopingcall.CerberusFixedIntervalLoopingCall))
        self.assertTrue(isinstance(tasks[1], threadgroup.CerberusThread))

    def test_get_tasks_(self):
        recurrent_task_id = 1
        unique_task_id = 2
        task_period = 5
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_period,
            task_id=recurrent_task_id)
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=unique_task_id)
        tasks = self.manager.get_tasks({'some': 'context'})
        self.assertTrue(len(tasks) == 2)

    def test_get_task_reccurent(self):
        task_id = 1
        task_period = 5
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_period,
            task_id=task_id)
        task = self.manager._get_task(task_id)
        self.assertTrue(
            isinstance(task, loopingcall.CerberusFixedIntervalLoopingCall))

    def test_get_task_unique(self):
        task_id = 1
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=task_id)
        task = self.manager._get_task(task_id)
        self.assertTrue(isinstance(task, threadgroup.CerberusThread))

    def test_get_task(self):
        recurrent_task_id = 1
        recurrent_task_name = "recurrent_task"
        unique_task_id = 2
        unique_task_name = "unique_task"
        task_period = 5
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_period,
            task_name=recurrent_task_name,
            task_period=task_period,
            task_id=recurrent_task_id)
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=unique_task_id,
            task_name=unique_task_name)
        task = self.manager.get_task({'some': 'context'}, 1)
        self.assertTrue(json.loads(task).get('name') == recurrent_task_name)
        self.assertTrue(int(json.loads(task).get('id')) == recurrent_task_id)
        task_2 = self.manager.get_task({'some': 'context'}, 2)
        self.assertTrue(json.loads(task_2).get('name') == unique_task_name)
        self.assertTrue(int(json.loads(task_2).get('id')) == unique_task_id)

    def test_stop_unique_task(self):
        task_id = 1
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=task_id)
        assert(len(self.manager.tg.threads) == 1)
        self.manager._stop_unique_task(task_id)
        assert(len(self.manager.tg.threads) == 0)

    def test_stop_recurrent_task(self):
        db_api.update_state_task = mock.MagicMock()
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        assert(self.manager.tg.timers[0]._running is True)
        self.manager._stop_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is False)

    def test_stop_task_recurrent(self):
        db_api.update_state_task = mock.MagicMock()
        recurrent_task_id = 1
        unique_task_id = 2
        task_period = 5
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_period,
            task_id=recurrent_task_id)
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=unique_task_id)
        self.assertTrue(len(self.manager.tg.timers) == 1)
        assert(self.manager.tg.timers[0]._running is True)
        self.assertTrue(len(self.manager.tg.threads) == 1)
        self.manager._stop_task(recurrent_task_id)
        self.assertTrue(len(self.manager.tg.timers) == 1)
        assert(self.manager.tg.timers[0]._running is False)
        self.assertTrue(len(self.manager.tg.threads) == 1)
        self.manager._stop_task(unique_task_id)
        self.assertTrue(len(self.manager.tg.timers) == 1)
        assert(self.manager.tg.timers[0]._running is False)
        self.assertTrue(len(self.manager.tg.threads) == 0)

    @mock.patch.object(manager.CerberusManager, "_stop_task")
    def test_stop_task(self, mock):
        self.manager.stop_task({'some': 'context'}, 1)
        mock.assert_called_with(1)

    def test_delete_recurrent_task(self):
        ctx = {"some": "context"}
        db_api.delete_task = mock.MagicMock()
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        recurrent_task = self.manager._get_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is True)
        assert(recurrent_task.gt.dead is False)
        self.manager.delete_recurrent_task(ctx, task_id)
        assert(recurrent_task.gt.dead is False)
        assert(len(self.manager.tg.timers) == 0)

    def test_force_delete_recurrent_task(self):
        task_id = 1
        ctx = {"some": "ctx"}
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        recurrent_task = self.manager._get_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is True)
        assert(recurrent_task.gt.dead is False)
        self.manager.force_delete_recurrent_task(ctx, task_id)
        assert(recurrent_task.gt.dead is True)
        assert(len(self.manager.tg.timers) == 0)

    def test_start_recurrent_task(self):
        ctxt = {'some': 'context'}
        db_api.update_state_task = mock.MagicMock()
        task_id = 1
        task_period = 5
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_period,
            task_id=task_id,
            task_period=task_period)
        assert(self.manager.tg.timers[0]._running is True)
        self.manager._stop_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is False)
        self.manager.start_recurrent_task(ctxt, task_id)
        assert(self.manager.tg.timers[0]._running is True)


class FaultyTestCerberusManager(base.TestCaseFaulty):

    def setUp(self):
        super(FaultyTestCerberusManager, self).setUp()
        self.plugin = FakePlugin()
        self.extension_mgr = extension.ExtensionManager.make_test_instance(
            [
                extension.Extension(
                    'plugin',
                    EntryPoint(),
                    None,
                    self.plugin, ),
            ]
        )
        self.db_plugin_info = DbPluginInfo(1, PLUGIN_UUID)
        self.manager = manager.CerberusManager()
        self.manager.cerberus_manager = self.extension_mgr

    def test_create_task_wrong_plugin_id(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.PluginNotFound, self.manager.create_task,
                          ctx, 'WRONG_UUID', 'fake_function')
        assert(len(self.manager.tg.threads) == 0)

    def test_create_task_incorrect_period(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.TaskPeriodNotInteger,
                          self.manager.create_task,
                          ctx,
                          PLUGIN_UUID,
                          'fake_function',
                          task_type='recurrent',
                          task_period='NOT_INTEGER')
        assert(len(self.manager.tg.threads) == 0)

    def test_create_task_wrong_plugin_method(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.MethodNotCallable,
                          self.manager.create_task, ctx, PLUGIN_UUID, 'fake')
        assert(len(self.manager.tg.threads) == 0)

    def test_create_task_method_not_as_string(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.MethodNotString,
                          self.manager.create_task,
                          ctx,
                          PLUGIN_UUID,
                          self.manager.cerberus_manager[
                              'plugin'].obj.fake_function)
        assert(len(self.manager.tg.threads) == 0)

    def test_create_recurrent_task_without_period(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.TaskPeriodNotInteger,
                          self.manager.create_task,
                          ctx,
                          PLUGIN_UUID,
                          'fake_function',
                          task_type='recurrent')
        assert(len(self.manager.tg.timers) == 0)

    def test_create_recurrent_task_wrong_plugin_method(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.MethodNotCallable,
                          self.manager.create_task, ctx, PLUGIN_UUID, 'fake',
                          task_type='recurrent', task_period=5)
        assert(len(self.manager.tg.timers) == 0)

    def test_create_recurrent_task_method_not_as_string(self):
        ctx = {"some": "context"}
        self.assertRaises(errors.MethodNotString,
                          self.manager.create_task,
                          ctx,
                          PLUGIN_UUID,
                          self.manager.cerberus_manager[
                              'plugin'].obj.fake_function,
                          task_type='recurrent',
                          task_period=5)
        assert(len(self.manager.tg.timers) == 0)

    def test_get_task_unique_wrong_id(self):
        task_id = 1
        ctx = {"some": "context"}
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        self.assertRaises(errors.TaskNotFound,
                          self.manager.get_task,
                          ctx,
                          task_id + 1)

    def test_stop_unique_task_wrong_id(self):
        task_id = 1
        self.manager._add_unique_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            task_id=task_id)
        assert(len(self.manager.tg.threads) == 1)
        self.assertRaises(errors.TaskNotFound,
                          self.manager._stop_unique_task,
                          task_id + 1)
        assert(len(self.manager.tg.threads) == 1)

    def test_stop_recurrent_task_wrong_id(self):
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        assert(self.manager.tg.timers[0]._running is True)
        self.assertRaises(errors.TaskNotFound,
                          self.manager._stop_recurrent_task,
                          task_id + 1)
        assert(self.manager.tg.timers[0]._running is True)

    def test_delete_recurrent_task_wrong_id(self):
        ctx = {"some": "context"}
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        recurrent_task = self.manager._get_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is True)
        assert(recurrent_task.gt.dead is False)
        self.assertRaises(errors.TaskDeletionNotAllowed,
                          self.manager.delete_recurrent_task,
                          ctx,
                          task_id + 1)
        assert(self.manager.tg.timers[0]._running is True)
        assert(recurrent_task.gt.dead is False)

    def test_force_delete_recurrent_task_wrong_id(self):
        ctx = {"some": "ctx"}
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        recurrent_task = self.manager._get_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is True)
        assert(recurrent_task.gt.dead is False)
        self.assertRaises(errors.TaskDeletionNotAllowed,
                          self.manager.force_delete_recurrent_task,
                          ctx,
                          task_id + 1)
        assert(recurrent_task.gt.dead is False)
        assert(len(self.manager.tg.timers) == 1)

    def test_start_recurrent_task_wrong_id(self):
        ctxt = {"some": "ctx"}
        db_api.update_state_task = mock.MagicMock()
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        assert(self.manager.tg.timers[0]._running is True)
        self.manager._stop_recurrent_task(task_id)
        assert(self.manager.tg.timers[0]._running is False)
        self.assertRaises(errors.TaskStartNotAllowed,
                          self.manager.start_recurrent_task,
                          ctxt,
                          task_id + 1)
        assert(self.manager.tg.timers[0]._running is False)

    def test_start_recurrent_task_running(self):
        ctxt = {"some": "ctx"}
        task_id = 1
        self.manager._add_recurrent_task(
            self.manager.cerberus_manager['plugin'].obj.fake_function,
            5,
            task_id=task_id)
        assert(self.manager.tg.timers[0]._running is True)
        self.assertRaises(errors.TaskStartNotPossible,
                          self.manager.start_recurrent_task,
                          ctxt,
                          task_id)
        assert(self.manager.tg.timers[0]._running is True)
