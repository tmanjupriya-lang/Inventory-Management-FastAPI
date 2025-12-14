"""normalize schema with consistent IDs

Revision ID: 108fd17cba39
Revises: d182008d0ad3
Create Date: 2025-11-19 12:19:34.976044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '108fd17cba39'
down_revision: Union[str, None] = 'd182008d0ad3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- CART ---
    op.add_column('cart', sa.Column('cart_id', sa.Integer(), nullable=False))
    op.drop_index(op.f('ix_cart_id'), table_name='cart')
    op.create_index(op.f('ix_cart_cart_id'), 'cart', ['cart_id'], unique=False)
    op.drop_column('cart', 'id')

    # --- PRODUCTS ---
    op.add_column('products', sa.Column('product_id', sa.Integer(), nullable=False))
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.create_index(op.f('ix_products_product_id'), 'products', ['product_id'], unique=False)
    op.drop_column('products', 'id')

    # --- PURCHASE HISTORY ---
    op.add_column('purchase_history', sa.Column('purchase_id', sa.Integer(), nullable=False))
    op.drop_index(op.f('ix_purchase_history_id'), table_name='purchase_history')
    op.create_index(op.f('ix_purchase_history_purchase_id'), 'purchase_history', ['purchase_id'], unique=False)
    op.drop_column('purchase_history', 'id')

    # --- FOREIGN KEYS (after new PKs exist) ---
    op.drop_constraint(op.f('cart_product_id_fkey'), 'cart', type_='foreignkey')
    op.drop_constraint(op.f('cart_user_id_fkey'), 'cart', type_='foreignkey')
    op.create_foreign_key(None, 'cart', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'cart', 'products', ['product_id'], ['product_id'], ondelete='CASCADE')

    op.drop_constraint(op.f('purchase_history_product_id_fkey'), 'purchase_history', type_='foreignkey')
    op.create_foreign_key(None, 'purchase_history', 'products', ['product_id'], ['product_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'purchase_history', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')

    # --- USERS ---
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)



def downgrade() -> None:
    """Downgrade schema."""

    # --- USERS ---
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # --- PURCHASE HISTORY ---
    op.drop_constraint(None, 'purchase_history', type_='foreignkey')
    op.drop_constraint(None, 'purchase_history', type_='foreignkey')
    op.add_column('purchase_history', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_index(op.f('ix_purchase_history_purchase_id'), table_name='purchase_history')
    op.create_index(op.f('ix_purchase_history_id'), 'purchase_history', ['id'], unique=False)
    op.create_foreign_key(op.f('purchase_history_product_id_fkey'), 'purchase_history', 'products', ['product_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('purchase_history_user_id_fkey'), 'purchase_history', 'users', ['user_id'], ['user_id'])
    op.drop_column('purchase_history', 'purchase_id')

    # --- PRODUCTS ---
    op.add_column('products', sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('products_id_seq'::regclass)"), autoincrement=True, nullable=False))
    op.drop_index(op.f('ix_products_product_id'), table_name='products')
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.drop_column('products', 'product_id')

    # --- CART ---
    op.drop_constraint(None, 'cart', type_='foreignkey')
    op.drop_constraint(None, 'cart', type_='foreignkey')
    op.add_column('cart', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_index(op.f('ix_cart_cart_id'), table_name='cart')
    op.create_index(op.f('ix_cart_id'), 'cart', ['id'], unique=False)
    op.create_foreign_key(op.f('cart_user_id_fkey'), 'cart', 'users', ['user_id'], ['user_id'])
    op.create_foreign_key(op.f('cart_product_id_fkey'), 'cart', 'products', ['product_id'], ['id'])
    op.drop_column('cart', 'cart_id')
