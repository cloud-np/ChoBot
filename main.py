from discordbot.balkbot import start_balkbot
from web_crawler.opgg_crawler import OpggCrawler


if __name__ == "__main__":
    crawler = OpggCrawler()
    start_balkbot()
    # print(crawler.get_summoner_info_for_discord("Cloud Madness"))
    # print(crawler.get_summoner_info_for_discord("Timokv"))
