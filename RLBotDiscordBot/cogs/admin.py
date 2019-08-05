import discord
from discord.ext import commands
import json
import requests

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def botmaker(self, ctx, action=None):
        botmaker_role = discord.utils.get(ctx.guild.roles, name='BotMaker')
        if action == 'add' or not action:
            await ctx.author.add_roles(botmaker_role)
        elif action == 'remove' or action == 'off':
            await ctx.author.remove_roles(botmaker_role)
        else:
            await ctx.send(f'Invalid action {action}.')

    @commands.command()
    async def add_command(self, ctx, name, *, output):

        if not self.check_perms(ctx):
            return

        exists = name in self.bot.settings['commands']

        if exists:
            previous_out = self.bot.settings['commands'][name]
            print(previous_out)

        self.bot.settings['commands'][name] = output
        with open('./RLBotDiscordBot/settings.json', 'w') as file:
            json.dump(self.bot.settings, file, indent=4)

        settings = open('./RLBotDiscordBot/settings.json', 'r')
        self.bot.settings = json.load(settings)

        if exists:
            print('sxis')
            edited_text = 'Previous output:\n' + previous_out
            + '\nCommand edited.'

            await ctx.send(edited_text)
            await ctx.send('Command edited.')
            return

        await ctx.send('Command added')

    @commands.command()
    async def del_command(self, ctx, *, name):
        if not self.check_perms(ctx):
            return

        if name in self.bot.settings['commands']:

            deleted_text = 'Previous output:\n' + str(self.bot.settings['commands'][name]
            + '\nCommand deleted')

            del self.bot.settings['commands'][name]
            with open('./RLBotDiscordBot/settings.json', 'w') as f:
                json.dump(self.bot.settings, f, indent=4)

            await ctx.send(deleted_text)

    @commands.command()
    async def edit_game(self, ctx, *, game):
        if not self.check_perms(ctx):
            return

        self.bot.settings['Status_message'] = game

        with open('./RLBotDiscordBot/settings.json', 'w') as f:
            json.dump(self.bot.settings, f, indent=4)

        await self.bot.change_presence(activity=discord.Game(name=game))
        await ctx.send('Game updated')

    @commands.command()
    async def give_settings(self, ctx):
        if not self.check_perms(ctx):
            return

        await ctx.send(file=discord.File('./RLBotDiscordBot/settings.json'))


    @commands.command()
    async def take_settings(self, ctx):
        if not self.check_perms(ctx):
            return
        attachment = ctx.message.attachments
        print("1")

        if len(attachment) > 0:
            print("2")
            url = attachment[0].url
            print(url)
            name = attachment[0].filename
            print(name)
            r = requests.get(url, allow_redirects=True)

            with open('./RLBotDiscordBot/settings.json', 'wb') as f:
                print(r.content)
                f.write(r.content)
            with open('./RLBotDiscordBot/settings.json', 'r') as f:
                self.bot.settings = json.load(f)

            await ctx.send('Settings updated')

        else:
            await ctx.send('You know very well you should provide a file!')

    @commands.command()
    async def commands(self, ctx):

        if not self.check_perms(ctx):
            return
        all_commands = '\n'.join(self.bot.settings['commands'])

        await ctx.send(all_commands)
        return

    def check_perms(self, ctx):
        roles_names = [r.name for r in ctx.author.roles]
        if ctx.message.channel.name != 'discord-bots':
            print("no")
            return False
        else:
            print("yes")
            return True



def setup(bot):
    bot.add_cog(AdminCommands(bot))
