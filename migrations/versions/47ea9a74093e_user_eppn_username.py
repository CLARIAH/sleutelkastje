"""user eppn-username

Revision ID: 47ea9a74093e
Revises: 33692aa70451
Create Date: 2024-08-28 11:19:36.971666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47ea9a74093e'
down_revision = '33692aa70451'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(), nullable=False))
        batch_op.drop_constraint('user_eppn_key', type_='unique')
        batch_op.create_unique_constraint(None, ['username'])
        batch_op.drop_column('eppn')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('eppn', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('user_eppn_key', ['eppn'])
        batch_op.drop_column('username')

    # ### end Alembic commands ###
