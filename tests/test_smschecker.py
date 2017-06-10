from smschecker import get_time_sender, get_sms_from_file
import shutil
import os


def test_get_time_sender():
    # 'IN20151010_090133_00_10010_00.txt' --> ('2015.10.10 09:01:33', '10010')
    time, sender = get_time_sender('IN20151010_090133_00_10010_00.txt')
    assert time == '2015.10.10 09:01:33'
    assert sender == '10010'


def test_get_sms_from_file():
    tmp_file = 'IN20151010_090133_00_10010_00.txt'
    content = '消息'
    with open(tmp_file, 'w',encoding='utf-16') as f:
        f.write(content)

    ret = get_sms_from_file(tmp_file)

    time, sender = get_time_sender(tmp_file)

    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    assert ret == "时间: " + time + "\n" + "来自: " + sender + "\n" + content
