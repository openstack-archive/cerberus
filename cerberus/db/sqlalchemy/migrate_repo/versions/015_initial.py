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

import sqlalchemy


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    plugin_info = sqlalchemy.Table(
        'plugin_info', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True,
                          nullable=False),
        sqlalchemy.Column('uuid', sqlalchemy.Text),
        sqlalchemy.Column('name', sqlalchemy.Text),
        sqlalchemy.Column('version', sqlalchemy.Integer),
        sqlalchemy.Column('provider', sqlalchemy.DateTime),
        sqlalchemy.Column('type', sqlalchemy.Text),
        sqlalchemy.Column('description', sqlalchemy.Text),
        sqlalchemy.Column('tool_name', sqlalchemy.Text),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted', sqlalchemy.Integer),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    security_report = sqlalchemy.Table(
        'security_report', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True,
                          nullable=False),
        sqlalchemy.Column('plugin_id', sqlalchemy.Text),
        sqlalchemy.Column('report_id', sqlalchemy.Text, unique=True),
        sqlalchemy.Column('component_id', sqlalchemy.Text),
        sqlalchemy.Column('component_type', sqlalchemy.Text),
        sqlalchemy.Column('component_name', sqlalchemy.Text),
        sqlalchemy.Column('project_id', sqlalchemy.Text),
        sqlalchemy.Column('title', sqlalchemy.Text),
        sqlalchemy.Column('description', sqlalchemy.Text),
        sqlalchemy.Column('security_rating', sqlalchemy.Float),
        sqlalchemy.Column('vulnerabilities', sqlalchemy.Text),
        sqlalchemy.Column('vulnerabilities_number', sqlalchemy.Integer),
        sqlalchemy.Column('last_report_date', sqlalchemy.DateTime),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted', sqlalchemy.Integer),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    tables = (
        security_report,
        plugin_info,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise


def downgrade(migrate_engine):
    raise NotImplementedError('Database downgrade not supported - '
                              'would drop all tables')
