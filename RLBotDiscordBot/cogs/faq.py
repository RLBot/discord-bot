from discord.ext import commands

from RLBotDiscordBot.bot import RLBotDiscordBot


class FaqCommands(commands.Cog):
    def __init__(self, bot: RLBotDiscordBot):
        self.bot = bot

    @commands.command()
    async def faq_channel(self, ctx, channel_id):
        if not self.check_perms(ctx):
            return

        try:
            channel_id_parsed = int(channel_id[3:-1])
            channel = ctx.guild.get_channel(channel_id_parsed)
            if channel is None:
                raise ValueError

            # Remove messages from old faq channel
            await self.remove_old_faq_messages(ctx)

            # Save new faq channel
            self.bot.settings['Faq_channel'] = channel_id_parsed

            await ctx.send('FAQ channel was successfully updated')
            await self.refresh_faq(ctx)   # Also saves changes to settings

        except ValueError:
            await ctx.send('Something went wrong. Expected a channel id, e.g. "\<#12345678987654321\>"')

    @commands.command()
    async def add_faq(self, ctx, question, answer):
        if not self.check_perms(ctx):
            return

        faqs = self.get_faqs()
        faqs.append({
            "Q": question,
            "A": answer,
            "msg": None,
        })

        await self.refresh_faq(ctx)   # Also saves changes to settings
        await ctx.send(f'Succesfully added FAQ:\n**Q{len(faqs)}: {question}**\nA: {answer}')

    @commands.command()
    async def edit_faq(self, ctx, id, question, answer):
        if not self.check_perms(ctx):
            return

        # Note that id is 1-indexed!
        id = int(id)

        faqs = self.get_faqs()
        if 0 < id <= len(faqs):

            faq = faqs[id - 1]
            faq['Q'] = question
            faq['A'] = answer

            await self.refresh_faq(ctx)   # Also saves changes to settings
            await ctx.send(f'Succesfully updated FAQ:\n**Q{id}: {question}**\nA: {answer}')

        else:
            await ctx.send(f'The question id is out of bounds. There are {len(faqs)} FAQs')

    @commands.command()
    async def del_faq(self, ctx, id):
        if not self.check_perms(ctx):
            return

        # Note that id is 1-indexed!
        id = int(id)

        faqs = self.get_faqs()
        if 0 < id <= len(faqs):
            await self.remove_old_faq_messages(ctx)

            question = faqs[id - 1]['Q']

            del faqs[id - 1]

            await self.refresh_faq(ctx)   # Also saves changes to settings
            await ctx.send(f'Succesfully removed "Q{id}: {question}"')

        else:
            await ctx.send(f'The question id is out of bounds. There are {len(faqs)} FAQs')

    @commands.command()
    async def swap_faqs(self, ctx, id1, id2):
        if not self.check_perms(ctx):
            return

        # Note that ids are 1-indexed!
        id1 = int(id1)
        id2 = int(id2)

        if id1 == id2:
            # Lol
            return

        faqs = self.get_faqs()
        if 0 < id1 <= len(faqs):
            if 0 < id2 <= len(faqs):
                await self.remove_old_faq_messages(ctx)

                faqs[id1 - 1], faqs[id2 - 1] = faqs[id2 - 1], faqs[id1 - 1]

                await self.refresh_faq(ctx)  # Also saves changes to settings
                await ctx.send(f'Successfully swapped Q{id1} and Q{id2}')
            else:
                await ctx.send(f'The question id2 is out of bounds. There are {len(faqs)} FAQs')
        else:
            await ctx.send(f'The question id1 is out of bounds. There are {len(faqs)} FAQs')

    @commands.command(aliases=['refresh_faq'])
    async def refresh_faq_cmd(self, ctx):
        if not self.check_perms(ctx):
            return
        await self.refresh_faq(ctx)

    async def refresh_faq(self, ctx):

        await self.remove_old_faq_messages(ctx)

        # Validate that faq channel exists
        faq_channel_id = self.bot.settings.get('Faq_channel')
        if faq_channel_id is None:
            print("hi1")
            await ctx.send('FAQ channel is not set. Use `!faq_channel <#channel_id>` to set it')
            return
        faq_channel = ctx.guild.get_channel(faq_channel_id)
        if faq_channel is None:
            print("hi2")
            await ctx.send('FAQ channel does not exist. Use `!faq_channel <#channel_id>` to set it')
            return

        # Send FAQ entries
        faqs = self.get_faqs()
        for i, faq in enumerate(faqs):
            question = faq["Q"]
            answer = faq["A"]
            msg = await faq_channel.send(f"**Q{i + 1}: {question}**\nA: {answer}")
            faq["msg"] = msg.id   # Updates settings

        # Save new message ids
        self.bot.save_and_reload_settings()

    async def remove_old_faq_messages(self, ctx):
        faq_channel_id = self.bot.settings.get('Faq_channel')
        if faq_channel_id is not None:
            faq_channel = ctx.guild.get_channel(faq_channel_id)
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

    def check_perms(self, ctx):
        return ctx.message.channel.id == self.bot.settings['Admin_channel']


def setup(bot):
    bot.add_cog(FaqCommands(bot))
