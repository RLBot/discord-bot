import random as r
import re
from urllib.parse import urlparse

import nextcord
from nextcord import Interaction
from nextcord.ext import commands

from bot import RLBotDiscordBot
from config import RLBOT


class SendClip(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @nextcord.slash_command(name="sendclip",description="Send a clip of your bot doing things!",guild_ids=[RLBOT])
    async def sendclip(self,interaction:Interaction, clip_desc:str = "Bot Clip", file:nextcord.Attachment=None, url:str=None):
        await interaction.response.defer(ephemeral=True)
        final_url = None
        if file != None and url != None:
            await interaction.followup.send("Please only attach a file or a URL, not both!",ephemeral=True)
            return
        elif file != None:
            final_url = file.url
        elif url != None:
            final_url = url
        else:
            await interaction.followup.send("Please attach a file or a URL!",ephemeral=True)
            return

        link = urlparse(final_url)

        valid_schemes = ["https", "http"]
        if link.scheme in valid_schemes:
            clip_domain = re.sub(r'^www\.', '', link.netloc, re.IGNORECASE)
            if clip_domain in self.bot.settings['Whitelisted_clip_domains']:
                await self.post_clip(clip_desc, link, interaction)
                await interaction.followup.send("Clip sent!",ephemeral=True)
            else:
                await interaction.followup.send(
                    f"That website / clip link is not on the whitelisted domains list, please contact a mod to add `{clip_domain}` to the list!",ephemeral=True)
        else:
            await interaction.followup.send(
                f"Invalid link! Links must be correctly formatted with the schemes {valid_schemes}. Link had scheme {link.scheme}.",ephemeral=True)

    async def post_clip(self, description, link, interaction:Interaction):
        avatar = interaction.user.display_avatar.url
        clips_channel = interaction.guild.get_channel(self.bot.settings['Clips_channel'])
        title = description
        bot_clip_embed = nextcord.Embed(
            title=title,
            description=f"This clip was posted by <@{interaction.user.id}>",
            color=nextcord.Color.green()
        )
        bot_clip_embed.set_author(name=interaction.user.nick or interaction.user.name, icon_url=avatar)
        final_embed = bot_clip_embed
        await clips_channel.send(" ", embed=final_embed)
        clip_message: nextcord.Message = await clips_channel.send(link.geturl())
        reaction_list = ["👍", "👀", "🔥", "👌", "😄", "😮"]
        await clip_message.add_reaction(r.choice(reaction_list))


def setup(bot):
    bot.add_cog(SendClip(bot))
