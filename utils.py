import asyncio
import discord
from discord.ext import commands

import aiofiles
import os
import time

#Single user large comment storage 
async def buildDatabase(username, channel):
    if os.path.exists("MessageLogs/" + username + ".txt"):
        if os.path.getmtime("MessageLogs/" + username + ".txt") < time.time() - 86400: #if a db is more than 1 day old
            async with aiofiles.open("MessageLogs/" + username + ".txt", 'w+') as file:
                async for message in channel.history(limit=10):
                    if message.author.id == int(username): # and str(message.content)[0] != "!":
                        await file.write("{}\n".format(message.content))
            await file.close()
    else:
        async with aiofiles.open("MessageLogs/" + username + ".txt", 'w+') as file:
            async for message in channel.history(limit=4000):
                if message.author.id == int(username): # and str(message.content)[0] != "!":
                    await file.write("{}\n".format(message.content))
            await file.close()
            