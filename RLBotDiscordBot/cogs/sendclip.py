from discord.ext import commands
from bot import RLBotDiscordBot
import random as r
from urllib.parse import urlparse
import re

import discord
from discord.ext import commands

class SendClip(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @commands.command()
    async def sendclip(self, ctx: discord.ext.commands.Context, *args):
        has_link = False
        valid_link = False
        attatchemnts_url = ''
        message = ctx.message
        if message.attachments:
            attatchemnts_url = message.attachments[0].url
        if args or attatchemnts_url:
            description = " ".join(args[0:])
            if attatchemnts_url:
                link = urlparse(attatchemnts_url)
            else:
                link = urlparse(args[0])
                description = " ".join(args[1:])
            if link.scheme in ["https", "http"]:
                has_link = True
                clip_domain = re.sub(r'^www\.', '', link.netloc, re.IGNORECASE)
                if clip_domain in self.bot.settings['Whitelisted_clip_domains']:
                    valid_link = True
            if valid_link:
                avatar = message.author.avatar_url or message.author.default_avatar_url
                clips_channel = message.guild.get_channel(self.bot.settings['Clips_channel'])

                if description:
                    title = description
                else:
                    title = 'Bot Clip'
                bot_clip_embed = discord.Embed(
                title=title,
                description=f"This clip was posted [here](https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id}) by <@{message.author.id}>",
                color=discord.Color.green()
                )
                bot_clip_embed.set_author(name=message.author.nick or message.author.name, icon_url=avatar)

                final_embed = bot_clip_embed
                await clips_channel.send(" ", embed=final_embed)
                clip_message: discord.Message = await clips_channel.send(link.geturl())
                reaction_list = ["👍", "👀", "🔥", "👌", "😄", "😮", "<:scratchcat:444921286703972352>",
                                 "<:rank_quantum:592004043832950784>", "<:platinumbot:811200370692063252>"]
                rNum = r.randint(0, len(reaction_list) - 1)
                await clip_message.add_reaction(reaction_list[rNum])
            elif not valid_link:
                await message.channel.send(
                    f"That website / clip link is not on the whitelisted domains list, please contact a mod to add `{clip_domain}` to the list!")
        if not has_link:
            await message.channel.send("That message did not contain a link, please add a link to your clip.")


def setup(bot):
    bot.add_cog(SendClip(bot))
