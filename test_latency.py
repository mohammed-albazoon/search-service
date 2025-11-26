import asyncio
import time
from app.searcher import search  # make sure this path is correct

async def main():
    query = "test"
    page = 1
    page_size = 10

    start = time.perf_counter()
    total, results = await search(query, page=page, page_size=page_size)
    end = time.perf_counter()

    print(f"Returned {len(results)} results in {(end - start)*1000:.2f} ms")

asyncio.run(main())
