import os
import sqlite3
import discord
from dotenv import find_dotenv, load_dotenv
from discord.ext import commands

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')

client = commands.Bot(command_prefix= '!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

try:
   client.run(TOKEN)
except Exception as e:
    print(e)


