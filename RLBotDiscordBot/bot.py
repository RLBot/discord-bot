import json
import logging
import os.path
import sys

import discord
from discord.ext import commands

try:
    from config import TOKEN
except ImportError:
    print('Unable to run bot, as token does not exist!')
    sys.exit()

initial_extensions = (
    'cogs.admin',
    'cogs.dm',
    'cogs.sendclip',
    'cogs.calendar'
)


class RLBotDiscordBot(commands.Bot):
    def __init__(self):
        if os.path.exists('./RLBotDiscordBot/settings.json'):
            self.settings_path = './RLBotDiscordBot/settings.json'
        else:
            self.settings_path = '../RLBotDiscordBot/settings.json'
        with open(self.settings_path, 'r') as settings:
            self.settings = json.load(settings)

        activity = discord.Game(name=self.settings['Status_message'])

        super().__init__(command_prefix='!', activity=activity)

        self.logger = logging.getLogger(__name__)
        self.remove_command('help')

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                print(f'Cog loaded: {extension}')
            except Exception as e:
                self.logger.error(f'There was an error loading the extension {extension}. Error: {e}')

    async def on_ready(self):
        self.logger.info(f'{self.user} online! (ID: {self.user.id})')

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
            # Check if the message doesn't start with other (not in settings.json) command
            # This is done to prevent conflits
            # Not sure if this is the best way to do it, but this is the best I could do.
            commands_tuple = tuple(self.command_prefix + c.name for c in self.commands)
            content = message.content.lower()
            if not content.startswith(commands_tuple):
                for command in self.settings['commands']:
                    string_divided = content.split()
                    for triggers in string_divided:
                        if triggers.startswith(command):
                            await message.channel.send(self.settings['commands'][command])
                            return

    async def on_command_error(self, error, ctx):
        if isinstance(error, commands.CommandNotFound):
            print(error)

    def run(self):
        super().run(TOKEN, reconnect=True)
