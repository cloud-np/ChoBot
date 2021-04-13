from decouple import config
from discord.ext import commands
from web_crawler.opgg_crawler import OpggCrawler

cogs_list = ["cogs.lolcommands"]
trolled_users = ["Balkanios#0651"]


async def on_ready(self):
    print(f"We have logged in as {self.user}")


async def on_message(self, message):
    if message.author == self.user:
        return

    if message.content.startswith("$lol"):
        # trolled = await troll_users(message)
        # if trolled is True:
        #     return
        info = await self.opgg_crawler.fetch_summoner(
            message.content.split("$lol")[1]
        )
        await message.channel.send(info)


def load_cogs(bot_, cogs_list_):
    # Load cogs.
    for cog in cogs_list_:
        bot_.load_extension(cog)
        print(f"Added {cog}")


if __name__ == "__main__":
    crawler = OpggCrawler()
    bot = commands.Bot(description="ChoBot", command_prefix=config("PREFIX"))

    load_cogs(bot, cogs_list)

    bot.run(config("TOKEN"))
