import aiohttp


class Crawler:
    @staticmethod
    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            html = await response.text()
            return html
