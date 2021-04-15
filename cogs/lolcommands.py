from discord.ext import commands
from riot_api.riot_api import RiotApi
from data.runes import RUNES
import discord
import utils.utils as ut
from web_crawler.lol_crawlers import LolCrawler


class LolCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.riot_api = RiotApi()
        self.lol_crawler = LolCrawler()

    @commands.command(pass_context=True)
    async def build(self, ctx):

        embed = discord.Embed(
            description="49.7% Win-Rate in 28,553 Matches", color=0x7C45A1
        )
        embed.set_author(
            name="Cho'Gath",
            icon_url="https://static.u.gg/assets/lol/riot_static/11.8.1/img/champion/Chogath.png",
        )
        embed.set_thumbnail(
            url="https://static.u.gg/assets/lol/riot_static/11.8.1/img/champion/Chogath.png"
        )
        embed.add_field(name="Resolve" + ut.fr("Resolve") + "  ", value=ut.fr("GraspOfTheUndying") + " || " + ut.fr("Demolish") + " " + ut.fr("Conditioning") + " " + ut.fr("Overgrowth"), inline=True)
        embed.add_field(name="Precision" + ut.fr("Precision") + "  ", value=ut.fr("Triumph") + " " + ut.fr("LegendTenacity"), inline=True)
        embed.add_field(name=".", value=".", inline=False)
        embed.add_field(name="Stats", value=f'{ut.fr("StatModsAttackSpeedIcon")}  {ut.fr("StatModsAdaptiveForceIcon")}  {ut.fr("StatModsArmorIcon")}', inline=True)
        embed.add_field(name="Summoners", value=ut.fr("SummonerFlash") + " " + ut.fr("SummonerTeleport"), inline=True)
        embed.set_footer(text="This build is for Top Cho'Gath")
        await ctx.send(embed=embed)
        # em = discord.Embed(title="Cho Gath", description="Mid-lane Build")
        # em.add_field(name="", value="", inline=True)
        # await ctx.send(embed=em)
        return

    @staticmethod
    def create_summoner_embed(summoner, n_champs=3):
        em = discord.Embed(
            title=summoner.elo, description=summoner.win_ratio, color=0xF3841B
        )
        em.set_author(name=summoner.name, icon_url=summoner.profile_icon)
        em.set_thumbnail(url=summoner.elo_icon)
        for champ in summoner.most_played_champs[0:n_champs]:
            em.add_field(
                name=champ.name + f" ({champ.games})",
                value=f"**CS:** {champ.cs}  **KDA:** {champ.kda}  **WR:** {champ.win_ratio}",
                inline=False,
            )
        em.set_footer(text=summoner.ladder_rank)
        return em

    @commands.command(pass_context=True)
    async def lol(self, ctx):
        msgs = ctx.message.content.split()

        # When not enough arguments were passed
        if len(msgs) <= 1:
            return

        summoner_name, region = ut.parse_summoner_name_and_region(
            msgs, self.lol_crawler.regions
        )
        # Once champion.gg api is back we may use this again.
        # try:
        #     summoner = await self.riot_api.fetch_summoner(summoner_name, region)
        # except Exception as e:
        #     print(e)
        #     print("Riot api fetch failed, try web-crawling from opgg.")

        summoner = await self.lol_crawler.fetch_summoner(summoner_name, region)
        # Format them into emded
        em = LolCommands.create_summoner_embed(summoner)

        # Send the embed to the region.
        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(LolCommands(bot))
