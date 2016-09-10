import discord
import asyncio

async def commandCommend(message):
	return

async def commandTest(message):
	counter = 0
	tmp = await client.send_message(message.channel, 'Calculating messages...')
	async for log in client.logs_from(message.channel, limit=100):
		if log.author == message.author:
			counter += 1

	await client.edit_message(tmp, 'You have {} messages.'.format(counter))
	
async def commandPoints(message):
	return

async def commandRoulette(message):
	return
	
async def commandQuote(message):
	return
	
async def commandCatgirl(message):
	return

async def commandHusbando(message):
	return

commands = {
	'!commend'	: commandCommend,
	'!test' 	: commandTest,
	'!points'	: commandPoints,
	'!roulette' : commandRoulette,
	'!quote'	: commandQuote,
	'!catgirl'	: commandCatgirl,
	'!husbando'	: commandHusbando
}
	
client = discord.Client()
	
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
	if message.content.startswith('!'):
		cmd = message.content.partition(' ')[0]
		if cmd in commands.keys():
			await commands[cmd](message)

