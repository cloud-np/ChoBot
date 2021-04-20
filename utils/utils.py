from data.runes import RUNES


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
    # if rspaces(str(ctx.message.author)) in trolled_users and randint(0, 10) >", 1:
    #     em = discord.Embed(title="Dead", description="Nai paraligo..")
    #     em.set_image(url="https://i.imgur.com/uclAkDA.png")
    #     await ctx.send(content=None, embed=em)
    #     return True
    return False


def fr(rune_name):
    rune_name = rune_name.lower()
    return f"<:{rune_name}:{RUNES[rune_name]}>"


def extract_rune_from_url(url):
    # We reverse the string to find the first occurance of the "/" char.
    pos = None
    for i, ch in enumerate(url[::-1]):
        if ch == "/":
            pos = i
            break
    return url[-pos:].replace(".png", "")


def extract_url_from_style_attr(div_style):
    s_pos = e_pos = None
    for i, ch in enumerate(div_style):
        if ch == "(":
            s_pos = i
        if ch == ")":
            e_pos = i
            break
    return div_style[s_pos + 1:e_pos]


def parse_champion_name_and_lane(user_input, lanes):

    if user_input[1].lower() in lanes:
        if user_input[1] in ["mid", "middle"]:
            lane = "middle"
        elif user_input[1] in ["bot", "adc"]:
            lane = "adc"
        elif user_input[1] in ["support", "supp"]:
            lane = "support"

        lane = user_input[1]
        offset = 2
    else:
        lane = ""
        offset = 1

    champion_name = "".join(user_input[offset:])
    return champion_name, lane


def parse_summoner_name_and_region(user_input, valid_regions):

    if user_input[1] == "west" or user_input[1] == "euwest":
        user_input[1] = "euw"

    if user_input[1] not in valid_regions:
        region = "eune"
        offset = 1
    elif user_input[1] in valid_regions:
        # Check if user put only the region e.g: "$lol euw"
        if len(user_input) == 2:
            return
        region = user_input[1]
        offset = 2
    summoner_name = "".join(user_input[offset:])
    return summoner_name, region


def format_summoner(summoner_name, text):

    words = text.split()
    base = f"- {bt(summoner_name)}\n▬▬▬▬▬▬▬▬▬\n{dt(f'{words[0]} {words[1]}')}"

    if len(words) == 3:
        return base
    else:
        return f"{base}\n{format_elo(words[2:6])}\n{format_wr(words[7:12])}\n{words[12]} {words[13]}"
