#REMEMBER TO CLEAN OLD HEADERS FOR INODES
import discord
from discord.ext import commands
from discord import app_commands
import asyncio  #asynchronous functions
import random   #rng generator
import hashlib  #for random
import time     #for random
import logging  #logs

#Active function files
import databaseProxy

textChatIDlist = [170682390786605057, 302137557896921089, 302965414793707522, 293186321395220481, 570471843538927638, 318824529478549504] #general, dev, nsf, other, spam

#bot instantiator
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', description='The official Waffle House bot', intents = intents)


async def main():  
    with open("secrets.txt", "r") as secretFile:
        secretKey = [key[:-1] for key in secretFile.readlines()]

    logging.basicConfig(level=logging.INFO) #INFO/DEBUG

    #add functionalities from each file
    await bot.load_extension("newMusic")
    await bot.load_extension("localPictureUpload")
    await bot.load_extension("databaseProxy")
    await bot.load_extension("reddit")
    await bot.load_extension("tweets")
    await bot.load_extension("botSpeak")
    #await bot.load_extension("loopback_speak")

    async with bot:
        await bot.start(secretKey[0])


#prints to console when bot starts up
@bot.event
async def on_ready():
    #bot.app_commands.CommandTree.sync()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await databaseProxy.updateLastMessage(message.author.id, int(time.time()))
    await bot.process_commands(message)
    
#tests if bot is actually functioning
@bot.hybrid_command()
async def test(ctx):
    await ctx.send('Test!')
    
@bot.hybrid_command()
async def dance(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await ctx.send("Time to Party!")
        messageToEdit = await ctx.send("(ノ^_^)ノ")
        for x in range(0,4):
            await asyncio.sleep(.75)
            await messageToEdit.edit(content="┗(＾0＾)┓")
            await asyncio.sleep(.75)
            await messageToEdit.edit(content="└( ＾ω＾ )」")
            await asyncio.sleep(.75)
            await messageToEdit.edit(content="（〜^∇^)〜")
            await asyncio.sleep(.75)
            await messageToEdit.edit(content= "~( •ᴗ•)~")
            await asyncio.sleep(.75)
            await messageToEdit.edit(content="└(=^‥^=)┐")
    return
                     
@bot.hybrid_command()
async def spell(ctx, message : str):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        if len(message) < 21:
            messageToEdit = await ctx.send(message[0])
            for x in range (0, len(message)):
                await messageToEdit.edit(content=message[0:x+1])
                await asyncio.sleep(.5)
        else:
            await ctx.send("That's too long!")
            
@bot.hybrid_command()
async def why(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
         await ctx.send("why not?")

#These need to be at the bottom
#bot token for connection to the chat
asyncio.run(main())