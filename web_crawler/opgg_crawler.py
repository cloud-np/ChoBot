# import requests
import aiohttp
import discord
from decouple import config
import utils.utils as ut
from bs4 import BeautifulSoup


class OpggCrawler:

    def __init__(self):
        # The empty one -> '' is kr.
        self.servers = ["eune", "euw", "na", '', "oce", "br", "tr"]
        self.base_URL = config("BASE_URL")
        self.summoner_base_URL = config("SUMMONER_BASE_URL")
        self.champion_base_URL = config("CHAMPION_BASE_URL")

    @staticmethod
    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            html = await response.text()
            return html

    async def fetch_summoner(self, summoner_name, server="eune"):
        print("summoner: " + summoner_name)
        print("server: " + server)
        em = discord.Embed(title="Ranked Solo", color=0xfc9e1b)
        em.set_image(url="https://ibb.co/KyqZ2s6")
        em.add_field(name=u'🎯:regional_indicator_e::regional_indicator_l::regional_indicator_o:  Rank', value="Elaaaa", inline=False)
        # em.add_field(name=u'🎯 Rank', icon_url="https://imgur.com/MvVwRod", inline=False, )
        return em
        # em.add_field(name=u'\u2328 Most Used Cmd', value=most_used_cmd, inline=False)
        # em.add_field(name=u'\U0001F4E4 Msgs sent', value=str(self.bot.icount))
        # em.add_field(name=u'\U0001F4E5 Msgs received', value=str(self.bot.message_count))
        # em.add_field(name=u'\u2757 Mentions', value=str(self.bot.mention_count))
        # em.add_field(name=u'\u2694 Servers', value=str(len(self.bot.guilds)))
        # em.add_field(name=u'\ud83d\udcd1 Channels', value=str(channel_count))
        # em.add_field(name=u'\u270F Keywords logged', value=str(self.bot.keyword_log))
        # g = u'\U0001F3AE Game'
        # if '=' in game: g = '\ud83c\udfa5 Stream'
        # em.add_field(name=g, value=game)


#             em.add_field(name='\ud83d\udd17 Link to download',
#                          value='[Github link](https://github.com/appu1232/Discord-Selfbot/tree/master)')
#             em.add_field(name='\ud83c\udfa5Quick examples:', value='[Simple commands](http://i.imgur.com/3H9zpop.gif)')
#             if txt == 'link': em.add_field(name='👋 Discord Server', value='Join the official Discord server [here](https://discord.gg/FGnM5DM)!')
#             em.set_footer(text='Made by appu1232#2569', icon_url='https://i.imgur.com/RHagTDg.png')
#             await ctx.send(content=None, embed=em)
#         else:
        page = await self.fetch(self.summoner_base_URL.replace("$SERVER", server.lower()) + summoner_name.replace(' ', '%20'))
        # page = await self.fetch("https://eune.op.gg/summoner/userName=Cloud%20Madness")
        soup = BeautifulSoup(page, "html.parser")
        try:
            text = soup.find(class_="TierRankInfo").text
        except Exception:
            pass
        return ut.format_summoner(summoner_name, "".join([text]))

    def get_champion_url(self, champion):
        return self.champion_base_URL.replace("$CHAMPION", champion.lower().replace(' ', ''))
