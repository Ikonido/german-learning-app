"""Initial schema: users, words, noun_details, verb_details, user_progress

Revision ID: 20260604_193510
Revises: 
Create Date: 2026-06-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20260604_193510'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    word_type_enum = postgresql.ENUM('noun', 'verb', name='wordtype', create_type=True)
    gender_enum = postgresql.ENUM('der', 'die', 'das', name='gender', create_type=True)
    auxiliary_enum = postgresql.ENUM('haben', 'sein', name='auxiliary', create_type=True)

    word_type_enum.create(op.get_bind(), checkfirst=True)
    gender_enum.create(op.get_bind(), checkfirst=True)
    auxiliary_enum.create(op.get_bind(), checkfirst=True)

    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # words
    op.create_table(
        'words',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('german', sa.String(length=255), nullable=False),
        sa.Column('translation', sa.Text(), nullable=False),
        sa.Column('word_type', word_type_enum, nullable=False),
        sa.Column('level', sa.String(length=10), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('example_sentence', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_words_id'), 'words', ['id'], unique=False)
    op.create_index(op.f('ix_words_german'), 'words', ['german'], unique=False)
    op.create_index(op.f('ix_words_word_type'), 'words', ['word_type'], unique=False)
    op.create_index(op.f('ix_words_level'), 'words', ['level'], unique=False)

    # noun_details
    op.create_table(
        'noun_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('word_id', sa.Integer(), nullable=False),
        sa.Column('gender', gender_enum, nullable=False),
        sa.Column('plural', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word_id')
    )
    op.create_index(op.f('ix_noun_details_word_id'), 'noun_details', ['word_id'], unique=False)

    # verb_details
    op.create_table(
        'verb_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('word_id', sa.Integer(), nullable=False),
        sa.Column('praeteritum', sa.String(length=255), nullable=False),
        sa.Column('perfekt', sa.String(length=255), nullable=False),
        sa.Column('auxiliary', auxiliary_enum, nullable=False),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word_id')
    )
    op.create_index(op.f('ix_verb_details_word_id'), 'verb_details', ['word_id'], unique=False)

    # user_progress
    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('word_id', sa.Integer(), nullable=False),
        sa.Column('ease_factor', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('interval_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('repetitions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_review_date', sa.Date(), nullable=True),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('incorrect_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'word_id', name='uq_user_word_progress')
    )
    op.create_index(op.f('ix_user_progress_user_id'), 'user_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_progress_word_id'), 'user_progress', ['word_id'], unique=False)
    op.create_index(op.f('ix_user_progress_next_review_date'), 'user_progress', ['next_review_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_progress_next_review_date'), table_name='user_progress')
    op.drop_index(op.f('ix_user_progress_word_id'), table_name='user_progress')
    op.drop_index(op.f('ix_user_progress_user_id'), table_name='user_progress')
    op.drop_table('user_progress')

    op.drop_index(op.f('ix_verb_details_word_id'), table_name='verb_details')
    op.drop_table('verb_details')

    op.drop_index(op.f('ix_noun_details_word_id'), table_name='noun_details')
    op.drop_table('noun_details')

    op.drop_index(op.f('ix_words_level'), table_name='words')
    op.drop_index(op.f('ix_words_word_type'), table_name='words')
    op.drop_index(op.f('ix_words_german'), table_name='words')
    op.drop_index(op.f('ix_words_id'), table_name='words')
    op.drop_table('words')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    # Drop enums (best effort)
    op.execute("DROP TYPE IF EXISTS auxiliary")
    op.execute("DROP TYPE IF EXISTS gender")
    op.execute("DROP TYPE IF EXISTS wordtype")
