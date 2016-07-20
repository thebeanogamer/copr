"""last_deferred column added for BuildChroot

Revision ID: 1ff696f006f1
Revises: 1c61e5b88e45
Create Date: 2016-06-28 21:04:27.036088

"""

# revision identifiers, used by Alembic.
revision = '1ff696f006f1'
down_revision = '1ea00801be9e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('build_chroot', sa.Column('last_deferred', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('build_chroot', 'last_deferred')
    ### end Alembic commands ###
