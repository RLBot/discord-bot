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
import natural
from natural import date

import discord
from discord.ext import commands
from discord.utils import get


async def checkCalendar(message):
    api_key = GOOGLE_API_KEY
    args = message.content.split(" ")
    if "!tournaments" in args:
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September","October", "November", "December"]
        FORMAT = "%Y-%m-%dT%H:%M:%SZ"
        FORMAT2 = "%H:%M UTC"
        FORMAT3 = "%d %m"
        today = datetime.datetime.utcnow()
        to_check = today.strftime(FORMAT)
        r = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/rlbotofficial@gmail.com/events?maxResults=3&timeMin={to_check}&key={api_key}")
        jsons = r.json()
        if len(jsons["items"]) > 0:
            name = jsons["items"][0]["summary"]
            start = jsons["items"][0]["start"]["dateTime"]
            new_date = datetime.datetime.strptime(start, FORMAT)
            some_time = new_date.strftime(FORMAT2)
            day_month = new_date.strftime(FORMAT3).split(" ")
            day = day_month[0]
            month = months[int(day_month[1])-1]
            month_day = month + " " + day
            time_until = date.duration(new_date, now=today, precision=3)
            tournaments_embed = discord.Embed(
                        title=name,
                        description=f"Will begin in {time_until}. ({month_day}, {some_time})" ,
                        color=discord.Color.green()
                        )
            tournaments_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
            if len(jsons["items"]) >= 2:
                name = jsons["items"][1]["summary"]
                start = jsons["items"][1]["start"]["dateTime"]
                new_date = datetime.datetime.strptime(start, FORMAT)
                some_time = new_date.strftime(FORMAT2)
                day_month = new_date.strftime(FORMAT3).split(" ")
                day = day_month[0]
                month = months[int(day_month[1])-1]
                month_day = month + " " + day
                time_until = date.duration(new_date, now=today, precision=3)
                tournaments_embed.add_field(name=name, value=f"Will begin in {time_until}. ({month_day}, {some_time})", inline=False)
            if len(jsons["items"]) == 3:
                name = jsons["items"][2]["summary"]
                start = jsons["items"][2]["start"]["dateTime"]
                new_date = datetime.datetime.strptime(start, FORMAT)
                some_time = new_date.strftime(FORMAT2)
                day_month = new_date.strftime(FORMAT3).split(" ")
                day = day_month[0]
                month = months[int(day_month[1])-1]
                month_day = month + " " + day
                time_until = date.duration(new_date, now=today, precision=3)
                tournaments_embed.add_field(name=name, value=f"Will begin in {time_until}. ({month_day}, {some_time})", inline=False)
        else:
            tournaments_embed = discord.Embed(
                        description=f"No tournaments currently scheduled, if any are, they will appear here!" ,
                        color=discord.Color.red()
                        )
            tournaments_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
        await message.channel.send(" ", embed=tournaments_embed)
