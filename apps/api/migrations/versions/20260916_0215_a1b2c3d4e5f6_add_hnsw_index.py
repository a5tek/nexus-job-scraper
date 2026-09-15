"""add_hnsw_index

Revision ID: a1b2c3d4e5f6
Revises: ce6fca3453b7
Create Date: 2026-09-16 02:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ce6fca3453b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # HNSW indexes with vector_cosine_ops are specific to PostgreSQL + pgvector
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_listings_embedding_hnsw 
            ON listings 
            USING hnsw (embedding vector_cosine_ops) 
            WITH (m = 16, ef_construction = 64);
            """
        )
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_resumes_embedding_hnsw 
            ON resumes 
            USING hnsw (embedding vector_cosine_ops) 
            WITH (m = 16, ef_construction = 64);
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_listings_embedding_hnsw;")
        op.execute("DROP INDEX IF EXISTS ix_resumes_embedding_hnsw;")
