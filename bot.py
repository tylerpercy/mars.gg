import os
import sqlite3
from image_parser import image_parser
from dotenv import find_dotenv, load_dotenv
from discord.ext import commands

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

client = commands.Bot(command_prefix= '!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):

    # prevent feedback loop
    if message.author == client.user:
            return

    if message.attachments:
        if message.attachments[0].filename[-4:] == '.png':
            await client.get_channel(CHANNEL_ID).send("Screenshot detected.")
            link = str(message.attachments[0])

            #create parser object
            ip = image_parser()
            try:
                image = ip.download_image(link)
            except:
                await client.get_channel(CHANNEL_ID).send("Image download not successful.")
                print("Image download not successful.")
            else:
                await client.get_channel(CHANNEL_ID).send("File download successful.")
                print("File download successful.")
            try:
                ip.detect_origin(image)
            except:
                await client.get_channel(CHANNEL_ID).send("No image found.")
                print("No image found.")
            else:
                await client.get_channel(CHANNEL_ID).send("Image origin detection successful.")
                print("Image origin detection successful.")
                ip.parse(image, ip.origin)
            finally:
                ip.clean() # remove all .pngs
                await client.get_channel(CHANNEL_ID).send("Clean successful.")
                print("Clean successful.")

                await client.get_channel(CHANNEL_ID).send("\nOperation successful.")
                print("\nOperation successful.")

try:
   client.run(TOKEN)
except Exception as e:
    print(e)


