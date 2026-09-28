import httpx
import asyncio

async def fetch_status(client: httpx.AsyncClient, url: str) -> int:
    response = await client.get(url)
    return response.status_code

async def fetch_all(urls: list[str]) -> list[int]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        coroutines = [fetch_status(client, url) for url in urls]
        results = await asyncio.gather(*coroutines)
        return results
    
async def fetch_sequential(urls: list[str]) -> list[int]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        return [await fetch_status(client, url) for url in urls]