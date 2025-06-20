"""initial

Revision ID: 4e17150d54cb
Revises: 
Create Date: 2025-05-25 04:00:26.289403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e17150d54cb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('profile_pic', sa.String(length=200), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.Column('oauth_login', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('decks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('public', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('front', sa.Text(), nullable=True),
    sa.Column('back', sa.Text(), nullable=True),
    sa.Column('deck_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('deck_id', sa.Integer(), nullable=True),
    sa.Column('studied', sa.Integer(), nullable=True),
    sa.Column('correct', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('progress')
    op.drop_table('cards')
    op.drop_table('decks')
    op.drop_table('users')
    # ### end Alembic commands ###
