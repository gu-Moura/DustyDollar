"""empty message

Revision ID: 39e731e15a00
Revises: b49212af82db
Create Date: 2023-12-21 16:21:56.006907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39e731e15a00'
down_revision = 'b49212af82db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('teste', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conta', schema=None) as batch_op:
        batch_op.drop_column('teste')

    # ### end Alembic commands ###
