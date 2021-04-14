from discord.ext import commands
from riot_api.riot_api import RiotApi
import discord
import utils.utils as ut
from web_crawler.opgg_crawler import OpggCrawler


class LolCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.riot_api = RiotApi()
        self.opgg = OpggCrawler()

    @commands.command(pass_context=True)
    async def build(self, ctx):
        # print('build ' + str(ctx.message.content))
        msg = ctx.message.content
        await ctx.send(self.opgg.get_champion_url(msg.split("$build")[1]))

    @staticmethod
    def create_summoner_embed(summoner, n_champs=3):
        em = discord.Embed(title=summoner.elo, description=summoner.win_ratio, color=0xf3841b)
        em.set_author(name=summoner.name, icon_url=summoner.profile_icon)
        em.set_thumbnail(url=summoner.elo_icon)
        for champ in summoner.most_played_champs[0:n_champs]:
            em.add_field(name=champ.name + f" ({champ.games})", value=f"**CS:** {champ.cs}  **KDA:** {champ.kda}  **WR:** {champ.win_ratio}", inline=False)
        em.set_footer(text=summoner.ladder_rank)
        return em

    @commands.command(pass_context=True)
    async def lol(self, ctx):
        msgs = ctx.message.content.split()

        await ctx.send(u":dorans_ring -> :dorans_ring:")
        return
        # print(str(ctx.message.author))
        # if await ut.troll_user(ctx) is True:
        #     return

        # When not enough arguments were passed
        if len(msgs) <= 1:
            return

        if msgs[1] == "west" or msgs[1] == "euwest":
            msgs[1] = "euw"

        if msgs[1] not in self.opgg.regions:
            region = "eune"
            offset = 1
        elif msgs[1] in self.opgg.regions:
            # Check if user put only the region e.g: "$lol euw"
            if len(msgs) == 2:
                return
            region = msgs[1]
            offset = 2

        summoner_name = "".join(msgs[offset:])
        try:
            summoner = await self.riot_api.fetch_summoner(summoner_name, region)
        except Exception as e:
            print(e)
            print("Riot api fetch failed, try web-crawling from opgg.")
            # Fetch summoner data
            summoner = await self.opgg.fetch_summoner(summoner_name, region)

        # Format them into emded
        em = LolCommands.create_summoner_embed(summoner)

        # Send the embed to the region.
        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(LolCommands(bot))
