import discord
from decouple import config
from random import randint


trolled_users = list()


def rspaces(text):
    return "".join(text.split())


def rss(text):
    return text.replace("\n", "").replace("\t", "")


# Bold Text
def bt(text):
    return f"**{text}**"


# Darker text
def dt(text):
    return f"`{text}`"


def format_elo(texts):
    return bt(f"{texts[0]} {texts[1]} | {texts[2]} {texts[3]}")


def format_wr(texts):
    # print(texts)
    return f"{texts[0].replace('W', ':white_check_mark:')} {texts[1].replace('L', ':x:')} {dt(''.join([t + ' ' for t in texts[2:5]]))}"


async def not_found(ctx):
    if rspaces(str(ctx.message.author)) in trolled_users and randint(0, 10) > 1:
        em = discord.Embed(title="Dead", description="Nai paraligo..")
        em.set_image(url="https://i.imgur.com/uclAkDA.png")
        await ctx.send(content=None, embed=em)
        return True
    return False


def setup(trolled_users_):
    global trolled_users
    trolled_users = trolled_users_


def format_summoner(summoner_name, text):

    words = text.split()
    base = f"- {bt(summoner_name)}\n▬▬▬▬▬▬▬▬▬\n{dt(f'{words[0]} {words[1]}')}"

    if len(words) == 3:
        return base
    else:
        return f"{base}\n{format_elo(words[2:6])}\n{format_wr(words[7:12])}\n{words[12]} {words[13]}"
