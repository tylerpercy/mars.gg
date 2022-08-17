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

            err_cnt = 0

            #create parser object
            ip = image_parser()

            try:
                image = ip.download_image(link)
            except:
                await client.get_channel(CHANNEL_ID).send("Image download failed.")
                print("Image download failed.")
                err_cnt += 1
            else:
                await client.get_channel(CHANNEL_ID).send("File download successful.")
                print("File download successful.")

            try:
                ip.detect_origin(image)
            except:
                await client.get_channel(CHANNEL_ID).send("No image found.")
                print("No image found.")
                err_cnt += 1
            else:
                await client.get_channel(CHANNEL_ID).send("Image origin detection successful.")
                print("Image origin detection successful.")

            try:
                return_code = ip.parse(image, ip.origin)
            except:
                await client.get_channel(CHANNEL_ID).send("Error has occurred with data parsing.")
                print("Error has occurred with data parsing.")
                err_cnt += 1
            else:
                if return_code == -1:
                    await client.get_channel(CHANNEL_ID).send("Error has occurred with data parsing.")
                    print("Error has occurred with data parsing.")
                    err_cnt += 1
                else:
                    await client.get_channel(CHANNEL_ID).send("Data parsing successful.")
                    print("Data parsing successful.")

            try:
                ip.clean() # remove all .pngs
            except:
                await client.get_channel(CHANNEL_ID).send("Clean failed.")
                print("Clean failed.")
                err_cnt += 1
            else:
                await client.get_channel(CHANNEL_ID).send("Clean successful.")
                print("Clean successful.")
            
            if err_cnt == 0:
                await client.get_channel(CHANNEL_ID).send("\nAll operations successful.")
                print("\nAll operations successful.")
            else:
                await client.get_channel(CHANNEL_ID).send(f"\n{err_cnt} error(s) occurred.")
                print(f"\n{err_cnt} error(s) occurred.")

try:
   client.run(TOKEN)
except Exception as e:
    print(e)


