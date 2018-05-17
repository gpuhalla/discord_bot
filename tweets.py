import asyncio
import discord
from discord.ext import commands

import tweepy

import random  

from datetime import datetime
import time

#https://gist.github.com/yanofsky/5436496

secretFile = open("secrets.txt","r")
secretKey = secretFile.readlines()
for x in range(0, len(secretKey)):
    secretKey[x] = secretKey[x][:-1]
    
#Twitter API credentials
consumer_key = secretKey[6]
consumer_secret = secretKey[7]
access_key = secretKey[8]
access_secret = secretKey[9]

textChatIDlist = ["170682390786605057", "302137557896921089", "293186321395220481"]
    
def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    #initialize a list to hold all the tweepy Tweets
    alltweets = []  
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=110)
    
    #save most recent tweets
    alltweets.extend(new_tweets)
    
    #save the id of the oldest tweet less one
    #oldest = alltweets[-1].id - 1
    
    #transform the tweepy tweets into a 2D array that will populate the csv 
    outtweets = [[tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]
    
    rngNumber = random.randint(2, 100)
    
    pickedTweet = outtweets[rngNumber]
    
    dt_obj = pickedTweet[0]   
    date_str = dt_obj.strftime("%m-%d-%Y    %H:%M:%S")
    
    tweetText = str(pickedTweet[1])
    #print(tweetText)
    tweetText = tweetText.replace('\\n', '\n')
    #print(tweetText)
    
    formattedTweet = "Twitter: @" + screen_name + "\n" + date_str + "\n" + tweetText[2: len(tweetText)-1]
    
    if '@' in tweetText[:8]:
        formattedTweet = get_all_tweets(screen_name)
    
    return str(formattedTweet)
    
class Twitter:

    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tweet(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            tweet = get_all_tweets("LuncanDucas")
            await self.bot.say(tweet)