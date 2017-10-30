#!/usr/bin/python3
from __future__ import print_function
import sys
import telegram
import logging
import time
import threading

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
        self._bot = telegram.Bot(token=config.TOKEN)
        self._chat_id = config.CHAT_ID
        self._sms_checker = SMS_CHECKER()
        self._daemon_thread = None

    def send_sms_via_telegram(self, text):
        # send text to telegram
        self._bot.sendMessage(chat_id=self._chat_id, text=text)
        logging.info('SMS sent to telegram')

    def send_all_incoming_sms(self):
        all_sms = self._sms_checker.get_sms()

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
        self._sms_checker.archieve(sent_sms)

    def loop(self, interval):
        logging.info('Starting main loop')
        self.send_sms_via_telegram('SMS service started ..')
        while True:
            self.send_all_incoming_sms()
            time.sleep(interval)

    def start_daemon(self, interval=0.5):
        try:
            thread_is_alive = self._daemon_thread.is_alive()
        except:
            thread_is_alive = False

        if thread_is_alive:
            self.send_sms_via_telegram("SMS转发已经运行中!")
        else:
            self._daemon_thread = threading.Thread(target=self.loop, args=(interval,))
            self._daemon_thread.start()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        loggingfile = sys.argv[1]
    else:
        loggingfile = ''
    logging_config(loggingfile)
    logging.info('Script: %s init finished'% sys.argv[0])
    sms_forwarder = SmsForworder()
    sms_forwarder.loop(0.5)

