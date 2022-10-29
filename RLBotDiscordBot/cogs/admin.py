import json
import re

import discord
from discord.ext import commands
from discord import app_commands
from discord.components import SelectOption
from discord.enums import ButtonStyle, ComponentType
from discord.emoji import Emoji
import requests
import sys

try:
    from ..bot import RLBotDiscordBot
except:
    from bot import RLBotDiscordBot



class AdminView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=30)
        self.bot: commands.Bot = bot

    @discord.ui.button(label="Refill Botmaker", style=ButtonStyle.secondary, emoji=None, disabled=False, row=0, custom_id='refill_botmaker')
    async def refill(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.message is not None
        await interaction.message.delete()
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            botmaker_role = None
            counter = 0
            for role in interaction.guild.roles:
                if role.name == "BotMaker":
                    botmaker_role = role
            for member in interaction.guild.members:
                if botmaker_role not in member.roles:
                    member_roles = member.roles
                    for role in member_roles:
                        if role.name in self.bot.settings["Language_roles"]:
                            counter += 1
                            await member.add_roles(discord.utils.get(interaction.guild.roles, name="BotMaker"), reason=None, atomic=True)
                            break
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)
        else:
            # await interaction.message.edit(view=None)
            await interaction.followup.send(f'Successfully added {counter} new botmakers!', ephemeral=False)


class CommandModal(discord.ui.Modal, title='Command Admin Panel'):
    name = discord.ui.TextInput(
        label='Command Name',
        placeholder='Command name ...',
        required=True
    )

    desc = discord.ui.TextInput(
        label='Command description',
        style=discord.TextStyle.short,
        placeholder='Small description ...',
        required=True
    )

    text = discord.ui.TextInput(
        label='Command output',
        style=discord.TextStyle.long,
        placeholder='Write it here ...',
        required=True
    )

    def __init__(self, bot, slash, name=None, text=None, desc=None):
        # super().__init__()
        super(CommandModal, self).__init__()
        if not slash:
            self.desc.required = False
            self.desc.placeholder = "IGNORE"
        self.bot: commands.Bot = bot
        self.slash: bool = slash
        self.old_name: str = name
        self.old_text: str = text
        self.old_desc = desc

        self.name.default = name
        self.text.default = text
        self.desc.default = desc


    async def on_submit(self, interaction: discord.Interaction):
        old_name = self.old_name
        name = self.name.value
        old_text = self.old_text
        text = self.text.value
        old_desc = None
        desc = None
        name_changed = name != old_name
        text_changed = text != old_text
        desc_changed = desc != old_desc

        name_lower = name.lower()
        if name != name_lower or " " in name:
            interaction.response.send_message(content="Command name must be lower case and contain no spaces",
                                              ephemeral=True)
            return

        if self.slash:
            filtered_name = re.sub('[^abcdefghijklmnopqrstuvxwyz0123456789\-_]', '', name)
            if filtered_name != name or len(name) > 32:
                interaction.response.send_message(content="Command name must be between 1-32 characters and contain "
                                                          "only lower-case letters, numbers, hyphens, or underscores",
                                                  ephemeral=True)

        if self.slash:
            desc = self.desc.value
            old_desc = self.old_desc
            if 'slash_commands' not in self.bot.settings:
                self.bot.settings['slash_commands'] = {}
            command_list = self.bot.settings['slash_commands']
        else:
            command_list: dict = self.bot.settings['commands']

        command_exists = old_name in command_list

        if command_exists:
            edited_text = f'Previous {"slash"*self.slash + "normal"*(not self.slash)} command:\n' +\
                          'Name:\n' + old_name + \
                          ('\nDescription:\n' + old_desc)*bool(self.desc) + \
                          '\nText:\n' + old_text
            await interaction.channel.send(edited_text)
            if old_name != name:
                command_list.pop(old_name)
        if self.slash:
            command_list[name] = [desc, text]
            if name_changed or desc_changed:
                try:
                    self.bot.tree.remove_command(old_name)
                except Exception as e:
                    await interaction.response.send_message(str(e), ephemeral=True)
                    return

            new_command: app_commands.Command = app_commands.Command(callback=self.bot.on_command, description=desc, name=name)

            try:
                self.bot.tree.add_command(new_command)
            except Exception as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return

        else:
            command_list[name] = text
        self.bot.save_and_reload_settings()

        await interaction.response.send_message(f'Added {"slash"*self.slash + "normal"*(not self.slash)} command "{name}"',
                                                ephemeral=False)


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.channel.send(content=f'Oops! Something went wrong:\n{str(error)}', ephemeral=True)

class CommandDeleteSelect(discord.ui.Select):
    def __init__(self, bot, commands, placeholder, slash) -> None:
        super().__init__(
            placeholder=placeholder,
            options=[SelectOption(label=key, value=key) for key in commands],
        )
        self.bot: commands.Bot = bot
        self.slash = slash

    async def callback(self, interaction: discord.Interaction):
        if not self.slash:
            self.bot.settings["commands"].pop(self.values[0])
        else:
            self.bot.tree.remove_command(self.values[0])
            self.bot.settings["slash_commands"].pop(self.values[0])
        self.bot.save_and_reload_settings()
        await interaction.response.send_message(content=f'Deleted {"slash"*self.slash + "normal"*(not self.slash)} command {self.values[0]}')
        self.view.stop()

class CommandEditSelect(discord.ui.Select):
    def __init__(self, bot, commands, placeholder, command_type) -> None:
        super().__init__(
            placeholder=placeholder,
            options=[SelectOption(label=key, value=key) for key in commands],
        )
        self.bot: commands.Bot = bot
        self.command_type = command_type

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.defer(ephemeral=False, thinking=True)
        # await interaction.delete_original_response()
        try:
            if self.command_type == "normal":
                name = self.values[0]
                text = self.bot.settings["commands"][self.values[0]]
                desc = None
            elif self.command_type == "slash":
                name = self.values[0]
                text = self.bot.settings["slash_commands"][self.values[0]][1]
                desc = self.bot.settings["slash_commands"][self.values[0]][0]

            modal = CommandModal(bot=self.bot, slash=self.command_type == "slash", name=name, text=text, desc=desc)
            await interaction.response.send_modal(modal)
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)

class CommandView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=30)
        self.bot: commands.Bot = bot

    @discord.ui.button(label="Add Slash Command", style=ButtonStyle.green, row=0, custom_id='add_slash')
    async def add_slash(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.message is not None
        # await interaction.message.edit(view=None)
        # await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            modal = CommandModal(bot=self.bot, slash=True)
            await interaction.response.send_modal(modal)
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)
        self.stop()

    @discord.ui.button(label="Add Normal Command", style=ButtonStyle.green, row=0, custom_id='add_normal')
    async def add_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.message is not None
        # await interaction.message.edit(view=None)
        # await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            modal = CommandModal(bot=self.bot, slash=False)
            await interaction.response.send_modal(modal)
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)
        self.stop()


    @discord.ui.button(label="Edit Command", style=ButtonStyle.secondary, row=0, custom_id='edit')
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.message is not None
        # await interaction.message.edit(view=None)
        # await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            def chunks(lst, n):
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            view = discord.ui.View()
            view.timeout = 60

            for command_chunk in chunks(list(self.bot.settings["commands"].keys()), 25):
                view.add_item(CommandEditSelect(self.bot, command_chunk, 'Choose normal command...', "normal"))

            for command_chunk in chunks(list(self.bot.settings["slash_commands"].keys()), 25):
                view.add_item(CommandEditSelect(self.bot, command_chunk, 'Choose slash command...', "slash"))

            await interaction.response.send_message(content="Choose the command to edit", view=view)
            # await interaction.message.delete()
            timout = await view.wait()
            await interaction.delete_original_response()
            # await interaction.delete_original_response()
            # await interaction.response.delete()
        except Exception as e:
            await interaction.channel.send(content="Error: " + str(e))
        self.stop()


    @discord.ui.button(label="Refresh / commands", style=ButtonStyle.blurple, row=0, custom_id='refresh')
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.message is not None
        await interaction.response.defer(ephemeral=False, thinking=True)
        # await interaction.message.edit(view=None)
        try:
            await self.bot.tree.sync()
            await interaction.followup.send(content="Slash commands successfully synced!")
        except Exception as e:
            await interaction.followup.send(str(e), ephemeral=True)
        self.stop()


    @discord.ui.button(label="Delete Command", style=ButtonStyle.red, row=0, custom_id='delete')
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.message is not None
        # await interaction.message.edit(view=None)
        # await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            def chunks(lst, n):
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            view = discord.ui.View()
            view.timeout = 60

            for command_chunk in chunks(list(self.bot.settings["commands"].keys()), 25):
                view.add_item(CommandDeleteSelect(self.bot, command_chunk, 'Choose normal command...', slash=False))

            for command_chunk in chunks(list(self.bot.settings["slash_commands"].keys()), 25):
                view.add_item(CommandDeleteSelect(self.bot, command_chunk, 'Choose slash command...', slash=True))

            await interaction.response.send_message(content="Choose the command to delete", view=view)
            # await interaction.message.delete()
            timeout = await view.wait()
            await interaction.delete_original_response()
            # await interaction.delete_original_response()
            # await interaction.response.delete()
        except Exception as e:
            await interaction.channel.send(str(e))
        self.stop()

class AdminCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot: commands.Bot = bot
        # self.admin_view = AdminView(self.bot)
        # self.command_view = CommandView(self.bot)
        # self.bot.add_view(self.admin_view)
        # self.bot.add_view(self.command_view)

    @commands.hybrid_command(name="admin_tools", description="Admin controls", )
    async def admin_tools(self, ctx: discord.ext.commands.Context):
        if not self.check_perms(ctx):
            await ctx.interaction.response.send_message(content="Not permitted", ephemeral=True)
            return
        aView = AdminView(self.bot)
        await ctx.interaction.response.send_message(content="Choose the command", view=aView)
        if await aView.wait():
            await ctx.interaction.delete_original_response()

    @commands.hybrid_command(name="admin", description="Command controls", )
    async def admin(self, ctx: discord.ext.commands.Context):
        if not self.check_perms(ctx):
            await ctx.interaction.response.send_message(content="Not permitted", ephemeral=True)
            return
        cView = CommandView(self.bot)
        await ctx.interaction.response.send_message(content="Choose the command", view=cView)
        timeout = await cView.wait()
        await ctx.interaction.delete_original_response()

    @commands.hybrid_command(name="botmaker", description="Toggle BotMaker role on yourself", )
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
        self.bot.save_and_reload_settings()

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
            self.bot.save_and_reload_settings()

            await ctx.send(deleted_text)

    # Todo: make stream a view/modal or use autocomplete
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
        commands_list.append('\n***Slash Commands:***')
        for command in self.bot.settings['slash_commands'].keys():
            commands_list.append("/" + str(command))
        commands_list.append('\n***Admin Commands:***')
        for command in self.bot.commands:
            commands_list.append(self.bot.command_prefix + str(command))
            if isinstance(command, commands.HybridCommand):
                commands_list.append("/" + str(command))

        all_commands = '\n'.join(commands_list)

        await ctx.send(all_commands)

    @commands.command()
    async def whitelist_domain(self, ctx, *, domain: str = ''):
        if not self.check_perms(ctx):
            return
        if domain:
            if domain not in self.bot.settings['Whitelisted_clip_domains']:
                self.bot.settings['Whitelisted_clip_domains'].append(domain)
                self.bot.save_and_reload_settings()
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


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
