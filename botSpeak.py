import asyncio
import discord
from discord.ext import commands

import utils
from chatterbot import ChatBot     #Lucas' chat stuff
import markovify    #for markov chains

textChatIDlist = ["170682390786605057", "302137557896921089", "302965414793707522", "293186321395220481"] #general, dev, nsf, other

# Create a new instance of a ChatBot
chatbot = ChatBot('DaisyBot')

def messageToBot(message):
    try:
        return chatbot.get_response(message)
        
    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        return "Debug: Bot failed to get response"
           
#Markov chains    
def buildComment(dbFilename):
    # Get raw text as string.
    with open("MessageLogs/" + dbFilename + ".txt") as f:
        text = f.read()
    # Build the model.
    text_model = markovify.NewlineText(text) 
    # Print randomly-generated sentences
    return text_model.make_sentence()

    
class BotSpeak:
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def simulate(self, ctx, username):
        channelID = ctx.message.channel.id
        channelToGetData = self.bot.get_channel("170682390786605057") #general
        username = username.strip("<>@!")
        if channelID in textChatIDlist:
            await utils.buildDatabase(username, channelToGetData, self.bot)
            comment = buildComment(username)
            if comment is None:
                comment = "Sorry, I'm having a hard time simulating that user."
            await self.bot.say(comment)