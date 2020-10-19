import asyncio
import discord
from discord.ext import commands

import utils
import markovify    #for markov chains

textChatIDlist = [170682390786605057, 302137557896921089, 302965414793707522, 293186321395220481, 570471843538927638, 318824529478549504] 

#Markov chains    
def buildComment(dbFilename):
    # Get raw text as string.
    with open("MessageLogs/" + dbFilename + ".txt") as f:
        text = f.read()
    # Build the model.
    text_model = markovify.NewlineText(text) 
    # Print randomly-generated sentences
    return text_model.make_sentence()

    
class BotSpeak(commands.Cog, name='BotSpeak'):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def simulate(self, ctx, username):
        channelID = ctx.message.channel.id
        channelToGetData = self.bot.get_channel(170682390786605057) #general
        username = username.strip("<>@!")
        if channelID in textChatIDlist:
            await utils.buildDatabase(username, channelToGetData)
            comment = buildComment(username)
            if comment is None:
                comment = "Sorry, I'm having a hard time simulating that user."
            await ctx.send(comment)
            
def setup(bot):
    bot.add_cog(BotSpeak(bot))