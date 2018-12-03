import asyncio
from bot import RLBotDiscordBot

import logging
import contextlib

""" Setup Logging for the bot """
@contextlib.contextmanager
def start_logging():

    try:
        log = logging.getLogger()
        log.setLevel(logging.INFO)

        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        # Initialize handlers for logging (Log to file and to the console)
        #file_handler = logging.FileHandler(filename='./RLBotDiscordBot/rlbotdiscord.log', encoding='utf-8', mode='w')
        console_handler = logging.StreamHandler()

        date_format = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', date_format, style='{')

        #file_handler.setFormatter(fmt)
        console_handler.setFormatter(fmt)

        #log.addHandler(file_handler)
        log.addHandler(console_handler)
        yield

    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

""" Runs the bot """
if __name__ == '__main__':
    with start_logging():
        bot = RLBotDiscordBot()
        bot.run()
