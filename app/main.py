import asyncio
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from .config import settings
from .indexer import init_db, index_from_remote
from .searcher import search
from .models import SearchResult, MessageRecord

app = FastAPI(title="Simple Search Service", version="0.1.0")

# On startup: initialize DB and optionally index
@app.on_event("startup")
async def startup_event():
    await init_db()
    if settings.REINDEX_ON_START:
        # run indexing in background but block until initial index built for low-latency searches
        # Do this synchronously (await) to ensure index available immediately.
        try:
            n = await index_from_remote()
            print(f"Indexed {n} records from remote.")
        except Exception as e:
            print("Indexing failed on startup:", e)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/search", response_model=SearchResult)
async def api_search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE)
):
    try:
        total, results = await search(q, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return SearchResult(total=total, page=page, page_size=page_size, results=results)
