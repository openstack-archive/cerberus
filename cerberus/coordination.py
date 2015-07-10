#
# Copyright (c) 2015 EUROGICIEL
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

from tooz import coordination
import uuid

from oslo.config import cfg

from cerberus.openstack.common.gettextutils import _LE, _LI  # noqa
from cerberus.openstack.common import log

LOG = log.getLogger(__name__)

OPTS = [
    cfg.StrOpt('backend_url',
               default='file:///tmp/cerberus',
               help='The backend URL to use for distributed coordination. If '
                    'left empty, per-deployment central agent and per-host '
                    'compute agent won\'t do workload '
                    'partitioning and will only function correctly if a '
                    'single instance of that service is running.'),
    cfg.FloatOpt('heartbeat',
                 default=1.0,
                 help='Number of seconds between heartbeats for distributed '
                      'coordination (float)'),
    cfg.StrOpt('agents_group',
               default='cerberus-agents',
               help='The coordination group that the cerberus agents join')
]
cfg.CONF.register_opts(OPTS, group='coordination')


class PartitionCoordinator(object):
    """Workload partitioning coordinator.

    This class uses the `tooz` library to manage group membership.

    To ensure that the other agents know this agent is still alive,
    the `heartbeat` method should be called periodically.

    Coordination errors and reconnects are handled under the hood, so the
    service using the partition coordinator need not care whether the
    coordination backend is down. The `extract_my_subset` will simply return an
    empty iterable in this case.
    """

    def __init__(self, my_id=None):
        self._coordinator = None
        self._groups = set()
        self._my_id = my_id or str(uuid.uuid4())
        self._started = False

    def stop(self):
        if not self._coordinator:
            return

        for group in list(self._groups):
            self.leave_group(group)

        try:
            self._coordinator.stop()
        except coordination.ToozError:
            LOG.exception(_LE('Error connecting to coordination backend.'))
        finally:
            self._coordinator = None
            self._started = False

    def start(self):
        backend_url = cfg.CONF.coordination.backend_url
        if backend_url:
            LOG.debug("Backend url is " + str(backend_url))
            try:
                self._coordinator = coordination.get_coordinator(
                    backend_url, self._my_id)
                self._coordinator.start()
                self._started = True
                LOG.info(_LI('Coordination backend started successfully.'))
            except coordination.ToozError:
                self._started = False
                LOG.exception(_LE('Error connecting to coordination backend.'))

    def is_active(self):
        return self._coordinator is not None

    def heartbeat(self):
        if self._coordinator:
            if not self._started:
                # re-connect
                self.start()
            try:
                self._coordinator.heartbeat()
            except coordination.ToozError:
                LOG.exception(_LE('Error sending a heartbeat to coordination '
                                  'backend.'))

    def join_group(self, group_id):
        if not self._coordinator or not self._started or not group_id:
            return
        while True:
            try:
                join_req = self._coordinator.join_group(group_id)
                join_req.get()
                LOG.info(_LI('Joined partitioning group %s'), group_id)
                break
            except coordination.MemberAlreadyExist:
                return
            except coordination.GroupNotCreated:
                LOG.debug(_LI('Creating partitioning group %s'), group_id)
                create_grp_req = self._coordinator.create_group(group_id)
                try:
                    create_grp_req.get()
                except coordination.GroupAlreadyExist:
                    pass
        self._groups.add(group_id)

    def leave_group(self, group_id):
        if group_id not in self._groups:
            return
        if self._coordinator:
            self._coordinator.leave_group(group_id)
            self._groups.remove(group_id)
            LOG.info(_LI('Left partitioning group %s'), group_id)

    def _get_members(self, group_id):
        if not self._coordinator:
            return [self._my_id]

        while True:
            get_members_req = self._coordinator.get_members(group_id)
            try:
                return get_members_req.get()
            except coordination.GroupNotCreated:
                self.join_group(group_id)
