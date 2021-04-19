from web_crawler.lol_crawlers.opgg import OpggCrawler
from web_crawler.lol_crawlers.ugg import UggCrawler


class LolCrawler:
    def __init__(self):
        self.regions = ["eune", "euw", "na", "kr", "oce", "br", "tr"]
        self.opgg = OpggCrawler()
        self.ugg = UggCrawler()

    async def fetch_summoner(self, summoner_name, region="EUNE", rank_type="Ranked Solo"):
        return await self.opgg.fetch_summoner(summoner_name, region, rank_type)

    async def fetch_build(self, champion_name, lane=""):
        return await self.opgg.fetch_build(champion_name, lane)
