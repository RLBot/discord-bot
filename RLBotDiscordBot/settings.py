import json

from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / 'settings.json'

SETTINGS_KEY_COMMANDS = "commands"
SETTINGS_KEY_ADMIN_CHANNEL = "admin_channel"
SETTINGS_KEY_LOG_CHANNEL = "log_channel"
SETTINGS_KEY_CLIPS_CHANNEL = "clips_channel"
SETTINGS_KEY_STATUS_MESSAGE = "status_message"
SETTINGS_KEY_WHITELISTED_CLIPS_DOMAINS = "whitelisted_clips_domains"
SETTINGS_KEY_FAQ_CHANNEL = "faq_channel"
SETTINGS_KEY_FAQ_CONTENT = "faqs"
SETTINGS_KEY_FAQ_ITEM_MSG = "msg"
SETTINGS_KEY_FAQ_ITEM_QUESTION = "question"
SETTINGS_KEY_FAQ_ITEM_ANSWER = "answer"
SETTINGS_KEY_ANTI_SCAM_ENABLED = "anti_scam_enabled"


def load_settings():
    if not SETTINGS_PATH.exists():
        save_settings({})
        return load_settings()
    else:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)


def save_settings(settings):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)
