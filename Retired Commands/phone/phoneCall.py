import asyncio
import discord
from discord.ext import commands

import json
import os

textChatIDlist = ["170682390786605057", "302137557896921089"]

mtime = 0
if os.path.exists("phonemsg.txt"):
    mtime = os.path.getmtime("phonemsg.txt")

async def manageMessageStore(message):
    msgData = []
    with open("message_store.txt", 'r') as file:
        msgData = json.load(file)
        msgData.pop(0)
        username = message.author.nick
        if username is None:
            username = message.author.name
        entry = {"time": {"month": message.timestamp.month, "day": message.timestamp.day,
                    "hour": message.timestamp.hour, "minute": message.timestamp.minute}, 
                    "user": username, "content": message.content}
        msgData.append(entry)
        #print(msgData)
    with open("message_store.txt", 'w') as outfile:
        json.dump(msgData, outfile)
        
async def checkPhoneMsg(bot):
    global mtime
    await bot.wait_until_ready()
    channel = bot.get_channel("170682390786605057")
    while not bot.is_closed:
        if os.path.exists("phonemsg.txt"):
            if os.path.getmtime("phonemsg.txt") > mtime:
                with open("phonemsg.txt", 'r') as file:
                    await bot.send_message(channel, file.read())
                mtime = os.path.getmtime("phonemsg.txt")
            await asyncio.sleep(60)

class Phone:
    
    def __init__(self, bot):
        self.bot = bot

