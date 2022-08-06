"""empty message

Revision ID: 98f2435e681d
Revises: 
Create Date: 2022-08-04 13:18:38.210112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98f2435e681d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('images', sa.UnicodeText(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('images')
    # ### end Alembic commands ###
