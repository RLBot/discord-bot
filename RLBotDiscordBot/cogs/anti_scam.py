"""
One of the modern scam bots typically sends 4 images in all public channels.
This cog detects such cases, kicks the user, and deletes the messages.
"""

import datetime
from dataclasses import dataclass
from typing import List

import nextcord
from nextcord.ext import commands

from bot import RLBotDiscordBot
from config import GUILDS
from settings import SETTINGS_KEY_LOG_CHANNEL, SETTINGS_KEY_ANTI_SCAM_ENABLED

OFFENDING_EMBED_COUNT = 3
OFFENDING_CHANNEL_COUNT = 3
OFFENDING_TIME_WINDOW = datetime.timedelta(seconds=30)
REMEMBERED_MESSAGE_COUNT = 15


@dataclass
class MaybeScamMessage:
    user_id: int
    channel_id: int
    message_id: int
    created_at: datetime.datetime


class AntiScamCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot
        self.recent_offending_messages: List[MaybeScamMessage] = []

    @nextcord.slash_command(name="anti_scam", description="Enable or disable the anti-scam functionality", guild_ids=GUILDS)
    async def disable(self, interaction: nextcord.Interaction, status: str = nextcord.SlashOption(name="status", choices=["enable", "disable"])):
        await interaction.response.defer()
        self.bot.settings[SETTINGS_KEY_ANTI_SCAM_ENABLED] = status == "enable"
        if status == "enabled":
            interaction.followup.send(f"Anti-scam enabled: Kicking users who sends messages contain"
                                      f"{OFFENDING_EMBED_COUNT}+ embeds/attachments in {OFFENDING_CHANNEL_COUNT}"
                                      f"within {OFFENDING_TIME_WINDOW.seconds} seconds.")
        else:
            interaction.followup.send("Anti-scam disabled.")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return
        if self.bot.settings.setdefault(SETTINGS_KEY_ANTI_SCAM_ENABLED, False):
            return

        embed_count = len(message.embeds) + len(message.attachments)
        if embed_count >= OFFENDING_EMBED_COUNT:
            off_msg = MaybeScamMessage(
                message.author.id,
                message.channel.id,
                message.id,
                message.created_at
            )
            self.recent_offending_messages.append(off_msg)

            self.bot.logger.debug(f'{message.author.name} ({message.author.id}) sent a message with {OFFENDING_EMBED_COUNT}+ embeds.')

            await self.inspect_recent_messages(message)

            # Remove old messages to avoid memory build up
            if len(self.recent_offending_messages) >= REMEMBERED_MESSAGE_COUNT:
                self.recent_offending_messages = self.recent_offending_messages[1:REMEMBERED_MESSAGE_COUNT]


    async def inspect_recent_messages(self, trigger_msg: nextcord.Message):
        msgs = []
        channels_spammed = set()
        for prev_msg in self.recent_offending_messages:
            if prev_msg.user_id != trigger_msg.author.id:
                continue
            if prev_msg.created_at + OFFENDING_TIME_WINDOW < trigger_msg.created_at:
                continue
            msgs.append(prev_msg)
            channels_spammed.add(prev_msg.channel_id)

        if len(channels_spammed) >= OFFENDING_CHANNEL_COUNT:
            # :boot:
            log_msg = (f'Kicking {trigger_msg.author.name} (id: {trigger_msg.author.id}) for sending '
                       f'{len(msgs)} messages with {OFFENDING_EMBED_COUNT}+ embeds in {OFFENDING_CHANNEL_COUNT}+ '
                       f'channels within {OFFENDING_TIME_WINDOW.seconds} seconds.')
            self.bot.logger.info(log_msg)

            for msg in msgs:
                try:
                    await trigger_msg.author.fetch_message(msg.id)
                except:
                    # Maybe a mod removed it already
                    pass

            try:
                await trigger_msg.guild.kick(trigger_msg.author, reason=log_msg)

                log_channel = self.bot.settings.get(SETTINGS_KEY_LOG_CHANNEL)
                if log_channel:
                    await trigger_msg.guild.get_channel(log_channel).send(log_msg)
            except:
                # Maybe a mod kicked/banned them already
                pass


def setup(bot):
    bot.add_cog(AntiScamCommands(bot))