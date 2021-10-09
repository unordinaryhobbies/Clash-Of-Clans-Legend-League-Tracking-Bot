import discord  #type: ignore
from discord.ext import commands, tasks  #type: ignore
from clashstat import PlayerStats
import os

Client = commands.Bot(command_prefix='@')

ID = os.environ.get('ID')
PW = os.environ.get('PW')
ChannelID = os.environ.get('Channel')
ChannelID2 = os.environ.get('Channel2')
Token = os.environ.get('Token')
ChannelIDs = [ChannelID, ChannelID2]

coc = PlayerStats(ID, PW, 'player.txt')  #type: ignore
coc.GetPlayerList()

#########################


@Client.event
async def on_ready():
    print("Bot Login as {}".format(Client))
    Main.start()


def MakeUrl(Name: str, Tags: str):
    RemoveSpecialChar = ''

    for ch in Name:
        if ord(ch) == 32:
            RemoveSpecialChar += '-'

        elif ord(ch) < 128:
            RemoveSpecialChar += ch.lower()

    Identification = RemoveSpecialChar + "-" + Tags[1:]
    Link = f"https://www.clashofstats.com/players/{Identification}/summary"
    return Link


def MakeEmbedMessageFormat(Name: str, TrophyChange: str,
                           Link: str) -> discord.Embed:
    if int(TrophyChange) > 0:
        TrophyInStr = "+" + TrophyChange
        Color = 0x00aaaa
    else:
        TrophyInStr = TrophyChange
        Color = 0xFF8CFF

    embed = discord.Embed(title="{} : {}".format(Name, TrophyInStr),
                          color=Color,
                          url=Link)
    return embed


@tasks.loop(seconds=60)
async def Main():
    PlayersUpdate = await coc.Run()

    print("Running...")

    ChannelIDList = list(
        map(lambda channel: Client.get_channel(int(channel)), ChannelIDs))

    if len(PlayersUpdate) == 0:
        return

    print("Size of Update = {}".format(len(PlayersUpdate)))

    for tag in PlayersUpdate.keys():
        Link = MakeUrl(PlayersUpdate[tag].get('name'),
                       PlayersUpdate[tag].get('tag'))
        embed = MakeEmbedMessageFormat(PlayersUpdate[tag].get('name'),
                                       str(PlayersUpdate[tag].get('trophies')),
                                       Link)
        for channelID in ChannelIDList:
            await channelID.send(embed=embed)


Client.run(Token)
