import logging
from smsutil import syscmd
from time import sleep

def get_bot_name(bot, update):
    name = str(bot.get_me())
    logging.info("%s: %s" % (update.message.text,name))
    bot.sendMessage(chat_id=update.message.chat_id, text=name)

class CommandHandler:
    def __init__(self, message=None):
        self.message = message

    def execute(self,telegram_bot, telegram_update):
        msg_list = self.message.text.split(' ')

        cmd = msg_list.pop(0).lower()

        if cmd == 'name':
            get_bot_name(telegram_bot, telegram_update)

        elif cmd == 'status':
            msg = syscmd.get_sms_process_info()
            logging.info(msg)
            telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)
        elif cmd == 'reboot':
            if not msg_list:
                msg = "缺少参数. reboot pi?"
                telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)
                return

            par = msg_list.pop(0).lower()
            if not par == 'pi':
                msg = "错误参数. reboot pi?"
                telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)
                return

            msg = "重启raspberry pi"
            logging.info(msg)
            telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)
            result =  syscmd.reboot() # reboot machine

            if not result == 0:
                # 执行命令直接返回错误
                msg = "重启raspberry pi失败"
                telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)
                return
            # 如果成功重启，一下命令不会被执行
            sleep(5)
            msg = "重启raspberry pi失败"
            telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)

        elif cmd == 'cmd':
            sys_cmd = " ".join(msg_list)

            if sys_cmd:
                try:
                    msg = syscmd.exec_cmd(sys_cmd)
                except Exception as e:
                    msg = str(e)
            else:
                # empty command
                msg = "Empty command"
            telegram_bot.sendMessage(chat_id=telegram_update.message.chat_id, text=msg)

        else:
            help(telegram_bot, telegram_update)
