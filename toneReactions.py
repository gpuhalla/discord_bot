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
    
#globals for switching tones on/off
toneSwitch = False
emojis = []

def get_tone(toneString):
    tone_analyzer = ToneAnalyzerV3(
        username=secretKey[10],
        password=secretKey[11],
        version='2017-09-21')
    tone_analyzer.set_default_headers({'x-watson-learning-opt-out': "true"})

    preTones = json.dumps(tone_analyzer.tone({"text": toneString}, "text/plain"), indent=2)
    tones = json.loads(preTones)
    #print(tones)

    toneList = []
    for tone in range(0,len(tones["document_tone"]["tones"])):
        toneList.append(tones["document_tone"]["tones"][tone]["tone_name"])

    return toneList
    
async def reactWithTones(bot, emojis, message, toneList):
    for tone in toneList:
        for emoji in emojis:
            if tone == emoji.name:
                await bot.add_reaction(message, emoji)
                break
            #print("no more than 6")
            
async def processReactions(bot, message):
    if toneSwitch:
        toneList = get_tone(message.content)
        await reactWithTones(bot, emojis, message, toneList)

class ToneReacts:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tones(self, ctx, switchArg):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            global emojis, toneSwitch
            emojiList = ["Anger", "Fear", "Joy", "Sadness", "Analytical", "Confident", "Tentative"]
            for emoji in emojiList:
                emojis.append(discord.utils.get(self.bot.get_all_emojis(), name=emoji))
            #print(emojis)
            if switchArg == "off":
                toneSwitch = False
                await self.bot.say("Tone analysis is Off")
            elif switchArg == "on":
                toneSwitch = True 
                await self.bot.say("Tone analysis is On")