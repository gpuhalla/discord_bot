import discord
from discord.ext import commands
import random
import sqlite3
import time

#Exact filepath may be needed.
conn = sqlite3.connect('bot_db.sqlite')
c = conn.cursor()

#Use second cursor for all the points stuff that happens 
#in the background task to reduce conflicts with other commands
points_cursor = conn.cursor()

bot = commands.Bot(command_prefix='!', description='The official BuckeyeLAN bot')

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	bot.loop.create_task(pointsBackgroundTask())


def checkTableExists(tableName):
	#Checks if a table exists
	c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = ?", (tableName, ))
	#Returns the query result. 0 for does not exist. 1 for exists.
	return c.fetchone()[0]
	

async def pointsBackgroundTask():
	if not checkTableExists("Points"):
		points_cursor.execute("""CREATE TABLE "Points" ("UserID" VARCHAR(20) PRIMARY KEY NOT NULL UNIQUE, "numPoints" INTEGER NOT NULL DEFAULT 0)""")
	while True:
		for server in bot.servers:
			for member in server.members:
				if member.status == discord.enums.Status.online:
					await addPoints(member.id, 1)
		time.sleep(30)
	
async def addPoints(userID, numPoints):
	points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
	if points_cursor.fetchall() is None:
		points_cursor.execute("INSERT INTO Points (UserID, numPoints) VALUES (?, 0)", (str(userID), ))
		conn.commit()
	points_cursor.execute("UPDATE Points SET numPoints = numPoints + ? WHERE UserID = ?", (int(numPoints), str(userID), ))
	conn.commit()
	
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
	points_cursor.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(userID), ))
	points = points_cursor.fetchone()
	points_cursor.fetchall()
	if points is None:
		await bot.say("{0} has a total of 0 points!".format(str(name)))
	else:
		await bot.say("{0} has a total of {1} points!".format(str(name), int(points[0])))
	

@bot.command()
async def roulette(amount : int):
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
		await bot.say(quote)
		await bot.say("  -" + attributor)
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
	catNumber = random.randint(1, 325)
	catName = catNumber
	if(catNumber >= 315):
		await bot.say("BONUS ROUND")
		bonusCatNumber = random.randint(1, 22)
		catName = 'BONUS' + str(bonusCatNumber)
	imageName = "CatgirlDB\\" + str(catName) + '.jpg'
	await bot.upload(imageName)
	return
	
@bot.command()
async def shrek():
	shrekNumber = random.randint(1, 34)
	shrekName = shrekNumber
	imageName = "shrek\\" + str(shrekName) + '.png'
	await bot.upload(imageName)
	return
	
@bot.command()
async def husbando():
	return

bot.run('MjI0MjM0MzUzMTcxODkwMTc3.CrjL4A.TwmYMflSnCkmz_MSueuSSx2Y6OE')
