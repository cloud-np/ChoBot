from dataclasses import dataclass


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
    region: str
    ladder_rank: str
    most_played_champs: list
