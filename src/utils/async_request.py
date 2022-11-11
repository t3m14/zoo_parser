import aiohttp
import requests
import asyncio
# Ассинхронное получение html
# async def get_html(url: str):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             text = await response.text()
#             return text
async def get_html(url):
    await asyncio.sleep(0)
    return requests.get(url).text