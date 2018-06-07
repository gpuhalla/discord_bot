from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Say
from twilio.twiml.messaging_response import MessagingResponse

import json
import datetime
import re

app = Flask(__name__)

secretFile = open("secrets.txt","r")
secretKey = secretFile.readlines()
for x in range(0, len(secretKey)):
    secretKey[x] = secretKey[x][:-1]

name = ""

@app.route("/answer_call", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()

    #Play intro sound?
    
    # Read a message aloud to the caller
    resp.say("Welcome to the Waffle House Discord Bot connection.", voice='alice')
    
    gather = Gather(input='dtmf', num_digits=6, action='/code_confirm')
    gather.say("To continue, please enter the six digit authorization code.", voice='alice')
    resp.append(gather)

    return str(resp)
    
@app.route("/code_confirm", methods=['GET', 'POST'])
def code_confirm():    
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
    
        if choice == secretKey[14]:
            resp.say("Code Confirmed. ", voice='alice')
            resp.redirect('/main_menu')
            
    return str(resp)    

    
@app.route("/main_menu", methods=['GET', 'POST'])
def main_menu():    
    resp = VoiceResponse()

    gather = Gather(num_digits=1, action='/discord_msg_menu',)
    gather.say("Main Menu. To Listen to recent messages in the discord, Press One. To post a message to the discord, Press Two.", voice='alice')
    resp.append(gather)
            
    return str(resp)
    
@app.route("/discord_msg_menu", methods=['GET', 'POST'])
def discord_msg_menu():    
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
    
        if choice =='1':
            gather = Gather(action='/call_discord_msgs')
            gather.say("Please enter the number of recent messages you would like to hear, followed by the pound sign", voice='alice')
            resp.append(gather)
        if choice =='2':
            gather = Gather(action='/msg_record_content', input='speech', timeout=3)
            gather.say("To Begin posting a message, please say your name.", voice='alice')
            resp.append(gather)
            
    return str(resp)
    
@app.route("/call_discord_msgs", methods=['GET', 'POST'])
def call_discord_msgs():    
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
    
        if int(choice) == 0:
            resp.say("Error, You must enter a value above zero", voice='alice')
            resp.redirect('/main_menu')
        elif int(choice) > 15:
            resp.say("Sorry, The Limit of messages to listen to is fifteen.", voice='alice')
            resp.redirect('/main_menu')
        else:
            #resp.say("This has not yet been implemented. Thank you for calling")
            date = datetime.date.today()
            with open("message_store.txt", 'r') as file:
                msgData = json.load(file)
                for data in range(len(msgData)-int(choice),len(msgData)):
                    msgTime = str(msgData[data]["time"]["minute"])
                    if len(msgTime) == 1:
                        msgTime = "0" + msgTime
                    if not (msgData[data]["time"]["month"] == date.month and msgData[data]["time"]["day"] == date.day):
                        resp.say("On " + str(msgData[data]["time"]["month"]) + " " + str(msgData[data]["time"]["day"]) 
                            + " at " + str(msgData[data]["time"]["hour"]) + " " + msgTime 
                            + " user " + msgData[data]["user"] + " said " + str(msgData[data]["content"]), voice='alice')
                    else:
                        resp.say("At " + str(msgData[data]["time"]["hour"]) + " " + msgTime
                            + " user " + msgData[data]["user"] + " said " + str(msgData[data]["content"]), voice='alice')
            resp.say("End of Messages.", voice='alice')
            resp.redirect('/main_menu')
            
    return str(resp)
    
@app.route("/msg_record_content", methods=['GET', 'POST'])
def msg_record_content():    
    resp = VoiceResponse()
    
    if 'SpeechResult' in request.values:
        global name
        name = request.values['SpeechResult']

        gather = Gather(action='/msg_post_content', input='speech', timeout=3)
        gather.say("Great!, Now go ahead and record your message.", voice='alice')
        resp.append(gather)
                
    return str(resp)
    
@app.route("/msg_post_content", methods=['GET', 'POST'])    
def msg_post_content():    
    resp = VoiceResponse()
    
    global name
    if 'SpeechResult' in request.values:
        message = request.values['SpeechResult']

        #post to discord
        discordMessage = "**Incoming Phone Message**\nPhone Number: " + request.values["From"][:-4] + "XXXX\tName: \"" + name + "\"\tType: Phone Call\n" + message
        with open("phonemsg.txt", 'w+') as file:
            file.write(discordMessage)
        resp.say("Okay!, the bot will post the following message. User " + name + " Message " + message, voice='alice')
        resp.redirect('/main_menu')
        
    return str(resp)
    

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message""" 
    # Start our TwiML response
    resp = MessagingResponse()
    
    # Get the message the user sent our Twilio number
    if 'Body' in request.values:
        body = request.values['Body']

        # Determine the right reply for this message
        method = re.findall(r"(?i)getmsgs|(?i)sendmsg", body)
        if method:
            if method[0].lower() == 'getmsgs':
                number = re.findall(r"\s(\d{1,2})", body)
                if number:
                    numMesgs = number[0]
                    date = datetime.date.today()
                    sendText = "\n"
                    if int(numMesgs) == 0:
                        resp.message("Error, You must enter a value above zero", voice='alice')
                    elif int(numMesgs) > 15:
                        resp.message("Sorry, The Limit of messages to listen to is fifteen.", voice='alice')
                    else:
                        with open("message_store.txt", 'r') as file:
                            msgData = json.load(file)
                            for data in range(len(msgData)-int(numMesgs),len(msgData)):
                                msgTime = str(msgData[data]["time"]["minute"])
                                if len(msgTime) == 1:
                                    msgTime = "0" + msgTime
                                if not (msgData[data]["time"]["month"] == date.month and msgData[data]["time"]["day"] == date.day):
                                    sendText += (str(msgData[data]["time"]["month"]) + "-" + str(msgData[data]["time"]["day"]) 
                                        + "\t" + str(msgData[data]["time"]["hour"]) + ":" + msgTime 
                                        + "\nUser: " + msgData[data]["user"] + "\n" + str(msgData[data]["content"]) + "\n")
                                else:
                                    sendText += (str(msgData[data]["time"]["hour"]) + ":" + msgTime 
                                        + "\nUser: " + msgData[data]["user"] + "\n" + str(msgData[data]["content"]) + "\n")
                        resp.message(sendText)
            elif method[0].lower() == 'sendmsg':
                name = re.findall(r"\n(.+)\n", body)
                content = re.findall(r"\n.+\n(.+)", body)
                if name and content:
                    discordMessage = "**Incoming Phone Message**\nPhone Number: " + request.values["From"][:-4] + "XXXX\tName: \"" + str(name[0]) + "\"\tType: Text Msg\n" + str(content[0])
                    with open("phonemsg.txt", 'w+') as file:
                        file.write(discordMessage)
                    resp.message("\nOkay! The bot will post the following message:\nUser: " + str(name[0]) + "\nMessage: " + str(content[0]))

    return str(resp)
    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)