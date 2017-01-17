import asyncio
import discord
from discord.ext import commands

import json
from watson_developer_cloud import ToneAnalyzerV3

textChatIDlist = ["227203270186106890", "222886725288984576", "218047094835904512", "227209642701357056"] #funzone id, staff id, admin id, bot_development id

def getClosestTone(json, toneCategory):
    forCounter = 5
    if toneCategory == 1:
        forCounter = 3

    scoreList = []
    directory = json["document_tone"]["tone_categories"][toneCategory]["tones"]
    for x in range(0, forCounter):
        scoreList.append([json["document_tone"]["tone_categories"][toneCategory]["tones"][x]["tone_name"],json["document_tone"]["tone_categories"][toneCategory]["tones"][x]['score']])

    #print(scoreList)    
    sortedList = sorted(scoreList, key=lambda x: x[1])
    #print(sortedList)


    highestPair = sortedList[-1]
    #highName = str(highestPair[0])
    #highScore = str(highestPair[1])

    #print(highName + " : " + highScore)
    
    return highestPair
"""
def getScore(json, toneCategory, tone):
    subTone = 0
    if tone == "anger" || tone == "analytical" || tone == "openness_big5":
        subTone = 0
    elif tone == "disgust" || tone == "confident" || tone == "conscientiousness_big5":
        subTone = 1
    elif tone == "fear" || tone == "tenative" || tone == "extraversion_big5":
        subTone = 2
    elif tone == "joy" || tone == "agreeableness":
        subTone = 3
    elif tone == "sadness" || tone == "neuroticism_big5": #aka Emotional Enage
        subTone = 4
        
    score = json["document_tone"]["tone_categories"][toneCategory]["tones"][subTone]["score"]

    return score

"""
def get_tone(toneString):
    tone_analyzer = ToneAnalyzerV3(
        username='',
        password='',
        version='2016-02-11')

    #print(json.dumps(tone_analyzer.tone(text='I am very happy'), indent=2))
    preTones = json.dumps(tone_analyzer.tone(text=toneString), indent=2)
    tones=json.loads(preTones)
    
    #0 for emotion, 1 for writing, 2 for social
    emotionPair = getClosestTone(tones, 0)
    emotionTone = emotionPair[0]
    emotionScore = str(emotionPair[1])
    
    writingPair = getClosestTone(tones, 1)
    writingTone = writingPair[0]
    writingScore = str(writingPair[1])
    
    socialPair = getClosestTone(tones, 2)
    socialTone = socialPair[0]
    socialScore = str(socialPair[1])
    
    prettyTones = "String: \"" + toneString + "\"\n" + "Results:\n" + emotionTone + ": " + emotionScore + "\n" + writingTone + ": " + writingScore + "\n" + socialTone + ": " + socialScore
    
    return prettyTones

class Tone:

    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tone(self, ctx, toneString):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            toneResponse = get_tone(toneString)
            await self.bot.say(toneResponse)