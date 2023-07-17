import discord
from discord.ext import commands, tasks
import asyncio  #asynchronous functions
import sqlite3  #database communication
import time
import random

conn = sqlite3.connect('bot_db.sqlite') #sqlite connection
c = conn.cursor()                       #sqlite communication cursor
points_cursor = conn.cursor()           #background cursor to reduce command conflicts

textChatIDlist = [170682390786605057, 302137557896921089, 302965414793707522, 293186321395220481, 570471843538927638, 318824529478549504] 

bettingTable = []
gambleStarter = ""
gambleOptions = []
removableOptions = []
gambleType = ""

#checks if a table exists
def checkTableExists(tableName):
    c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = ?", (tableName, ))
    #Returns the query result. 0 for does not exist. 1 for exists.
    return c.fetchone()[0]

#adds points to a user
#e.g. addPoints(member.id, 1)       
async def addPoints(userID, numPoints):
    points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
    if points_cursor.fetchone() is None:
        points_cursor.execute("INSERT INTO Points (UserID, numPoints, lastMessage) VALUES (?, 0, 0)", (str(userID), ))
        conn.commit()
    points_cursor.fetchall()
    points_cursor.execute("UPDATE Points SET numPoints = numPoints + ? WHERE UserID = ?", (int(numPoints), str(userID), ))
    conn.commit()

#removes points from a user
#e.g. deductPoints(member.id, 1) 
async def deductPoints(userID, numPoints):
    points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
    if points_cursor.fetchone() is None:
        points_cursor.execute("INSERT INTO Points (UserID, numPoints, lastMessage) VALUES (?, 0, 0)", (str(userID), ))
        conn.commit()
    points_cursor.fetchall()
    points_cursor.execute("UPDATE Points SET numPoints = numPoints - ? WHERE UserID = ?", (int(numPoints), str(userID), ))
    conn.commit()

#updates a user's entry with the unix time of their last message sent
async def updateLastMessage(userID, uTime):
    points_cursor.execute("SELECT * FROM Points WHERE UserID = ?", (str(userID), ))
    if points_cursor.fetchone() is None:
        points_cursor.execute("INSERT INTO Points (UserID, numPoints, lastMessage) VALUES (?, 0, 0)", (str(userID), ))
        conn.commit()
    points_cursor.fetchall()
    points_cursor.execute("UPDATE Points SET lastMessage = ? WHERE UserID = ?", (uTime, str(userID), ))
    conn.commit()
    

class DatabaseProxy(commands.Cog, name='DatabaseProxy'):
    
    def __init__(self, bot):
        self.bot = bot
        self.pointsBackgroundTask.start()

    #prints how many points the user has that issued the command
    @commands.command()
    async def points(self, ctx):
        userID = ctx.message.author.id
        name = ctx.message.author.name
        c.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(userID), ))
        points = c.fetchone()
        c.fetchall()
        if points is None:
            await ctx.send("{0} has a total of 0 points!".format(str(name)))
        else:
            await ctx.send("{0} has a total of {1} points!".format(str(name), int(points[0])))
        
    #prints the top five point holders
    @commands.command()
    async def leaderboard(self, ctx):
        c.execute("SELECT UserID, numPoints FROM Points ORDER BY numPoints DESC LIMIT 5")
        leaders = c.fetchall()
        boardstring = "\n__***LEADERBOARD***__\n"
        position = 1
        for leader in leaders:
            userID = leader[0]
            points = int(leader[1])
            boardstring += "{0}.) <@{1}> with {2} points\n".format(position, userID, points)
            position += 1
        
        await ctx.send(boardstring)

    #plays a 50% winrate game with double prize payout for the user
    #e.g. !roulette 50
    #e.g. !roulette all
    @commands.command()
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
            await ctx.send("You have no points to wager, baka!")
        elif amount <= 0:
            await ctx.send("You can't wager nothing, baka!")
        elif amount > points:
            await ctx.send("That wager is too high! You can only wager {0} points! :money_mouth:".format(points))
        else:
            choice = bool(random.getrandbits(1))
            if choice:
                await addPoints(userID, amount)
                await ctx.send(":100: :ok_hand: :100: WINNER! :100: :ok_hand: :100:")
                await ctx.send("{0} now has {1} points!".format(name, points + amount))
            else:
                await deductPoints(userID, amount)
                await ctx.send(":sob: :crying_cat_face: :sob: LOSER! :sob: :crying_cat_face: :sob:")
                await ctx.send("{0} now has {1} points...".format(name, points - amount))
        return

    #prints a random quote from the sqlite database
    @commands.command()
    async def quote(self, ctx):
        #Checks if table exists first. Prints a random result if it does.
        if not checkTableExists("quotes"):
            await ctx.send("Quote table does not exist");
        else:
            cursor = c.execute('''SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1''')
            #should pick out the second  and third fields of what the command returns
            returned = c.fetchall().pop()
            attributor = returned[1]
            quote = returned[2]
            await ctx.send(quote + "\n  -" + attributor)
        return

    #adds a quote to the sqlite database
    #e.g. !addquote "I like food" "Lucas"
    @commands.command()
    async def addquote(self, ctx, quote, attributor):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            #Checks if table exists before adding quote. Creates table if it does not.
            if not checkTableExists("quotes"):
                c.execute('''CREATE TABLE "quotes" ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `attributor` text NOT NULL, `quote` text NOT NULL )''')
            c.execute("INSERT INTO quotes (quote, attributor) VALUES (?, ?);", (quote, attributor))
        conn.commit()
        
    @commands.command()
    async def bet(self, ctx, option, amount):
        channelID = ctx.message.channel.id
        if channelID == 318824529478549504:
            userID = ctx.message.author.id
            name = ctx.message.author.name
            global gambleStarter, gambleType, gambleOptions, removableOptions
            if gambleStarter == "":
                await ctx.send("No gamble running, baka!")
            elif gambleType == "double" and gambleStarter == userID:
                await ctx.send("STOP CHEATING BAAAAKAAAA!!!")
            else:
                if option not in gambleOptions:
                    await ctx.send("That isn't a gamble option!")
                elif gambleType == "all" and option not in removableOptions:
                    await ctx.send("Someone already took that, baka!")
                else:
                    if gambleType == "all":
                        removableOptions.remove(option)
                
                    c.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(userID), ))
                    points = c.fetchone()
                    c.fetchall()

                    points = int(points[0])
                    if amount.strip().lower() == "all":
                        amount = points
                    else:
                        amount = int(float(amount))
                        
                    emoji = '❌' 
                    if points is None or points == 0:
                        await ctx.message.add_reaction(emoji)
                        await ctx.send("You have no points to bet, baka!")
                    elif amount <= 0:
                        await ctx.message.add_reaction(emoji)
                        await ctx.send("You can't bet nothing, baka!")
                    elif amount > points:
                        await ctx.message.add_reaction(emoji)
                        await ctx.send("That bet is too high! You can only bet {0} points!".format(points))
                    else:
                        global bettingTable
                        for bet in bettingTable:
                            if bet[0] == ctx.message.author.id:
                                bettingTable.remove(bet)
                                break
                        bettingTable.append([ctx.message.author.id, ctx.message.author.name, option, amount])
                        emoji = '✅'
                        await ctx.message.add_reaction(emoji)
    
                
    @commands.command()
    async def gamble(self, ctx, type, *options):
        channelID = ctx.message.channel.id
        userID = ctx.message.author.id
        global gambleStarter, gambleOptions, gambleType, removableOptions
        if channelID == 318824529478549504:
            if gambleStarter != "":
                await ctx.send("A gamble is already in progress!")
            elif type.lower() not in ["weighted", "all", "double"]:
                await ctx.send("That isn't a gamble type!")
            elif options == None or len(options) < 2:
                await ctx.send("Your gamble needs multiple options!")
            else:
                gambleStarter = userID
                gambleOptions = list(options)
                gambleType = type.lower()
                #print(type(gamebleOptions)
                removableOptions = gambleOptions
                gamestring = ""
                if gambleType == "weighted":
                    gamestring = "It's a weighted gamble, bet more win more! "
                elif gambleType == "all":
                    gamestring = "It's all or nothing, winner takes all! "
                else:
                    gamestring = "It's double or nothing, double your wager! "
                gambleString = "Gamble has Started! " + gamestring + "Please select one of the following options: "
                for option in options:
                    gambleString = gambleString + "\n" + option
                await ctx.send(gambleString)
            
    @commands.command()
    async def winner(self, ctx, option):
        channelID = ctx.message.channel.id
        userID = ctx.message.author.id
        global bettingTable, gambleType, gambleStarter
        if channelID == 318824529478549504 and userID == gambleStarter: #needs to be me
            fullWinnerString = "No bets, baka!"
            winString = ""
            if gambleType == "double":
                for bet in bettingTable:
                    if bet[2] == option:
                        fullWinnerString = ""
                        await addPoints(bet[0], bet[3])
                        winString = "<@" + str(bet[0]) + "> is a winner! +" + str(bet[3]) + " points!\n"
                        fullWinnerString += winString
                    else:
                        await deductPoints(bet[0], bet[3])
                        lostString = "<@" + str(bet[0]) + "> is a loser! -" + str(bet[3]) + " points!\n"
                        fullWinnerString += lostString
            elif gambleType == "weighted":
                value = 0
                valueWinners = 0
                winners = []
                for bet in bettingTable:
                    value += bet[3]
                    await deductPoints(bet[0], bet[3])
                    if bet[2] == option:
                        winners.append([bet[0], bet[3]])
                        valueWinners += bet[3]
                if len(winners) == 0:
                    winString = "No winners, everyone loses!"
                else:
                    for winner in winners:
                        await addPoints(winner[0], value * (winner[1] // valueWinners))
                        winString = "<@" + str(winner[0]) + "> is a winner! +" + str((value * (winner[1] // valueWinners)) - winner[1]) + " points!\n"
                fullWinnerString = ""
                fullWinnerString += winString
            elif gambleType == "all":
                fullWinnerString = ""
                value = 0
                winner = ""
                for bet in bettingTable:
                    value += bet[3]
                    await deductPoints(bet[0], bet[3])
                    if bet[2] == option:
                        winner = bet[0]              
                await addPoints(winner, value)
                winString = "<@" + str(bet[0]) + "> is the winner! The pot was " + str(value) + " points!\n"
                fullWinnerString += winString
            await ctx.send(fullWinnerString)
            bettingTable = []
            gambleStarter = ""
            gambleOptions = []
            removableOptions = []
            gambleType = ""
        elif channelID == 318824529478549504 and userID == 147867330917957633 and option == "x":
            await ctx.send("Bet ended manually!")
            bettingTable = []
            gambleStarter = ""
            gambleOptions = []
            removableOptions = []
            gambleType = ""
        else:
            await ctx.send("No gamble in progress, baka!")
        
    #increments points for each user currently in the channel every 60s
    @tasks.loop(seconds=60)
    async def pointsBackgroundTask(self):
        await self.bot.wait_until_ready()
        if not checkTableExists("Points"):
            points_cursor.execute("""CREATE TABLE "Points" ("UserID" VARCHAR(20) PRIMARY KEY NOT NULL UNIQUE, "numPoints" INTEGER NOT NULL DEFAULT 0, "lastMessage" INTEGER NOT NULL DEFAULT 0)""")
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                for member in guild.members:
                    points_cursor.execute("SELECT lastMessage FROM Points WHERE UserID = ?", (str(member.id), ))
                    lastMessage = points_cursor.fetchone()
                    points_cursor.fetchall()
                    if lastMessage == None:
                        lastMessage = (0, 0) #LUCAS
                    userActive = (int(time.time()) - lastMessage[0]) <= 2592000
                    if userActive and member.status == discord.enums.Status.online and member.id != self.bot.user.id:
                        await addPoints(member.id, 1)
            await asyncio.sleep(60)
        
def setup(bot):
    bot.add_cog(DatabaseProxy(bot))
        