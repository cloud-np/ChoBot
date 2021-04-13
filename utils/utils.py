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


def format_summoner(summoner_name, text):

    words = text.split()
    base = f"- {bt(summoner_name)}\n▬▬▬▬▬▬▬▬▬\n{dt(f'{words[0]} {words[1]}')}"

    if len(words) == 3:
        return base
    else:
        return f"{base}\n{format_elo(words[2:6])}\n{format_wr(words[7:12])}\n{words[12]} {words[13]}"
