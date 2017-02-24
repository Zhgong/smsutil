#!/usr/bin/python3
from __future__ import print_function
import os
import logging
import re
import shutil


class SMS_CHECKER:
    def __init__(self):
        self.inbox = '/var/spool/gammu/inbox/'
        self.path_archieve = '/var/spool/gammu/archieve'

    def _get_sms_inbox_list(self):
        files = os.listdir(self.inbox)
        files.sort()

        abs_files = [os.path.join(self.inbox, f) for f in files]

        self.inbox_files = abs_files.copy()
        self.inbox_files.sort()
        if self.inbox_files:
            logging.info("inbox_files: %s" % self.inbox_files)

    def _move_to_archieve(self, file):
        if not os.path.exists(file):
            logging.info("file '%s' is not exists." % file)
            return

        # check if file is already exists in archieve
        file_base_name = os.path.basename(file)
        file_archieve = os.path.join(self.path_archieve, file_base_name)

        # if already exists remove file
        if os.path.exists(file_archieve):
            os.remove(file_archieve)

        # move file to 'archieve'
        shutil.move(file, self.path_archieve)

    def get_sms(self):
        sms = []
        self._get_sms_inbox_list()

        if not self.inbox_files:
            return []

        tmp_sms = dict()
        for f in self.inbox_files:
            tmp_sms['file'] = f
            tmp_sms['text'] = get_sms_from_file(f)
            sms.append(tmp_sms.copy())

        return sms

    def archieve(self,sms_list=[]):
        files = [i.get('file', '') for i in sms_list]

        if not files:
            return

        logging.info("Archieving files: %s" % files)
        for f in files:
            self._move_to_archieve(f)


def get_sms_from_file(file):
    # output:
    # 时间: 2015.10.10 09:01:33
    # 来自: 10010
    # 温馨提示：截止北京时间10月09日24时，您当日使用的国际漫游数据流量0.29MB、费用5.00元，本月累计使用国际漫游数据流量0

    sms = ''
    encoding = 'utf-16'
    # get time stamp and sender
    try:
        date_time, sender = get_time_sender(file)
        sms = '时间: ' + date_time + '\n'
        sms = sms + '来自: ' + sender + '\n'
    except Exception as e:
        logging.info('Error while getting time and sender: %s' % e)
        exit(1)

    # open file with 'utf-16' encoding
    logging.info('Opening file with %s format.' % encoding)

    try:
        with open(file, encoding=encoding) as f:
            text = f.readlines()
        sms += "".join(text)
        return sms
    except Exception as e:
        logging.info('Error while getting sms content: %s' % e)
        exit(1)


def get_time_sender(file):
    # 'IN20151010_090133_00_10010_00.txt' --> ('2015.10.10 09:01:33', '10010')
    timeSenderRegx = re.compile(r'IN(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})_\d{2}_(.*)_\d{2}')
    mo = timeSenderRegx.search(file)
    res = mo.groups()
    date = ".".join(res[0:3])
    time = ":".join(res[3:6])
    date_time = '%s %s' % (date, time)

    sender = res[6]
    return (date_time, sender)

if __name__ == '__main__':
    sms = SMS_CHECKER()
    sms.inbox = 'inbox'
    sms.path_archieve = 'archieve'
    all_sms = sms.get_sms()
    for s in all_sms:
        print(s)
    sms.archieve(all_sms)

