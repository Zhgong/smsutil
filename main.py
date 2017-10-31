from sms_forwarder import SmsForworder
from smsbot import Bot
from config import TOKEN

if __name__ == '__main__':

    print("start sms_monitor_thread")
    sms_forworder = SmsForworder()
    sms_forworder.start_daemon()

    print("start msg_bot")
    msg_bot = Bot(token=TOKEN)
    msg_bot.start()

    sms_forworder._daemon_thread.join()
    msg_bot._daemon_thread.join()
    print("exit")
