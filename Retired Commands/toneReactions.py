import asyncio
import discord
from discord.ext import commands

import json
from watson_developer_cloud import ToneAnalyzerV3

textChatIDlist = ["170682390786605057", "302137557896921089"]

secretFile = open("secrets.txt","r")
secretKey = secretFile.readlines()
for x in range(0, len(secretKey)):
    secretKey[x] = secretKey[x][:-1]
    
toneSwitch = True

def get_tone(toneString):
    tone_analyzer = ToneAnalyzerV3(
        username=secretKey[10],
        password=secretKey[11],
        version='2017-09-21')

    #print(json.dumps(tone_analyzer.tone(text='I am very happy'), indent=2))
    preTones = json.dumps(tone_analyzer.tone({"text": toneString}, "text/plain"), indent=2)
    tones = json.loads(preTones)
    print(tones)
    
    toneList = []
    
    for tone in tones["document_tone"]["tones"]:
        #print(tones["document_tone"]["tones"])
        toneList.append(tones["document_tone"]["tones"][0]["tone_name"])
    
    return toneList
    
def reactWithTones(bot, emojis, message, toneList):
    #for tone in toneList:
        #create emojis to react with
        #emojis.append(get(bot.get_all_emojis(), name=tone))
    print(emojis)
    for tone in toneList:
        for emoji in emojis:
            if tone == emoji.name:
                self.bot.add_reaction(message, emoji)
                break
            print("no more than 6")

class toneReacts:

    def __init__(self, bot):
        self.bot = bot
        self.emojis = []
        emojiList = ["Anger", "Fear", "Joy", "Sadness", "Analytical", "Confident", "Tentative"]
        for emoji in emojiList:
            self.emojis.append(discord.utils.get(self.bot.get_all_emojis(), name=emoji))

    @commands.command(pass_context=True)
    async def tones(self, ctx, switchArg):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            global toneSwitch
            if switchArg == "off":
                toneSwitch = False
                await self.bot.say("Tone analysis is Off")
            elif switchArg == "on":
                toneSwitch = True 
                await self.bot.say("Tone analysis is On")
        
    #@self.bot.event
    async def on_message(self, message):
        if message.author.bot:
            return
        channelID = message.channel.id
        global toneSwitch
        if channelID in textChatIDlist and toneSwitch and message.content[0] != "!":
            toneList = get_tone(message.content)
            reactWithTones(self.bot, self.emojis, message, toneList)