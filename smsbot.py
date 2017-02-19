#!/usr/bin/python3
from __future__ import print_function
import sys
import telegram
import logging
import time

import config # import config file

from smsutil import SMS_CHECKER


# Copied from antoher as template, needs to be adapted
def logging_config(loggingfile):
    # configure logging, log data will be store with the same name.log under the same folder.

    FORMAT = '%(asctime)-15s %(name)s %(levelname)s: %(message)s'
    # logging.basicConfig(level=logging.INFO,filename=loggingfile, format=FORMAT)
    if loggingfile:
        logging.basicConfig(level=logging.DEBUG, filename=loggingfile, format=FORMAT)
        print('Logging file for is: %s' % loggingfile)
    else:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def sendSmsTelegram(text):
    # send text to telegram
    token = config.TOKEN
    bot = telegram.Bot(token=token)
    chat_id = config.CHAT_ID
    bot.sendMessage(chat_id=chat_id, text=text)
    logging.debug('SMS sent to telegram')

def main(sms_checker):
    all_sms = sms_checker.get_sms()

    if not all_sms:
        # print('No new messages', end='\r')
        return

    logging.debug('%d Message in inbox:\n%s' %(len(all_sms), all_sms))

    sent_sms = []
    for s in all_sms:
        try:
            text = s.get('text', '')
            print(text)
            logging.info(s.get('file', ''))
            logging.info('\n' + text)
        except Exception as e:
            err_info = 'error while getting %s. %s'%(s, e)
            print(err_info)
            logging.debug(err_info)
            sendSmsTelegram(err_info)
            exit(1)
        sendSmsTelegram(text)

        sent_sms.append(s)
    sms_checker.archieve(sent_sms)


def loop(break_time):
    logging.debug('Starting main loop')
    sendSmsTelegram('SMS service started ..')
    sms_checker = SMS_CHECKER()
    while True:
        main(sms_checker)
        time.sleep(break_time)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        loggingfile = sys.argv[1]
    else:
        loggingfile = ''
    logging_config(loggingfile)
    logging.debug('Script: %s init finished'% sys.argv[0])
    loop(0.5)

