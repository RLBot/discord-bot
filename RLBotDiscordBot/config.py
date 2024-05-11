import os

TOKEN = os.getenv('TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GUILDS = list(filter(lambda x: x, [
    348658686962696195,  # The RLBot server
    os.getenv('TEST_GUILD')
]))
