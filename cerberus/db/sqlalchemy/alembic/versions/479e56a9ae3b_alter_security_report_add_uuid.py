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

"""alter_security_report_add_uuid

Revision ID: 479e56a9ae3b
Revises: 4426f811d4d9
Create Date: 2015-06-25 10:48:06.260041

"""

# revision identifiers, used by Alembic.
revision = '479e56a9ae3b'
down_revision = '4426f811d4d9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('security_report',
                  sa.Column('uuid', sa.VARCHAR(255), unique=True))
    op.drop_constraint('report_id', 'security_report', type_='unique')
    op.create_unique_constraint('unique_uuid',
                                'security_report',
                                ['uuid'])
    op.create_unique_constraint('unique_report_id_plugin_id',
                                'security_report',
                                ['report_id', 'plugin_id'])


def downgrade():
    op.drop_column('security_report', 'uuid')
    op.drop_constraint('unique_report_id_plugin_id',
                       'security_report',
                       type_='unique')
    op.create_unique_constraint('report_id', 'security_report', ['report_id'])
