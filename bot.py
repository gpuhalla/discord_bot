import discord
from discord.ext import commands
import random
import sqlite3
import asyncio
import os

#Exact filepath may be needed.
conn = sqlite3.connect('bot_db.sqlite')
c = conn.cursor()

#Use second cursor for all the points stuff that happens 
#in the background task to reduce conflicts with other commands
points_cursor = conn.cursor()

bot = commands.Bot(command_prefix='!', description='The official BuckeyeLAN bot')
masterDBList = {}
bonusDBList = {}

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')


def checkTableExists(tableName):
	#Checks if a table exists
	c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = ?", (tableName, ))
	#Returns the query result. 0 for does not exist. 1 for exists.
	return c.fetchone()[0]
	
#Method for picking a random picture in a folder located in the same directory
#as the bot. Format is "!pic exampledb" or "!pic exampledb 200" for custom
#probability
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
	bonusfolder = folderName + "\\" + folderName + "bonus"
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
		await bot.upload(bonusfolder + "\\" + bonusDBList.get(bonusfolder)[rngNumber])
		return
	
	#normal operations
	length = len(masterDBList.get(folderName))
	rngNumber = random.randint(0, length - 1)
	fileName = masterDBList.get(folderName)[rngNumber]
	while fileName == "Thumbs.db":
		rngNumber = random.randint(0, length - 1)
		fileName = masterDBList.get(folderName)[rngNumber]
	await bot.upload(folderName + "\\" + masterDBList.get(folderName)[rngNumber])
	return

async def pointsBackgroundTask():
	await bot.wait_until_ready()
	if not checkTableExists("Points"):
		points_cursor.execute("""CREATE TABLE "Points" ("UserID" VARCHAR(20) PRIMARY KEY NOT NULL UNIQUE, "numPoints" INTEGER NOT NULL DEFAULT 0)""")
	while not bot.is_closed:
		for server in bot.servers:
			for member in server.members:
				if member.status == discord.enums.Status.online and member.id is not bot.user.id:
					await addPoints(member.id, 1)
		await asyncio.sleep(60)
	
async def addPoints(userID, numPoints):
	points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
	if points_cursor.fetchone() is None:
		points_cursor.execute("INSERT INTO Points (UserID, numPoints) VALUES (?, 0)", (str(userID), ))
		conn.commit()
	points_cursor.fetchall()
	points_cursor.execute("UPDATE Points SET numPoints = numPoints + ? WHERE UserID = ?", (int(numPoints), str(userID), ))
	conn.commit()
	
async def deductPoints(userID, numPoints):
	points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
	if points_cursor.fetchone() is None:
		points_cursor.execute("INSERT INTO Points (UserID, numPoints) VALUES (?, 0)", (str(userID), ))
		conn.commit()
	points_cursor.fetchall()
	points_cursor.execute("UPDATE Points SET numPoints = numPoints - ? WHERE UserID = ?", (int(numPoints), str(userID), ))
	conn.commit()
	
@bot.command()
async def printusers():
	await bot.say("Members")
	for server in bot.servers:
		for member in server.members:
			await bot.say("***Member***")
			await bot.say(member)
			await bot.say("***Member ID***")
			await bot.say(member.id)
	await bot.say("***bot.user.id***")
	await bot.say(bot.user.id)
	await bot.say("***bot.user***")
	await bot.say(bot.user)
	await bot.say("***bot***")
	await bot.say(bot)
	
@bot.command()
async def commend():
	await bot.say('Added one point to !')
	return

@bot.command()
async def test():
	await bot.say('Test!')

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
	
@bot.command()
async def addquote(quote : str, attributor: str):
	#Checks if table exists before adding quote. Creates table if it does not.
	if not checkTableExists("quotes"):
		c.execute('''CREATE TABLE "quotes" ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `attributor` text NOT NULL, `quote` text NOT NULL )''')
	c.execute("INSERT INTO quotes (quote, attributor) VALUES (?, ?);", (quote, attributor))
	conn.commit()
	
@bot.command()
async def catgirl():
	await uploadRandomPicture("CatgirlDB", 100)
	return
	
@bot.command()
async def shrek():
	await uploadRandomPicture("shrek", 0)
	return
	
@bot.command()
async def husbando():
	await uploadRandomPicture("husbandodb")
	return

@bot.command()
async def pic(folder : str):
	await uploadRandomPicture(folder, 0)
	return

@bot.command()
async def fuckmarrykill():
	await bot.say("Bachelor(ette) #1")
	await uploadRandomPicture("fmk", 0)
	await asyncio.sleep(2)
	await bot.say("Bachelor(ette) #2")
	await uploadRandomPicture("fmk", 0)
	await asyncio.sleep(2)
	await bot.say("Bachelor(ette) #3")
	await uploadRandomPicture("fmk", 0)
	return
	
bot.loop.create_task(pointsBackgroundTask())
bot.run('MjI0MjM0MzUzMTcxODkwMTc3.CrjL4A.TwmYMflSnCkmz_MSueuSSx2Y6OE')
