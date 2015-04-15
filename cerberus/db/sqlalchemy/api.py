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

import sqlalchemy
import sys
import threading

from oslo.config import cfg

from cerberus.common import exception
from cerberus.db.sqlalchemy import migration
from cerberus.db.sqlalchemy import models
from cerberus.openstack.common.db import exception as db_exc
from cerberus.openstack.common.db.sqlalchemy import session as db_session
from cerberus.openstack.common import log


CONF = cfg.CONF

LOG = log.getLogger(__name__)


_ENGINE_FACADE = None
_LOCK = threading.Lock()


_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade(
            CONF.database.connection,
            **dict(CONF.database.iteritems())
        )
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.
    :param session: if present, the session to use
    """
    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def _alert_get_all(session=None):
    session = get_session()

    return model_query(models.Alert, read_deleted="no",
                       session=session).all()


def alert_create(values):
    alert_ref = models.Alert()
    alert_ref.update(values)
    try:
        alert_ref.save()
    except db_exc.DBDuplicateEntry:
        raise exception.AlertExists(id=values['id'])
    return alert_ref


def alert_get_all():
    return _alert_get_all()


def _security_report_get_all(project_id=None):
    session = get_session()

    try:
        if project_id is None:
            return model_query(models.SecurityReport, read_deleted="no",
                               session=session).all()
        else:
            return model_query(models.SecurityReport, read_deleted="no",
                               session=session).\
                filter(models.SecurityReport.project_id == project_id).all()
    except Exception as e:
        LOG.exception(e)
        raise e


def _security_report_get(id):
    session = get_session()

    return model_query(models.SecurityReport, read_deleted="no",
                       session=session).filter(models.SecurityReport.
                                               id == id).first()


def _security_report_get_from_report_id(report_id):
    session = get_session()
    return model_query(models.SecurityReport, read_deleted="no",
                       session=session).filter(models.SecurityReport.report_id
                                               == report_id).first()


def security_report_create(values):
    security_report_ref = models.SecurityReport()
    security_report_ref.update(values)
    try:
        security_report_ref.save()
    except sqlalchemy.exc.OperationalError as e:
        LOG.exception(e)
        raise db_exc.ColumnError
    return security_report_ref


def security_report_update_last_report_date(id, date):
    session = get_session()
    report = model_query(models.SecurityReport, read_deleted="no",
                         session=session).filter(models.SecurityReport.id
                                                 == id).first()
    report.last_report_date = date
    try:
        report.save(session)
    except sqlalchemy.exc.OperationalError as e:
        LOG.exception(e)
        raise db_exc.ColumnError


def security_report_get_all(project_id=None):
    return _security_report_get_all(project_id=project_id)


def security_report_get(id):
    return _security_report_get(id)


def security_report_get_from_report_id(report_id):
    return _security_report_get_from_report_id(report_id)


def _plugin_info_get(name):
    session = get_session()

    return model_query(models.PluginInfo,
                       read_deleted="no",
                       session=session).filter(models.PluginInfo.name ==
                                               name).first()


def _plugin_info_get_from_uuid(id):
    session = get_session()

    return model_query(models.PluginInfo,
                       read_deleted="no",
                       session=session).filter(models.PluginInfo.uuid ==
                                               id).first()


def _plugins_info_get():
    session = get_session()

    return model_query(models.PluginInfo,
                       read_deleted="no",
                       session=session).all()


def plugin_info_create(values):
    plugin_info_ref = models.PluginInfo()
    plugin_info_ref.update(values)
    try:
        plugin_info_ref.save()
    except db_exc.DBDuplicateEntry:
        raise exception.PluginInfoExists(id=values['id'])
    return plugin_info_ref


def plugin_info_get(name):
    return _plugin_info_get(name)


def plugin_info_get_from_uuid(id):
    return _plugin_info_get_from_uuid(id)


def plugins_info_get():
    return _plugins_info_get()


def plugin_version_update(id, version):
    session = get_session()
    plugin = model_query(models.PluginInfo, read_deleted="no",
                         session=session).filter(models.PluginInfo.id ==
                                                 id).first()
    plugin.version = version
    try:
        plugin.save(session)
    except sqlalchemy.exc.OperationalError as e:
        LOG.exception(e)
        raise db_exc.ColumnError


def db_sync(engine, version=None):
    """Migrate the database to `version` or the most recent version."""
    return migration.db_sync(engine, version=version)


def db_version(engine):
    """Display the current database version."""
    return migration.db_version(engine)


def _security_alarm_get_all():

    session = get_session()
    try:
        return model_query(models.SecurityAlarm, read_deleted="no",
                           session=session).all()
    except Exception as e:
        LOG.exception(e)
        raise e


def _security_alarm_get(id):

    session = get_session()
    return model_query(models.SecurityAlarm, read_deleted="no",
                       session=session).filter(models.SecurityAlarm.
                                               id == id).first()


def security_alarm_create(values):
    security_alarm_ref = models.SecurityAlarm()
    security_alarm_ref.update(values)
    try:
        security_alarm_ref.save()
    except sqlalchemy.exc.OperationalError as e:
        LOG.exception(e)
        raise db_exc.ColumnError
    return security_alarm_ref


def security_alarm_get_all():
    return _security_alarm_get_all()


def security_alarm_get(id):
    return _security_alarm_get(id)
