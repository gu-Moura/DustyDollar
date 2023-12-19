"""empty message

Revision ID: 2e6d9d2643b3
Revises: 02a5a4c6e748
Create Date: 2023-12-18 11:48:36.153947

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2e6d9d2643b3'
down_revision = '02a5a4c6e748'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conta', schema=None) as batch_op:
        batch_op.alter_column('limite_saque_diario',
               existing_type=mysql.DECIMAL(precision=10, scale=0),
               type_=sa.DECIMAL(precision=10, scale=2),
               existing_nullable=True)

    with op.batch_alter_table('transacao', schema=None) as batch_op:
        batch_op.alter_column('valor',
               existing_type=mysql.DECIMAL(precision=10, scale=0),
               type_=sa.DECIMAL(precision=10, scale=2),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transacao', schema=None) as batch_op:
        batch_op.alter_column('valor',
               existing_type=sa.DECIMAL(precision=10, scale=2),
               type_=mysql.DECIMAL(precision=10, scale=0),
               existing_nullable=False)

    with op.batch_alter_table('conta', schema=None) as batch_op:
        batch_op.alter_column('limite_saque_diario',
               existing_type=sa.DECIMAL(precision=10, scale=2),
               type_=mysql.DECIMAL(precision=10, scale=0),
               existing_nullable=True)

    # ### end Alembic commands ###
