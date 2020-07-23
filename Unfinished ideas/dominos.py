import discord
from discord.ext import commands
import asyncio  #asynchronous functions

import dominos


#https://github.com/tomasbasham/dominos

#https://rrwen.github.io/google_streetview/

textChatIDlist = ["170682390786605057", "302137557896921089", "293186321395220481"]


def getDominos(location):
    dominosApi = dominos.Client()
    response = dominosApi.get_nearest_store('AB12 000')
    print(response.json())
    return response
    
def googleView(location):
    # Import google_streetview for the api module
    import google_streetview.api

    # Define parameters for street view api
    params = [{
      'size': '600x300', # max 640x640 pixels
      'location': '46.414382,10.013988',
      'heading': '151.78',
      'pitch': '-0.76',
      'key': 'your_dev_key'
    }]

    # Create a results object
    results = google_streetview.api.results(params)

    # Preview results
    results.preview()

    # Download images to directory 'downloads'
    results.download_links('downloads')

    # Save links
    results.save_links('links.txt')

    # Save metadata
    results.save_metadata('metadata.json')
    

    
class Dominos:
    
    def __init__(self, bot):
        self.bot = bot

    #given a location, return the closest dominos?
    #maybe some extra google maps api stuff?
    #-given a location, find nearest store, translate to lat/long(?) and then produce streetview picture/maybe maps picture?
    @commands.command(pass_context=True)
    async def dominos(self, ctx, store):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            dominos = getDominos(store)
            await self.bot.say(store)
            
            
    '''        
    #get a store menu(which store?)
    #get store menu, create browse-able menu using message reactions
    @commands.command(pass_context=True)
    async def dominosmenu(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            await self.bot.say("todo2")
    '''
    