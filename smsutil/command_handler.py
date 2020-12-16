import logging
from smsutil import cmd
from time import sleep


class CommandMiddleWare:
    def __init__(self, message=None, telegram_update=None, telegram_context=None):
        self.message = message
        self.telegram_bot = telegram_context.bot
        self.telegram_update = telegram_update
        self.msg_list = None
        self.cmd_dict = dict()
        self.gen_cmd_list()

    def send_message(self, msg=None):
        if not msg:
            # Empty message
            return
        logging.info("%s: %s" % (self.telegram_update.message.text, msg))
        self.telegram_bot.sendMessage(
            chat_id=self.telegram_update.message.chat_id, text=msg)

    def execute_cmd(self):
        msg = None  # message to be returned
        self.msg_list = self.message.text.split(' ')

        msg_cmd = self.msg_list.pop(0).lower()

        temp_cmd = self.cmd_dict.get(msg_cmd)

        if temp_cmd:
            msg = temp_cmd()
        else:
            msg = cmd.get_help_msg()
        return msg

    def execute(self):
        msg = self.execute_cmd()
        self.send_message(msg)

    def name_cmd(self):
        msg = cmd.get_bot_name(self.telegram_bot)
        return msg

    def status_cmd(self):
        msg = cmd.get_sms_process_info()
        return msg

    def reboot_cmd(self):
        if not self.msg_list:
            msg = "缺少参数. reboot pi?"
            return msg

        par = self.msg_list.pop(0).lower()
        if not par == 'pi':
            msg = "错误参数. reboot pi?"
            return msg

        msg = "重启raspberry pi"
        self.send_message(msg)
        result = cmd.reboot()  # reboot machine

        if not result == 0:
            # 执行命令直接返回错误
            msg = "重启raspberry pi失败"
            return msg
        # 如果成功重启，一下命令不会被执行
        sleep(5)
        msg = "重启raspberry pi失败"
        return msg

    def cmd_cmd(self):
        sys_cmd = " ".join(self.msg_list)

        if sys_cmd:
            try:
                msg = cmd.exec_cmd(sys_cmd)
            except Exception as e:
                msg = str(e)
        else:
            # empty command
            msg = "Empty command"

        return msg

    def gen_cmd_list(self):
        self.cmd_dict['name'] = self.name_cmd
        self.cmd_dict['status'] = self.status_cmd
        self.cmd_dict['reboot'] = self.reboot_cmd
        self.cmd_dict['cmd'] = self.cmd_cmd
