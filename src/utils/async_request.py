import aiohttp
# Ассинхронное получение html
async def get_html(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            return text
