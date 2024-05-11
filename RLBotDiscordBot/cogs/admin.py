import json

import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from config import RLBOT

import requests

from bot import RLBotDiscordBot


class AdminCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @nextcord.slash_command(name="refill_botmaker",
                            description="Refills the botmaker role to everyone with language roles", guild_ids=[RLBOT])
    async def refill_botmaker(self, interaction: Interaction):
        await interaction.response.defer()
        for member in interaction.guild.members:
            member_roles = member.roles
            for role in member_roles:
                if role.name in self.bot.settings["Language_roles"]:
                    await member.add_roles(nextcord.utils.get(interaction.guild.roles, name="BotMaker"), reason=None,
                                           atomic=True)
        await interaction.followup.send("BotMaker role refilled!")

    @nextcord.slash_command(name="botmaker", description="Toggles a user's BotMaker role!", guild_ids=[RLBOT])
    async def botmaker(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        botmaker_role = nextcord.utils.get(interaction.guild.roles, name='BotMaker')
        if botmaker_role in interaction.user.roles:
            await interaction.user.remove_roles(botmaker_role)
        else:
            await interaction.user.add_roles(botmaker_role)

        await interaction.followup.send("BotMaker toggled!", ephemeral=True)

    @nextcord.slash_command(name="add_command", description="Adds a command!", guild_ids=[RLBOT])
    async def add_command(self, interaction: Interaction, name: str, output: str):
        await interaction.response.defer()
        name = name.lower()
        exists = name in self.bot.settings['commands']

        if exists:
            previous_out = self.bot.settings['commands'][name]

        self.bot.settings['commands'][name] = output
        self.bot.save_and_reload_settings()

        if exists:
            edited_text = 'Previous output:\n' + previous_out + '\nCommand edited.'
            await interaction.followup.send(edited_text)
        else:
            await interaction.followup.send('Command added')

    @nextcord.slash_command(name="del_command", description="Deletes a command!", guild_ids=[RLBOT])
    async def del_command(self, interaction: Interaction, name: str):
        await interaction.response.defer()
        name = name.lower()
        if name in self.bot.settings['commands']:
            deleted_text = 'Previous output:\n' + str(self.bot.settings['commands'][name] + '\nCommand deleted')

            del self.bot.settings['commands'][name]
            self.bot.save_and_reload_settings()

            await interaction.followup.send(deleted_text)
            return
        await interaction.followup.send(f"No command named {name} found!")

    PRESENCE_OPTIONS = ["reset", "stream", "playing", "listening", "competing", "watching"]

    @nextcord.slash_command(name="change_presence", description="Change the presence!", guild_ids=[RLBOT])
    async def presence(self, interaction: Interaction,
                       type: str = nextcord.SlashOption(name="type", choices=PRESENCE_OPTIONS), action: str = "Bots",
                       url: str = None):
        await interaction.response.defer()

        presence_dict = {'playing': nextcord.ActivityType.playing,
                         'listening': nextcord.ActivityType.listening,
                         'competing': nextcord.ActivityType.competing,
                         'watching': nextcord.ActivityType.watching}

        if type == 'stream':
            await self.bot.change_presence(activity=nextcord.Streaming(name=action, url=url))

        elif type in presence_dict.keys():
            presence = presence_dict[type]
            await self.bot.change_presence(activity=nextcord.Activity(type=presence, name=action))

        elif type == 'reset':
            await self.bot.change_presence()

        await interaction.followup.send('Presence updated')

    @nextcord.slash_command(name="get_settings", description="Get the settings for the bot!", guild_ids=[RLBOT])
    async def give_settings(self, interaction: Interaction):
        await interaction.response.defer()
        await interaction.followup.send(file=nextcord.File(self.bot.settings_path))

    @nextcord.slash_command(name="set_settings", description="Set the settings for the bot!", guild_ids=[RLBOT])
    async def take_settings(self, interaction: Interaction, attachment: nextcord.Attachment):
        await interaction.response.defer()
        url = attachment.url
        r = requests.get(url, allow_redirects=True)

        with open(self.bot.settings_path, 'wb') as f:
            f.write(r.content)
        with open(self.bot.settings_path, 'r') as f:
            self.bot.settings = json.load(f)

        await interaction.followup.send('Settings updated')

    @nextcord.slash_command(name="commands", description="List every bot command", guild_ids=[RLBOT])
    async def command_list(self, interaction: Interaction):
        await interaction.response.defer()
        commands_list: list = list(self.bot.settings['commands'].keys())
        commands_list.sort()
        all_commands = '\n'.join(commands_list)

        await interaction.followup.send(all_commands)

    @nextcord.slash_command(name="whitelist_domain", description="Whitelist a given domain (blank to list all domains)",
                            guild_ids=[RLBOT])
    async def whitelist_domain(self, interaction: Interaction, domain: str = None):
        await interaction.response.defer()

        if domain:
            if domain not in self.bot.settings['Whitelisted_clip_domains']:
                self.bot.settings['Whitelisted_clip_domains'].append(domain)
                self.bot.save_and_reload_settings()
                current_domains = "\n".join(self.bot.settings["Whitelisted_clip_domains"])
                await interaction.followup.send(f'Domain added.\nCurrent domains:\n```{current_domains}```')
            else:
                current_domains = "\n".join(self.bot.settings["Whitelisted_clip_domains"])
                await interaction.followup.send(f'Domain already existed.\nCurrent domains:\n```{current_domains}```')
        else:
            current_domains = "\n".join(self.bot.settings["Whitelisted_clip_domains"])
            await interaction.followup.send(f'Current domains:\n```{current_domains}```')


def setup(bot):
    bot.add_cog(AdminCommands(bot))
