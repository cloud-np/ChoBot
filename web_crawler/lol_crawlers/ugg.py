from decouple import config
from web_crawler.crawler import Crawler
from classes.lol_classes import RunePage, ChampionBuild, ItemBuild
from bs4 import BeautifulSoup
import utils.utils as ut


class UggCrawler:
    def __init__(self):
        # We can still use OPGG's links to get images etc for the time being
        # since these are static data across platoforms. Also we should cache
        # these data at one point so we can retrieve them much faster.
        self.base_url = config("OPGG_BASE_URL")
        self.summoner_url = config("OPGG_SUMMONER_URL")
        self.champion_url = config("UGG_CHAMPION_URL")
        self.champion_counters_url = config("UGG_CHAMPION_URL")
        self.profile_icons = config("OPGG_PROFILE_ICON_URL")
        self.elo_icons_url = config("OPGG_ELO_ICON_URL")
        self.champion_icon_url = config("OPGG_CHAMPION_ICON_URL")

    @staticmethod
    def find_champion_stats_rank(soup):
        stats = soup.find("div", class_="champion-ranking-stats")
        win_ratio = f'{stats.find("div", class_="win-rate").find("div", class_="value").text} Win Ratio'
        games = (
            f'{stats.find("div", class_="matches").find("div", class_="value").text} '
        )

        return f"{win_ratio} in {games} Games"

    @staticmethod
    def find_runes(soup):
        primary_tree = soup.select("div.rune-tree_v2.primary-tree")[0]
        secondary_tree = soup.select("div.secondary-tree")[0]
        tree_type = primary_tree.find("div", class_="perk-style-title").text
        keystone = (
            primary_tree.find("div", class_="perk-active")
            .img["alt"]
            .replace("The Keystone ", "")
        )
        tree_runes = []
        for tree in [primary_tree, secondary_tree]:
            for perk_row in tree.find_all("div", class_="perk-row"):
                # In ugg the first row for these trees are not needed.
                if len(perk_row["class"]) != 1:
                    continue
                tmp_rune = ut.extract_rune_from_url(
                    perk_row.find("div", class_="perk-active").img["src"]
                )
                tree_runes.append(tmp_rune)
        shards = []
        for shard_row in secondary_tree.find_all("div", class_="stat-shard-row"):
            tmp_rune = ut.extract_rune_from_url(
                shard_row.find("div", class_="shard-active").img["src"]
            )
            shards.append(tmp_rune)

        summoners_con = soup.find("div", class_="summoner-spells")
        summoners = [
            ut.extract_rune_from_url(img["src"])
            for img in summoners_con.find_all("img")
        ]

        return RunePage(
            type_=tree_type,
            keystone=keystone,
            primaries=tree_runes[0:3],
            secondaries=tree_runes[3:],
            stats=shards,
            summoners=summoners,
        )

    @staticmethod
    def find_counters(soup):
        matchups = soup.find("div", class_="matchups")
        return [
            {
                "name": counter.find("div", class_="champion-name").text,
                "win_ratio": counter.find("div", class_="win-rate").strong.text,
                "games": counter.find("div", class_="total-matches").text,
            }
            for counter in matchups
        ]

    @staticmethod
    def find_skill_priority(soup):
        sp = soup.find("div", class_="skill-priority-path")
        return [label.text for label in sp.find_all("div", class_="skill-label")]

    @staticmethod
    def find_item_build(soup):
        build = soup.find("div", class_="recommended-build_items")

        icons = []
        stats = []
        for con in build:
            for item in con.find_all("div", class_="item-img"):
                icons.append(ut.extract_url_from_style_attr(item.div.div["style"]))
            for sts in con.find_all("div", class_="item-stats"):
                stats.append({"win_ratio": sts.find("div", class_="winrate").text, "games": sts.find("div", class_="matches").text})

        return ItemBuild(
            start_items={"icons": icons[0:2], "stats": stats[0]},
            core_build={"icons": icons[2:5], "stats": stats[1]},
            fourth_items={"icons": icons[5:7], "stats": stats[2:4]},
            fifth_items={"icons": icons[7:10], "stats": stats[4:7]},
            sixth_items={"icons": icons[10:], "stats": stats[7:]},
        )

    # TODO Needs to be changed to something else.
    async def fetch_champion(self, champion_name, lane):
        print("champion: " + champion_name)
        print(f"lane: {lane}")

        page = await Crawler.fetch(
            self.champion_url.replace("$CHAMPION", champion_name.lower())
        )
        soup = BeautifulSoup(page, "html.parser")

        # Champion Icon - Name
        profile = soup.find("img", class_="champion-image")
        champion_name = profile["alt"]
        icon = profile["src"]

        # Winratio/games
        win_ratio = UggCrawler.find_champion_stats_rank(soup)

        # Runes
        runes = UggCrawler.find_runes(soup)

        # Matchups
        counters = UggCrawler.find_counters(soup)

        # Skill Priority
        skill_priority = UggCrawler.find_skill_priority(soup)

        # Item Build
        # item_build = OpggCrawler.find_item_build()
        item_build = None

        # summoner = Summoner(name=summoner_name, region=region)
        return ChampionBuild(
            name=champion_name,
            icon=icon,
            lane=lane,
            win_ratio=win_ratio,
            counters=counters,
            runes=runes,
            skill_priority=skill_priority,
            item_build=item_build
        )
