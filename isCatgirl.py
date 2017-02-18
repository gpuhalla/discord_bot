import asyncio
import discord
from discord.ext import commands

import json
from watson_developer_cloud import VisualRecognitionV3


textChatIDlist = ["227203270186106890", "222886725288984576", "218047094835904512", "227209642701357056"] #funzone id, staff id, admin id, bot_development id

def getCatgirlScore(json):

    scoreList = []
    forCounter = 5
    for x in range(0, forCounter):
        scoreList.append([json[0]["classes"][x]["class"],json[0]["classes"][x]['score']])

    #print(scoreList)    
    sortedList = sorted(scoreList, key=lambda x: x[1])
    #print(sortedList)

    highestPair = sortedList[-1]

    return highestPair

def is_Catgirl(url):
    visual_recognition = VisualRecognitionV3('2016-05-20', api_key='')


    jsonResponse = json.dumps(visual_recognition.classify(images_url=url, classifier_ids=['CatgirlsandLewd_1188193286']), indent=2)
    responseLoader=json.loads(jsonResponse)
    #print(responseLoader)
    
    #isCatgirlPair = getCatgirlScore(responseLoader)
    #if('classes' in responseLoader):
    isCatgirlClass = responseLoader["images"][0]["classifiers"][0]["classes"][0]["class"]
    isCatgirlScore = float(responseLoader["images"][0]["classifiers"][0]["classes"][0]["score"])*10
    #else:
    #    isCatgirlClass = "catgirls"
    #    isCatgirlScore = 0
    prettyResponse = "Bot-chan thinks that that picture is " + str(isCatgirlScore) + "% likely to be a picture of " + isCatgirlClass + "!"
    
    return prettyResponse

class isCatgirl:

    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def iscatgirl(self, ctx, imageURL):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            result = is_Catgirl(imageURL)
            await self.bot.say(result)