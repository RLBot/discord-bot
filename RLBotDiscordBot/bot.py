import logging

import nextcord
from nextcord.ext import commands

from config import TOKEN
from settings import load_settings, save_settings

initial_extensions = (
    'cogs.admin',
    'cogs.calendar',
    'cogs.faq',
)


class RLBotDiscordBot(commands.Bot):
    def __init__(self):
        self.settings = load_settings()

        intents = nextcord.Intents.all()
        activity = nextcord.Game(name=self.settings.setdefault("Status_message", "with bots!"))
        super().__init__(command_prefix='!', activity=activity, intents=intents)

        self.logger = logging.getLogger(__name__)
        self.remove_command('help')

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                self.logger.info(f'Cog loaded: {extension}')
            except Exception as e:
                self.logger.error(f'There was an error loading the extension {extension}. Error: {e}')

    async def on_ready(self):
        self.logger.info(f'{self.user} online! (ID: {self.user.id})')

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

            # We find the longest command mentioned to allow some commands to be prefixes of others.
            # E.g. assume we have two commands !league and !leagueranks, the message "!leagueranks" should
            # trigger !leagueranks and not !league
            longest_found_cmd = None
            for command in self.settings.setdefault('commands', {}):
                if longest_found_cmd is None or len(command) > len(longest_found_cmd):
                    string_divided = message.content.lower().split()
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
        save_settings(self.settings)
        self.settings = load_settings()

    def run(self):
        super().run(TOKEN, reconnect=True)
