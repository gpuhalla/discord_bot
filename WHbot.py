#REMEMBER TO CLEAN OLD HEADERS FOR INODES
import discord
from discord.ext import commands
import asyncio  #asynchronous functions
import random   #rng generator
import hashlib  #for random
import time     #for random
import logging  #logs
from subprocess import Popen

#Active function files
import music    #music file
import localPictureUpload
import databaseProxy
import reddit
import tweets   #tweets
import botSpeak
#import toneReactions
#import personality
#import phoneCall

    
with open("secrets.txt", "r") as secretFile:
    secretKey = [key[:-1] for key in secretFile.readlines()]

logging.basicConfig(level=logging.INFO) #INFO/DEBUG

textChatIDlist = ["170682390786605057", "302137557896921089", "302965414793707522", "293186321395220481"] #general, dev, nsf, other

#bot instantiator
bot = commands.Bot(command_prefix='!', description='The official Waffle House bot')
#add functionalities from each file
bot.add_cog(music.Music(bot))
bot.add_cog(localPictureUpload.LocalPictureUpload(bot))
bot.add_cog(databaseProxy.DatabaseProxy(bot))
bot.add_cog(reddit.Reddit(bot))
bot.add_cog(tweets.Twitter(bot))
bot.add_cog(botSpeak.BotSpeak(bot))
#bot.add_cog(toneReactions.ToneReacts(bot))
#bot.add_cog(personality.Personality(bot))
#bot.add_cog(phoneCall.Phone(bot))


#prints to console when bot starts up
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    channelID = message.channel.id
    #bot_chat stuff
    if channelID == "318824529478549504":
        botmessage = botSpeak.messageToBot(message.content)
        if botmessage != "":
            await bot.send_message(message.channel, botmessage)
        else:
            await bot.send_message(message.channel, "Debug: Blank response")
    #Json storage for phone
    #elif channelID == "170682390786605057":
     #   await phoneCall.manageMessageStore(message)

    #tone reaction stuff
    #if channelID in ["170682390786605057", "302137557896921089"]:# and message.content[0] != "!": #could be no content
    #   await toneReactions.processReactions(bot, message)

    await bot.process_commands(message)
    

def getAmazonLink(number):
    f = open("amazonlist.txt","r")
    lines = f.readlines()
    line = lines[number]
    start = line.index('h')
    #print(line)
    amazonLink = line[start:]
    return str(amazonLink)
    
            
#tests if bot is actually functioning
@bot.command()
async def test():
    await bot.say('Test!')
    
@bot.command(pass_context=True)
async def dance(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await bot.say("Time to Party!")
        messageToEdit = await bot.say("(ノ^_^)ノ")
        for x in range(0,4):
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "┗(＾0＾)┓")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "└( ＾ω＾ )」")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "（〜^∇^)〜")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "~( •ᴗ•)~")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "└(=^‥^=)┐")
    return
                     
@bot.command(pass_context=True)
async def spell(ctx, message : str):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        if len(message) < 21:
            messageToEdit2 = await bot.say(message[0])
            for x in range (0, len(message)):
                await bot.edit_message(messageToEdit2, message[0:x+1])
                await asyncio.sleep(.5)
        else:
            await bot.say("That's too long!")
            
@bot.command(pass_context=True)
async def why(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
         await bot.say("why not?")
         
@bot.command(pass_context=True)
async def amazon(ctx): #number : int
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        number = random.randint(0, 941)
        amazonLink = getAmazonLink(number)
        await bot.say("How many quality Amazon products are there? At least " + str(number) + ". " + str(amazonLink))
        
        
#These need to be at the bottom
#sets up loop
bot.loop.create_task(databaseProxy.pointsBackgroundTask(bot))
#bot.loop.create_task(phoneCall.checkPhoneMsg(bot))
#Dirty way that works
#Popen(["python3", "answer_call.py"])
#bot token for connection to the chat
bot.run(secretKey[0])