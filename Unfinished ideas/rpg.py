import discord
from discord.ext import commands
import sqlite3  #database communication
import random


class Character:
	
	def __init__(self, id):
		self.conn = sqlite3.connect('bot_db.sqlite') #sqlite connection
		self.c = self.conn.cursor()                       #sqlite communication cursor
		self.id = id
		self.level = 1
		self.exp = 0
		self.points = 0
		self.physicalDamage = 5
		self.fireDamage = 0
		self.iceDamage = 0
		self.shockDamage = 0
		self.primaryHand = 0
		self.secondaryHand = 0
		self.physicalArmor = 0
		self.fireArmor = 0
		self.iceArmor = 0
		self.shockArmor = 0
		self.body = 0
		self.pants = 0
		self.helmet = 0
		self.gloves = 0
		self.boots = 0
		self.health = 20
		self.getCharacter(id)
		
	def getCharacter(self, id = "0"):
		if id == "0":
			print("No user input id")
		else:
			self.c.execute("SELECT * FROM rpgcharacter WHERE userID = ?", (str(id), ))
			fetched = self.c.fetchone()
			self.level = fetched[1]
			self.exp = fetched[2]
			self.c.execute("SELECT numPoints FROM Points WHERE UserID = ?", (str(fetched[3]), ))
			points = self.c.fetchone()
			self.points = points[0]
			self.physicalDamage = fetched[4]
			self.fireDamage = fetched[5]
			self.iceDamage = fetched[6]
			self.shockDamage = fetched[7]
			self.primaryHand = fetched[8]
			self.secondaryHand = fetched[9]
			self.physicalArmor = fetched[10]
			self.fireArmor = fetched[11]
			self.iceArmor = fetched[12]
			self.shockArmor = fetched[13]
			self.body = fetched[14]
			self.pants = fetched[15]
			self.helmet = fetched[16]
			self.gloves = fetched[17]
			self.boots = fetched[18]
			self.health = fetched[19]
			
	def saveCharacter(self):
		
		if self.id == "0":
			print("No user input id")
		else:
			self.c.execute("UPDATE rpgcharacter SET level = ?, exp = ?, points = ?, physicalDamage = ?, fireDamage = ?, iceDamage = ?, shockDamage = ?, primaryHand = ?, secondaryHand = ?, physicalArmor = ?, fireArmor = ?, iceArmor = ?, shockArmor = ?, body = ?, pants = ?, helmet = ?, gloves = ?, boots = ?, health = ? WHERE userID = ?", (self.level, self.exp, str(self.id), self.physicalDamage, self.fireDamage, self.iceDamage, self.shockDamage, self.primaryHand, self.secondaryHand, self.physicalArmor, self.fireArmor, self.iceArmor, self.shockArmor, self.body, self.pants, self.helmet, self.gloves, self.boots, self.health, str(self.id), ))
			self.conn.commit()
			
	def getItems(self):
		if self.id == "0":
			print("No user input id")
		else:
			self.c.execute("SELECT * FROM rpgitems WHERE owner = ?", (str(self.id), ))
			items = self.c.fetchall()
			return items
		
class Item:
	def __init__(self, id = 0, owner = 0, price = 0, type = "", hands = 0, physicalDamage = 0, fireDamage = 0, iceDamage = 0, shockDamage = 0, physicalArmor = 0, fireArmor = 0, iceArmor = 0, shockArmor = 0, attributes = "", name = ""):
		self.conn = sqlite3.connect('bot_db.sqlite') #sqlite connection
		self.c = self.conn.cursor()                       #sqlite communication cursor
		self.id = id
		self.owner = owner
		self.price = price
		self.type = type
		self.hands = hands
		self.physicalDamage = physicalDamage
		self.fireDamage = fireDamage
		self.iceDamage = iceDamage
		self.shockDamage = shockDamage
		self.physicalArmor = physicalArmor
		self.fireArmor = fireArmor
		self.iceArmor = iceArmor
		self.shockArmor = shockArmor
		self.attributes = attributes
		self.name = name
#		if id != 0:
#			self.getItem(id)
#		else:
#			self.genItem
		
	def getItem(self, id = "0"):
		if id == "0":
			print("No item input id")
		else:
			self.c.execute("SELECT * FROM rpgitems WHERE ID = ?", (str(id), ))
			fetched = self.c.fetchone()
			self.owner = fetched[1]
			self.price = fetched[2]
			self.type = fetched[3]
			self.hands = fetched[4]
			self.physicalDamage = fetched[5]
			self.fireDamage = fetched[6]
			self.iceDamage = fetched[7]
			self.shockDamage = fetched[8]
			self.physicalArmor = fetched[9]
			self.fireArmor = fetched[10]
			self.iceArmor = fetched[11]
			self.shockArmor = fetched[12]
			self.attributes = fetched[13]
			self.name = fetched[14]
	
	def addItem(self, userid = "0"):
		if userid == "0":
			print("No user input id")
		else:
			self.c.execute("INSERT INTO rpgitems (owner, price, type, hands, physicalDamage, fireDamage, iceDamage, shockDamage, physicalArmor, fireArmor, iceArmor, shockArmor, attributes, name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(userid), self.price, self.type, self.hands, self.physicalDamage, self.fireDamage, self.iceDamage, self.shockDamage, self.physicalArmor, self.fireArmor, self.iceArmor, self.shockArmor, self.attributes, self.name, ))
			self.conn.commit()
	
	def genWeapon(self):
		tier = random.randint(1, 5)
		#type: (base price, hands, base damage)
		types = {"Sword": (50, 2, 10)}
		#quality: (price multiplier, damage multiplier)
		qualities = {"Fine": (2, 2)}
		#material: (price additive, physicalDamage additive, fireDamage additive, iceDamage additive, shockDamage additive)
		materials = {"Glass": (50, 0, 0, 0, 10)}
		#attribute: (price additive, marker)
		attributes = {"of Vampirism": (100, "V")}
		
		typekey = random.choice(list(types.keys()))
		type = types.get(typekey)
		qualitykey = random.choice(list(qualities.keys()))
		quality = qualities.get(qualitykey)
		materialkey = random.choice(list(materials.keys()))
		material = materials.get(materialkey)
		attributekey = random.choice(list(attributes.keys()))
		attribute = attributes.get(attributekey)
		
		self.price = type[0]
		self.hands = type[1]
		self.physicalDamage = type[2]
			
		self.price += material[0]
		self.physicalDamage += material[1]
		self.fireDamage += material[2]
		self.iceDamage += material[3]
		self.shockDamage += material[4]
		
		self.price += attribute[0]
		self.attribute = attribute[1]
		
		self.price *= quality[0] * tier
		self.physicalDamage *= quality[1] * tier
		self.fireDamage *= quality[1] * tier
		self.iceDamage *= quality[1] * tier
		self.shockDamage *= quality[1] * tier
		
		self.name = qualitykey + " " + materialkey + " " + typekey + " " + attributekey
        
        
    def getShopItems(self):
        shopList = [rpg.Item(0)]*10
        for each item in shoplist:
            item.genWeapon()
        return shopList
        
    @commands.command(pass_context=True)
    async def rpgitemshop(self, ctx):
        itemList = getShopItems()
        markdownString = "```\n__**Item Shop**__\n"
        counter = 0
        for item in shopList:
            itemName = item.name[counter]
            itemPrice = item.price[counter]
            markdownString += "{0}.) <@{1}>      {2} points\n".format(counter+1, itemName, itemPrice)
            counter += 1
            
        markdownString += "```"
        self.bot.say(markdownString)
		
    @commands.command(pass_context=True)
    async def rpgbuy(self, ctx, item: int):
		if item < 11 and item > 0:
            #subtract points
            #aaaaaaa this involves me figuring out the same problem for sr
            
            #add item to character inv
            c.execute("SELECT UserID, numPoints FROM Points ORDER BY RANDOM() LIMIT 10")
            leaders = c.fetchall()
            
            #remove item from shop
            
        
        else
            self.bot.say("Not a valid Item Shop number")
        
        
        