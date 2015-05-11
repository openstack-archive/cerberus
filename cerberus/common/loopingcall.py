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
import sys

from eventlet import event
from eventlet import greenthread

from cerberus.openstack.common.gettextutils import _LE, _LW  # noqa
from cerberus.openstack.common import log as logging
from cerberus.openstack.common import loopingcall
from cerberus.openstack.common import timeutils


LOG = logging.getLogger(__name__)


class CerberusFixedIntervalLoopingCall(loopingcall.FixedIntervalLoopingCall):
    """A fixed interval looping call."""

    def start(self, interval, initial_delay=None):
        self._running = True
        done = event.Event()

        def _inner():
            if initial_delay:
                greenthread.sleep(initial_delay)

            try:
                while self._running:
                    start = timeutils.utcnow()
                    self.f(*self.args, **self.kw)
                    end = timeutils.utcnow()
                    if not self._running:
                        break
                    delay = interval - timeutils.delta_seconds(start, end)
                    if delay <= 0:
                        LOG.warn(_LW('task run outlasted interval by %s sec') %
                                 -delay)
                    greenthread.sleep(delay if delay > 0 else 0)
            except loopingcall.LoopingCallDone as e:
                self.stop()
                done.send(e.retvalue)
            except Exception:
                LOG.exception(_LE('in fixed duration looping call'))
                done.send_exception(*sys.exc_info())
                return
            else:
                done.send(True)

        self.done = done

        self.gt = greenthread.spawn(_inner)
        return self.done
