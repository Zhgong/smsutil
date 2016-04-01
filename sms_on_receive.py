#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import telegram
import logging
import re
import shutil
import time

import config # import config file


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

def getSMSFromFile(file):

    # output:
    # 时间: 2015.10.10 09:01:33
    # 来自: 10010
    # 温馨提示：截止北京时间10月09日24时，您当日使用的国际漫游数据流量0.29MB、费用5.00元，本月累计使用国际漫游数据流量0

    sms = ''
    encoding = 'utf-16'
    # get time stamp and sender
    try:
        date_time, sender = getTimeSender(file)
        sms = '时间: ' + date_time + '\n'
        sms = sms + '来自: ' + sender + '\n'
    except Exception as e:
        logging.debug('Error while getting time and sender: %s' % e)
        exit(1)

    # open file with 'utf-16' encoding
    logging.debug('Opening file with %s format.' % encoding)

    with open(file, encoding=encoding) as f:
        text = f.readlines()
    sms += "".join(text)
    return sms


def sendSmsTelegram(text):
    # send text to telegram
    token = config.TOKEN
    bot = telegram.Bot(token=token)
    chat_id = config.CHAT_ID
    bot.sendMessage(chat_id=chat_id, text=text)
    logging.debug('SMS sent to telegram')


def getTimeSender(file):
    # 'IN20151010_090133_00_10010_00.txt' --> ('2015.10.10 09:01:33', '10010')
    timeSenderRegx = re.compile(r'IN(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})_\d{2}_(.*)_\d{2}')
    mo = timeSenderRegx.search(file)
    res = mo.groups()
    date = ".".join(res[0:3])
    time = ":".join(res[3:6])
    date_time = '%s %s'%(date, time)

    sender = res[6]
    return (date_time, sender)

def moveToArchieve(file):
    path_archieve = '/var/spool/gammu/archieve'
    # check if file is already exists
    file_base_name = os.path.basename(file)
    file_archieve = os.path.join(path_archieve, file_base_name)

    # if already exists remove file
    if os.path.exists(file_archieve):
        os.remove(file_archieve)

    # move file to 'archieve'
    shutil.move(file, path_archieve)
    
def getSMSinboxList():
    inbox = '/var/spool/gammu/inbox/'
    files = os.listdir(inbox)
    files.sort()
    absFile = []

    for f in files:
        absFile.append(os.path.join(inbox, f))
    
    # absFile.sort()
    return(absFile)   


def main():
    inboxFiles = getSMSinboxList()    

    if not inboxFiles:
        logging.debug('No new messages' + str(inboxFiles))
        # print('No new messages', end='\r')
        return


    for f in inboxFiles:
        try:
            text = getSMSFromFile(f)
            print(text)
            logging.info(f)
            logging.info('\n' + text)
        except Exception as e:
            err_info = 'error while getting %s. %s'%(f, e)
            print(err_info)
            logging.debug(err_info)
            sendSmsTelegram(err_info)
            exit(1)
        sendSmsTelegram(text)
     
        moveToArchieve(f)

if __name__ == '__main__':
    loggingfile = os.path.join('/var/log/', os.path.basename(__file__)) + '.log'
    logging_config(loggingfile)
    logging.debug('Script: %s init finished'% sys.argv[0])
    main()

