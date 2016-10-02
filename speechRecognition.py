#!/usr/bin/env python3
# NOTE: this example requires PyAudio because it uses the Microphone class

import asyncio
import discord
from discord.ext import commands

import music

#from bot import getHotSubRedditImage

from gtts import gTTS
from tempfile import TemporaryFile

import speech_recognition as sr

textChatIDlist = ["227209642701357056"] #bot_development id



if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')
    
        

async def readUsingTTS(ttsMessage, voiceIn):
   
    tts = gTTS(text=ttsMessage, lang="en")
    voiceTempFile = TemporaryFile()
    tts.write_to_fp(voiceTempFile)
    
    #voiceConnect = yield from client.join_voice_channel(channel)
    voicePlayer = voiceIn.create_ffmpeg_player(voiceTempFile)
    voicePlayer.start()
    voiceTempFile.close()
    return  


    
class Speech:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass
                
    @commands.command(pass_context=True, no_pm=True)
    async def listen(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
        
            summoned_channel = ctx.message.author.voice_channel
            voice = await self.bot.join_voice_channel(summoned_channel)
            
        
            # obtain audio from the microphone
            r = sr.Recognizer()
            
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
            
            print("Say something!")
            
            activeListening = True
            while(activeListening):
            
                with sr.Microphone() as source:
                    #print("Say something!")
                    audio = r.listen(source)

                # recognize speech using Google Speech Recognition
                try:
                    # for testing purposes, we're just using the default API key
                    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                    # instead of `r.recognize_google(audio)`
                    voiceData = r.recognize_google(audio)
                    print(voiceData)
                    #print("Google Speech Recognition thinks you said " + voiceData)
                    #await self.bot.say("Google Speech Recognition thinks you said " + voiceData)
                    if 'banana' in voiceData:
                        await self.bot.say("Banana!")
                    elif 'bot search' in voiceData:
                        imageInfo = voiceData[7:]
                        #bot.getHotSubRedditImage(imageInfo, 25)
                    elif 'build turret' in voiceData:
                        await self.bot.say("__***CANCEL COMMAND***__")
                    elif 'cat girl' in voiceData:
                        await self.bot.say("_NYAA_")
                        await readUsingTTS("NYAAAAA", voice)
                    elif 'robot stop' in voiceData:
                        activeListening = False
                    
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                    #await self.bot.say("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    #await self.bot.say("Could not request results from Google Speech Recognition service; {0}".format(e))
                
                
                
from bot.py import getHotSubRedditImage #this doesn't work :/
