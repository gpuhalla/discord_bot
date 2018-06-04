import asyncio
import discord
from discord.ext import commands

import json

textChatIDlist = ["170682390786605057", "302137557896921089"]

secretFile = open("secrets.txt","r")
secretKey = secretFile.readlines()
for x in range(0, len(secretKey)):
    secretKey[x] = secretKey[x][:-1]

async def manageMessageStore(message):
    with open("message_store.txt", 'r+') as file:
        msgData = json.load(file)
        msgData = msgData["messages"][1:]
        entry = {"time": {"month": message.timestamp.month, "day": message.timestamp.day,
                    "hour": message.timestamp.hour, "minute": message.timestamp.minute}, 
                    "user": message.author.nick, "content": message.content}
        msgData.append(entry)
        #print(msgData)
        file.write(json.dumps(msgData, indent=2))
        file.truncate()
        file.close()

class Phone:
    
    def __init__(self, bot):
        self.bot = bot

    async def inbound(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            print("test")