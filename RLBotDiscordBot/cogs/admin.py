import json

import discord
import requests
from discord.ext import commands

from bot import RLBotDiscordBot


class AdminCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @commands.command()
    async def refill_botmaker(self, ctx: discord.ext.commands.Context):
        if not self.check_perms(ctx):
            return
        for member in ctx.guild.members:
            member_roles = member.roles
            for role in member_roles:
                if role.name in self.bot.settings["Language_roles"]:
                    await member.add_roles(discord.utils.get(ctx.guild.roles, name="BotMaker"), reason=None,
                                           atomic=True)

    @commands.command()
    async def botmaker(self, ctx: discord.ext.commands.Context):
        botmaker_role = discord.utils.get(ctx.guild.roles, name='BotMaker')
        if botmaker_role in ctx.author.roles:
            await ctx.author.remove_roles(botmaker_role)
        else:
            await ctx.author.add_roles(botmaker_role)

    @commands.command()
    async def add_command(self, ctx, name, *, output: str):
        if not self.check_perms(ctx):
            return

        name = name.lower()
        exists = name in self.bot.settings['commands']

        if exists:
            previous_out = self.bot.settings['commands'][name]

        self.bot.settings['commands'][name] = output
        with open(self.bot.settings_path, 'w') as file:
            json.dump(self.bot.settings, file, indent=4)

        settings = open(self.bot.settings_path, 'r')
        self.bot.settings = json.load(settings)

        if exists:
            edited_text = 'Previous output:\n' + previous_out + '\nCommand edited.'
            await ctx.send(edited_text)
        else:
            await ctx.send('Command added')

    @commands.command()
    async def del_command(self, ctx, *, name):
        if not self.check_perms(ctx):
            return

        name = name.lower()
        if name in self.bot.settings['commands']:
            deleted_text = 'Previous output:\n' + str(self.bot.settings['commands'][name] + '\nCommand deleted')

            del self.bot.settings['commands'][name]
            with open(self.bot.settings_path, 'w') as f:
                json.dump(self.bot.settings, f, indent=4)

            await ctx.send(deleted_text)

    @commands.command()
    async def presence(self, ctx, *args):
        if not self.check_perms(ctx):
            return
        if not args:
            help_message = 'Example uses:\n' \
                           '!presence reset\n' \
                           '!presence "`stream`" "`stream name`" "`stream url`"\n' \
                           '`Streaming ...`\n' \
                           '!presence "`playing`" "`custom name`"\n' \
                           '`Playing ...`\n' \
                           '!presence "`listening`" "`custom name`"\n' \
                           '`Listening to ...`\n' \
                           '!presence "`competing`" "`custom name`"\n' \
                           '`Competing in ...`\n' \
                           '!presence "`watching`" "`custom name`"\n' \
                           '`Watching ...`'
            await ctx.send(help_message)
            return
        presence_type = args[0].lower()

        name = ' '.join(args[1:])
        presence_dict = {'playing': discord.ActivityType.playing,
                         'listening': discord.ActivityType.listening,
                         'competing': discord.ActivityType.competing,
                         'watching': discord.ActivityType.watching}

        if presence_type == 'stream':
            name = args[1]
            url = args[2]

            await self.bot.change_presence(activity=discord.Streaming(name=name, url=url))

        elif presence_type in presence_dict.keys():
            presence = presence_dict[presence_type]
            await self.bot.change_presence(activity=discord.Activity(type=presence, name=name))

        elif presence_type == 'reset':
            await self.bot.change_presence()

        else:
            await ctx.send(f'Presence type unsupported: `{presence_type}`')
            return

        await ctx.send('Presence updated')

    @commands.command()
    async def give_settings(self, ctx):
        if not self.check_perms(ctx):
            return

        await ctx.send(file=discord.File(self.bot.settings_path))

    @commands.command()
    async def take_settings(self, ctx):
        if not self.check_perms(ctx):
            return
        attachment = ctx.message.attachments

        if len(attachment) > 0:
            url = attachment[0].url
            r = requests.get(url, allow_redirects=True)

            with open(self.bot.settings_path, 'wb') as f:
                f.write(r.content)
            with open(self.bot.settings_path, 'r') as f:
                self.bot.settings = json.load(f)

            await ctx.send('Settings updated')

        else:
            await ctx.send('You know very well you should provide a file!')

    @commands.command(aliases=['commands'])
    async def command_list(self, ctx):
        if not self.check_perms(ctx):
            return
        commands_list: list = list(self.bot.settings['commands'].keys())
        commands_list.sort()
        commands_list.append('\n***Admin Commands:***')
        for command in self.bot.commands:
            commands_list.append(self.bot.command_prefix + str(command))
        all_commands = '\n'.join(commands_list)

        await ctx.send(all_commands)

    @commands.command()
    async def whitelist_domain(self, ctx, *, domain: str = ''):
        if not self.check_perms(ctx):
            return
        if domain:
            if domain not in self.bot.settings['Whitelisted_clip_domains']:
                self.bot.settings['Whitelisted_clip_domains'].append(domain)
                with open(self.bot.settings_path, 'w') as f:
                    json.dump(self.bot.settings, f, indent=4)
                current_domains = "\n".join(self.bot.settings["Whitelisted_clip_domains"])
                await ctx.send(f'Domain added.\nCurrent domains:\n```{current_domains}```')
            else:
                current_domains = "\n".join(self.bot.settings["Whitelisted_clip_domains"])
                await ctx.send(f'Domain already existed.\nCurrent domains:\n```{current_domains}```')
        else:
            current_domains = "\n".join(self.bot.settings["Whitelisted_clip_domains"])
            await ctx.send(f'Current domains:\n```{current_domains}```')

    def check_perms(self, ctx):
        return ctx.message.channel.id == self.bot.settings['Admin_channel']


def setup(bot):
    bot.add_cog(AdminCommands(bot))
