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

import datetime
import eventlet


from cerberus.openstack.common import log
from cerberus.plugins import base


LOG = log.getLogger(__name__)

_IMAGE_UPDATE = 'image.update'


class TaskPlugin(base.PluginBase):

    def __init__(self):
        super(TaskPlugin, self).__init__()

    @base.PluginBase.webmethod
    def act_long(self, *args, **kwargs):
        '''
        Each second, log the date during 40 seconds.
        :param args:
        :param kwargs:
        :return:
        '''
        LOG.info(str(kwargs.get('task_name', 'unknown')) + " :"
                 + str(datetime.datetime.time(datetime.datetime.now())))
        i = 0
        while(i < 60):
            LOG.info(str(kwargs.get('task_name', 'unknown')) + " :"
                     + str(datetime.datetime.time(datetime.datetime.now())))
            i += 1
            eventlet.sleep(1)
        LOG.info(str(kwargs.get('task_name', 'unknown')) + " :"
                 + str(datetime.datetime.time(datetime.datetime.now())))

    @base.PluginBase.webmethod
    def act_short(self, *args, **kwargs):
        LOG.info(str(kwargs.get('task_name', 'unknown')) + " :"
                 + str(datetime.datetime.time(datetime.datetime.now())))

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):
        pass
