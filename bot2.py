import discord
from discord.ext import commands
import random   #rng generator
import sqlite3  #database communication
import asyncio  #asynchronous functions
import os       #folder scanning
import praw     #reddit api
import hashlib  #for random
import time     #for random

import music    #music file
import youtube_dl #for music converting

#import speechRecognition #speech stuff 

#import systools

import tweets

#import tone

#import isCatgirl

r = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='',
                     username='')
conn = sqlite3.connect('bot_db.sqlite') #sqlite connection
c = conn.cursor()                       #sqlite communication cursor
points_cursor = conn.cursor()           #background cursor to reduce command conflicts
masterDBList = {}                       #List of folders in the same directory as the bot
bonusDBList = {}                        #List of nested bonus folders
textChatIDlist = ["170682390786605057", "302137557896921089", "302965414793707522", "293186321395220481"] 

#a whole bunch of nonsense to get somewhat better random values
timeCounter = str(time.time())
timeCounter = timeCounter.encode('utf-8')
sudoRandom = hashlib.sha256(timeCounter).hexdigest()
random.seed(sudoRandom)

#bot instantiator
bot = commands.Bot(command_prefix='!', description='The official BuckeyeLAN bot')
#add music functionaility from file
bot.add_cog(music.Music(bot))
#bot.add_cog(speechRecognition.Speech(bot)) 
#bot.add_cog(systools.SysTools(bot))
bot.add_cog(tweets.Twitter(bot))
#bot.add_cog(tone.Tone(bot))
#bot.add_cog(isCatgirl.isCatgirl(bot))

#prints to console when bot starts up
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

#checks if a table exists
def checkTableExists(tableName):
    c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = ?", (tableName, ))
    #Returns the query result. 0 for does not exist. 1 for exists.
    return c.fetchone()[0]
    
#Method for picking a random picture in a folder located in the same directory
#as the bot. Default probability is 1/100
#e.g. !pic husbandodb
#e.g. !pic husbandodb 200
async def uploadRandomPicture(inputFolder, bonusProb=100):
    folderName = inputFolder
    
    #adds folder to dictionary if it is not already there.
    #key: folder name, value: list of items in folder
    if not folderName in masterDBList:
        try:
            masterDBList[folderName] = os.listdir(folderName)
        except:
            await bot.say("Error in directory listing. Check that folder exists.")
            return
            
    #bonus operations
    rngNumber=0
    if bonusProb != 0:
        rngNumber = random.randint(1, bonusProb)
    bonusfolder = folderName + "//" + folderName + "bonus"
    if rngNumber == 1:
        if not bonusfolder in bonusDBList:
            try:
                bonusDBList[bonusfolder] = os.listdir(bonusfolder)
            except:
                await bot.say("Error in directory listing. Check that bonusfolder exists.")
                return
        await bot.say("__***BONUS ROUND***__")
        length = len(bonusDBList.get(bonusfolder))
        rngNumber = random.randint(0, length - 1)
        fileName = bonusDBList.get(bonusfolder)[rngNumber]
        while fileName == "Thumbs.db":
            rngNumber = random.randint(0, length - 1)
            fileName = bonusDBList.get(bonusfolder)[rngNumber]
        #print(bonusfolder + "\\" + bonusDBList.get(bonusfolder)[rngNumber]) #debug for bonus error
        await bot.upload(bonusfolder + "//" + bonusDBList.get(bonusfolder)[rngNumber])
        return
    
    #normal operations
    length = len(masterDBList.get(folderName))
    rngNumber = random.randint(0, length - 1)
    fileName = masterDBList.get(folderName)[rngNumber]
    while fileName == "Thumbs.db":
        rngNumber = random.randint(0, length - 1)
        fileName = masterDBList.get(folderName)[rngNumber]
    #print(folderName + "//" + masterDBList.get(folderName)[rngNumber])
    await bot.upload(folderName + "//" + masterDBList.get(folderName)[rngNumber])
    return

#increments points for each user currently in the channel every 60s
async def pointsBackgroundTask():
    await bot.wait_until_ready()
    if not checkTableExists("Points"):
        points_cursor.execute("""CREATE TABLE "Points" ("UserID" VARCHAR(20) PRIMARY KEY NOT NULL UNIQUE, "numPoints" INTEGER NOT NULL DEFAULT 0)""")
    while not bot.is_closed:
        for server in bot.servers:
            for member in server.members:
                if member.status == discord.enums.Status.online and member.id != bot.user.id:
                    await addPoints(member.id, 1)
        await asyncio.sleep(60)

#adds points to a user
#e.g. addPoints(member.id, 1)       
async def addPoints(userID, numPoints):
    points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
    if points_cursor.fetchone() is None:
        points_cursor.execute("INSERT INTO Points (UserID, numPoints) VALUES (?, 0)", (str(userID), ))
        conn.commit()
    points_cursor.fetchall()
    points_cursor.execute("UPDATE Points SET numPoints = numPoints + ? WHERE UserID = ?", (int(numPoints), str(userID), ))
    conn.commit()

#removes points from a user
#e.g. deductPoints(member.id, 1) 
async def deductPoints(userID, numPoints):
    points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
    if points_cursor.fetchone() is None:
        points_cursor.execute("INSERT INTO Points (UserID, numPoints) VALUES (?, 0)", (str(userID), ))
        conn.commit()
    points_cursor.fetchall()
    points_cursor.execute("UPDATE Points SET numPoints = numPoints - ? WHERE UserID = ?", (int(numPoints), str(userID), ))
    conn.commit()

#pulls the top few hot posts from the requested subreddit
#e.g. getHotSubRedditImage("awwnime", 25)
async def getHotSubRedditImage(subreddit, numHot):
    #returns an array of the top # hot posts from a subreddit
    subredditPics = r.subreddit(subreddit).hot(limit=numHot)
    #set up url array
    i = 0
    urlArray = [0] * 25
    #create url array
    for item in subredditPics:
        urlArray[i] = (item.url)
        i+=1
    #random number in array
    subrngNumber = random.randint(0, numHot - 1)
    #picks a random url from the array
    await bot.say(urlArray[subrngNumber])
    return 

def getAmazonLink(number):
    f = open("amazonlist.txt","r")
    lines = f.readlines()
    line = lines[number]
    start = line.index('h')
    #print(line)
    amazonLink = line[start:]

    return str(amazonLink)
    
#tests if bot is actually functioning
@bot.command()
async def test():
    await bot.say('Test!')

#prints how many points the user has that issued the command
@bot.command(pass_context=True)
async def points(ctx):
    userID = ctx.message.author.id
    name = ctx.message.author.name
    c.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(userID), ))
    points = c.fetchone()
    c.fetchall()
    if points is None:
        await bot.say("{0} has a total of 0 points!".format(str(name)))
    else:
        await bot.say("{0} has a total of {1} points!".format(str(name), int(points[0])))
    
#prints the top five point holders
@bot.command()
async def leaderboard():
    c.execute("SELECT UserID, numPoints FROM Points ORDER BY numPoints DESC LIMIT 5")
    leaders = c.fetchall()
    boardstring = "\n__***LEADERBOARD***__\n"
    position = 1
    for leader in leaders:
        userID = leader[0]
        points = int(leader[1])
        boardstring += "{0}.) <@{1}> with {2} points\n".format(position, userID, points)
        position += 1
    
    await bot.say(boardstring)

#plays a 50% winrate game with double prize payout for the user
#e.g. !roulette 50
#e.g. !roulette all
@bot.command(pass_context=True)
async def roulette(ctx, amount : str):
    userID = ctx.message.author.id
    name = ctx.message.author.name
    c.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(userID), ))
    points = c.fetchone()
    c.fetchall()

    points = int(points[0])
    if amount.strip().lower() == "all":
        amount = points
    else:
        amount = int(float(amount))
        
    if points is None or points == 0:
        await bot.say("You have no points to wager, baka!")
    elif amount <= 0:
        await bot.say("You can't wager nothing, baka!")
    elif amount > points:
        await bot.say("That wager is too high! You can only wager {0} points! :money_mouth:".format(points))
    else:
        choice = bool(random.getrandbits(1))
        if choice:
            await addPoints(userID, amount)
            await bot.say(":100: :ok_hand: :100: WINNER! :100: :ok_hand: :100:")
            await bot.say("{0} now has {1} points!".format(name, points + amount))
        else:
            await deductPoints(userID, amount)
            await bot.say(":sob: :crying_cat_face: :sob: LOSER! :sob: :crying_cat_face: :sob:")
            await bot.say("{0} now has {1} points...".format(name, points - amount))
    return

#prints a random quote from the sqlite database
@bot.command()
async def quote():
    #Checks if table exists first. Prints a random result if it does.
    if not checkTableExists("quotes"):
        await bot.say("Quote table does not exist");
    else:
        cursor = c.execute('''SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1''')
        #should pick out the second  and third fields of what the command returns
        returned = c.fetchall().pop()
        attributor = returned[1]
        quote = returned[2]
        await bot.say(quote + "\n  -" + attributor)
    return

#adds a quote to the sqlite database
#e.g. !addquote "I like food" "Lucas"
@bot.command(pass_context=True)
async def addquote(ctx, quote : str, attributor: str):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        #Checks if table exists before adding quote. Creates table if it does not.
        if not checkTableExists("quotes"):
            c.execute('''CREATE TABLE "quotes" ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `attributor` text NOT NULL, `quote` text NOT NULL )''')
        c.execute("INSERT INTO quotes (quote, attributor) VALUES (?, ?);", (quote, attributor))
    conn.commit()

#the whole reason this bot exists
@bot.command(pass_context=True)
async def catgirl(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await uploadRandomPicture("CatgirlDB", 100)
    return

@bot.command(pass_context=True)
async def shrek(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await uploadRandomPicture("shrek", 0)
    return
    
@bot.command(pass_context=True)
async def husbando(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await uploadRandomPicture("husbandodb", 100)
    return

@bot.command(pass_context=True)
async def scute(ctx):
    channelID = ctx.message.channel.id
    #print(channelID) debug to find channel id
    if channelID in textChatIDlist:
        await getHotSubRedditImage("awwnime", 25)
    return

@bot.command(pass_context=True)
async def reddit(ctx, reddit : str):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await getHotSubRedditImage(reddit, 25)
    return      

@bot.command(pass_context=True)
async def fuckmarrykill(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
		#Old functionaility
        # await bot.say("Bachelor(ette) #1")
        # await uploadRandomPicture("fmk", 0)
        # await asyncio.sleep(2)
        # await bot.say("Bachelor(ette) #2")
        # await uploadRandomPicture("fmk", 0)
        # await asyncio.sleep(2)
        # await bot.say("Bachelor(ette) #3")
        # await uploadRandomPicture("fmk", 0)
		await bot.say("Bachelor(ette) #1")
        await getHotSubRedditImage("gentlemanboners", 25)
		await bot.say("Bachelor(ette) #2")
        await getHotSubRedditImage("LadyBoners", 25)
		await bot.say("Bachelor(ette) #3")
		rngNumber = random.randint(1, 3)
		if rngNumber == 1:
			await getHotSubRedditImage("gentlemanboners", 25)
		elif rngNumber == 2:
			await getHotSubRedditImage("LadyBoners", 25)
		else:
			await uploadRandomPicture("fmk", 0)
    return
    
@bot.command(pass_context=True)
async def dance(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        await bot.say("Time to Party!")
        messageToEdit = await bot.say("(ノ^_^)ノ")
        for x in range(0,4):
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "┗(＾0＾)┓")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "└( ＾ω＾ )」")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "（〜^∇^)〜")
            await asyncio.sleep(.75)
            await bot.edit_message(messageToEdit, "└(=^‥^=)┐")
    return
                     
@bot.command(pass_context=True)
async def spell(ctx, message : str):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        if len(message) < 21:
            messageToEdit2 = await bot.say(message[0])
            for x in range (0, len(message)):
                await bot.edit_message(messageToEdit2, message[0:x+1])
                await asyncio.sleep(.5)
        else:
            await bot.say("That's too long!")
            
@bot.command(pass_context=True)
async def why(ctx):
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
         await bot.say("why not?")
         
@bot.command(pass_context=True)
async def amazon(ctx): #number : int
    channelID = ctx.message.channel.id
    if channelID in textChatIDlist:
        #can't check for nonexistant arguements in commands extension?
        '''
        if number == "":
            number = random.randint(0, 941)
        elif number < 0:
            number = 0
        elif number > 941:
            number  = 941
        '''
        number = random.randint(0, 941)
        amazonLink = getAmazonLink(number)
        await bot.say("How many quality Amazon products are there? At least " + str(number) + ". " + str(amazonLink))         

        
        
#These need to be at the bottom
#sets up loop
bot.loop.create_task(pointsBackgroundTask())
#bot token for connection to the chat
bot.run('')