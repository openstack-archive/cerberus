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
import os

from oslo.config import cfg
from oslotest import base

from cerberus.tests.unit import config_fixture
from cerberus.tests.unit import policy_fixture


CONF = cfg.CONF


class TestCase(base.BaseTestCase):

    """Test case base class for all unit tests."""
    def setUp(self):
        super(TestCase, self).setUp()
        self.useFixture(config_fixture.ConfigFixture(CONF))
        self.policy = self.useFixture(policy_fixture.PolicyFixture())

    def path_get(self, project_file=None):
        """Get the absolute path to a file. Used for testing the API.
        :param project_file: File whose path to return. Default: None.
        :returns: path to the specified file, or path to project root.
        """
        root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..',
                                            '..',
                                            )
                               )
        if project_file:
            return os.path.join(root, project_file)
        else:
            return root


class TestCaseFaulty(TestCase):
    """This test ensures we aren't letting any exceptions go unhandled."""
