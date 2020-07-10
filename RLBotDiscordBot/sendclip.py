import json
import logging
import requests
import sys
import random as r
from urllib.parse import urlparse
import re

import discord
from discord.ext import commands
from discord.utils import get

async def sendclip(message):
    Has_link = False
    valid_link = False
    base_channel = 0
    base_id = 0
    args = message.content.split(" ")
    whitelisted_links = {
        "clips.twitch.tv", "twitch.tv",
        "gfycat.com",
        "youtube.com", "youtu.be",
        "i.gyazo.com", "gyazo.com",
        "i.imgur.com", "imgur.com",
        "streamable.com",
        "gifyourgame.com",
        "cdn.discordapp.com",
    }
    for i in range(len(args)):

        if args[i] == "!sendclip":
            base_channel = message.channel.id
            base_id = message.id
            if len(message.attachments) >= 1:
                for attachment in message.attachments:
                    args.append(attachment.url)
            del args[i]
            for j in range(len(args)+1):
                try:
                    link = urlparse(args[j])
                    if link.scheme == "https" or link.scheme == "http":
                        Has_link = True
                        if re.sub(r'^www\.', '', link.netloc, re.IGNORECASE) in whitelisted_links:
                            del args[j]
                            valid_link = True
                            break
                        break
                except:
                    pass
            if valid_link:
                avatar = message.author.avatar_url or message.author.default_avatar_url
                message.channel.id = 352507627928027138
                to_send = " ".join(args[0:])
                bot_clip_embed = discord.Embed(
                title="Poster",
                description=f"This clip was posted [here](https://discordapp.com/channels/348658686962696195/{base_channel}/{base_id}) by <@{message.author.id}>" ,
                color=discord.Color.green()
                )
                bot_clip_embed.set_author(name="Bot Clip", icon_url = avatar)
                if len(args) >=1:
                    bot_clip_embed.add_field(name="Description", value=to_send, inline=False)

                final_embed = bot_clip_embed
                await message.channel.send(" ", embed=final_embed)
                await message.channel.send(link.geturl())
                message.channel.id = base_channel
                break
            if not Has_link:
                message.channel.id = base_channel
                await message.channel.send("That message did not contain a link, please add a link to your clip.")
                break
            elif not valid_link:
                message.channel.id = base_channel
                await message.channel.send("That website / clip link is not on the whitelisted links list, please contact a mod to add it to the list!")
                break
