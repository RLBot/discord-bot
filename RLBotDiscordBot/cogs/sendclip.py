import random as r
import re
from urllib.parse import urlparse

import discord
from discord.ext import commands
from discord import app_commands

from bot import RLBotDiscordBot


class ClipModal(discord.ui.Modal, title='Send a Clip'):
    link = discord.ui.TextInput(
        label='link',
        placeholder='Insert the link here...',
    )

    # This is a longer, paragraph style input, where user can submit feedback
    # Unlike the name, it is not required. If filled out, however, it will
    # only accept a maximum of 300 characters, as denoted by the
    # `max_length=300` kwarg.
    description = discord.ui.TextInput(
        label='What is this AWESOME clip?',
        style=discord.TextStyle.long,
        placeholder='Describe here...',
        required=False
    )

    def __init__(self, bot, post_clip_callback):
        super(ClipModal, self).__init__()
        self.bot = bot
        self.post_clip = post_clip_callback

    async def on_submit(self, interaction: discord.Interaction):

        link = urlparse(self.link.value)
        description = self.description.value

        valid_schemes = ["https", "http"]
        if link.scheme in valid_schemes:
            clip_domain = re.sub(r'^www\.', '', link.netloc, re.IGNORECASE)
            if clip_domain in self.bot.settings['Whitelisted_clip_domains']:
                response: discord.InteractionResponse = interaction.response
                await response.send_message(f"{link.geturl()}\n{description}", ephemeral=False)
                original_message = await interaction.original_response()
                # original_message = await original_message.to_reference().jump_url()
                await self.post_clip(description, link, original_message, interaction)
            else:
                error = f"That website / clip link is not on the whitelisted domains list, please contact a mod to add `{clip_domain}` to the list!"
                await interaction.response.send_message(error, ephemeral=True)
        else:
            error = f"Invalid link! Links must be correctly formatted with the schemes {valid_schemes}. Link had scheme {link.scheme}."
            await interaction.response.send_message(error, ephemeral=True)


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)


class SendClip(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @commands.hybrid_command(name="sendclip", alias="shareclip", description="Share a clip of your bot")
    async def sendclip(self, ctx: discord.ext.commands.Context, link=None, description=None):
        def post_clip_callback(description, link, origin_message, interaction):
            return self.post_clip(description, link, origin_message, interaction)

        if not link:
            modal = ClipModal(bot=self.bot, post_clip_callback=post_clip_callback)
            await ctx.interaction.response.send_modal(modal)
        else:
            link = urlparse(link)
            valid_schemes = ["https", "http"]
            if link.scheme in valid_schemes:
                clip_domain = re.sub(r'^www\.', '', link.netloc, re.IGNORECASE)
                if clip_domain in self.bot.settings['Whitelisted_clip_domains']:
                    await self.post_clip(description, link, ctx.message)
                else:
                    await ctx.message.channel.send(
                        f"That website / clip link is not on the whitelisted domains list, please contact a mod to add `{clip_domain}` to the list!")
            else:
                await ctx.message.channel.send(
                    f"Invalid link! Links must be correctly formatted with the schemes {valid_schemes}. Link had scheme {link.scheme}.")

    async def post_clip(self, description, link, origin_message: discord.Message = None, interaction: discord.Interaction = None):
        if interaction:
            author = interaction.user
            guild = interaction.guild
            channel = interaction.channel
            avatar = author.display_avatar.url or author.default_avatar.url
            clips_channel = guild.get_channel(self.bot.settings['Clips_channel'])
        elif origin_message:
            avatar = origin_message.author.display_avatar.url or origin_message.author.default_avatar.url
            clips_channel = origin_message.guild.get_channel(self.bot.settings['Clips_channel'])
            guild = origin_message.guild
            channel = origin_message.channel
            author = origin_message.author
        else:
            return
        if description:
            title = description
        else:
            title = 'Bot Clip'
        bot_clip_embed = discord.Embed(
            title=title,
            description=f"This clip was posted [here](https://discordapp.com/channels/{guild.id}/{channel.id}/{origin_message.id}) by <@{author.id}>",
            color=discord.Color.green()
        )
        bot_clip_embed.set_author(name=author.nick or author.name, icon_url=avatar)
        final_embed = bot_clip_embed
        await clips_channel.send(" ", embed=final_embed)
        clip_message: discord.Message = await clips_channel.send(link.geturl())
        reaction_list = ["👍", "👀", "🔥", "👌", "😄", "😮", "<:scratchcat:444921286703972352>",
                         "<:rank_quantum:592004043832950784>", "<:platinumbot:811200370692063252>"]
        await clip_message.add_reaction(r.choice(reaction_list))


async def setup(bot):
    await bot.add_cog(SendClip(bot))
