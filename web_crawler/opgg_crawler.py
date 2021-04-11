import requests
from decouple import config
import utils as ut
from bs4 import BeautifulSoup


class OpggCrawler:

    def __init__(self, server="eune"):
        self.server = server
        self.setup_urls(self.server)

    def setup_urls_server(self, server):
        self.server = server
        self.base_URL = config("BASE_URL").replace("$SERVER", self.server)
        self.summoner_base_URL = config("SUMMONER_BASE_URL").replace("$SERVER", self.server)
        self.champion_base_URL = config("CHAMPION_BASE_URL").replace("$SERVER", self.server)

    def get_summoner_soup(self, summoner_name):
        page = requests.get(self.summoner_base_URL + summoner_name.replace(' ', '%20'))
        return BeautifulSoup(page.content, "html.parser")

    def get_summoner_info_for_discord(self, summoner_name):
        soup = self.get_summoner_soup(summoner_name)

        try:
            text = soup.find(class_="TierRankInfo").text
        except Exception:
            return ''
        return ut.format_summoner(summoner_name, "".join([text]))

    def get_champion_url(self, champion):
        return self.champion_base_URL.replace("$CHAMPION", champion.replace(' ', ''))
