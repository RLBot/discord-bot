import json
import logging
import requests
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
    'cogs.dm'
)


class RLBotDiscordBot(commands.Bot):

    def __init__(self):

        settings = open('./settings.json', 'r')
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

    async def on_message(self, message):
        Has_link = False
        valid_link = False
        if message.author.bot:
            return
        else:
            await self.process_commands(message)
            # Check if the message doesn't start with other (not in settings.json) command
            # This is done to prevent conflits
            # Not sure if this is the best way to do it, but this is the best I could do.
            commands_tuple = tuple(self.command_prefix + c.name for c in self.commands)
            if not message.content.startswith(commands_tuple):
                for command in self.settings['commands']:
                    string_divided = message.content.lower().split()
                    for triggers in string_divided:
                        if triggers.startswith(command):
                            await message.channel.send(self.settings['commands'][command])
                            return
            args = message.content.split(" ")
            base_channel = message.channel.id
            whitelisted_links = ["clips.twitch.tv","www.twitch.tv","gfycat.com","www.youtube.com","i.gyazo.com","i.imgur.com","gyazo.com","streamable.com","www.gifyourgame.com"]
            for i in range(len(args)):
                #print(i)
                if args[i] == "!clip":
                    del args[i]
                    for j in range(len(args)):
                        try:
                            link_test = args[j].split("://")
                            if link_test[0] == "https" or link_test[0] == "http":
                                valid_link_test = link_test[1].split("/")
                                Has_link = True
                                for i in range(len(whitelisted_links)-1):
                                    #print(valid_link_test)
                                    if valid_link_test[0] == whitelisted_links[i]:
                                        del args[j]
                                        #print(args)
                                        link = "://".join(link_test[0:])
                                        #print("Has Link!")
                                        message.channel.id = YOUR CHANNEL ID HERE
                                        to_send = " ".join(args[0:])
                                        #print(to_send)
                                        status_help_embed = discord.Embed(
                                        description="",
                                        color=discord.Color.green()
                                        )
                                        status_help_embed.set_author(name="Bot Clip by " + message.author.name)
                                        if len(args) >=1:
                                            status_help_embed.add_field(name="Description", value=to_send, inline=False)

                                        final_embed = status_help_embed
                                        await message.channel.send(" ", embed=final_embed)
                                        await message.channel.send(link)
                                        valid_link = True
                                        break
                                break
                        except:
                            pass
                    if valid_link:
                        break
                    if not Has_link:
                        message.channel.id = base_channel
                        await message.channel.send("That message did not contain a link, please add a link to your clip.")
                    elif not valid_link:
                        message.channel.id = base_channel
                        await message.channel.send("That website / clip link is not on the whitelisted links list, please contact a mod to add it to the list!")
                    

    async def on_command_error(self, error, ctx):
        if isinstance(error, commands.CommandNotFound):
            print(error)



    def run(self):
        super().run(TOKEN, reconnect=True)
