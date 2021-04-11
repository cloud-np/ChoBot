import discord
from web_crawler.opgg_crawler import OpggCrawler
from random import randint
from decouple import config


trolled_users = ["Balkanios#0651"]


def start_balkbot():

    client = discord.Client()
    opgg_crawler = OpggCrawler()

    @client.event
    async def on_ready():
        print(f"We have logged in as {client}")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith("$lol"):
            trolled = await troll_users(message)
            if trolled is True:
                return
            info = opgg_crawler.get_summoner_info_for_discord(message.content.split("$lol")[1])
            await message.channel.send(info)

        elif message.content.startswith("$build"):
            trolled = await troll_users(message)
            if trolled is True:
                return
            await message.channel.send(opgg_crawler.get_champion_url(message.content.split("$build")[1]))

    async def troll_users(message):
        if (str(message.author) in trolled_users) and randint(0, 10) > 5:
            await message.channel.send(":dead:")
            return True
        return False

    # @client.command(pass_context=True)
    # async def build(ctx, arg):
    #     print(ctx)
    #     print(arg)
    #     await ctx.send(ctx.sender())
    #     pass

    client.run(config('TOKEN'))
