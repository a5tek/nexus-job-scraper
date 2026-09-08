import json
from typing import List, Optional
from sqlalchemy import TypeDecorator, Text
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

try:
    from pgvector.sqlalchemy import Vector as PgVector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    PgVector = None


class CompatibleVector(TypeDecorator):
    """
    Vector type that uses pgvector.sqlalchemy.Vector on PostgreSQL,
    and falls back to JSON-serialized floats on SQLite or other engines for testing.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dim: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return dialect.type_descriptor(PgVector(self.dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Optional[List[float]], dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        # In SQLite/fallback, serialize list of floats to JSON text
        return json.dumps([float(x) for x in value])

    def process_result_value(self, value, dialect) -> Optional[List[float]]:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [float(x) for x in parsed]
            except Exception:
                # Handle pgvector string representation like "[0.1,0.2,...]"
                cleaned = value.strip("[]").split(",")
                return [float(x.strip()) for x in cleaned if x.strip()]
        return value
