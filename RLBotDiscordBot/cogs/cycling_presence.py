import datetime
import random

import nextcord
from nextcord.ext import commands, tasks

from bot import RLBotDiscordBot
from config import GUILDS
from settings import SETTINGS_KEY_STATUE_MESSAGE_LIST, DEFAULT_STATUS_MESSAGE


class CyclingPresenceCog(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot
        self.update_presence.start()

    @nextcord.slash_command(name="presence_list", description="Lists all presence activities")
    async def presence_list(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        statuses = self.bot.settings.setdefault(SETTINGS_KEY_STATUE_MESSAGE_LIST, [])
        if len(statuses) == 0:
            await interaction.followup.send("There are no presence activities. Use `/presence_add` to add some.")
        else:
            msg = f"**All presence activities:**\n" + "\n".join(statuses)
            await interaction.followup.send(msg)

    @nextcord.slash_command(name="presence_add", description="Add a presence")
    async def presence_add(self, interaction: nextcord.Interaction, activity: str):
        await interaction.response.defer()

        self.bot.settings.setdefault(SETTINGS_KEY_STATUE_MESSAGE_LIST, []).append(activity.strip())
        self.bot.save_and_reload_settings()

        await interaction.followup.send("Added presence: " + activity)

    @nextcord.slash_command(name="presence_del", description="Delete a presence")
    async def presence_del(self, interaction: nextcord.Interaction, activity: str):
        await interaction.response.defer()

        activities = self.bot.settings.setdefault(SETTINGS_KEY_STATUE_MESSAGE_LIST, [])
        exists = activity in activities
        updated_activities = list(filter(lambda a: a != activity, activities))
        self.bot.settings[SETTINGS_KEY_STATUE_MESSAGE_LIST] = updated_activities

        if exists:
            self.bot.save_and_reload_settings()
            await interaction.followup.send("Deleted presence: " + activity)
        else:
            await interaction.followup.send("Presence was not found and could not be deleted.")

    @tasks.loop(seconds=300, reconnect=True)  # Runs every X seconds
    async def update_presence(self):
        # Stream/watch if an event is located on twitch
        guild = self.bot.get_guild(GUILDS[-1])   # RLBot server in production, TEST_GUILD in tests
        if guild:
            now = datetime.datetime.now(datetime.timezone.utc)
            async for event in guild.fetch_scheduled_events():
                if not (event.start_time < now < event.end_time):
                    continue
                if event.location is None:
                    continue

                if event.location.lower() == "https://www.twitch.tv/rlbotofficial":
                    # We are streaming
                    activity = nextcord.Streaming(
                        name="Streaming " + event.name,
                        url="https://www.twitch.tv/rlbotofficial",
                        platform="Twitch",
                    )
                    await self.bot.change_presence(activity=activity)
                    return

                elif event.location.lower().startswith("https://www.twitch.tv/"):
                    # Someone else is streaming
                    activity = nextcord.Activity(
                        name="Watching twitch.tv/" + event.location[len("https://www.twitch.tv/"):],
                        type=nextcord.ActivityType.watching,
                        url=event.location.lower(),
                        platform="Twitch",
                    )
                    await self.bot.change_presence(activity=activity)
                    return

        # Use one from the list
        activities = self.bot.settings.setdefault(SETTINGS_KEY_STATUE_MESSAGE_LIST, [])
        if len(activities) > 0:
            activity = random.choice(activities)
            await self.bot.change_presence(activity=nextcord.Game(activity))
            return

        # Fallback
        await self.bot.change_presence(activity=nextcord.Game(DEFAULT_STATUS_MESSAGE))

    @update_presence.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()  # Wait until bot logs in


def setup(bot):
    bot.add_cog(CyclingPresenceCog(bot))