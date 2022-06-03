import datetime

import discord
import requests
from config import GOOGLE_API_KEY
from discord.ext import commands
from discord.ext import commands
from natural import date

from bot import RLBotDiscordBot

FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FORMAT2 = "%B %d, %H:%M UTC"
FORMAT3 = "%Y%m%dT%H%M%SZ"


class Calendar(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @commands.command(aliases=['tournaments'])
    async def tournament(self, ctx: discord.ext.commands.Context, *args):

        today = datetime.datetime.utcnow()
        to_check = today.strftime(FORMAT)
        api_key = GOOGLE_API_KEY
        r = requests.get(
            f"https://www.googleapis.com/calendar/v3/calendars/rlbotofficial@gmail.com/events?maxResults=10&timeMin={to_check}&key={api_key}")
        jsons = r.json()
        if len(jsons["items"]) != 0:
            tournaments_embed = await self.create_tournament_embed(jsons, today)
        else:
            tournaments_embed = discord.Embed(
                description=f"No tournaments currently scheduled, if any are, they will appear here!",
                color=discord.Color.red())

        tournaments_embed.set_author(name="Upcoming Tournaments",
                                     icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128",
                                     url="http://rlbot.org/tournament/")
        tournaments_embed.set_footer(text="http://rlbot.org/tournament/")
        await ctx.channel.send(" ", embed=tournaments_embed)

    @staticmethod
    async def create_tournament_embed(jsons, today):
        tournaments_embed = discord.Embed(color=discord.Color.green())
        events = []
        for raw_event in jsons["items"]:
            name, some_time, time_until, raw_date = date_time_check(today, raw_event)
            verb_tense = "Begins" if "now" in time_until else "Began"
            events.append({"name": name,
                           "some_time": some_time,
                           "time_until": time_until,
                           "raw_date": raw_date,
                           "verb_tense": verb_tense,
                           "location": raw_event.get("location"),
                           "docs": raw_event.get("description")})
        events.sort(key=lambda ev: ev["raw_date"])
        tournaments_embed = discord.Embed(
            title='',
            description='',
            color=discord.Color.green()
        )
        for i, event in enumerate(events):
            if event["docs"]:
                docs = f'[Docs]({event["docs"]})'
            else:
                docs = ""
            if event["location"]:
                twitch = f'[Twitch]({event["location"]})'
                if docs != '':
                    twitch = ' | ' + twitch
            else:
                twitch = ''
            if twitch == '' and docs == '':
                docs = 'No added info'
            tournaments_embed.add_field(name=event["name"] + f' - <t:{int(some_time.timestamp())}:R>',
                                            value=f'{docs}{twitch}',
                                            inline=False)
        return tournaments_embed


def date_time_check(today, event):
    names = event["summary"]
    start = event["start"]["dateTime"]
    new_date = datetime.datetime.strptime(start, FORMAT)
    raw_date = new_date.timestamp()
    try:
        recurrence = event["recurrence"][0].split(";")
        rec_type = recurrence[0].split("=")[1]
        interval = recurrence[2].split("=")[1]
        end_date_type = recurrence[2].split("=")[0]
        end_date_raw = recurrence[2].split("=")[1]
        if end_date_type == "COUNT":
            if rec_type == "WEEKLY":
                end_date = new_date + datetime.timedelta(days=7*int(interval)*int(end_date_raw))
            elif rec_type == "MONTHLY":
                end_date = new_date + datetime.timedelta(weeks=4*int(interval)*int(end_date_raw))
        else:
            end_date = datetime.datetime.strptime(end_date_raw, FORMAT3)
        if rec_type == "WEEKLY":
            while new_date <= end_date:
                if new_date > today:
                    break
                new_date += datetime.timedelta(days=7)
        elif rec_type == "MONTHLY":
            while new_date <= end_date:
                if new_date > today:
                    break
                new_date += datetime.timedelta(weeks=4)
    except Exception as e:
        print("Error checking recurrence:" + str(e))
    time_untils = date.duration(new_date, now=today, precision=3)
    return names, new_date, time_untils, raw_date


def setup(bot):
    bot.add_cog(Calendar(bot))
