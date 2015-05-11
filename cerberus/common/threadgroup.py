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

from cerberus.common import loopingcall
from cerberus.db.sqlalchemy import api as db_api
from cerberus.openstack.common import threadgroup


class CerberusThread(threadgroup.Thread):
    def __init__(self, f, thread, group, *args, **kwargs):
        super(CerberusThread, self).__init__(thread, group)
        self.f = f
        self.args = args
        self.kw = kwargs


class CerberusThreadGroup(threadgroup.ThreadGroup):

    def add_stopped_timer(self, callback, *args, **kwargs):
        pulse = loopingcall.CerberusFixedIntervalLoopingCall(callback,
                                                             *args,
                                                             **kwargs)
        self.timers.append(pulse)
        return pulse

    def add_timer(self, interval, callback, initial_delay=None,
                  *args, **kwargs):
        pulse = loopingcall.CerberusFixedIntervalLoopingCall(callback,
                                                             *args,
                                                             **kwargs)
        pulse.start(interval=interval,
                    initial_delay=initial_delay)
        self.timers.append(pulse)
        return pulse

    def add_thread(self, callback, *args, **kwargs):
        gt = self.pool.spawn(callback, *args, **kwargs)
        th = CerberusThread(callback, gt, self, *args, **kwargs)
        self.threads.append(th)
        return th

    def thread_done(self, thread):
        self.threads.remove(thread)
        try:
            db_api.delete_task(thread.kw.get('task_id'))
        except Exception:
            raise
