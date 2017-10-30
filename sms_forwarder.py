#!/usr/bin/python3
from __future__ import print_function
import sys
import telegram
import logging
import time

import config # import config file

from smschecker import SMS_CHECKER


# Copied from antoher as template, needs to be adapted
def logging_config(loggingfile):
    # configure logging, log data will be store with the same name.log under the same folder.

    FORMAT = '%(asctime)-15s %(filename)s %(lineno)d %(message)s'
    if loggingfile:
        logging.basicConfig(level=logging.DEBUG, filename=loggingfile, format=FORMAT)
        print('Logging file for is: %s' % loggingfile)
    else:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)


class SmsForworder:
    def __init__(self):
        self.bot = telegram.Bot(token=config.TOKEN)
        self.chat_id = config.CHAT_ID
        self.sms_checker = SMS_CHECKER()

    def send_sms_via_telegram(self, text):
        # send text to telegram
        self.bot.sendMessage(chat_id=self.chat_id, text=text)
        logging.info('SMS sent to telegram')

    def send_all_incoming_sms(self):
        all_sms = self.sms_checker.get_sms()

        if not all_sms:
            # print('No new messages', end='\r')
            return

        logging.info('%d Message in inbox:\n%s' %(len(all_sms), all_sms))

        sent_sms = []
        for s in all_sms:
            try:
                # text = s.get('text', '')
                text = s.text
                print(text)
                # logging.info(s.get('file', ''))
                logging.info(s.file)
                logging.info('\n' + text)
                self.send_sms_via_telegram(text)
                sent_sms.append(s) # append the sms file to list will be achieved later
            except Exception as e:
                err_info = 'error while getting %s. %s'%(s, e)
                print(err_info)
                logging.info(err_info)
                self.send_sms_via_telegram(err_info)
                # should it be an break?
                break
        self.sms_checker.archieve(sent_sms)

    def loop(self, interval):
        logging.info('Starting main loop')
        self.send_sms_via_telegram('SMS service started ..')
        while True:
            self.send_all_incoming_sms()
            time.sleep(interval)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        loggingfile = sys.argv[1]
    else:
        loggingfile = ''
    logging_config(loggingfile)
    logging.info('Script: %s init finished'% sys.argv[0])
    sms_forwarder = SmsForworder()
    sms_forwarder.loop(0.5)

