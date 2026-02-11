import os

TOKEN = os.getenv('TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# RLBot is a public Discord bot, but this ensures some admin commands
# can only be run in the RLBot server to protect the settings file.
GUILDS = list(filter(lambda x: x, [
    348658686962696195,  # The RLBot server
    int(os.getenv('TEST_GUILD') or '0'),  # Optional test server
]))
