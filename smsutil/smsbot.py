# coding=utf-8
import logging
import threading
from time import sleep

import requests
import telegram
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from config import TOKEN, CHAT_ID
from .utils import authorize
from .command_handler import CommandMiddleWare
from smsutil import cmd


ALLOWED_ID =CHAT_ID# chat_id of 01726060309

@authorize(ALLOWED_ID)
def help(telegram_update, telegram_context):
    message = telegram_update.message
    msg = cmd.get_help_msg()
    telegram_context.bot.sendMessage(chat_id=message.chat_id, text=msg)


@authorize(ALLOWED_ID)
def unkown(telegram_update, telegram_context):
    message = telegram_update.message
    telegram_context.bot.sendMessage(chat_id=message.chat_id, text="Unkown command")
    help(telegram_update, telegram_context)

@authorize(ALLOWED_ID)
def message_reactor(telegram_update, telegram_context):
    # handles all the message received from client
    message = telegram_update.message
    cmd = CommandMiddleWare(message, telegram_update, telegram_context)
    cmd.execute()


class Bot:
    def __init__(self, token):
        self.token = token
        self.is_network_ok = False
        self.is_network_ok_last_time = False
        self.status = {
            'is_network_ok': False,
            'is_network_ok_last_time': False,
                       }
        self.init = False

        # create telegram bot
        self._telegram_bot = telegram.Bot(token=token)
        self._chat_id = ALLOWED_ID
        self._daemon_thread = None
        self._msg_updater = None

    def start(self):

        self.start_updater()

        # network works well
        self.start_check_loop_daemon()

    def start_updater(self):
        updater = Updater(token=self.token)

        dispatcher = updater.dispatcher

        # echo handler
        msg_handler = MessageHandler(Filters.text, message_reactor)
        dispatcher.add_handler(msg_handler)

        # help handler
        help_handler = CommandHandler('help', help)
        dispatcher.add_handler(help_handler)

        # handler for unkown command
        unkown_handler = MessageHandler(Filters.command, unkown)
        dispatcher.add_handler(unkown_handler)

        logging.info("Start polling in bot")
        updater.start_polling()

        self._msg_updater = updater

    def check_network(self):
        self.status['is_network_ok_last_time'] = self.status['is_network_ok']
        try:
            res = requests.get("http://www.google.com")
            self.status['is_network_ok'] = True
            self.status['off_line_count'] = 0
        except requests.ConnectionError as e:
            logging.info("Network Error.")
            self.status['off_line_count'] = self.status.get('off_line_count', 0) + 1
            logging.info("off_line_count: %d" % self.status.get('off_line_count'))

            if self.status['off_line_count'] >3:
                self.status['is_network_ok'] = False

    def check_network_loop(self):
        while True:
            self.check_network()
            if self.init:
                if self.status['is_network_ok'] and not self.status['is_network_ok_last_time']:
                    self.send_sms_via_telegram('短信转发程序网络OK')
            else:
                self.init = True
            sleep(5)

    def send_sms_via_telegram(self, text):
        # send text to telegram
        self._telegram_bot.sendMessage(chat_id=self._chat_id, text=text)

    def start_check_loop_daemon(self):
        try:
            thread_is_alive = self._daemon_thread.is_alive()
        except:
            thread_is_alive = False

        if thread_is_alive:
            self.send_sms_via_telegram("Check network has already been started!")
        else:
            self._daemon_thread = threading.Thread(target=self.check_network_loop, args=())
            self._daemon_thread.setName("Check network")
            self._daemon_thread.start()

if __name__ == '__main__':

    print("start sms_monitor_thread")

    print("start msg_bot")
    msg_bot = Bot(token=TOKEN)
    msg_bot.start()

    msg_bot._daemon_thread.join()
    print("exit")
