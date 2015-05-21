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

import sys

from oslo.config import cfg
from sqlalchemy import create_engine

from cerberus.common import config


def main():
    argv = sys.argv
    config.parse_args(argv)

    engine = create_engine(cfg.CONF.database.connection)

    conn = engine.connect()
    try:
        conn.execute("CREATE DATABASE cerberus")
    except Exception:
        pass

    conn.close()

if __name__ == '__main__':
    main()
