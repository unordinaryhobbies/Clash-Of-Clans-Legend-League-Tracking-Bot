import discord
from discord.ext import commands, tasks
from clashstat import PlayerStats
import os
import asyncio
import logging
import traceback


Client = commands.Bot(command_prefix='@')

# ID = os.environ.get('ID')
# PW = os.environ.get('PW')
# ChannelID = os.environ.get('Channel')
# Token = os.environ.get('Token')
ID = 'bigmart000918@gmail.com'
PW = 'dhrans99'
ChannelID = '856111241083617311'
Token = 'ODU2MDk3ODE1NDgyMzM1MjUy.YM8FOA.Sd2Ce35UzLBGDSP1x4v7OQ9V0Fw'
coc = PlayerStats(ID, PW)


@Client.event
async def on_ready():
    print("Bot Login as {}".format(Client))

    Spy.start()


async def on_error(event, *args, **kwargs):
    print('Something went wrong!')
    logging.warning(traceback.format_exc())


async def MakeUrl(Name: str, Tags: str):
    RemoveSpecialChar = ''

    for ch in Name:
        if ord(ch) == 32:
            RemoveSpecialChar += '-'

        elif (ord(ch) < 128):
            RemoveSpecialChar += ch.lower()

    Identification = RemoveSpecialChar + "-" + Tags[1:]
    Link = "https://www.clashofstats.com/players/{}/summary".format(
        Identification)
    return Link


async def MakeEmbed(Name: str, TrophyChange: str, Link: str) -> discord.Embed:
    if int(TrophyChange) > 0:
        TrophyInStr = "+" + TrophyChange
        Color = 0x00aaaa
    else:
        TrophyInStr = TrophyChange
        Color = 0xFF8CFF

    embed = discord.Embed(title="{} : {}".format(Name, TrophyInStr), color=Color, url=Link)
    return embed


@tasks.loop(seconds=60)
async def Spy():
    PlayersUpdate = await coc.Run()

    print("Running...")

    Channel = Client.get_channel(int(ChannelID))
    if len(PlayersUpdate) == 0:
        return
    print("Size of Update = {}".format(len(PlayersUpdate)))
    for PlayerInfo in PlayersUpdate:
        Link = await MakeUrl(PlayerInfo.get('name'), PlayerInfo.get('tag'))
        embed = await MakeEmbed(PlayerInfo.get('name'), str(PlayerInfo.get('trophies')), Link)
        await Channel.send(embed=embed)


Client.run(Token)
