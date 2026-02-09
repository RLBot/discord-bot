import nextcord
from nextcord import Interaction
from nextcord.ext import commands

from bot import RLBotDiscordBot
from config import GUILDS
from settings import SETTINGS_KEY_FAQ_CONTENT, SETTINGS_KEY_FAQ_CHANNEL, SETTINGS_KEY_FAQ_ITEM_MSG, \
    SETTINGS_KEY_FAQ_ITEM_QUESTION, SETTINGS_KEY_FAQ_ITEM_ANSWER


class FaqCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @nextcord.slash_command(name="faq_channel_set", description="Update FAQ channel", guild_ids=GUILDS)
    async def faq_channel(self, interaction: Interaction, channel: nextcord.TextChannel):
        await interaction.response.defer()
        await self.remove_old_faq_messages(interaction)

        # Save new faq channel
        self.bot.settings[SETTINGS_KEY_FAQ_CHANNEL] = channel.id

        await interaction.followup.send('FAQ channel was successfully updated')
        await self.refresh(interaction)  # Also saves changes to settings

    @nextcord.slash_command(name="faq_add", description="Add an FAQ", guild_ids=GUILDS)
    async def add_faq(self, interaction: Interaction, question: str, answer: str):
        await interaction.response.defer()

        faqs = self.bot.settings.setdefault(SETTINGS_KEY_FAQ_CONTENT, [])
        faqs.append({
            SETTINGS_KEY_FAQ_ITEM_QUESTION: question,
            SETTINGS_KEY_FAQ_ITEM_ANSWER: answer,
            SETTINGS_KEY_FAQ_ITEM_MSG: None,
        })

        await self.refresh(interaction)  # Also saves changes to settings
        await interaction.followup.send(f'Successfully added FAQ:\n**Q{len(faqs)}: {question}**\n{answer}')

    @nextcord.slash_command(name="faq_edit", description="Edit a FAQ", guild_ids=GUILDS)
    async def edit_faq(self, interaction: Interaction, qid: int, question: str, answer: str):
        await interaction.response.defer()

        # Convert to 0-indexed
        qid = int(qid) - 1

        faqs = self.bot.settings.setdefault(SETTINGS_KEY_FAQ_CONTENT, [])
        if 0 <= qid < len(faqs):

            faq = faqs[qid]
            faq[SETTINGS_KEY_FAQ_ITEM_QUESTION] = question
            faq[SETTINGS_KEY_FAQ_ITEM_ANSWER] = answer

            await self.refresh(interaction)  # Also saves changes to settings
            await interaction.followup.send(f'Successfully updated FAQ:\n**Q{qid + 1}: {question}**\n{answer}')

        else:
            await interaction.followup.send(f'The question id is out of bounds. There are {len(faqs)} FAQs')

    @nextcord.slash_command(name="faq_del", description="Delete an FAQ", guild_ids=GUILDS)
    async def del_faq(self, interaction: Interaction, qid: int):
        await interaction.response.defer()
        # Convert to 0-indexed
        qid = int(qid) - 1

        faqs = self.bot.settings.setdefault(SETTINGS_KEY_FAQ_CONTENT, [])
        if 0 <= qid < len(faqs):
            await self.remove_old_faq_messages(interaction)

            question = faqs[qid][SETTINGS_KEY_FAQ_ITEM_QUESTION]
            answer = faqs[qid][SETTINGS_KEY_FAQ_ITEM_ANSWER]

            del faqs[qid]

            await self.refresh(interaction)  # Also saves changes to settings
            await interaction.followup.send(f'Successfully removed FAQ:\n"**Q{qid + 1}: {question}**\n{answer}"')

        else:
            await interaction.followup.send(f'The question id is out of bounds. There are {len(faqs)} FAQs')

    @nextcord.slash_command(name="faq_swap", description="Swap two FAQs", guild_ids=GUILDS)
    async def swap_faqs(self, interaction: Interaction, qid1: int, qid2: int):
        await interaction.response.defer()
        # Convert to 0-indexed
        qid1 = int(qid1) - 1
        qid2 = int(qid2) - 1

        if qid1 == qid2:
            # Lol
            return

        faqs = self.bot.settings.setdefault(SETTINGS_KEY_FAQ_CONTENT, [])
        if 0 <= qid1 < len(faqs):
            if 0 <= qid2 < len(faqs):
                await self.remove_old_faq_messages(interaction)

                faqs[qid1], faqs[qid2] = faqs[qid2], faqs[qid1]

                await self.refresh(interaction)  # Also saves changes to settings
                await interaction.followup.send(f'Successfully swapped Q{qid1 + 1} and Q{qid2 + 1}')
            else:
                await interaction.followup.send(f'The question id2 is out of bounds. There are {len(faqs)} FAQs')
        else:
            await interaction.followup.send(f'The question id1 is out of bounds. There are {len(faqs)} FAQs')

    @nextcord.slash_command(name="faq_refresh", description="Refresh FAQs", guild_ids=GUILDS)
    async def refresh_faq(self, interaction: Interaction):
        await interaction.response.defer()
        await self.refresh(interaction)
        await interaction.followup.send("FAQ refreshed")

    async def refresh(self, interaction: Interaction):

        await self.remove_old_faq_messages(interaction)

        # Validate that faq channel is set and exists
        faq_channel_id = self.bot.settings.get(SETTINGS_KEY_FAQ_CHANNEL)
        if faq_channel_id is None:
            await interaction.followup.send('FAQ channel is not set. Use `/faq_channel_set` to set it')
            return
        faq_channel = interaction.guild.get_channel(faq_channel_id)
        if faq_channel is None:
            await interaction.followup.send('FAQ channel does not exist. Use `/faq_channel_set` to set it')
            return

        # Send FAQ entries
        faqs = self.bot.settings.setdefault(SETTINGS_KEY_FAQ_CONTENT, [])
        for i, faq in enumerate(faqs):
            question = faq[SETTINGS_KEY_FAQ_ITEM_QUESTION]
            answer = faq[SETTINGS_KEY_FAQ_ITEM_ANSWER]
            msg = await faq_channel.send(f"## Q{i + 1}: {question}\n{answer}\n")
            faq[SETTINGS_KEY_FAQ_ITEM_MSG] = msg.id  # Updates settings

        # Save new message ids
        self.bot.save_and_reload_settings()

    async def remove_old_faq_messages(self, interaction: Interaction):
        faq_channel_id = self.bot.settings.get(SETTINGS_KEY_FAQ_CHANNEL)
        if faq_channel_id is not None:
            faq_channel = interaction.guild.get_channel(faq_channel_id)
            if faq_channel is not None:
                faqs = self.bot.settings.setdefault(SETTINGS_KEY_FAQ_CONTENT, [])
                for faq in faqs:
                    msg_id = faq[SETTINGS_KEY_FAQ_ITEM_MSG]
                    if msg_id is not None:
                        try:
                            msg = await faq_channel.fetch_message(msg_id)
                            if msg is not None:
                                await msg.delete()
                        except Exception:
                            pass


def setup(bot):
    bot.add_cog(FaqCommands(bot))
