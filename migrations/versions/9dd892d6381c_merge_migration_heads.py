"""merge migration heads

Revision ID: 9dd892d6381c
Revises: 06473eb5f032, 16e8d4ab9a00
Create Date: 2025-05-27 14:55:02.677604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dd892d6381c'
down_revision = ('06473eb5f032', '16e8d4ab9a00')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
