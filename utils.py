import asyncio
import discord
from discord.ext import commands

import aiofiles
import os
import time

#Single user large comment storage 
async def buildDatabase(username, channel, bot):
    if os.path.exists("MessageLogs/" + username + ".txt"):
        if os.path.getmtime("MessageLogs/" + username + ".txt") < time.time() - 86400: #if a db is more than 1 day old
            async with aiofiles.open("MessageLogs/" + username + ".txt", 'w+') as file:
                async for message in bot.logs_from(channel, limit=4000):
                    if message.author.id == username: # and str(message.content)[0] != "!":
                        #print(message.content)     #somehow it breaks without these lines
                        #print(message.author.id)
                        #print(username[3:len(username)-1])
                        await file.write("{}\n".format(message.content))
            await file.close()
    else:
        async with aiofiles.open("MessageLogs/" + username + ".txt", 'w+') as file:
            async for message in bot.logs_from(channel, limit=4000):
                if message.author.id == username: # and str(message.content)[0] != "!":
                    #print(message.content)     #somehow it breaks without these lines
                    #print(message.author.id)
                    #print(username[3:len(username)-1])
                    await file.write("{}\n".format(message.content))
            await file.close()
            