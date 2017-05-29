from chatterbot import ChatBot

# Create a new instance of a ChatBot
bot = ChatBot(
    'Feedback Learning Bot',
    storage_adapter='chatterbot.storage.JsonFileStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.BestMatch'
    ],
    input_adapter='chatterbot.input.TerminalAdapter',
    output_adapter='chatterbot.output.TerminalAdapter'
)

DEFAULT_SESSION_ID = bot.default_session.id



# Get a response to an input statement
bot.get_response("Hello, how are you today?")

# The following loop will execute each time the user enters input
async def message(message):
    try:
        response = bot.get_response(message)
		
    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break