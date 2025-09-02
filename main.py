import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from discord.utils import get
import sys
import config
import json
import asyncio
import sqlite3
from discord_interactions import *
from Commands.Check.avatar import Avatar
from Commands.Check.banner import Banner
from Commands.Check.bxh import Bxh
from Commands.Funs.event import Event
from Commands.Funs.fun import Fun
from Commands.Funs.hpbd import HPBD
from Commands.Funs.loto import Loto
from Commands.Funs.ship import Ship
from Commands.Funs.theard_food import Theard_food
from Commands.Funs.gameso import Gameso
from Commands.Funs.gametu import Gametu
from Commands.Funs.noitutv import Noitutv
from Commands.Mod.afk import AFK
from Commands.Mod.automess import AutoMessage
from Commands.Mod.confession import Confession
from Commands.Mod.emoji import Emoji
from Commands.Mod.giveaway import Giveaway
from Commands.Mod.help import Help
from Commands.Mod.lock import Lock
from Commands.Mod.moderation import Moderation
from Commands.Mod.nsfw import Nsfw
from Commands.Mod.ping import Ping
from Commands.Mod.prefix import Prefix
from Commands.Mod.reaction import Reaction
from Commands.Mod.reponse import Reponse
from Commands.Mod.role import Role
from Commands.Mod.say import Say
from Commands.Mod.server import Server
from Commands.Mod.snipe import Snipe
from Commands.Mod.welcome import Welcome
from Commands.Mod.toggle import Toggle
from Commands.Mod.link_invite import InviteLink
from Commands.More.instagram import Instagram
from Commands.More.speak import Speak
from Commands.More.marry import Marry
from Commands.More.tiktok import Tiktok
from Commands.More.facebook import Facebook
from Economy.Gambles.baucua import Baucua
from Economy.Gambles.blackjack import Blackjack
from Economy.Gambles.bet import Bet
from Economy.Gambles.coinflip import Coinflip
from Economy.Gambles.slot import Slot
from Economy.Gambles.taixiu import Taixiu
from Economy.Gambles.vietlott import Vietlott
from Economy.Gambles.pikachu import Pikachu
from Economy.Gambles.roulette import Roulette
from Economy.Relax.keobuabao import KeoBuaBao
from Economy.Relax.dhbc import Dhbc
from Economy.Relax.drop import DropPickup
from Economy.Relax.lamtoannhanh import Lamtoan
from Economy.Relax.vuatiengviet import Vtv
from Economy.economy import Economy
from Economy.shop import Shop
from Events.Fishing.eventfish import EventFish
from Events.Fishing.fishingshop import Fishingshop
from Events.Trungthu.lambanh import Lambanh
from Events.Halloween.cooking_candy import Naukeo
from Events.Halloween.sanma import Sanma
from Events.Event_30_4.cauhoi_30_4 import Cauhoi30_4
from Events.Event_30_4.daily_30_4 import Daily_30_4
from Events.Event_30_4.checkin import Checkin
from Events.level import Level
from Events.quest import Quest
from Events.ve import Ve
from Events.velenh import Velenh
from Events.Valentine_2025.unbox import Valentine2025

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()


def prefix_default(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix=prefix_default, intents=intents)
token = config.TOKEN


async def load():
    for root, dirs, files in os.walk("./Commands"):
        for filename in files:
            if filename.endswith(".py"):
                # Tạo đường dẫn module từ file path
                module_path = os.path.join(root, filename)
                # Chuyển đổi đường dẫn file thành module import
                module_name = module_path.replace(
                    "./", "").replace("/", ".").replace("\\", ".").replace(".py", "")
                try:
                    await client.load_extension(module_name)
                    print(f"Loaded extension: {module_name}")
                except Exception as e:
                    print(f"Failed to load extension {module_name}: {e}")

    for root, dirs, files in os.walk("./Economy"):
        for filename in files:
            if filename.endswith(".py"):
                # Tạo đường dẫn module từ file path
                module_path = os.path.join(root, filename)
                # Chuyển đổi đường dẫn file thành module import
                module_name = module_path.replace(
                    "./", "").replace("/", ".").replace("\\", ".").replace(".py", "")
                try:
                    client.load_extension(module_name)
                    print(f"Loaded extension: {module_name}")
                except Exception as e:
                    print(f"Failed to load extension {module_name}: {e}")

    for root, dirs, files in os.walk("./Events"):
        for filename in files:
            if filename.endswith(".py"):
                # Tạo đường dẫn module từ file path
                module_path = os.path.join(root, filename)
                # Chuyển đổi đường dẫn file thành module import
                module_name = module_path.replace(
                    "./", "").replace("/", ".").replace("\\", ".").replace(".py", "")
                try:
                    client.load_extension(module_name)
                    print(f"Loaded extension: {module_name}")
                except Exception as e:
                    print(f"Failed to load extension {module_name}: {e}")


@client.event
async def on_ready():
    await client.wait_until_ready()  # thay vì client.fetch_guilds()
    print('Đã đăng nhập thành công với tên là {0.user}'.format(client))
    for guild in client.guilds:
        cursor.execute(
            'INSERT OR IGNORE INTO servers (server_id, server_name, channel_simsimi) VALUES (?, ?, ?)', (guild.id, guild.name, None))
    conn.commit()
    await client.change_presence(activity=discord.Streaming(name="𝗛𝗮̣𝘁 𝗚𝗶𝗼̂́𝗻𝗴 𝗧𝗮̂𝗺 𝗧𝗵𝗮̂̀𝗻", url="https://www.twitch.tv/thanhvidev"))
    # -------------------Commands/Check==-----------------#
    #await client.add_cog(Avatar(client))
    # await client.add_cog(Banner(client))
    #await client.add_cog(Bxh(client))
    # -------------------Commands/Funs==-----------------=#
    #await client.add_cog(Event(client))
    await client.add_cog(Fun(client))
    # await client.add_cog(HPBD(client))
    # await client.add_cog(Loto(client))
    # await client.add_cog(Ship(client))
#    await client.add_cog(Trainbot(client))
    # await client.add_cog(Theard_food(client))
    # await client.add_cog(Gameso(client))
    # await client.add_cog(Gametu(client))   
    await client.add_cog(Noitutv(client))
    # -------------------Commands/Mod==-----------------#
    # await client.add_cog(AFK(client))
    # await client.add_cog(AutoMessage(client))
    # await client.add_cog(Confession(client))
    # await client.add_cog(Emoji(client))
    # await client.add_cog(Giveaway(client))
    # await client.add_cog(Help(client))
    # await client.add_cog(Lock(client))
    # await client.add_cog(Moderation(client))
    # await client.add_cog(Nsfw(client))
    # await client.add_cog(Ping(client))
    # await client.add_cog(Prefix(client))
    # await client.add_cog(Reaction(client))
    # await client.add_cog(Reponse(client))
    # await client.add_cog(Role(client))
    # await client.add_cog(Say(client))
    # await client.add_cog(Server(client))
    # await client.add_cog(Snipe(client))
    # await client.add_cog(Welcome(client))
    # await client.add_cog(InviteLink(client))
    # -------------------Commands/More==-----------------#
    # await client.add_cog(Instagram(client))
    # await client.add_cog(Speak(client))
    # await client.add_cog(Marry(client))
    await client.add_cog(Tiktok(client))
    await client.add_cog(Facebook(client))
    # -------------------Economy/Gamble==-----------------#
    # await client.add_cog(Baucua(client))
    # await client.add_cog(Blackjack(client))
    # await client.add_cog(Bet(client))
    # await client.add_cog(Coinflip(client))
    # await client.add_cog(KeoBuaBao(client))
    # await client.add_cog(Slot(client))
    # await client.add_cog(Taixiu(client))
    # await client.add_cog(Vietlott(client))
    # await client.add_cog(Pikachu(client))
    await client.add_cog(Roulette(client))
    # -------------------Economy/Relax==-----------------#
    # await client.add_cog(Dhbc(client))
    # await client.add_cog(DropPickup(client))
    # await client.add_cog(Lamtoan(client))
    #await client.add_cog(Vtv(client))
    # -------------------Economy/Main==-----------------#
    await client.add_cog(Economy(client))
    #await client.add_cog(Shop(client))
    # -------------------Events/Fishing==-----------------#
    # await client.add_cog(EventFish(client))
    # await client.add_cog(Fishingshop(client))
    # -------------------Events/Trungthu==-----------------#
    # await client.add_cog(Lambanh(client)) 
    # -------------------Events/Halloween==-----------------#
    # await client.add_cog(Naukeo(client))
    # await client.add_cog(Sanma(client))    
    # -------------------Events/Valentine_2025==-----------------#
    #await client.add_cog(Valentine2025(client))
    # -------------------Events/30_4==-----------------#
    # await client.add_cog(Cauhoi30_4(client))
    # await client.add_cog(Daily_30_4(client))
    # await client.add_cog(Checkin(client))
    # -------------------Events/Main==-----------------#
    # await client.add_cog(Level(client))
#    await client.add_cog(Quest(client))
    #await client.add_cog(Ve(client))
    #await client.add_cog(Velenh(client))
    # -------------------END==-----------------#
    await client.add_cog(Toggle(client))      
    # Thực hiện đồng bộ hóa  
    try: 
        synced = await client.tree.sync() 
        print(f"Synced {len(synced)} Command(s)")
    except Exception as e: 
        print(f"Failed to sync Commands: {e}")  
# async def load():
#     for filename in os.listdir("./Commands"):
#         if filename.endswith(".py"):
#             client.load_extension(f"Commands.{filename[:-3]}")


client.run(token)
