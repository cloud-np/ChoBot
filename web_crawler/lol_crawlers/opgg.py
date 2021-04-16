from decouple import config
from web_crawler.crawler import Crawler
from bs4 import BeautifulSoup
import re
from classes.lol_classes import (
    SummonerChampion,
    Summoner,
    RunePage,
    ChampionBuild,
    ItemBuild,
)
import utils.utils as ut

SHARDS_CODES = {
    "5001": "Health",
    "5002": "Armor",
    "5003": "MagicResist",
    "5005": "AttackSpeed",
    "5007": "AbilityHaste",
    "5008": "AdaptiveForce",
}


class OpggCrawler:
    def __init__(self):
        self.base_url = config("OPGG_BASE_URL")
        self.summoner_url = config("OPGG_SUMMONER_URL")
        self.champion_url = config("OPGG_CHAMPION_URL")
        self.profile_icons = config("OPGG_PROFILE_ICON_URL")
        self.elo_icons_url = config("OPGG_ELO_ICON_URL")
        self.champion_icon_url = config("OPGG_CHAMPION_ICON_URL")

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
            most_played_champs = soup.find_all(
                "div", class_=lambda class_: class_ and "ChampionBox" in class_
            )
            for champ_box in most_played_champs:
                c_name = champ_box.find("div", class_="ChampionName")["title"]
                c_icon = "https:" + champ_box.find("div", class_="Face").a.img["src"]
                c_played = OpggCrawler.find_played(
                    champ_box.find("div", class_="Played")
                )
                c_kda = OpggCrawler.find_kda(
                    champ_box.find("div", class_="PersonalKDA")
                )
                c_cs = ut.rss(
                    champ_box.find("div", class_="ChampionMinionKill").text
                ).split()[1]
                champions.append(
                    SummonerChampion(
                        name=c_name,
                        icon=c_icon,
                        win_ratio=c_played["win_ratio"],
                        games=c_played["games"],
                        kda=c_kda,
                        cs=c_cs,
                    )
                )
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
        img = tier_box.find("div", class_="Medal").img["src"]
        elo = tier_box.find("div", class_="TierRank").text
        win_ratio = ""

        if elo != "Unranked":
            elo += " " + ut.rss(tier_info.find("span", class_="LeaguePoints").text)
            win_ratio = OpggCrawler.find_win_ratio(tier_info)

        return {"elo_icon": "http:" + img, "win_ratio": win_ratio, "elo": elo}

    async def fetch_summoner(self, summoner_name, region, rank_type):
        print("summoner: " + summoner_name)
        print("region: " + region)
        page = await Crawler.fetch(
            self.summoner_url.replace("$REGION", region.lower())
            + summoner_name.replace(" ", "%20")
        )
        soup = BeautifulSoup(page, "html.parser")

        # Most played champions
        champions = OpggCrawler.find_champions(soup)

        # Ladder Rank
        ladder_rank = OpggCrawler.find_ladder_rank(soup)

        # Summoner Icon
        profile_icon = "http:" + soup.find("img", class_="ProfileImage")["src"]

        # Elo Icon / WinRatio / Elo
        tier = OpggCrawler.find_tier_box(soup)

        # summoner = Summoner(name=summoner_name, region=region)
        return Summoner(
            name=summoner_name,
            elo=tier["elo"],
            win_ratio=tier["win_ratio"],
            profile_icon=profile_icon,
            elo_icon=tier["elo_icon"],
            region=region,
            ladder_rank=ladder_rank,
            most_played_champs=champions,
        )

    @staticmethod
    def find_spell_name(url):
        return re.findall(r'(?:Summoner)(.*).png', url)

    @staticmethod
    def find_champion_stats_rank(soup):
        win_ratio = soup.find("div", class_="champion-stats-trend-rate").text
        text = soup.find("div", class_="champion-stats-trend-average").text
        return f"{ut.rss(win_ratio)} {ut.rss(text)}"

    @staticmethod
    def find_runes(soup):
        rune_table = soup.find("tbody", class_="ChampionKeystoneRune-1").tr
        tree_types = ut.rss(
            soup.find("div", class_="champion-stats-summary-rune__name").text
        )
        tree_types = tree_types.split(" + ")

        runes = []
        stats = []
        for perk_page in rune_table.find_all("div", class_="perk-page__row"):
            active_rune = perk_page.find_all("div", class_="perk-page__item--active")
            if active_rune is not None and len(active_rune) != 0:
                runes.append(active_rune[0].img["alt"])

        for shard_row in rune_table.find_all("div", class_="fragment__row"):
            for img in shard_row.find_all("img"):
                if img['class'][0] == 'active':
                    stats.append(OpggCrawler.find_shard_name(img["src"]))

        summoners_con = soup.find("td", class_="champion-overview__data")
        summoners = [OpggCrawler.find_spell_name(sspell.img['src']) for sspell in summoners_con.find_all("li", class_="champion-stats__list__item")]

        return RunePage(
            types=tree_types,
            keystone=runes[0],
            primaries=runes[1:4],
            secondaries=runes[4:],
            stats=stats,
            summoners=summoners,
        )

    @staticmethod
    def find_shard_name(url):
        for shard_code, shard_name in SHARDS_CODES.items():
            if url.__contains__(f"perkShard/{shard_code}"):
                return shard_name

    @staticmethod
    def find_counters(soup):
        counters_con = soup.find("table", class_="champion-stats-header-matchup__table")
        return ut.rss(counters_con.text).replace("Win Ratio", " Win Ratio ").split("Counter")

    @staticmethod
    def find_skill_priority(soup):
        ul_sp = soup.find_all("ul", class_="champion-stats__list")
        skill_priority = []
        for ul in ul_sp:
            for li in ul.find_all("li", class_="champion-stats__list__item"):
                if li.span is not None:
                    skill_priority.append(li.span.text)
        return skill_priority

    @staticmethod
    def find_item_build(soup):
        build = soup.find_all("table", class_="champion-overview__table")[1].tbody

        items = []
        for con in build.find_all("tr", class_="champion-overview__row"):
            icons = []
            ul = con.find("ul", class_="champion-stats__list")
            for li in ul.find_all("li", class_="champion-stats__list__item"):
                icons.append(f"https:{li.img['src']}")

            items.append({"stats": con.text.split(), "icons": icons})

        recommended_pos = boots_pos = -1
        for i, item in enumerate(items):
            if item["stats"][0] == "Recommended":
                recommended_pos = i
            elif item["stats"][0] == "Boots":
                boots_pos = i

        if boots_pos == -1 or recommended_pos == -1:
            raise Exception("Could not found Recommend or Boots in items list.")

        return ItemBuild(
            start_items=items[0:recommended_pos],
            core_build=items[recommended_pos:boots_pos],
            boots=items[boots_pos:]
        )

    async def fetch_build(self, champion_name, lane=""):
        print("champion: " + champion_name)
        print(f"lane: {lane}")

        page = await Crawler.fetch(
            self.champion_url.replace("$CHAMPION", champion_name.lower()).replace(
                "$LANE", lane.lower()
            )
        )
        soup = BeautifulSoup(page, "html.parser")

        # Champion Icon
        icon = f'https:{soup.find("div", class_="champion-stats-header-info__image").img["src"]}'

        # Lane
        lane = soup.find("span", class_="champion-stats-header__position__role").text

        # Champion Name - Tier
        champion_name = soup.find("h1", class_="champion-stats-header-info__name").text
        tier = soup.find("div", class_="champion-stats-header-info__tier").b.text

        # Winratio/games
        win_ratio = OpggCrawler.find_champion_stats_rank(soup)

        # Runes
        runes = OpggCrawler.find_runes(soup)

        # Matchups
        counters = OpggCrawler.find_counters(soup)

        # Skill Priority
        skill_priority = OpggCrawler.find_skill_priority(soup)

        # Item Build
        item_build = OpggCrawler.find_item_build(soup)

        # summoner = Summoner(name=summoner_name, region=region)
        return ChampionBuild(
            champ_name=champion_name,
            champ_icon=icon,
            champ_tier=tier,
            lane=lane,
            win_ratio=win_ratio,
            counters=counters,
            runes=runes,
            skill_priority=skill_priority,
            item_build=item_build,
        )
