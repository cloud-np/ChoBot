# import requests
import aiohttp
from decouple import config
from dataclasses import dataclass
import utils.utils as ut
from bs4 import BeautifulSoup


@dataclass(frozen=True, order=True)
class Champion:
    name: str
    icon: str
    win_ratio: str
    kda: str
    cs: str
    games: str


@dataclass(frozen=True, order=True)
class Summoner:
    name: str
    elo: str
    win_ratio: str
    profile_icon: str
    elo_icon: str
    server: str
    ladder_rank: str
    most_played_champs: list


class OpggCrawler:

    def __init__(self):
        # The empty one -> '' is kr.
        self.servers = ["eune", "euw", "na", '', "oce", "br", "tr"]
        self.base_url = config("OPGG_BASE_URL")
        self.summoner_url = config("OPGG_SUMMONER_URL")
        self.champion_url = config("OPGG_CHAMPION_URL")
        self.profile_icons = config("OPGG_PROFILE_ICON_URL")
        self.elo_icons_url = config("OPGG_ELO_ICON_URL")
        self.champion_icon_url = config("OPGG_CHAMPION_ICON_URL")

    @staticmethod
    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            html = await response.text()
            return html

    @staticmethod
    def find_kda(kda_soup):
        kda_each = kda_soup.find("div", class_="KDAEach")
        kill = kda_each.find("span", class_="Kill").text
        death = kda_each.find("span", class_="Death").text
        assist = kda_each.find("span", class_="Assist").text
        return f"{kill} / {death} / {assist}"

    @staticmethod
    def find_played(played_soup):
        win_ratio = ut.rspaces(played_soup.find("div", class_="WinRatio").text)
        games = played_soup.find("div", class_="Title").text.replace("Played", "Games")
        return {"win_ratio": win_ratio, "games": games}

    @staticmethod
    def find_champions(soup):
        champions = list()
        if soup.find(class_="MostChampionContent") is not None:
            most_played_champs = soup.find_all("div", class_=lambda class_: class_ and "ChampionBox" in class_)
            for champ_box in most_played_champs:
                c_name = champ_box.find("div", class_="ChampionName")['title']
                c_icon = 'https:' + champ_box.find("div", class_="Face").a.img['src']
                c_played = OpggCrawler.find_played(champ_box.find("div", class_="Played"))
                c_kda = OpggCrawler.find_kda(champ_box.find("div", class_="PersonalKDA"))
                c_cs = ut.rss(champ_box.find("div", class_="ChampionMinionKill").text).split()[1]
                champions.append(Champion(name=c_name, icon=c_icon, win_ratio=c_played["win_ratio"], games=c_played["games"], kda=c_kda, cs=c_cs))
        return champions

    @staticmethod
    def find_ladder_rank(soup):
        ladder_con = soup.find("div", class_="LadderRank")
        if ladder_con is not None:
            top = ut.rss(ladder_con.a.contents[2])
            ranking = ladder_con.a.span.text
            ladder_rank = f"Ladder Rank {ranking} {top}"
        else:
            ladder_rank = ""
        return ladder_rank

    @staticmethod
    def find_win_ratio(tier_box):
        wins = tier_box.find("span", class_="wins").text
        losses = tier_box.find("span", class_="losses").text
        winratio = tier_box.find("span", class_="winratio").text
        return f"{wins} {losses} ({winratio})"

    @staticmethod
    def find_tier_box(soup):
        tier_box = soup.find("div", class_="TierBox")
        tier_info = tier_box.find("div", class_="TierInfo")
        img = tier_box.find("div", class_="Medal").img['src']
        elo = tier_box.find("div", class_="TierRank").text
        win_ratio = ""

        if elo != "Unranked":
            elo += " " + ut.rss(tier_info.find("span", class_="LeaguePoints").text)
            win_ratio = OpggCrawler.find_win_ratio(tier_info)

        return {"elo_icon": "http:" + img, "win_ratio": win_ratio, "elo": elo}

    async def fetch_summoner(self, summoner_name, server="eune", rank_type="Ranked Solo"):
        print("summoner: " + summoner_name)
        print("server: " + server)
        page = await self.fetch(self.summoner_url.replace("$SERVER", server.lower()) + summoner_name.replace(' ', '%20'))
        soup = BeautifulSoup(page, "html.parser")

        # Most played champions
        champions = OpggCrawler.find_champions(soup)

        # Ladder Rank
        ladder_rank = OpggCrawler.find_ladder_rank(soup)

        # Summoner Icon
        profile_icon = "http:" + soup.find("img", class_="ProfileImage")['src']

        # Elo Icon / WinRatio / Elo
        tier = OpggCrawler.find_tier_box(soup)

        # summoner = Summoner(name=summoner_name, server=server)
        return Summoner(
            name=summoner_name,
            elo=tier["elo"],
            win_ratio=tier["win_ratio"],
            profile_icon=profile_icon,
            elo_icon=tier["elo_icon"],
            server=server,
            ladder_rank=ladder_rank,
            most_played_champs=champions)

    def get_champion_url(self, champion):
        pass
        # return self.champion_url.replace("$CHAMPION", champion.lower().replace(' ', ''))
