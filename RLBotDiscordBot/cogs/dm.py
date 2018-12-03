import discord
from discord.ext import commands
import json

class welcome:
    def __init__(self, bot):
        self.bot = bot
        settings = open('./settings.json', 'r')
        self.settings = json.load(settings)

    async def on_member_join(self, member):
        await member.send(self.settings['commands']['welcome_message'])


def setup(bot):
    bot.add_cog(welcome(bot))
