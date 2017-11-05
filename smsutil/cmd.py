import subprocess
import threading


def reboot():
    res = subprocess.check_call("sudo reboot", stderr=subprocess.STDOUT, shell=True)
    return res

def get_process_info(name):
    output = subprocess.check_output("ps aux | grep -v grep | grep %s"%name, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
    return output

def get_sms_process_info():
    gammu = get_process_info('gammu-smsd')
    gammu_check = get_process_info('gammu-check')
    smsutil = get_process_info('smsutil')

    return gammu + '\n' + gammu_check + '\n'  + smsutil

def exec_cmd(cmd):
    output = subprocess.check_output(str(cmd), stderr=subprocess.STDOUT, shell=True).decode('utf-8')
    return output

def get_daemon_info(thread):
    if isinstance(thread, threading.Thread):
        return thread.getName()
    else:
        return "No thread name."

def get_status(thread):
    process_info = get_sms_process_info()
    daemon_info = get_daemon_info(thread)

    return process_info + '/n' + daemon_info

def get_bot_name(bot, update):
    name = str(bot.get_me())
    return name


def get_help_msg():
    msg = "命令：\n"
    msg += "%s %s\n" %("/help", "查看帮助信息")
    msg += "%s %s\n" %("name", "查看bot名")
    msg += "%s %s\n" %("status", "查看状态信息")
    msg += "%s %s\n" %("reboot pi", "重启raspberry pi")
    msg += "%s %s\n" %("cmd xxx", "执行xxxm命令")
    return msg
