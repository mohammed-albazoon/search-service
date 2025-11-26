import os
import aiosqlite
import asyncio
import random
import httpx
from typing import Any
from .config import settings

# -----------------------------
# Database schema (messages + FTS)
# -----------------------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    title TEXT,
    body TEXT,
    raw JSON
);
"""

CREATE_FTS_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    title, body, content='messages', content_rowid='rowid'
);
"""

CREATE_TRIGGER_INSERT = """
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
  INSERT INTO messages_fts(rowid, title, body)
  VALUES (new.rowid, new.title, new.body);
END;
"""

CREATE_TRIGGER_DELETE = """
CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, title, body)
  VALUES ('delete', old.rowid, old.title, old.body);
END;
"""

CREATE_TRIGGER_UPDATE = """
CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, title, body)
  VALUES ('delete', old.rowid, old.title, old.body);
  INSERT INTO messages_fts(rowid, title, body)
  VALUES (new.rowid, new.title, new.body);
END;
"""

# -----------------------------
# DB Initialization
# -----------------------------

async def init_db():
    os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH) or ".", exist_ok=True)
    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        await db.executescript(
            "\n".join([
                CREATE_TABLE_SQL,
                CREATE_FTS_SQL,
                CREATE_TRIGGER_INSERT,
                CREATE_TRIGGER_DELETE,
                CREATE_TRIGGER_UPDATE
            ])
        )
        await db.commit()

# -----------------------------
# Remote API fetcher with retry & delays
# -----------------------------

async def fetch_page(page: int, page_size: int = settings.MAX_PAGE_SIZE):
    """
    Fetch a page from the remote API with realistic headers and retry to avoid 403.
    """
    url = f"{settings.MESSAGES_API_BASE}{settings.MESSAGES_ENDPOINT}"
    params = {"page": page, "page_size": page_size}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    retries = 3
    for attempt in range(1, retries + 1):
        # Random delay to avoid rate-limits
        await asyncio.sleep(random.uniform(0.2, 1.5))
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 403:
                    print(f"❌ 403 Forbidden on page {page} (attempt {attempt}). Retrying after 5s...")
                    await asyncio.sleep(5)
                    continue
                elif status == 402:
                    print(f"ℹ️ 402 Payment Required on page {page}. Stopping pagination.")
                    return None
                else:
                    print(f"❌ HTTP {status} on page {page}: {exc}")
                    return None

            except Exception as e:
                print(f"❌ Network error on page {page} (attempt {attempt}): {e}")
                await asyncio.sleep(2)
                continue

    print(f"⛔ Giving up on page {page} after {retries} attempts.")
    return None

# -----------------------------
# JSON helper
# -----------------------------

def json_dumps(obj):
    import json
    return json.dumps(obj, ensure_ascii=False)

# -----------------------------
# Indexer: Remote → SQLite
# -----------------------------

async def index_from_remote():
    page = 1
    per_page = settings.MAX_PAGE_SIZE
    total_indexed = 0

    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        while True:
            data = await fetch_page(page, per_page)

            if not data:
                break

            # Detect API response shape
            if isinstance(data, dict) and "items" in data:
                items = data["items"]
            elif isinstance(data, dict) and "results" in data:
                items = data["results"]
            elif isinstance(data, list):
                items = data
            else:
                items = data.get("data") if hasattr(data, "get") else []

            if not items:
                break

            # Insert items into DB
            async with db.execute("BEGIN"):
                for item in items:
                    id_ = str(
                        item.get("id")
                        or item.get("_id")
                        or item.get("message_id")
                        or ""
                    )
                    title = item.get("title") or ""
                    body = item.get("body") or item.get("text") or item.get("message") or ""

                    await db.execute(
                        "INSERT OR REPLACE INTO messages(id, title, body, raw)"
                        " VALUES (?, ?, ?, ?)",
                        (id_, title, body, json_dumps(item))
                    )
                    total_indexed += 1

                await db.commit()

            page += 1

    return total_indexed
