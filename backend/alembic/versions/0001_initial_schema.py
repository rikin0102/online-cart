"""Initial database schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-08 18:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    # 1. users table
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. products table (baseline without image_url)
    if 'products' not in existing_tables:
        op.create_table(
            'products',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('category', sa.String(length=100), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
        op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)

    # 3. cart_items table
    if 'cart_items' not in existing_tables:
        op.create_table(
            'cart_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('product_id', sa.Integer(), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'product_id', name='uq_user_product_cart')
        )
        op.create_index(op.f('ix_cart_items_id'), 'cart_items', ['id'], unique=False)
        op.create_index(op.f('ix_cart_items_user_id'), 'cart_items', ['user_id'], unique=False)
        op.create_index(op.f('ix_cart_items_product_id'), 'cart_items', ['product_id'], unique=False)

    # 4. orders table
    if 'orders' not in existing_tables:
        op.create_table(
            'orders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('grand_total', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('email_status', sa.String(length=20), nullable=False, server_default='failed'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
        op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)

    # 5. order_items table
    if 'order_items' not in existing_tables:
        op.create_table(
            'order_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('product_name', sa.String(length=255), nullable=False),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('line_total', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)
        op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)


def downgrade() -> None:
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('cart_items')
    op.drop_table('products')
    op.drop_table('users')
