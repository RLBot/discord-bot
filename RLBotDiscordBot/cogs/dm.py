import nextcord
from nextcord.ext import commands

from bot import RLBotDiscordBot


class welcome(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    async def on_member_join(self, member:nextcord.Member):
        if self.bot.settings['commands']['welcome_message']:
            await member.send(self.bot.settings['commands']['welcome_message'])


def setup(bot):
    bot.add_cog(welcome(bot))
