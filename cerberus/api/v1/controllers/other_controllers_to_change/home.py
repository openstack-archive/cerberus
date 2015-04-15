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

JSON_HOME = {
    'resources': {
        # -----------------------------------------------------------------
        # Plugins
        # -----------------------------------------------------------------
        'rel/plugins': {
            'href-template': '/v1/plugins{?id}',
            'href-vars': {
                'method_name': 'param/method_name',
                'task_name': 'param/task_name',
                'task_type': 'param/task_type',
                'task_period': 'param/task_period',
            },
            'hints': {
                'allow': ['GET', 'POST'],
                'formats': {
                    'application/json': {},
                },
            },
        }
    }
}


class Resource(object):
    def __init__(self):
        document = json.dumps(JSON_HOME, ensure_ascii=False, indent=4)
        self.document_utf8 = document.encode('utf-8')

    def on_get(self, req, resp):
        resp.data = self.document_utf8
        resp.content_type = 'application/json-home'
        resp.cache_control = ['max-age=86400']
