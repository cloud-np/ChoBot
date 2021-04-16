from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class SummonerChampion:
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
    region: str
    ladder_rank: str
    most_played_champs: list


@dataclass(frozen=True, order=True)
class Item:
    win_ratio: int
    games: int
    icon: str


class ItemBuild:
    def __init__(self, start_items, core_build, boots):
        self.start = start_items
        self.core_build = core_build
        self.boots = boots


class ChampionBuild:

    def __init__(self, champ_name, champ_icon, champ_tier, lane, win_ratio, counters, skill_priority, runes, item_build):
        self.champ_name = champ_name
        self.champ_icon = champ_icon
        self.champ_tier = champ_tier
        self.lane = lane
        self.win_ratio = win_ratio
        self.counters = counters
        self.skills_priority = skill_priority
        self.runes = runes
        self.item_build = item_build


class RunePage:

    def __init__(self, types, keystone, primaries, secondaries, stats, summoners):
        self.types = types
        self.keystone = keystone
        self.primaries = primaries
        self.secondaries = secondaries
        self.stats = stats
        self.summoners = summoners

    def format_rune(self):
        pass
