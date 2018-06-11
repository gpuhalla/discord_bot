import discord
from discord.ext import commands
import asyncio  #asynchronous functions

import os
import random

masterDBList = {}                       #List of folders in the same directory as the bot
bonusDBList = {}                        #List of nested bonus folders

textChatIDlist = ["170682390786605057", "302137557896921089", "302965414793707522", "293186321395220481"] #general, dev, nsf, other

#Method for picking a random picture in a folder located in the same directory
#as the bot. Default probability is 1/100
#e.g. !pic husbandodb
#e.g. !pic husbandodb 200
async def uploadRandomPicture(bot, inputFolder, bonusProb=100):
    folderName = inputFolder
    
    #adds folder to dictionary if it is not already there.
    #key: folder name, value: list of items in folder
    if not folderName in masterDBList:
        try:
            masterDBList[folderName] = os.listdir(folderName)
        except:
            await bot.say("Error in directory listing. Check that folder exists.")
            return
            
    #bonus operations
    rngNumber=0
    if bonusProb != 0:
        rngNumber = random.randint(1, bonusProb)
    bonusfolder = folderName + "//" + folderName + "bonus"
    if rngNumber == 1:
        if not bonusfolder in bonusDBList:
            try:
                bonusDBList[bonusfolder] = os.listdir(bonusfolder)
            except:
                await bot.say("Error in directory listing. Check that bonusfolder exists.")
                return
        await bot.say("__***BONUS ROUND***__")
        length = len(bonusDBList.get(bonusfolder))
        rngNumber = random.randint(0, length - 1)
        fileName = bonusDBList.get(bonusfolder)[rngNumber]
        while fileName == "Thumbs.db":
            rngNumber = random.randint(0, length - 1)
            fileName = bonusDBList.get(bonusfolder)[rngNumber]
        #print(bonusfolder + "\\" + bonusDBList.get(bonusfolder)[rngNumber]) #debug for bonus error
        await bot.upload(bonusfolder + "//" + bonusDBList.get(bonusfolder)[rngNumber])
        return
    
    #normal operations
    length = len(masterDBList.get(folderName))
    rngNumber = random.randint(0, length - 1)
    fileName = masterDBList.get(folderName)[rngNumber]
    while fileName == "Thumbs.db":
        rngNumber = random.randint(0, length - 1)
        fileName = masterDBList.get(folderName)[rngNumber]
    #print(folderName + "//" + masterDBList.get(folderName)[rngNumber])
    await bot.upload(folderName + "//" + masterDBList.get(folderName)[rngNumber])
    return
    

class LocalPictureUpload:
    
    def __init__(self, bot):
        self.bot = bot    

    #the whole reason this bot exists
    @commands.command(pass_context=True)
    async def catgirl(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            await uploadRandomPicture(self.bot, "CatgirlDB", 100)
        return

    @commands.command(pass_context=True)
    async def shrek(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            await uploadRandomPicture(self.bot, "shrek", 0)
        return
        
    @commands.command(pass_context=True)
    async def husbando(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            await uploadRandomPicture(self.bot, "husbandodb", 100)
        return   
    
    # Supplanted by version in reddit - Old functionaility
    # @commands.command(pass_context=True)
    # async def fuckmarrykill(self, ctx):
        # channelID = ctx.message.channel.id
        # if channelID in textChatIDlist:
            # await self.bot.say("Bachelor(ette) #1")
            # await uploadRandomPicture("fmk", 0)
            # await asyncio.sleep(2)
            # await self.bot.say("Bachelor(ette) #2")
            # await uploadRandomPicture("fmk", 0)
            # await asyncio.sleep(2)
            # await self.bot.say("Bachelor(ette) #3")
            # await uploadRandomPicture("fmk", 0)