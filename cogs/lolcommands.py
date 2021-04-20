from discord.ext import commands
from riot_api.riot_api import RiotApi
import discord
import utils.utils as ut
from web_crawler.lol_crawlers.lol_crawler import LolCrawler


class LolCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.riot_api = RiotApi()
        self.lol_crawler = LolCrawler()
        self.lanes = ["top", "jungle", "mid", "middle", "bot", "adc", "support", "supp"]

    @staticmethod
    def not_found_build(build: dict):
        em = discord.Embed(description=f'No builds were found for {build["name"]} - {build["lane"]}', color=0x7C45A1)
        em.set_author(name="Not found\t (╯°□°）╯︵ ┻━┻")
        em.set_thumbnail(url=build["icon"])
        return em

    @staticmethod
    def create_build_embed(build):
        em = discord.Embed(title=build.champ_name + " " + build.lane, description=f"{build.win_ratio} {build.champ_tier}", color=0x7C45A1)
        em.set_author(name=build.champ_name, icon_url=build.champ_icon)
        em.set_thumbnail(url=build.champ_icon)

        runes = build.runes
        stats = runes.emojify_stats()
        keystone, prim, secon = runes.emojify_runes()
        types = runes.emojify_rune_types()
        summoners = runes.emojify_summoners()

        em.add_field(name=types[0], value=f"{keystone}  ||  {prim}", inline=True)
        em.add_field(name=types[1], value=secon, inline=True)
        em.add_field(
            name="Skill Priotity",
            value="".join([spell + " -> " for spell in build.skills_priority]),
            inline=False,
        )
        em.add_field(name="Stats", value=stats, inline=True)
        em.add_field(name="Summoners", value=summoners, inline=True)
        counters = ""
        for ctr in build.counters:
            tmp = ctr.split(" Win Ratio ")
            if len(tmp) > 1:
                counters += f"**{tmp[0]}** - {tmp[1]} Win Ratio\n"

        em.add_field(name="Main Counters", value=counters, inline=False)
        em.set_footer(text=f"This build is for {build.lane} {build.champ_name}")
        return em

    @staticmethod
    def not_valid_url(user_input, msg):
        em = discord.Embed(title="Invalid Input", description=msg, color=0x7C45A1)
        em.add_field(name=f"**{user_input}**", value='.')
        return em

    @staticmethod
    async def show_build(build, ctx):
        # em = discord.Embed(title=build.champ_name + " " + build.lane, description=f"{build.win_ratio} {build.champ_tier}", color=0x7C45A1)

        starting = build.item_build.start[0]
        s_stats = "".join(s + " " for s in starting['stats'][2:])
        em = discord.Embed(title="Starting Items", description=s_stats, color=0x7C45A1)

        for icon in starting['icons']:
            em.set_image(url=icon)
            await ctx.send(embed=em)
            em.description = " "

        core = build.item_build.core_build[0]
        c_stats = "".join(s + " " for s in core['stats'][2:])
        em = discord.Embed(title="Core Items", description=c_stats, color=0x7C45A1)

        for icon in build.item_build.core_build[0]['icons']:
            em.set_image(url=icon)
            await ctx.send(embed=em)
            em.description = " "

        boots = build.item_build.boots[0]
        b_stats = "".join(s + " " for s in boots['stats'][2:])
        em = discord.Embed(title="Boots", description=b_stats, color=0x7C45A1)

        for icon in build.item_build.boots[0]['icons']:
            em.set_image(url=icon)
            await ctx.send(embed=em)
            em.description = " "

    @commands.command(pass_context=True)
    async def runes(self, ctx):
        pass

    @commands.command(pass_context=True)
    async def build(self, ctx):
        msgs = ctx.message.content.split()

        # When not enough arguments were passed
        if len(msgs) <= 1:
            return

        champion_name, lane = ut.parse_summoner_name_and_region(msgs, self.lanes)

        # Fetch the build from a website.
        build = await self.lol_crawler.fetch_build(champion_name, lane)

        if build is None:
            embed = LolCommands.not_valid_url(user_input=champion_name, msg="Are you sure this is a valid champion?")
        elif build.__class__ == dict:
            embed = LolCommands.not_found_build(build)
        else:
            embed = LolCommands.create_runes_embed(build)
            await LolCommands.show_build(build, ctx)

        await ctx.send(embed=embed)

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

        summoner_name, region = ut.parse_summoner_name_and_region(msgs, self.lol_crawler.regions)
        # Once champion.gg api is back we may use this again.
        # try:
        #     summoner = await self.riot_api.fetch_summoner(summoner_name, region)
        # except Exception as e:
        #     print(e)
        #     print("Riot api fetch failed, try web-crawling from opgg.")

        summoner = await self.lol_crawler.fetch_summoner(summoner_name, region)
        if summoner is None:
            em = LolCommands.not_valid_url(user_input=summoner_name, msg="Are you sure this is a valid summoner?\n\t\tDid you select the right server?")
        else:
            # Format them into emded
            em = LolCommands.create_summoner_embed(summoner)

        # Send the embed to the region.
        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(LolCommands(bot))
