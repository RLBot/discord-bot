"""
One of the modern scam bots typically sends 4 images in all public channels.
This cog detects such cases and bans the user.
"""

import datetime
from dataclasses import dataclass
from typing import List

import nextcord
from nextcord.ext import commands

from bot import RLBotDiscordBot
from settings import SETTINGS_KEY_LOG_CHANNEL

OFFENDING_EMBED_COUNT = 3
OFFENDING_CHANNEL_COUNT = 3
OFFENDING_TIME_INTERVAL = datetime.timedelta(minutes=5)
REMEMBERED_MESSAGE_COUNT = 15


@dataclass
class MaybeScamMessage:
    user_id: int
    channel_id: int
    created_at: datetime.datetime


class AntiScamCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot
        self.recent_offending_messages: List[MaybeScamMessage] = []

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        embed_count = len(message.embeds) + len(message.attachments)
        if embed_count >= OFFENDING_EMBED_COUNT:
            off_msg = MaybeScamMessage(
                message.author.id,
                message.channel.id,
                message.created_at
            )
            self.recent_offending_messages.append(off_msg)

            self.bot.logger.debug(f'{message.author.name} ({message.author.id}) sent a message with {OFFENDING_EMBED_COUNT}+ embeds.')

            await self.inspect_recent_messages(message)

            # Remove old messages
            if len(self.recent_offending_messages) >= REMEMBERED_MESSAGE_COUNT:
                self.recent_offending_messages = self.recent_offending_messages[1:REMEMBERED_MESSAGE_COUNT]


    async def inspect_recent_messages(self, trigger_msg: nextcord.Message):
        msg_count = 0
        channels_spammed = set()
        for prev_msg in self.recent_offending_messages:
            if prev_msg.user_id != trigger_msg.author.id:
                continue
            if prev_msg.created_at + OFFENDING_TIME_INTERVAL < trigger_msg.created_at:
                continue
            msg_count += 1
            channels_spammed.add(prev_msg.channel_id)

        if len(channels_spammed) >= OFFENDING_CHANNEL_COUNT:
            # BAN :hammer:
            log_msg = (f'Banning {trigger_msg.author.name} (id: {trigger_msg.author.id}) for sending '
                       f'{msg_count} messages with {OFFENDING_EMBED_COUNT}+ embeds in {OFFENDING_CHANNEL_COUNT}+ '
                       f'channels within {OFFENDING_TIME_INTERVAL.seconds} seconds.')
            self.bot.logger.info(log_msg)

            try:
                await trigger_msg.guild.ban(trigger_msg.author, reason=log_msg, delete_message_seconds=OFFENDING_TIME_INTERVAL.seconds)
                log_channel = self.bot.settings.get(SETTINGS_KEY_LOG_CHANNEL)
                if log_channel:
                    await trigger_msg.guild.get_channel(log_channel).send(log_msg)
            except:
                # Maybe a mod banned them already
                pass

def setup(bot):
    bot.add_cog(AntiScamCommands(bot))