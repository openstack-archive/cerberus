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

"""text_to_varchar

Revision ID: 4426f811d4d9
Revises: 2dd6320a2745
Create Date: 2015-06-25 10:47:00.485303

"""

# revision identifiers, used by Alembic.
revision = '4426f811d4d9'
down_revision = '2dd6320a2745'

from alembic import op
import sqlalchemy as sa


def upgrade():

    # In table plugin_info
    op.alter_column(
        table_name='plugin_info',
        column_name='uuid',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='name',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='version',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='provider',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='type',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='description',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='tool_name',
        type_=sa.VARCHAR(255)
    )

    # In table security_report, except column vulnerabilities
    op.alter_column(
        table_name='security_report',
        column_name='plugin_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_report',
        column_name='component_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_report',
        column_name='component_type',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_report',
        column_name='component_name',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_report',
        column_name='project_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_report',
        column_name='title',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_report',
        column_name='description',
        type_=sa.VARCHAR(255)
    )

    # In table security_alarm
    op.alter_column(
        table_name='security_alarm',
        column_name='plugin_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='component_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='project_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='ticket_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='summary',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='severity',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='status',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='description',
        type_=sa.VARCHAR(255)
    )

    # In table task
    op.alter_column(
        table_name='task',
        column_name='type',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='task',
        column_name='plugin_id',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='task',
        column_name='uuid',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='task',
        column_name='name',
        type_=sa.VARCHAR(255)
    )
    op.alter_column(
        table_name='task',
        column_name='method',
        type_=sa.VARCHAR(255)
    )


def downgrade():
    # In table plugin_info
    op.alter_column(
        table_name='plugin_info',
        column_name='uuid',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='name',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='version',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='provider',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='type',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='description',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='plugin_info',
        column_name='tool_name',
        type_=sa.TEXT
    )

    # In table security_report, except column vulnerabilities (still Text)
    # and report_id (already varchar)
    op.alter_column(
        table_name='security_report',
        column_name='plugin_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_report',
        column_name='component_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_report',
        column_name='component_type',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_report',
        column_name='component_name',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_report',
        column_name='project_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_report',
        column_name='title',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_report',
        column_name='description',
        type_=sa.TEXT
    )

    # In table security_alarm, except alarm_id (already varchar)
    op.alter_column(
        table_name='security_alarm',
        column_name='plugin_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='component_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='project_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='ticket_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='summary',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='severity',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='status',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='security_alarm',
        column_name='description',
        type_=sa.TEXT
    )

    # In table task
    op.alter_column(
        table_name='task',
        column_name='type',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='task',
        column_name='plugin_id',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='task',
        column_name='uuid',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='task',
        column_name='name',
        type_=sa.TEXT
    )
    op.alter_column(
        table_name='task',
        column_name='method',
        type_=sa.TEXT
    )
