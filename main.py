import discord
from discord.ext import commands, tasks
from clashstat import PlayerStats
import os
import asyncio
import logging, traceback


Client = commands.Bot(command_prefix='@')


os.environ['ID'] = 'bigmart000918@gmail.com'
os.environ['PW'] = 'dhrans99'
os.environ['Channel'] = '856111241083617311'
os.environ['Token'] = 'ODU2MDk3ODE1NDgyMzM1MjUy.YM8FOA.42VBQUzdqiSOVXfy6Tg4zjR4lm0'

ID = os.environ.get('ID')
PW = os.environ.get('PW')
ChannelID = os.environ.get('Channel')
Token = os.environ.get('Token')

coc = PlayerStats(ID, PW)

@Client.event
async def on_ready():
    print("Bot Login as {}".format(Client))
    
    Spy.start()

async def on_error(event, *args, **kwargs):
    print('Something went wrong!')
    logging.warning(traceback.format_exc())

async def MakeEmbed(Name: str, TrophyChange: str) -> discord.Embed:
    if int(TrophyChange) > 0:
        TrophyInStr = "+" + TrophyChange
        Color = 0x00aaaa
    else:
        TrophyInStr = TrophyChange
        Color = 0xFF8CFF
    
    embed = discord.Embed(title="{}  :  {}".format(Name, TrophyInStr), color=Color)
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
        embed = await MakeEmbed(PlayerInfo.get('name'), str(PlayerInfo.get('trophies')))
        await Channel.send(embed=embed)


Client.run(Token)