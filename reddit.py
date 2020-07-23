import asyncio
import discord
from discord.ext import commands

import random
import praw     #reddit api

textChatIDlist = [170682390786605057, 302137557896921089, 302965414793707522, 293186321395220481, 570471843538927638] 

with open("secrets.txt", "r") as secretFile:
    secretKey = [key[:-1] for key in secretFile.readlines()]

redd = praw.Reddit(client_id=secretKey[1],
                client_secret=secretKey[2],
                password=secretKey[3],
                user_agent=secretKey[4],
                username=secretKey[5])


#pulls the top few hot posts from the requested subreddit
#e.g. getHotSubRedditImage("awwnime", 25)
def getHotSubRedditImage(subreddit, numHot):
    #returns an array of the top # hot posts from a subreddit
    subredditPics = redd.subreddit(subreddit).hot(limit=numHot)
    #set up url array
    i = 0
    urlArray = [0] * 25
    #create url array
    for item in subredditPics:
        urlArray[i] = (item.url)
        i+=1
    #random number in array
    subrngNumber = random.randint(0, numHot - 1)
    #picks a random url from the array
    return urlArray[subrngNumber]
    
class Reddit(commands.Cog, name='Reddit'):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def scute(self, ctx):
        channelID = ctx.message.channel.id
        #print(channelID) debug to find channel id
        if channelID in textChatIDlist:
            link =  getHotSubRedditImage("awwnime", 25)
            await ctx.send(link)
        return

    @commands.command(pass_context=True)
    async def reddit(self, ctx, subreddit):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            link = getHotSubRedditImage(subreddit, 25)
            await ctx.send(link)
        return   
        
    
    @commands.command(pass_context=True)
    async def fuckmarrykill(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            await ctx.send("Bachelor(ette) #1")
            link = getHotSubRedditImage("gentlemanboners", 25)
            await ctx.send(link)
            await ctx.send("Bachelor(ette) #2")
            link = getHotSubRedditImage("LadyBoners", 25)
            await ctx.send(link)
            await ctx.send("Bachelor(ette) #3")
            rngNumber = random.randint(1, 3)
            if rngNumber == 1:
                link = getHotSubRedditImage("gentlemanboners", 25)
                await ctx.send(link)
            elif rngNumber == 2:
                link = getHotSubRedditImage("LadyBoners", 25)
                await ctx.send(link)

        return

def setup(bot):
    bot.add_cog(Reddit(bot))