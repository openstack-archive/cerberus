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

from cerberus.common import threadgroup
from cerberus.openstack.common import service


class CerberusService(service.Service):

    def __init__(self, threads=1000):
        super(CerberusService, self).__init__(threads)
        self.tg = threadgroup.CerberusThreadGroup(threads)


class CerberusServices(service.Services):

    def __init__(self):
        super(CerberusServices, self).__init__()
        self.tg = threadgroup.CerberusThreadGroup()
