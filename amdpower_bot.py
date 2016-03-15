#!/usr/bin/env python
# -*- coding: utf-8 -*-

# importing modules
import telegram, configparser, logging, os, sys, re, random
from time import sleep, localtime
from urllib.request import urlopen
from urllib.error import URLError

try:
    sys.path.append('.private'); from config import TOKEN, GROUP, BOTNAME, BOTFIRSTNAME       # importing private data
except ImportError:
    print("I need TOKEN, GROUP, BOTNAME, BOTFIRSTNAME from .private/config.py!")
    sys.exit(1)

# variables
log_file = "bot.log"
welcome_text = ['Рады приветствовать на старейшем канале, посвященном AMD и всему остальному не менее важному',
            'AMD loves you (and me)']
yesno_text = ['Да', 'Нет', 'Вероятно']
help_text = 'Привет, я *amdpower_bot*. \n' \
            '1. Я буду здороваться со всеми пришедшими. \n' \
            '2. Я могу утвердительно отвечать на ваши вопросы, для этого просто задайте мне вопрос. \n' \
            '3. Я считаю сообщения в этом чатике. Чтобы узнать, сколько их, напиши мне /counter.'

global msg_counter
msg_counter = 0

def echo(bot, update_id):
        global msg_counter
        for update in bot.getUpdates(offset=update_id, timeout=10):
            chat_id = update.message.chat_id
            update_id = update.update_id + 1
            message = update.message.text
            new_chat_participant = update.message.new_chat_participant
            left_chat_participant = update.message.left_chat_participant
            if chat_id == GROUP:
                msg_counter += 1
                if new_chat_participant:
                    if new_chat_participant.first_name != BOTFIRSTNAME:
                        msg = "%s, *%s*!" % ( random.choice(welcome_text), new_chat_participant.first_name)
                        sendMessage(chat_id, msg)
                    elif new_chat_participant.first_name == BOTFIRSTNAME:
                        msg = help_text
                        sendMessage(chat_id, msg)
                # if bot is asked, it sends random answer from yesno_text
                elif (BOTNAME and "?") in message:
                    msg = "* %s *" % random.choice(yesno_text)
                    sendMessage(chat_id, msg)
                elif "/counter" in message:
                    msg = "*Сообщений, что я посчитал: %d*" % msg_counter
                    sendMessage(chat_id, msg)
                elif left_chat_participant.first_name == BOTFIRSTNAME:
                    msg_counter = 0
                else:
                    msg = "*Не понимаю, о чем ты сейчас.*"
                    sendMessage(chat_id, msg)
            else:
                msg = "Я *amdpower_bot*, и я отвечаю только в чате *[AMD POWER]*."
                sendMessage(chat_id, msg)

        return update_id

logging.basicConfig(level = logging.WARNING,filename=log_file,format='%(asctime)s:%(levelname)s - %(message)s')

def sendMessage(chat_id, msg):
    bot.sendMessage(chat_id, msg, parse_mode="Markdown")

bot = telegram.Bot(TOKEN)

def main(**args):

# initialization
    open(log_file, 'w').close()
    logging.warning('bot started...')

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
