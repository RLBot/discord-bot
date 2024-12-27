import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from config import GUILDS

from bot import RLBotDiscordBot


class FaqCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @nextcord.slash_command(name="faq_channel", description="Update FAQ channel", guild_ids=GUILDS)
    async def faq_channel(self, interaction: Interaction, channel: nextcord.TextChannel):
        await interaction.response.defer()
        await self.remove_old_faq_messages(interaction)

        # Save new faq channel
        self.bot.settings['Faq_channel'] = channel.id

        await interaction.followup.send('FAQ channel was successfully updated')
        await self.refresh(interaction)  # Also saves changes to settings

    @nextcord.slash_command(name="add_faq", description="Add an FAQ", guild_ids=GUILDS)
    async def add_faq(self, interaction: Interaction, question: str, answer: str):
        await interaction.response.defer()

        faqs = self.get_faqs()
        faqs.append({
            "Q": question,
            "A": answer,
            "msg": None,
        })

        await self.refresh(interaction)  # Also saves changes to settings
        await interaction.followup.send(f'Succesfully added FAQ:\n**Q{len(faqs)}: {question}**\n{answer}')

    @nextcord.slash_command(name="edit_faq", description="Edit a FAQ", guild_ids=GUILDS)
    async def edit_faq(self, interaction: Interaction, qid: int, question: str, answer: str):
        await interaction.response.defer()

        # Convert to 0-indexed
        qid = int(qid) - 1

        faqs = self.get_faqs()
        if 0 <= qid < len(faqs):

            faq = faqs[qid]
            faq['Q'] = question
            faq['A'] = answer

            await self.refresh(interaction)  # Also saves changes to settings
            await interaction.followup.send(f'Succesfully updated FAQ:\n**Q{qid + 1}: {question}**\n{answer}')

        else:
            await interaction.followup.send(f'The question id is out of bounds. There are {len(faqs)} FAQs')

    @nextcord.slash_command(name="del_faq", description="Delete an FAQ", guild_ids=GUILDS)
    async def del_faq(self, interaction: Interaction, qid: int):
        await interaction.response.defer()
        # Convert to 0-indexed
        qid = int(qid) - 1

        faqs = self.get_faqs()
        if 0 <= qid < len(faqs):
            await self.remove_old_faq_messages(interaction)

            question = faqs[qid]['Q']
            answer = faqs[qid]['A']

            del faqs[qid]

            await self.refresh(interaction)  # Also saves changes to settings
            await interaction.followup.send(f'Succesfully removed FAQ:\n"**Q{qid + 1}: {question}**\n{answer}"')

        else:
            await interaction.followup.send(f'The question id is out of bounds. There are {len(faqs)} FAQs')

    @nextcord.slash_command(name="swap_faq", description="Swap two FAQs", guild_ids=GUILDS)
    async def swap_faqs(self, interaction: Interaction, qid1: int, qid2: int):
        await interaction.response.defer()
        # Convert to 0-indexed
        qid1 = int(qid1) - 1
        qid2 = int(qid2) - 1

        if qid1 == qid2:
            # Lol
            return

        faqs = self.get_faqs()
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

    @nextcord.slash_command(name="refresh_faq", description="Refresh FAQs", guild_ids=GUILDS)
    async def refresh_faq(self, interaction: Interaction):
        await interaction.response.defer()
        await self.refresh(interaction)
        await interaction.followup.send("FAQ refreshed")

    async def refresh(self, interaction: Interaction):

        await self.remove_old_faq_messages(interaction)

        # Validate that faq channel exists
        faq_channel_id = self.bot.settings.get('Faq_channel')
        if faq_channel_id is None:
            await interaction.followup.send('FAQ channel is not set. Use `/faq_channel` to set it')
            return
        faq_channel = interaction.guild.get_channel(faq_channel_id)
        if faq_channel is None:
            await interaction.followup.send('FAQ channel does not exist. Use `/faq_channel` to set it')
            return

        # Send FAQ entries
        faqs = self.get_faqs()
        for i, faq in enumerate(faqs):
            question = faq["Q"]
            answer = faq["A"]
            msg = await faq_channel.send(f"## Q{i + 1}: {question}\n{answer}\n")
            faq["msg"] = msg.id  # Updates settings

        # Save new message ids
        self.bot.save_and_reload_settings()

    async def remove_old_faq_messages(self, interaction: Interaction):
        faq_channel_id = self.bot.settings.get('Faq_channel')
        if faq_channel_id is not None:
            faq_channel = interaction.guild.get_channel(faq_channel_id)
            if faq_channel is not None:
                faqs = self.get_faqs()
                for faq in faqs:
                    msg_id = faq["msg"]
                    if msg_id is not None:
                        try:
                            msg = await faq_channel.fetch_message(msg_id)
                            if msg is not None:
                                await msg.delete()
                        except Exception:
                            pass

    def get_faqs(self):
        # Ensures that FAQ list exists in settings (but does not reload settings)
        faqs = self.bot.settings.get('Faqs')
        if faqs is None:
            faqs = []
            self.bot.settings['Faqs'] = faqs
        return faqs


def setup(bot):
    bot.add_cog(FaqCommands(bot))
