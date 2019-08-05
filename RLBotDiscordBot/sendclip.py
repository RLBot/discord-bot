import json
import logging
import requests
import sys
import random as r

import discord
from discord.ext import commands
from discord.utils import get

async def sendclip(message):
    Has_link = False
    valid_link = False
    base_channel = 0
    base_id = 0
    args = message.content.split(" ")
    whitelisted_links = ["clips.twitch.tv","www.twitch.tv","gfycat.com","www.youtube.com","i.gyazo.com","i.imgur.com","gyazo.com","streamable.com","www.gifyourgame.com","cdn.discordapp.com"]
    for i in range(len(args)):
        #print(i)
        #print(args[i])
        if args[i] == "!sendclip":
            base_channel = message.channel.id
            base_id = message.id
            #print(base_channel)
            #print(base_id)
            #print("has sendclip")
            if len(message.attachments) >= 1:
                for attachment in message.attachments:
                    args.append(attachment.url)
                    #print(attachment.url)
            del args[i]
            for j in range(len(args)+1):
                try:
                    link_test = args[j].split("://")
                    if link_test[0] == "https" or link_test[0] == "http":
                        valid_link_test = link_test[1].split("/")
                        Has_link = True
                        for link in whitelisted_links:
                            #print(valid_link_test)
                            if valid_link_test[0] == link:
                                #print("Valid Link!")
                                del args[j]
                                #print(args)
                                valid_link = True
                                break
                        break
                except:
                    pass
            if valid_link:
                avatar = message.author.avatar_url or message.author.default_avatar_url
                link = "://".join(link_test[0:])
                #print("Has Link!")
                message.channel.id = 352507627928027138
                to_send = " ".join(args[0:])
                #print(to_send)
                bot_clip_embed = discord.Embed(
                title="Poster",
                description="This clip was posted [here](https://discordapp.com/channels/348658686962696195/"+str(base_channel)+"/"+str(base_id) + ") by <@" + str(message.author.id) + ">" ,
                color=discord.Color.green()
                )
                bot_clip_embed.set_author(name="Bot Clip", icon_url = avatar)
                if len(args) >=1:
                    bot_clip_embed.add_field(name="Description", value=to_send, inline=False)

                final_embed = bot_clip_embed
                await message.channel.send(" ", embed=final_embed)
                await message.channel.send(link)
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