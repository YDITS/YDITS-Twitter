#
# kmoni.py | ydits_twitter/module | YDITS for Twitter
#
# Copyright (c) 2022-2023 よね/Yone
# Licensed under the Apache License 2.0
#

import datetime
import json

import requests


def make_getNiedDT(DT):
    nideDate = DT + datetime.timedelta(seconds=-2)
    getNideDate = nideDate.strftime('%Y%m%d%H%M%S')
    return getNideDate


async def get_eew(DT):
    getNiedDate = make_getNiedDT(DT)
    url = f'https://www.lmoni.bosai.go.jp/monitor/webservice/hypo/eew/{getNiedDate}.json'

    try:
        res = requests.get(url)
    except Exception as e:
        return {'status': 0x0201, 'data': e}

    if res.status_code == requests.codes.ok:
        try:
            data = json.loads(res.text)
        except Exception as e:
            return {'status': 0x0202, 'data': e}
    elif res.status_code == 502:
        return {'status': 0x0000, 'data': None}
    else:
        return {'status': 0x0203, 'data': res.status_code}

    eew_time = data['origin_time']
    eew_timeYear = eew_time[0:4]
    eew_timeMonth = eew_time[4:6]
    eew_timeDay = eew_time[6:8]
    eew_timeHour = eew_time[8:10]
    eew_timeMinute = eew_time[10:12]
    eew_timeSecond = eew_time[12:14]

    eew_repNum = data['report_num']

    if eew_repNum != '':
        eew_repNum_put = f"第{eew_repNum}報"
    else:
        eew_repNum_put = ""

    if eew_repNum != '':
        eew_alertflg = data['alertflg']
    else:
        eew_alertflg = ''

    eew_isTraining = data['is_training']

    eew_isFinal = data['is_final']

    if eew_isFinal:
        eew_repNum_put = "最終報"

    eew_hypoName = data['region_name']

    if eew_hypoName == '':
        eew_hypoName = "不明"

    eew_maxInt = data['calcintensity']

    if eew_maxInt == '':
        eew_maxInt = "不明"

    eew_magunitude = data['magunitude']

    if eew_magunitude == '':
        eew_magunitude = "不明"
    else:
        eew_magunitude = f"M{eew_magunitude}"

    eew_depth = data['depth']

    if eew_depth == '':
        eew_depth = "不明"
    else:
        eew_depth = f"約{eew_depth}"

    return {
        'status': 0x0101,
        'data': {
            'raw': data,
            'text': f'【#緊急地震速報 ({eew_alertflg})  {eew_repNum_put}】\n' +
                    f'{eew_timeDay}日{eew_timeHour}時{eew_timeMinute}分頃\n' +
                    f'{eew_hypoName}を震源とする地震が発生しました。\n' +
                    f'最大震度は{eew_maxInt}程度、地震の規模は{eew_magunitude}程度、\n' +
                    f'震源の深さは{eew_depth}と推定されています。\n' +
                    '今後の情報に注意してください\n' +
                    '#地震 #地震速報'
        }
    }
