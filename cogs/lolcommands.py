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
        em.set_author(icon_url="https://i.imgur.com/8e2JUFB.png", name="Not found\t (╯°□°）╯︵ ┻━┻")
        em.set_thumbnail(url=build["icon"])
        return em

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        em = discord.Embed(title=":grey_question: Usage guide for ChoBot", color=discord.Color.greyple())
        for cmd in [["summoner", "$summoner eune Cloud Madness"], ["build", "$build jungle ChoGath"], ["runes", "$runes mid Lee Sin"], ["fullbuild", "$fullbuild adc Kennen"]]:
            if cmd[0] == "summoner":
                em.add_field(name=f"${cmd[0]} [region] [summoner-name]", value=cmd[1], inline=False)
            else:
                em.add_field(name=f"${cmd[0]} [lane] [champion-name]", value=cmd[1], inline=False)
        await ctx.send(embed=em)

    @staticmethod
    async def send_runes(build, ctx):
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
        await ctx.send(embed=em)

    @staticmethod
    def not_valid_url(user_input, msg):
        em = discord.Embed(title=":x: Invalid Input", description=msg, color=0x7C45A1)
        em.add_field(name=f"**{user_input}**", value='.')
        return em

    # TODO Would be nice to write this one a bit cleaner.. one day I hope I will lol.
    @staticmethod
    async def send_build(build, ctx):
        starting = build.item_build.start[0]
        em = discord.Embed(title="Starting Items", description=ut.format_stats(starting['stats'][2:]), color=0x7C45A1)

        for icon in starting['icons']:
            em.set_image(url=icon)
            await ctx.send(embed=em)
            em.description = " "

        core = build.item_build.core_build[0]
        em = discord.Embed(title="Core Items", description=ut.format_stats(core['stats'][2:]), color=0x7C45A1)

        for icon in build.item_build.core_build[0]['icons']:
            em.set_image(url=icon)
            await ctx.send(embed=em)
            em.description = " "

        boots = build.item_build.boots[0]
        em = discord.Embed(title="Boots", description=ut.format_stats(boots['stats'][1:]), color=0x7C45A1)

        for icon in build.item_build.boots[0]['icons']:
            em.set_image(url=icon)
            await ctx.send(embed=em)
            em.description = " "

    @commands.command(pass_context=True)
    async def runes(self, ctx):
        build, error_embed = await self.try_fetching_fullbuild(ctx, "runes")

        if error_embed is None:
            await LolCommands.send_runes(build, ctx)
        else:
            await ctx.send(embed=error_embed)
        return

    @staticmethod
    def not_enough_args(cmd):
        em = discord.Embed(title=f"Not enough args for command: ${cmd}")
        em.description = f"An example usage of the **${cmd}** command:"
        if cmd == "build" or cmd == "runes" or cmd == "fullbuild":
            em.add_field(name=f"${cmd} [lane] [champion-name]", value="$build mid ChoGath")
        elif cmd == "summoner":
            em.add_field(name="$summoner [region] [summoner-name]", value="$summoner west Faker1")
        return em

    async def try_fetching_fullbuild(self, ctx, cmd):
        msgs = ctx.message.content.split()

        # When not enough arguments were passed
        if len(msgs) <= 1:
            error_embed = LolCommands.not_enough_args(cmd)
            return None, error_embed

        champion_name, lane = ut.parse_champion_name_and_lane(msgs, self.lanes)

        # Fetch the build from a website.
        build = await self.lol_crawler.fetch_build(champion_name, lane)

        error_embed = None
        if build is None:
            error_embed = LolCommands.not_valid_url(user_input=champion_name, msg="Are you sure this is a valid champion?")
        elif build.__class__ == dict:
            error_embed = LolCommands.not_found_build(build)
        return build, error_embed

    @commands.command(pass_context=True)
    async def fullbuild(self, ctx):
        build, error_embed = await self.try_fetching_fullbuild(ctx, "fullbuild")

        if error_embed is None:
            await LolCommands.send_build(build, ctx)
            await LolCommands.send_runes(build, ctx)
        else:
            await ctx.send(embed=error_embed)
        return

    @commands.command(pass_context=True)
    async def build(self, ctx):
        build, error_embed = await self.try_fetching_fullbuild(ctx, "build")

        if error_embed is None:
            await LolCommands.send_build(build, ctx)
        else:
            await ctx.send(embed=error_embed)
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
    async def summoner(self, ctx):
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
