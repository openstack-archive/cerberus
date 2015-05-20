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

import pecan
from webob import exc
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from cerberus.api.v1.controllers import base
from cerberus.api.v1.datamodels import security_alarm as alarm_models
from cerberus.common import errors
from cerberus import db
from cerberus.db.sqlalchemy import models
from cerberus.openstack.common import log

LOG = log.getLogger(__name__)


class SecurityAlarmsController(base.BaseController):

    @pecan.expose()
    def _lookup(self, alarm_id, *remainder):
        return SecurityAlarmController(alarm_id), remainder

    def list_security_alarms(self):
        """ List all the security alarms of all projects or just one. """
        try:
            security_alarms = db.security_alarm_get_all()
        except Exception as e:
            LOG.exception(e)
            raise errors.DbError(
                "Security alarms could not be retrieved"
            )
        return security_alarms

    @wsme_pecan.wsexpose(alarm_models.SecurityAlarmResourceCollection)
    def get_all(self):
        """ Get stored security alarms.

        :return: list of security alarms
        :raises:
            HTTPNotFound: Any database error
        """
        try:
            security_alarms = self.list_security_alarms()
        except errors.DbError:
            raise exc.HTTPNotFound()

        alarms_resource = []
        # todo(eglamn3) : no need to serialize here
        for security_alarm in security_alarms:
            alarms_resource.append(
                alarm_models.SecurityAlarmResource(
                    models.SecurityAlarmJsonSerializer().
                    serialize(security_alarm)))

        return alarm_models.SecurityAlarmResourceCollection(
            security_alarms=alarms_resource)


class SecurityAlarmController(base.BaseController):

    _custom_actions = {
        'tickets': ['PUT']
    }

    def __init__(self, alarm_id):
        super(SecurityAlarmController, self).__init__()
        pecan.request.context['alarm_id'] = alarm_id
        self._uuid = alarm_id

    def get_security_alarm(self, alarm_id):
        try:
            security_alarm = db.security_alarm_get(alarm_id)
        except Exception as e:
            LOG.exception(e)
            raise errors.DbError(
                "Security alarm %s could not be retrieved" % alarm_id
            )
        return security_alarm

    @wsme_pecan.wsexpose(alarm_models.SecurityAlarmResource,
                         wtypes.text)
    def get(self):
        """Get security alarm in db

        :return: a security alarm
        :raises:
            HTTPNotFound: Alarm not found or any database error
        """
        try:
            security_alarm = self.get_security_alarm(self._uuid)
        except errors.DbError:
            raise exc.HTTPNotFound()
        s_alarm = models.SecurityAlarmJsonSerializer().\
            serialize(security_alarm)

        return alarm_models.SecurityAlarmResource(initial_data=s_alarm)

    @pecan.expose("json")
    def tickets(self, ticket_id):
        """Modify the ticket id associated to a security alarm in db.

        :param ticket_id: the ticket_id to store in db.
        :raises:
            HTTPNotFound: Alarm not found or any database error
        """
        try:
            db.security_alarm_update_ticket_id(self._uuid, ticket_id)
        except Exception:
            raise exc.HTTPNotFound()
