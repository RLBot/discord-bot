from discord.ext import commands


class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, member):
        if self.bot.settings['commands']['welcome_message']:
            await member.send(self.bot.settings['commands']['welcome_message'])


async def setup(bot):
    await bot.add_cog(welcome(bot))
