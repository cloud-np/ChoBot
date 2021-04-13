from discord.ext import commands
from web_crawler.opgg_crawler import OpggCrawler


class LolCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.opgg = OpggCrawler()

    @commands.command(pass_context=True)
    async def build(self, ctx):
        # print('build ' + str(ctx.message.content))
        msg = ctx.message.content
        await ctx.send(self.opgg.get_champion_url(msg.split("$build")[1]))

    @commands.command(pass_context=True)
    async def lol(self, ctx):
        msgs = ctx.message.content.split()

        if msgs[1] == "west" or msgs[1] == "euwest":
            msgs[1] = "euw"
        lol_server = msgs[1] if msgs[1] in self.opgg.servers else "eune"

        await ctx.send(
            content=None,
            embed=await self.opgg.fetch_summoner(
                summoner_name="".join(msgs[2:]), server=lol_server
            ),
        )


def setup(bot):
    bot.add_cog(LolCommands(bot))
