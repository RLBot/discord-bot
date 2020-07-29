import requests
import datetime
import json
import logging
import sys
import random as r
from urllib.parse import urlparse
import re
import os
from config import GOOGLE_API_KEY

import discord
from discord.ext import commands
from discord.utils import get


async def checkCalendar(message):
    load_dotenv()
    api_key = GOOGLE_API_KEY
    args = message.content.split(" ")
    can_run = False
    for i in args:
        if i == "!tournaments":
            can_run = True
    if can_run:
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September","October", "November", "December"]
        today = str(datetime.datetime.now())
        checkDay = today.split(" ")[0] + "T"
        checkTime = today.split(" ")[1]
        checkTime = checkTime.split(":")
        checkTime[2] = str(int(float(checkTime[2])))
        checkTime[2] = checkTime[2] + "0Z" if checkTime[2] == "0" else checkTime[2] + "Z"
        checkTime = ":".join(checkTime)
        toCheck = checkDay + checkTime
        r = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/rlbotofficial@gmail.com/events?maxResults=3&timeMin={toCheck}&key={api_key}")
        jsons = r.json()
        if len(jsons["items"]) > 0:
            name = jsons["items"][0]["summary"]
            start = jsons["items"][0]["start"]["dateTime"]
            start = start.split("T")
            date = start[0]
            time = start[1]
            date2 = date.split("-")
            date = date.split("-")
            date2.reverse()
            accDate = f"{months[(int(date2[1]) - 1)]} {date2[0]}"
            time = time.strip("Z").split(":")
            del time[2]
            accTime = ":".join(time)
            td = datetime.datetime(int(date[0]), int(date[1]), int(date[2]),hour=int(time[0]),minute=int(time[1])) - datetime.datetime.now()
            days, hours, mins, secs = td.days, td.seconds // 3600, (td.seconds % 3600) // 60, (td.seconds % 3600) % 60
            dates = ""
            if days < 3: 
                if days > 1:
                    dates += f"{days} days, "
                elif days == 1:
                    dates += f"{days} day, "
                if hours > 1:
                    dates += f"{hours} hours, "
                elif hours == 1:
                    dates += f"{hours} hour, "
                if mins > 1:
                    dates += f"{mins} minutes, "
                elif mins == 1:
                    dates += f"{mins} minute, "
                if secs > 1:
                    dates += f"{secs} seconds"
                elif secs == 1:
                    dates += f"{secs} second"
            else:
                dates += f"{days} days"
            bot_clip_embed = discord.Embed(
                        title=name,
                        description=f"Will begin in {dates}. ({accDate}, {accTime} UTC)" ,
                        color=discord.Color.green()
                        )
            bot_clip_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
            if len(jsons["items"]) >= 2:
                name = jsons["items"][1]["summary"]
                start = jsons["items"][1]["start"]["dateTime"]
                start = start.split("T")
                date = start[0]
                time = start[1]
                date2 = date.split("-")
                date = date.split("-")
                date2.reverse()
                accDate = f"{months[(int(date2[1]) - 1)]} {date2[0]}"
                time = time.strip("Z").split(":")
                del time[2]
                accTime = ":".join(time)
                td = datetime.datetime(int(date[0]), int(date[1]), int(date[2]),hour=int(time[0]),minute=int(time[1])) - datetime.datetime.now()
                days, hours, mins, secs = td.days, td.seconds // 3600, (td.seconds % 3600) // 60, (td.seconds % 3600) % 60
                dates = ""
                if days < 3: 
                    if days > 1:
                        dates += f"{days} days, "
                    elif days == 1:
                        dates += f"{days} day, "
                    if hours > 1:
                        dates += f"{hours} hours, "
                    elif hours == 1:
                        dates += f"{hours} hour, "
                    if mins > 1:
                        dates += f"{mins} minutes, "
                    elif mins == 1:
                        dates += f"{mins} minute, "
                    if secs > 1:
                        dates += f"{secs} seconds"
                    elif secs == 1:
                        dates += f"{secs} second"
                else:
                    dates += f"{days} days"
                bot_clip_embed.add_field(name=name, value=f"Will begin in {dates}. ({accDate}, {accTime} UTC)", inline=False)
            if len(jsons["items"]) == 3:
                name = jsons["items"][2]["summary"]
                start = jsons["items"][2]["start"]["dateTime"]
                start = start.split("T")
                date = start[0]
                time = start[1]
                date2 = date.split("-")
                date = date.split("-")
                date2.reverse()
                accDate = f"{months[(int(date2[1]) - 1)]} {date2[0]}"
                time = time.strip("Z").split(":")
                del time[2]
                accTime = ":".join(time)
                td = datetime.datetime(int(date[0]), int(date[1]), int(date[2]),hour=int(time[0]),minute=int(time[1])) - datetime.datetime.now()
                days, hours, mins, secs = td.days, td.seconds // 3600, (td.seconds % 3600) // 60, (td.seconds % 3600) % 60
                dates = ""
                if days < 3: 
                    if days > 1:
                        dates += f"{days} days, "
                    elif days == 1:
                        dates += f"{days} day, "
                    if hours > 1:
                        dates += f"{hours} hours, "
                    elif hours == 1:
                        dates += f"{hours} hour, "
                    if mins > 1:
                        dates += f"{mins} minutes, "
                    elif mins == 1:
                        dates += f"{mins} minute, "
                    if secs > 1:
                        dates += f"{secs} seconds"
                    elif secs == 1:
                        dates += f"{secs} second"
                else:
                    dates += f"{days} days"
                bot_clip_embed.add_field(name=name, value=f"Will begin in {dates}. ({accDate}, {accTime} UTC)", inline=False)
        else:
            bot_clip_embed = discord.Embed(
                        description=f"No tournaments currently scheduled, if any are, they will appear here!" ,
                        color=discord.Color.red()
                        )
            bot_clip_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
        await message.channel.send(" ", embed=bot_clip_embed)