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
        dates_list = []
        for i in range(len(jsons["items"])):
            dates_list.append(date_time_check(today, jsons, i))
        dates_list.sort(key=lambda tup: tup[2])

        if len(dates_list) > 0:
            name, some_time, time_until = dates_list[0]
            tournaments_embed = discord.Embed(
                        title=name,
                        description=f"Will begin in {time_until}. ({some_time})" , #after even has started but not finished, this will say "Will being in {time} ago" I am not sure how to fix this using the API arguments
                        color=discord.Color.green()
                        )
            tournaments_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
            if len(dates_list) >= 2:
                name, some_time, time_until = dates_list[1]
                tournaments_embed.add_field(name=name, value=f"Will begin in {time_until}. ({some_time})", inline=False)
            if len(dates_list) == 3:
                name, some_time, time_until = dates_list[2]
                tournaments_embed.add_field(name=name, value=f"Will begin in {time_until}. ({some_time})", inline=False)
        else:
            tournaments_embed = discord.Embed(
                        description=f"No tournaments currently scheduled, if any are, they will appear here!" ,
                        color=discord.Color.red()
                        )
            tournaments_embed.set_author(name="Upcoming Tournaments", icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128")
        tournaments_embed.set_footer(text="http://rlbot.org/tournament/")
        await message.channel.send(" ", embed=tournaments_embed)


def date_time_check(today, jsons, num):
    FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    FORMAT2 = "%B %d, %H:%M UTC"
    names = jsons["items"][num]["summary"]
    start = jsons["items"][num]["start"]["dateTime"]
    new_date = datetime.datetime.strptime(start, FORMAT)
    try:
        recurrence = jsons["items"][num]["recurrence"][0].split(";")
        rec_type = recurrence[0].split("=")[1]
        num_recs = recurrence[2].split("=")[1]
        if rec_type == "WEEKLY":
            for i in range(int(num_recs)):
                if new_date > today:
                    break
                new_date += datetime.timedelta(days=7)
        elif rec_type == "MONTHLY":
            for i in range(int(num_recs)):
                if new_date > today:
                    break
                new_date += datetime.timedelta(months=1)
    except:
        pass
    some_times = new_date.strftime(FORMAT2)
    time_untils = date.duration(new_date, now=today, precision=3)
    return (names, some_times, time_untils)
