from dataclasses import dataclass
import utils.utils as ut


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
        self.keystone = ut.rspaces(keystone)
        self.primaries = self.format_input_runes(primaries)
        self.secondaries = self.format_input_runes(secondaries)
        self.stats = stats
        self.summoners = summoners

    def format_input_runes(self, runes):
        # Remove any invalid chars and spaces.
        return [ut.rspaces(
            rune
            .replace(":", "")
            .replace("'", "")
            .lower())
            for rune in runes]

    def emojify_rune_types(self):
        return [f"{type_} {ut.fr(type_)}" for type_ in self.types]

    def emojify_runes(self):
        keystone = ut.fr(self.keystone)
        return keystone, "".join([f' {ut.fr(rune)} ' for rune in self.primaries]), "".join([f' {ut.fr(rune)} ' for rune in self.secondaries])

    def emojify_stats(self):
        return "".join([f" {ut.fr(ut.rspaces(stat.lower()))} " for stat in self.stats])

    # TODO refactor this once you fix summoners
    def emojify_summoners(self):
        return f"{ut.fr(self.summoners[0][0].lower())}  {ut.fr(self.summoners[1][0].lower())}"

    def format_rune(self):
        pass
