from smschecker import get_time_sender


def test_get_time_sender():
    # 'IN20151010_090133_00_10010_00.txt' --> ('2015.10.10 09:01:33', '10010')
    time, sender = get_time_sender('IN20151010_090133_00_10010_00.txt')
    assert time == '2015.10.10 09:01:33'
    assert sender == '10010'
