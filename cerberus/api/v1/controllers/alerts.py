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
import pecan
from pecan import response

from cerberus.api.v1.controllers import base
from cerberus.db import api
from cerberus.db.sqlalchemy import models
from cerberus.openstack.common._i18n import _  # noqa
from cerberus.openstack.common import log


LOG = log.getLogger(__name__)


class AlertsController(base.BaseController):

    @pecan.expose("json")
    def get(self):
        """
        Get all alerts of tasks
        :param req: the HTTP request
        :param resp: the HTTP response, including a description and the number
         of alerts
        :return:
        :raises:
            HTTPBadRequest
        """
        all = api.alert_get_all()

        response = {}
        response['description'] = _("Number of alerts")
        response['alert_count'] = len(all)
        response['alerts'] = []
        for a in all:
            response['alerts'].append(models.AlertJsonSerializer()
                                      .serialize(a))

        response.status = 200
        response.body = json.dumps(response)

    @pecan.expose()
    def post(self, **kwargs):
        try:
            api.alert_create(kwargs)
        except Exception as e:
            LOG.exception(e)
            response.body = json.dumps(e.message)
            response.status = 500
