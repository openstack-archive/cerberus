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

"""initial_migration

Revision ID: 2dd6320a2745
Revises: None
Create Date: 2015-06-25 10:45:10.853595

"""

# revision identifiers, used by Alembic.
revision = '2dd6320a2745'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'plugin_info',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.Text),
        sa.Column('name', sa.Text),
        sa.Column('version', sa.Text),
        sa.Column('provider', sa.Text),
        sa.Column('type', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('tool_name', sa.Text),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('deleted', sa.Integer),
        mysql_ENGINE='InnoDB',
        mysql_DEFAULT_CHARSET='utf8'
    )
    op.create_table(
        'security_report',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('plugin_id', sa.Text),
        sa.Column('report_id', sa.VARCHAR(255), unique=True),
        sa.Column('component_id', sa.Text),
        sa.Column('component_type', sa.Text),
        sa.Column('component_name', sa.Text),
        sa.Column('project_id', sa.Text),
        sa.Column('title', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('security_rating', sa.Float),
        sa.Column('vulnerabilities', sa.Text),
        sa.Column('vulnerabilities_number', sa.Integer),
        sa.Column('last_report_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('deleted', sa.Integer),
        mysql_ENGINE='InnoDB',
        mysql_DEFAULT_CHARSET='UTF8'
    )
    op.create_table(
        'security_alarm',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('plugin_id', sa.Text),
        sa.Column('alarm_id', sa.VARCHAR(255), unique=True),
        sa.Column('component_id', sa.Text),
        sa.Column('project_id', sa.Text),
        sa.Column('ticket_id', sa.Text),
        sa.Column('timestamp', sa.DateTime),
        sa.Column('summary', sa.Text),
        sa.Column('severity', sa.Text),
        sa.Column('status', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('deleted', sa.Integer),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    op.create_table(
        'task',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('type', sa.Text),
        sa.Column('plugin_id', sa.Text),
        sa.Column('uuid', sa.Text),
        sa.Column('name', sa.Text),
        sa.Column('method', sa.Text),
        sa.Column('running', sa.Boolean),
        sa.Column('period', sa.Integer),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('deleted', sa.Integer),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )


def downgrade():
    raise NotImplementedError(('Downgrade from initial migration is'
                              ' unsupported.'))
