# coding=utf-8
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from time import sleep
import threading
import telegram
import requests
from config import TOKEN, CHAT_ID
from sms_monitor import loop
import sys
import syscmd

# Todo: doesn't work under main function
logging.basicConfig(format="%(asctime)-15s %(filename)s %(message)s",level=logging.INFO)

ALLOWED_ID =CHAT_ID# chat_id of 01726060309

def sendMsgTelegram(text):
    # send text to telegram
    token = TOKEN
    bot = telegram.Bot(token=token)
    chat_id = ALLOWED_ID
    bot.sendMessage(chat_id=chat_id, text=text)

def authorize(allowed_id):
    logging.info("Authorize: %s" % allowed_id)

    # function decorator
    def func_deco(func):
        logging.info("Wrapper Decorating function: %s" % func.__name__)

        # function wrapper
        def check_id(bot, update, *args, **kwargs):
            message = update.message
            chat_id = message.chat_id
            if chat_id == allowed_id:
                func(bot, update, *args, **kwargs)
            else:
                bot.sendMessage(chat_id=message.chat_id, text="Do I know you?")
        return check_id
    return func_deco

@authorize(ALLOWED_ID)
def help(bot, update):
    message = update.message
    msg = "命令：\n"
    msg += "%s %s\n" %("/help", "查看帮助信息")
    msg += "%s %s\n" %("name", "查看bot名")
    msg += "%s %s\n" %("status", "查看状态信息")
    msg += "%s %s\n" %("reboot pi", "重启raspberry pi")
    bot.sendMessage(chat_id=message.chat_id, text=msg)


@authorize(ALLOWED_ID)
def unkown(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text="Unkown command")
    help(bot, update)

@authorize(ALLOWED_ID)
def message_reactor(bot, update):
    # handles all the message received from client
    message = update.message
    msg_list = message.text.lower().split(' ')

    cmd = msg_list.pop(0)

    if cmd == 'name':
        get_bot_name(bot, update)

    elif cmd == 'status':
        msg = syscmd.get_sms_process_info()
        logging.info(msg)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    elif cmd == 'reboot':
        if not msg_list:
            msg = "缺少参数. reboot pi?"
            bot.sendMessage(chat_id=update.message.chat_id, text=msg)
            return

        par = msg_list.pop(0)
        if not par == 'pi':
            msg = "错误参数. reboot pi?"
            bot.sendMessage(chat_id=update.message.chat_id, text=msg)
            return

        msg = "重启raspberry pi"
        logging.info(msg)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
        result =  syscmd.reboot() # reboot machine

        if not result == 0:
            # 执行命令直接返回错误
            msg = "重启raspberry pi失败"
            bot.sendMessage(chat_id=update.message.chat_id, text=msg)
            return
        # 如果成功重启，一下命令不会被执行
        sleep(5)
        msg = "重启raspberry pi失败"
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    else:
        help(bot, update)


def get_bot_name(bot, update):
    name = str(bot.get_me())
    logging.info("%s: %s" % (update.message.text,name))
    bot.sendMessage(chat_id=update.message.chat_id, text=name)


class Bot:
    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token=token)
        self.is_network_ok = False
        self.is_network_ok_last_time = False
        self.status = {
            'is_network_ok': False,
            'is_network_ok_last_time': False,
                       }

    def main(self):

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

        # network works well
        # self.check_network_loop()

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
            if self.status['is_network_ok'] and not self.status['is_network_ok_last_time']:
                sendMsgTelegram('短信转发程序在线')
            sleep(5)

if __name__ == '__main__':
    # print("start program")
    # if len(sys.argv) == 2:
    #     loggingfile = sys.argv[1]
    # else:
    #     loggingfile = ''
    # logging_config(loggingfile)

    print("start sms_monitor_thread")
    sms_monitor_thread = threading.Thread(target=loop, args=(0.5,))  # create a new thread
    sms_monitor_thread.start()  # start the thread

    print("start msg_bot")
    msg_bot = Bot(token=TOKEN)
    msg_bot.main()

    print("working ...")
    sms_monitor_thread.join()
    print("exit")
