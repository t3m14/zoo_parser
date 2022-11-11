import aiohttp
import asyncio
from utils.load_config import get_json
retries = get_json()["max_retries"]
# Ассинхронное получение html
async def get_html(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                text = await response.text()
                return text
        except Exception as e:
            print(e)
            global retries
            if retries > 0:
                await asyncio.sleep(10)
                await get_html(url)
                retries -= 1
            else:
                retries = get_json()["max_retries"]
                return
# import requests
# async def get_html(url):
#     await asyncio.sleep(0)
#     return requests.get(url).text