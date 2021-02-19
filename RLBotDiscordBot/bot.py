import json
import logging
import requests
import sys
import random as r
import os.path
import discord
from discord.ext import commands
from discord.utils import get
from sendclip import sendclip
from calendars import checkCalendar


try:
    from config import TOKEN
except ImportError:
    print('Unable to run bot, as token does not exist!')
    sys.exit()


initial_extensions = (
    'cogs.admin',
    'cogs.dm'
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

        super().__init__(command_prefix='!',  activity=activity)

        self.logger = logging.getLogger(__name__)

        self.remove_command('help')

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                self.logger.error(f'There was an error loading the extension {extension}. Error: {e}')

    async def on_ready(self):
        self.logger.info(f'{self.user} online! (ID: {self.user.id})')
        self.has_reacted = 0
        self.has_checked = False

    async def on_message(self, message):
        if not self.has_checked:
            if message.guild is not None:  # its None for dms
                self.has_checked = True
                for member in message.guild.members:
                    y = member.roles
                    for role in y:
                        if role.name == "Python" or role.name == "Java" or role.name == "C#" or role.name == "Rust" or role.name == "Scratch" or role.name == "C++":
                            await member.add_roles(get(member.guild.roles, name="botmaker"), reason=None, atomic=True)

        if message.author.bot:
            if message.channel.id == 352507627928027138:
                self.has_reacted += 1
                if self.has_reacted % 2 == 0:
                    reaction_list = ["👍","👀","🔥","👌","😄","😮","<:scratchcat:444921286703972352>","<:rank_quantum:592004043832950784>"]
                    rNum = r.randint(0, len(reaction_list)-1)
                    await message.add_reaction(reaction_list[rNum])
        else:
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
            await sendclip(message)
            await checkCalendar(message)
                    
    async def on_command_error(self, error, ctx):
        if isinstance(error, commands.CommandNotFound):
            print(error)



    def run(self):
        super().run(TOKEN, reconnect=True)
