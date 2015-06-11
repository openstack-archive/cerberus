#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


def upgrade(migrate_engine):

    if migrate_engine.name == "mysql":
        security_report = 'security_report'
        sql = "ALTER TABLE %s ADD uuid VARCHAR(255)" \
              " NOT NULL AFTER id," \
              "ADD UNIQUE(uuid);" % security_report
        sql += "ALTER TABLE %s DROP INDEX report_id;" % security_report
        sql += "ALTER TABLE %s ADD UNIQUE (report_id, plugin_id);" \
               % security_report
        migrate_engine.execute(sql)


def downgrade(migrate_engine):
    raise NotImplementedError('Database downgrade not supported - '
                              'would drop all tables')
