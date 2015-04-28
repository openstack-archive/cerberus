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

from cerberus.openstack.common import log
from cerberus.plugins import base


LOG = log.getLogger(__name__)


class TestPlugin(base.PluginBase):

    def __init__(self):
        self.task_id = None
        super(TestPlugin, self).__init__()
        super(TestPlugin, self).subscribe_event('image.update')

    def act_short(self, *args, **kwargs):
        LOG.info(str(kwargs.get('task_name', 'unknown')) + " :"
                 + str(datetime.datetime.time(datetime.datetime.now())))

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):

        LOG.info('--> Plugin %(plugin)s managed event %(event)s'
                 'payload %(payload)s'
                 % {'plugin': self._name,
                    'event': event_type,
                    'payload': payload})
        if ('START' in payload['name']and self.task_id is None):
            self.task_id = self.manager.\
                _add_recurrent_task(self.act_short,
                                    1,
                                    task_name='TEST_PLUGIN_START_PAYLOAD')
            LOG.info('Start cycling task id %s', self.task_id)
        if ('STOP' in payload['name']):
            try:
                self.manager._force_delete_recurrent_task(self.task_id)
                LOG.info('Stop cycling task id %s', self.task_id)
                self.task_id = None
            except StopIteration as e:
                LOG.debug('Error when stopping task')
                LOG.exception(e)
        return self._name
