"""profile completeness, default values

Revision ID: d9910c18ba5e
Revises: 14dede4adbcb
Create Date: 2024-09-19 13:07:51.267914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9910c18ba5e'
down_revision = '14dede4adbcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_complete', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('is_oidc', sa.Boolean(), server_default='0', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_oidc')
        batch_op.drop_column('profile_complete')

    # ### end Alembic commands ###