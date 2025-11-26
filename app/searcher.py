import aiosqlite
from .config import settings
from typing import List, Tuple
from .models import MessageRecord

# -----------------------------
# Search function using FTS5
# -----------------------------

async def search(query: str, page: int = 1, page_size: int = 20) -> Tuple[int, List[MessageRecord]]:
    """
    Search messages using SQLite FTS5.
    Returns total count and a list of MessageRecord objects with pagination.
    """
    offset = (page - 1) * page_size
    q = query.strip()
    
    if not q:
        return 0, []

    # Escape quotes for FTS5 MATCH
    q_escaped = q.replace('"', '""')

    # Use parameterized queries safely
    count_sql = "SELECT COUNT(*) as cnt FROM messages_fts WHERE messages_fts MATCH ?;"
    select_sql = """
    SELECT m.id, m.title, m.body
    FROM messages_fts f
    JOIN messages m ON f.rowid = m.rowid
    WHERE f MATCH ?
    LIMIT ? OFFSET ?;
    """

    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get total matching count
        cur = await db.execute(count_sql, (q_escaped,))
        row = await cur.fetchone()
        total = row["cnt"] if row else 0

        # Fetch paginated results
        cur = await db.execute(select_sql, (q_escaped, page_size, offset))
        rows = await cur.fetchall()

        results = [
            MessageRecord(id=r["id"], title=r["title"], body=r["body"])
            for r in rows
        ]

    return total, results
