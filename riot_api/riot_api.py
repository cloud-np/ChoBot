import cassiopeia as cass
# from cassiopeia import Champion
from classes.lol_classes import Summoner
from decouple import config

# s.name
# s.profile_icon.url
# s.ranks
#  ranks.
# s.league_entries.fives.league_points
# s.league_entries.fives.hot_streak
# s.league_entries.fives.veteran
# s.league_entries.fives.fresh_blood
# s.league_entries.fives.wins
# s.league_entries.fives.losses
# s.league_entries.fives.division.value = 'III'
# s.league_entries.fives.tier.name
# s.
# s.


class RiotApi:

    def __init__(self, region="EUNE"):
        cass.set_default_region(region)
        cass.set_riot_api_key(config("RIOT_API"))

    # TODO: Implement a cached method with REDIS. So you can save some api calls.
    def get_cached_summoner(self, summoner_name, region):
        return None

    def fetch_summoner(self, summoner_name, region):
        summoner = self.get_cached_summoner(summoner_name, region)
        if summoner is None:
            summoner = cass.get_summoner(name=summoner_name, region="EUNE")
        return summoner
