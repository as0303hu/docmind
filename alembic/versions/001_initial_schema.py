"""Create documents and chunks tables.

Revision ID:001
Create Date: 2024-01-01
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision ="001"
down_revesion = None
branch_labels = None
depends_on = None

def upgrade()->None:
    op.execute("CREATE EXTERNSION IF NOT EXISTS vector")
    
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("filename",sa.String,nullable=False),
        sa.Column("file_size",sa.Integer, nullable=False),
        sa.Column("page_count", sa.Integer, nullable=False),
        sa.Column("chunk_count", sa.Integer,nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),server_default=sa.text("now()"))
    )
    op.create_table(
        "chunks",
        sa.Column("id",sa.Uuid,primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", sa.Text, sa.ForeignKey("documents.id", ondelete="CASCADE"),nullable=False),
        sa.Column("content",sa.Text,nullable=False),
        sa.Column("page_number",sa.Integer,nullable=False),
        sa.Column("chunk_index",sa.Integer,nullable=False),
        sa.Column("embedding",Vector(1536)),
        sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()")),
    )
    
    op.create_index("ix_chunks_document_id","chunks",["document_id"])
    
    def downgrade()->None:
        op.drop_table("chunks")
        op.drop_table("documnets")