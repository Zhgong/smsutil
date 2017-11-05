import logging
from smsutil import cmd
from time import sleep


class CommandMiddleWare:
    def __init__(self, message=None, telegram_bot=None, telegram_update=None):
        self.message = message
        self.telegram_bot = telegram_bot
        self.telegram_update = telegram_update

    def send_message(self, msg=None):
        if not msg:
            # Empty message
            return
        logging.info("%s: %s" % (self.telegram_update.message.text,msg))
        self.telegram_bot.sendMessage(chat_id=self.telegram_update.message.chat_id, text=msg)

    def execute_cmd(self):
        msg = None # message to be returned
        msg_list = self.message.text.split(' ')

        msg_cmd = msg_list.pop(0).lower()

        if msg_cmd == 'name':
            msg = cmd.get_bot_name(self.telegram_bot, self.telegram_update)

        elif msg_cmd == 'status':
            msg = cmd.get_sms_process_info()
        elif msg_cmd == 'reboot':
            if not msg_list:
                msg = "缺少参数. reboot pi?"
                return msg

            par = msg_list.pop(0).lower()
            if not par == 'pi':
                msg = "错误参数. reboot pi?"
                return msg

            msg = "重启raspberry pi"
            self.send_message(msg)
            result =  cmd.reboot() # reboot machine

            if not result == 0:
                # 执行命令直接返回错误
                msg = "重启raspberry pi失败"
                return msg
            # 如果成功重启，一下命令不会被执行
            sleep(5)
            msg = "重启raspberry pi失败"

        elif msg_cmd == 'cmd':
            sys_cmd = " ".join(msg_list)

            if sys_cmd:
                try:
                    msg = cmd.exec_cmd(sys_cmd)
                except Exception as e:
                    msg = str(e)
            else:
                # empty command
                msg = "Empty command"

        else:
            msg = cmd.get_help_msg()
        return msg

    def execute(self):
            msg = self.execute_cmd()
            self.send_message(msg)
