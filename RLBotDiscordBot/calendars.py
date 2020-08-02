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
    FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    FORMAT2 = "%B %d, %H:%M UTC"
    today = datetime.datetime.utcnow()
    to_check = today.strftime(FORMAT)
    api_key = GOOGLE_API_KEY
    args = message.content.split(" ")
    if "!tournaments" in args:
        r = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/rlbotofficial@gmail.com/events?maxResults=3&timeMin={to_check}&key={api_key}")
        jsons = r.json()
        if len(jsons["items"]) > 0:
            name, some_time, time_until = date_time_check(today, jsons, 0)
            tournaments_embed = discord.Embed(
                        title=name,
                        description=f"Will begin in {time_until}. ({some_time})" ,
                        color=discord.Color.green()
                        )
            tournaments_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
            if len(jsons["items"]) >= 2:
                name, some_time, time_until = date_time_check(today, jsons, 1)
                tournaments_embed.add_field(name=name, value=f"Will begin in {time_until}. ({month_day}, {some_time})", inline=False)
            if len(jsons["items"]) == 3:
                name, some_time, time_until = date_time_check(today, jsons, 2)
                tournaments_embed.add_field(name=name, value=f"Will begin in {time_until}. ({month_day}, {some_time})", inline=False)
        else:
            tournaments_embed = discord.Embed(
                        description=f"No tournaments currently scheduled, if any are, they will appear here!" ,
                        color=discord.Color.red()
                        )
            tournaments_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
        tournaments_embed.set_footer(text="http://www.rlbot.org/tournament/")
        await message.channel.send(" ", embed=tournaments_embed)


def date_time_check(today, jsons, num):
    FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    FORMAT2 = "%B %d, %H:%M UTC"
    names = jsons["items"][num]["summary"]
    start = jsons["items"][num]["start"]["dateTime"]
    new_date = datetime.datetime.strptime(start, FORMAT)
    some_times = new_date.strftime(FORMAT2)
    time_untils = date.duration(new_date, now=today, precision=3)
    return names, some_times, time_untils
