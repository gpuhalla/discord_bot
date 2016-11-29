import asyncio
import discord
from discord.ext import commands

import hashlib                          #for random
import time                             #for random

import smtplib                          #for email
from email.mime.text import MIMEText    #for writing email

import sys                              #to be able to shutdown/restart
import os                               #file management

import time     #for random


#MOST STUFF COMMENTED OUT RELATES TO GMAIL API, I'LL GET AROUND TO IT EVENTUALLY


#GMAIL Imports
"""
from httplib2 #import Http
import base64
from apiclient import errors

from apiclient.discovery import build

credentials = get_credentials()
service = build('gmail', 'v1', http=credentials.authorize(Http()))
"""

userIDlist = ["147867330917957633"] #Gap ID
generatedCode = 0                   #need global for check
commandToBeRun = ''
actionToBeRun = ''
emailTextFile = 'emailTextFile.txt' #where the email is written


#GMAIL Block
"""
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Quickstart'


def get_credentials():
    """#Gets valid user credentials from storage.

    #If nothing has been stored, or if the stored credentials are invalid,
    #the OAuth2 flow is completed to obtain the new credentials.

    #Returns:
        #Credentials, the obtained credential.
"""
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials
"""



#generates 2 factor code
def generateCode():
    timeCounter = str(time.time())
    timeCounter = timeCounter.encode('utf-8')
    sudoRandom = hashlib.sha256(timeCounter).hexdigest()
    sudoRandom = sudoRandom[:6]
    return sudoRandom

#writes email and appends 2 factor code
def writeEmail(action):
    global generatedCode
    generatedCode = generateCode()
    fp = open(emailTextFile, 'w')
    fp.write("A remote " + action + " action has been called in the Discord. To allow this action to execute, please enter the following code on your next message.\n" + generatedCode)
    fp.close()
    #print(generatedCode) debug

def sendEmail(action):

    #GMAIL
    """
    emailMessage = writeEmail(action)
    service = 
    user_id = toaddr
    try:
        emailMessage = (service.users().messages().send(userId=user_id, body=emailMessage).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    """
    
    #creates email from text file
    writeEmail(action)
    fp = open(emailTextFile, 'r')
    msg = MIMEText(fp.read())
    fp.close()
    
    #reads login and destination info from file (so it isn't on thew web)
    with open('emailLoginTextFile.txt') as fp: lines = [line.rstrip('\n') for line in fp]
    fp.close();
    
    #build email
    subjectString = 'BuckeyeLAN Discord Bot Notification'
    from_addr = lines[0]
    to_addr = lines[2]
    msg['Subject'] = subjectString
    msg['From'] = from_addr
    msg['To'] = to_addr
    
    #send email
    smtpserver = 'smtp.gmail.com:587'
    login = lines[0]
    password = lines[1]
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()
    
        
class SysTools:

    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def execute(self, ctx, action, *commandOrCode):
        #stored code and action to check
        global generatedCode
        global actionToBeRun
        userID = ctx.message.author.id
        if userID in userIDlist:
            if action in ['shutdown', 'restart', 'command', 'nuke']:
                #store command and action
                commandToBeRun = commandOrCode
                actionToBeRun = action
                await self.bot.say("A remote " + action + " command has been issued by <@147867330917957633>. A security code has been emailed to your address to confirm the action.")
                #send email
                sendEmail(action)
            elif action == 'confirm':
                if(commandOrCode[0] == generatedCode):
                    await self.bot.say("Security code Confirmed. Starting " + actionToBeRun)
                    
                    if actionToBeRun == 'shutdown':
                        #shutdown
                        print('shutdown executed')
                        await sys.exit() #quit() would only kill one script
                        
                    elif actionToBeRun == 'restart':
                        #restart
                        print('restart executed')
                        await os.execv(sys.executable, ['python'] + sys.argv)
                        
                    elif actionToBeRun == 'nuke':
                        print('nuke executed')
                        await self.bot.say("The nuke will detonate in 60 seconds unless the disarm command is sent.")
                    
                    """    
                    elif actionToBeRun == 'command':
                        #execute command
                        exec(commandToBeRun) #hahaha what could ever go wrong here
                    """
                    
                    #else:
                    #    print('Something went wrong') #More Debug
                        
                else:
                     await self.bot.say("Incorrect Security Code")
                     
                     
    """                 
    @commands.command(pass_context=True)
    async def rewrite(self, ctx, messageID, editedMessage):
        channelID = ctx.message.channel.id
        userID = ctx.message.author.id
        if userID in userIDlist:
            channelWithMessage = self.bot.loop.get_channel(channelID)
            print(channelWithMessage)
            messageToBeRewritten = self.bot.loop.get_message(channelWithMessage,messageID)
            print(messageToBeRewritten)
            await self.bot.edit_message(messageToBeRewritten, editedMessage)
    """
        

                     

