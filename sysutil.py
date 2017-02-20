import subprocess


def reboot():
    res = subprocess.check_call("sudo reboot")
    return res

def get_process_info(name):
    output = subprocess.check_output("ps aux | grep -v grep | grep %s"%name, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
    return output

def get_sms_process_info():
    gammu = get_process_info('gammu-smsd')
    gammu_check = get_process_info('gammu-check')
    smsutil = get_process_info('smsutil')

    return gammu + '\n' + gammu_check + '\n'  + smsutil

