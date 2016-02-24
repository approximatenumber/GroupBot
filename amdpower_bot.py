#!/usr/bin/env python
# -*- coding: utf-8 -*-

# importing modules
import telegram, configparser, logging, os, sys, re
from time import sleep, localtime
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen                          # python 2 (raspbian)
try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError                                # python 2 (raspbian)
try:
    sys.path.append('.private'); from config import TOKEN       # importing secret TOKEN
except ImportError:
    print("need TOKEN from .private/config.py")
    sys.exit(1)

# variables
log_file = "bot.log"
amd_group = -132848042

def main():
    logging.basicConfig(level = logging.WARNING,filename=log_file,format='%(asctime)s:%(levelname)s - %(message)s')

    sendMessage = lambda chat_id, msg: bot.sendMessage(chat_id, msg)

    def echo(bot, update_id):                                                       # Request updates after the last update_id
        for update in bot.getUpdates(offset=update_id, timeout=10):                 # chat_id is required to reply to any message
            chat_id = update.message.chat_id
            update_id = update.update_id + 1
            message = update.message.text
            new_chat_participant = update.message.new_chat_participant
            left_chat_participant = update.message.left_chat_participant
            if message and chat_id == amd_group:
                msg = "i`m talking in group now"
                sendMessage(chat_id, msg)
            elif left_chat_participant:
                msg = "%s нас покинул(а). Какая жалость..." % left_chat_participant["first_name"]
                sendMessage(chat_id, msg)
            elif new_chat_participant:
                msg = "Добро пожаловать, %s!" % new_chat_participant["first_name"]
                sendMessage(chat_id, msg)
            elif message:
                msg = "Я бот, такие дела."
                sendMessage(chat_id, msg)
        return update_id

# initialization
    open(log_file, 'w').close()
    logging.warning('bot started...')

    bot = telegram.Bot(TOKEN)
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

# body

    while True:
        try:
            update_id = echo(bot, update_id)
        except telegram.TelegramError as e:
            # These are network problems with Telegram.
            if e.message in ("Bad Gateway", "Timed out"):
                sleep(1)
            elif e.message == "Unauthorized":
                # The user has removed or blocked the bot.
                update_id += 1
            else:
                raise e
        except URLError as e:
            # These are network problems on our end.
            sleep(1)

if __name__ == '__main__':
    main()
