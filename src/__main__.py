#
# __main__.py | YDITS for Twitter
#
# (c) 2022-2023 よね/Yone
# Licensed under the Apache License 2.0
#

import datetime
import inspect
import json
import os
from time import sleep
import requests
from data.config import VERSION, TWITTER_API
from module.kmoni import get_eew
from module.p2peqinfo import get_eqinfo
from requests_oauthlib import OAuth1Session


class YditsTwitter:
    def __init__(self):
        clearConsole()

        print(
            f"YDITS for Twitter  Ver {VERSION}\n" +
            f"(c) 2022-2023 よね/Yone\n\n" +
            f"--------------------\n"
        )

        self.get_date()

        self.frame = inspect.currentframe()

        self.eew_repNum = -1
        self.eew_repNum_last = -1
        self.eqinfo_id = -1
        self.eqinfo_id_last = -1
        self.eew_tree = ""
        self.cnt_getEew = 0
        self.cnt_getEqinfo = 0

        self.twitterClient = OAuth1Session(
            TWITTER_API['CLIENT']['CONSUMER_KEY'], TWITTER_API['CLIENT']['CONSUMER_SECRET'],
            TWITTER_API['CLIENT']['ACCESS_TOKEN'], TWITTER_API['CLIENT']['ACCESS_TOKEN_SECRET']
        )

        print('>Waiting for EEW and earthquake information.\n')

        self.mainloop()


    def mainloop(self):
        while True:
            self.get_date()

            if self.cnt_getEew >= 1:
                eewData = get_eew(self.dateNow)

                if eewData['status'] == 0x0101:
                    self.eew_repNum = eewData['data']['raw']['report_num']
                    if self.eew_repNum_last != self.eew_repNum and self.eew_repNum != '' and eewData['data']['raw']['calcintensity'] in ['3', '4', '5弱', '5強', '6弱', '6強', '7']:
                        self.upload(eewData['data']['text'], eewData['data']['raw']['is_final'])
                        self.eew_repNum_last = self.eew_repNum
                else:
                    self.error(errCode=eewData['status'], line=self.frame.f_lineno, errContent=eewData['data'])

                self.cnt_getEew = 0

            if self.cnt_getEqinfo >= 10:
                eqinfoData = get_eqinfo()

                if eqinfoData['status'] == 0x0101:
                    self.eqinfo_id = eqinfoData['data']['raw'][0]['id']
                    if self.eqinfo_id_last != self.eqinfo_id and self.eqinfo_id_last != -1:
                        self.upload(eqinfoData['data']['text'], False)
                        self.eqinfo_id_last = self.eqinfo_id
                else:
                    self.error(errCode=eqinfoData['status'], line=self.frame.f_lineno, errContent=eqinfoData['data'])

                self.cnt_getEqinfo = 0

            self.cnt_getEew += 1
            self.cnt_getEqinfo += 1

            sleep(1)


    def error(self, errCode, line, errContent):
        date = self.dateNow.strftime('%Y/%m/%d %H:%M:%S')
        print(f'[ERROR]\n{date}; {hex(errCode)}; Line: {str(line)}\n{errContent}\n')
        return


    def get_date(self):
        self.dateNow = datetime.datetime.now()
        return


    def gotNewdata(self):
        date = self.dateNow.strftime('%Y/%m/%d %H:%M:%S')
        print(f'[LOG]\n{date}; Earthquake information was retrieved.')
        return


    def upload(self, content, eew_isFinal):
        if self.eew_tree != "":
            params = {
                'status': content,
                'in_reply_to_status_id': self.eew_tree
            }
        else:
            params = {
                'status': content
            }

        res = self.twitterClient.post(TWITTER_API['URL'], params=params)

        if res.status_code == requests.codes.ok:
            if eew_isFinal:
                self.eew_tree = ""
            else:
                data = json.loads(res.text)
                self.eew_tree = data['id_str']
            print('Successfully distributed.\n')
        else:
            self.error(errCode=0x0221, line=self.frame.f_lineno, errContent=res.status_code)
        
        return


def clearConsole():
    return os.system('cls' if os.name in ('nt', 'dos') else 'clear')


if __name__ == "__main__":
    YditsTwitter()
