import json
import logging
import os.path
import sys
import re

import discord
from discord.ext import commands
from discord import app_commands

try:
    from config import TOKEN
except ImportError:
    print('Unable to run bot, as token does not exist!')
    sys.exit()

initial_extensions = (
    'cogs.admin',
    'cogs.dm',
    'cogs.sendclip',
    'cogs.calendar',
    'cogs.faq',
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

        super().__init__(command_prefix='!', activity=activity, intents=discord.Intents.all())

        self.logger = logging.getLogger(__name__)
        self.remove_command('help')

    async def setup_hook(self) -> None:

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
                print(f'Cog loaded: {extension}')
            except Exception as e:
                self.logger.error(f'There was an error loading the extension {extension}. Error: {e}')

    async def on_ready(self):
        self.logger.info(f'{self.user} online! (ID: {self.user.id})')

        if 'slash_commands' in self.settings:
            for name in self.settings['slash_commands']:
                desc = self.settings['slash_commands'][name][0]
                # command = re.sub('[^abcdefghijklmnopqrstuvxwyz0123456789\-_]', '', command)
                # skip = False
                # for ready_command in self.tree.get_commands():
                #     if command == ready_command.name:
                #         skip = True
                d_command: app_commands.Command = app_commands.Command(callback=self.on_command, description=desc, name=name)
                # if not skip:
                self.tree.add_command(d_command)

        await self.tree.sync()

    async def on_command(self, interaction: discord.Interaction):
        if interaction.command.name in self.settings['slash_commands']:
            await interaction.response.send_message(self.settings['slash_commands'][interaction.command.name][1])
        return

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
            # Check if the message doesn't start with other (not in settings.json) command
            # This is done to prevent conflits
            # Not sure if this is the best way to do it, but this is the best I could do.
            commands_tuple = tuple(self.command_prefix + c.name for c in self.commands)
            content = message.content.lower()
            if not content.startswith(commands_tuple):
                # We find the longest command mentioned to allow some commands to be prefixes of others.
                # E.g. assume we have two commands !league and !leagueranks, the message "!leagueranks" should
                # trigger !leagueranks and not !league
                longest_found_cmd = None
                for command in self.settings['commands']:
                    if longest_found_cmd is None or len(command) > len(longest_found_cmd):
                        string_divided = content.split()
                        for triggers in string_divided:
                            if triggers.startswith(command):
                                longest_found_cmd = command
                                break
                if longest_found_cmd is not None:
                    await message.channel.send(self.settings['commands'][longest_found_cmd])
                    return

    async def on_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        self.logger.exception(error)

    def save_and_reload_settings(self):
        with open(self.settings_path, 'w') as file:
            json.dump(self.settings, file, indent=4)

        settings = open(self.settings_path, 'r')
        self.settings = json.load(settings)

    def run(self):
        super().run(TOKEN, reconnect=True)
