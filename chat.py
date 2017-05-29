from chatterbot import ChatBot

# Create a new instance of a ChatBot
chatbot = ChatBot(
    'Feedback Learning Bot',
    storage_adapter='chatterbot.storage.JsonFileStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.BestMatch'
    ],
    input_adapter='chatterbot.input.TerminalAdapter',
    output_adapter='chatterbot.output.TerminalAdapter'
)

DEFAULT_SESSION_ID = chatbot.default_session.id

def message(message):
    try:
        return chatbot.get_response(message)
        
    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        return "Debug: Bot failed to get response"
