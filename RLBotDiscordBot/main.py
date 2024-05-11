import contextlib
import logging
import sys

from bot import RLBotDiscordBot
from config import TOKEN, GOOGLE_API_KEY


@contextlib.contextmanager
def start_logging():
    """ Setup Logging for the bot """
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    try:

        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        # Initialize handlers for logging (Log to file and to the console)
        # file_handler = logging.FileHandler(filename='./RLBotDiscordBot/rlbotdiscord.log', encoding='utf-8', mode='w')
        console_handler = logging.StreamHandler()

        date_format = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', date_format, style='{')

        # file_handler.setFormatter(fmt)
        console_handler.setFormatter(fmt)

        # log.addHandler(file_handler)
        log.addHandler(console_handler)
        yield

    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


if __name__ == '__main__':
    """ Runs the bot """
    with start_logging():
        logger = logging.getLogger(__name__)

        if TOKEN is None:
            logger.fatal(
                'Unable to run bot as environment variable \'TOKEN\' is not set! Please set it to a valid Discord bot token.')
            sys.exit(1)

        if GOOGLE_API_KEY is None:
            logger.warning('Environment variable \'GOOGLE_API_KEY\' is not set. Some commands might not work.')

        bot = RLBotDiscordBot()
        bot.run()
