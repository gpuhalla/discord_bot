import discord
from discord.ext import commands
import random
import sqlite3

#Exact filepath may be needed.
conn = sqlite3.connect('bot_db.sqlite')
c = conn.cursor()

bot = commands.Bot(command_prefix='!', description='The official BuckeyeLAN bot')

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
	
	
@bot.command()
async def commend():
	await bot.say('Added one point to !')
	return

@bot.command()
async def test():
	await bot.say('Test!')

@bot.command()
async def points():
	await bot.say(' has a total of xxx points!')
	return

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
		returned = c.fetchall()
		await bot.say(returned)
		await bot.say(type(returned))
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

bot.run('MjI0MjM0MzUzMTcxODkwMTc3.CrYQfA.gA246SiyVTS_SICctEo-7JJKwRU')
