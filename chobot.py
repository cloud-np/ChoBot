from decouple import config
from discord.ext import commands

cogs_list = ["cogs.lolcommands"]

bot = commands.Bot(description="ChoBot", command_prefix=config("PREFIX"))


def load_cogs(bot_, cogs_list_):
    # Load cogs.
    for cog in cogs_list_:
        bot_.load_extension(cog)
        print(f"Added {cog}")


load_cogs(bot, cogs_list)
bot.run(config("CHOBOT_TOKEN"))
