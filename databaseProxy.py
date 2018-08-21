import discord
from discord.ext import commands
import asyncio  #asynchronous functions
import sqlite3  #database communication
import random

conn = sqlite3.connect('bot_db.sqlite') #sqlite connection
c = conn.cursor()                       #sqlite communication cursor
points_cursor = conn.cursor()           #background cursor to reduce command conflicts

textChatIDlist = ["170682390786605057", "302137557896921089", "293186321395220481"]

#checks if a table exists
def checkTableExists(tableName):
    c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = ?", (tableName, ))
    #Returns the query result. 0 for does not exist. 1 for exists.
    return c.fetchone()[0]

#increments points for each user currently in the channel every 60s
async def pointsBackgroundTask(bot):
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


class DatabaseProxy:
    
    def __init__(self, bot):
        self.bot = bot

    #prints how many points the user has that issued the command
    @commands.command(pass_context=True)
    async def points(self, ctx):
        userID = ctx.message.author.id
        name = ctx.message.author.name
        c.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(userID), ))
        points = c.fetchone()
        c.fetchall()
        if points is None:
            await self.bot.say("{0} has a total of 0 points!".format(str(name)))
        else:
            await self.bot.say("{0} has a total of {1} points!".format(str(name), int(points[0])))
        
    #prints the top five point holders
    @commands.command()
    async def leaderboard(self):
        c.execute("SELECT UserID, numPoints FROM Points ORDER BY numPoints DESC LIMIT 5")
        leaders = c.fetchall()
        boardstring = "\n__***LEADERBOARD***__\n"
        position = 1
        for leader in leaders:
            userID = leader[0]
            points = int(leader[1])
            boardstring += "{0}.) <@{1}> with {2} points\n".format(position, userID, points)
            position += 1
        
        await self.bot.say(boardstring)

    #plays a 50% winrate game with double prize payout for the user
    #e.g. !roulette 50
    #e.g. !roulette all
    @commands.command(pass_context=True)
    async def roulette(self, ctx, amount):
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
            await self.bot.say("You have no points to wager, baka!")
        elif amount <= 0:
            await self.bot.say("You can't wager nothing, baka!")
        elif amount > points:
            await self.bot.say("That wager is too high! You can only wager {0} points! :money_mouth:".format(points))
        else:
            choice = bool(random.getrandbits(1))
            if choice:
                await addPoints(userID, amount)
                await self.bot.say(":100: :ok_hand: :100: WINNER! :100: :ok_hand: :100:")
                await self.bot.say("{0} now has {1} points!".format(name, points + amount))
            else:
                await deductPoints(userID, amount)
                await self.bot.say(":sob: :crying_cat_face: :sob: LOSER! :sob: :crying_cat_face: :sob:")
                await self.bot.say("{0} now has {1} points...".format(name, points - amount))
        return

    #prints a random quote from the sqlite database
    @commands.command()
    async def quote(self):
        #Checks if table exists first. Prints a random result if it does.
        if not checkTableExists("quotes"):
            await self.bot.say("Quote table does not exist");
        else:
            cursor = c.execute('''SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1''')
            #should pick out the second  and third fields of what the command returns
            returned = c.fetchall().pop()
            attributor = returned[1]
            quote = returned[2]
            await self.bot.say(quote + "\n  -" + attributor)
        return

    #adds a quote to the sqlite database
    #e.g. !addquote "I like food" "Lucas"
    @commands.command(pass_context=True)
    async def addquote(self, ctx, quote, attributor):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            #Checks if table exists before adding quote. Creates table if it does not.
            if not checkTableExists("quotes"):
                c.execute('''CREATE TABLE "quotes" ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `attributor` text NOT NULL, `quote` text NOT NULL )''')
            c.execute("INSERT INTO quotes (quote, attributor) VALUES (?, ?);", (quote, attributor))
        conn.commit()
        
        
        