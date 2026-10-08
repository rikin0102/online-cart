"""Add image_url to products table

Revision ID: 0002_add_image_url_to_products
Revises: 0001_initial_schema
Create Date: 2026-10-08 18:12:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = '0002_add_image_url_to_products'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('products')]

    if 'image_url' not in columns:
        op.add_column(
            'products',
            sa.Column('image_url', sa.String(length=500), nullable=True)
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('products')]

    if 'image_url' in columns:
        op.drop_column('products', 'image_url')
