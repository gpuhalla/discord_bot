from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Say

import json
import datetime

app = Flask(__name__)

secretFile = open("secrets.txt","r")
secretKey = secretFile.readlines()
for x in range(0, len(secretKey)):
    secretKey[x] = secretKey[x][:-1]

name = ""

@app.route("/answer", methods=['GET', 'POST'])
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
            gather = Gather(action='/discord_msgs')
            gather.say("Please enter the number of recent messages you would like to hear, followed by the pound sign", voice='alice')
            resp.append(gather)
        if choice =='2':
            gather = Gather(action='/msg_record_content', input='speech', timeout=3)
            gather.say("To Begin posting a message, please say your name.", voice='alice')
            resp.append(gather)
            
    return str(resp)
    
@app.route("/discord_msgs", methods=['GET', 'POST'])
def discord_msgs():    
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
    
        if int(choice) == 0:
            resp.say("You must enter a value above zero", voice='alice')
            resp.redirect('/main_menu')
        elif int(choice) > 15:
            resp.say("The Limit of messages to hear is fifteen.", voice='alice')
            resp.redirect('/main_menu')
        else:
            #resp.say("This has not yet been implemented. Thank you for calling")
            date = datetime.date.today()
            with open("message_store.txt", 'r') as file:
                msgData = json.load(file)
                for data in range(len(msgData)-int(choice),len(msgData)):
                    if not (msgData[data]["time"]["month"] == date.month and msgData[data]["time"]["day"] == date.day):
                        resp.say("On " + str(msgData[data]["time"]["month"]) + " " + str(msgData[data]["time"]["day"]) 
                            + " at " + str(msgData[data]["time"]["hour"]) + " " + str(msgData[data]["time"]["minute"]) 
                            + " user " + msgData[data]["user"] + " said " + msgData[data]["content"] + "\n", voice='alice')
                    else:
                        resp.say("At " + str(msgData[data]["time"]["hour"]) + " " + str(msgData[data]["time"]["minute"]) 
                            + " user " + msgData[data]["user"] + " said " + msgData[data]["content"] + "\n", voice='alice')
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
        discordMessage = "**Phone Message**\n__Phone Number__: " + request.values["From"][:-4] + "XXXX\t__Name:__ \"" + name + "\"\n" + message
        with open("phonemsg.txt", 'w+') as file:
            file.write(discordMessage)
        resp.say("Okay!, the bot will post the following message. User " + name + " has posted the following message over the phone. " + message, voice='alice')
        resp.redirect('/main_menu')
        
    return str(resp)
    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)