# RLBotDiscordBot

This is the Discord bot running in the [RLBot](https://rlbot.org/) Discord server.

## Info

It uses the [nextcord](https://github.com/nextcord/nextcord) framework.

The main bot is RLBotDiscordBot.py and its modules is located in the cog folder.

To run/test the bot you need the following environment variables set:
- `TOKEN`, a Discord Bot Token.
- `GOOGLE_API_KEY` (optional), a Google API key in order to fetch tournaments from the Google Calendar.
- `TEST_GUILD` (optional), a Discord server id of a test server to allow of testing admin commands which otherwise only work in RLBot.