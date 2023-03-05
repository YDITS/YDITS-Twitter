#
# main.py | YDITS for Twitter
#
# (c) 2022-2023 よね/Yone
# licensed under the Apache License 2.0
#
import datetime
import inspect
import json
import os
from time import sleep
import requests
from data.config import CLIENT, version
from module.kmoni import get_eew
from module.p2peqinfo import get_eqinfo
from requests_oauthlib import OAuth1Session


# ---------- Init ---------- #
def clearConsole():
    return os.system('cls' if os.name in ('nt', 'dos') else 'clear')


clearConsole()

print(
    f"YDITS for Twitter  Ver {version}\n" +
    f"(c) 2022-2023 よね/Yone\n\n" +
    f"--------------------\n"
)

frame = inspect.currentframe()

eew_repNum = -1
eew_repNum_last = -1
eqinfo_id = -1
eqinfo_id_last = -1
eew_tree = None
cnt_getEew = 0
cnt_getEqinfo = 0

print('>Waiting for EEW and earthquake information.\n')


# ---------- Functions ---------- #
def get_time():
    global DT
    DT = datetime.datetime.now()


def gotNewdata():
    global DT
    date = DT.strftime('%Y/%m/%d %H:%M:%S')
    print(f'[LOG]\n{date}; Earthquake information was retrieved.')


def upload(content, eew_isFinal):
    global eew_tree

    twitter = OAuth1Session(
        CLIENT['CONSUMER_KEY'], CLIENT['CONSUMER_SECRET'],
        CLIENT['ACCESS_TOKEN'], CLIENT['ACCESS_TOKEN_SECRET']
    )

    url = 'https://api.twitter.com/1.1/statuses/update.json'

    if eew_tree != "":
        params = {
            'status': content,
            'in_reply_to_status_id': eew_tree
        }
    else:
        params = {
            'status': content
        }

    res = twitter.post(url, params=params)

    if res.status_code == requests.codes.ok:
        if eew_isFinal:
            eew_tree = ""
        else:
            data = json.loads(res.text)
            eew_tree = data['id_str']
        print('Successfully distributed.\n')
    else:
        error(errCode=0x0221, line=frame.f_lineno, errContent=res.status_code)


def error(errCode, line, errContent):
    global DT
    date = DT.strftime('%Y/%m/%d %H:%M:%S')
    print(f'[ERROR]\n{date}; {hex(errCode)}; Line: {str(line)}\n{errContent}\n')
    return


# ---------- Mainloop ---------- #
while True:
    get_time()

    if cnt_getEew >= 1:
        eewData = get_eew(DT)

        if eewData['status'] == 0x0101:
            eew_repNum = eewData['data']['raw']['report_num']
            if eew_repNum_last != eew_repNum and eew_repNum != '' and eewData['data']['raw']['calcintensity'] in ['3', '4', '5弱', '5強', '6弱', '6強', '7']:
                upload(eewData['data']['text'],
                       eewData['data']['raw']['is_final'])
                eew_repNum_last = eew_repNum
        else:
            error(errCode=eewData['status'],
                  line=frame.f_lineno, errContent=eewData['data'])

        cnt_getEew = 0

    if cnt_getEqinfo >= 10:
        eqinfoData = get_eqinfo()

        if eqinfoData['status'] == 0x0101:
            eqinfo_id = eqinfoData['data']['raw'][0]['id']
            if eqinfo_id_last != eqinfo_id and eqinfo_id_last != -1:
                upload(eqinfoData['data']['text'], False)
                eqinfo_id_last = eqinfo_id
        else:
            error(errCode=eqinfoData['status'],
                  line=frame.f_lineno, errContent=eqinfoData['data'])

        cnt_getEqinfo = 0

    # cnt_getEew += 1
    cnt_getEqinfo += 1

    sleep(1)
