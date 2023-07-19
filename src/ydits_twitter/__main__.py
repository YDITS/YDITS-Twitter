"""

ydits_twitter.py | ydits_twitter | YDITS for Twitter

Copyright (c) 2022-2023 よね/Yone
licensed under the Apache License 2.0

"""

import asyncio
import datetime
import inspect
import json

from requests_oauthlib import OAuth1Session

from . import api
from ydits_twitter.database import Database


class YditsTwitter:
    def __init__(
        self,
        *,
        consumer_key: str,
        consumer_secret: str,
        access_token: None | str,
        access_token_secret: None | str,
        database: Database,
    ) -> None:
        self.get_date()

        self.frame = inspect.currentframe()

        self.eew_repNum = -1
        self.eew_repNum_last = -1
        self.eqinfo_id = -1
        self.eqinfo_id_last = -1
        self.eew_tree = ""
        self.cnt_getEew = 0
        self.cnt_getEqinfo = 0

        if (access_token is None) or (access_token_secret is None):
            oauth_tokens = self.connection_setup(
                consumer_key=consumer_key, consumer_secret=consumer_secret
            )
            access_token = oauth_tokens["oauth_token"]
            access_token_secret = oauth_tokens["oauth_token_secret"]
            database.set_twitter_token(name="accessToken", value=access_token)
            database.set_twitter_token(
                name="accessTokenSecret", value=access_token_secret
            )

        print(
            f"{consumer_key}\n"
            f"{consumer_secret}\n"
            f"{access_token}\n"
            f"{access_token_secret}"
        )

        self.client = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        print(">Waiting for EEW and earthquake information.\n")

        asyncio.run(self.mainloop())

        return None

    def connection_setup(self, *, consumer_key: str, consumer_secret: str) -> dict:
        print("[INFO] アプリ連携が必要です。")

        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        request_token = api.twitter.RequestToken(oauth=oauth)
        tokens = request_token.get_token()
        if tokens is None:
            print("[ERROR] Consumer Key もしくは Consumer Secret Key が不正です。")
            exit()

        owner_key = tokens.get("oauth_token")
        owner_secret = tokens.get("oauth_token_secret")

        authorization = api.twitter.Authorization(oauth=oauth)
        authorization_url = authorization.get_url()
        print("下記の連携用URLにアクセスして，アプリ連携をしてください。")
        print(f"{authorization_url}")
        verifier = input("認証ボタンをクリック後，表示された認証PINコードを入力> ")

        get_access_token = api.twitter.AccessToken(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            owner_key=owner_key,
            owner_secret=owner_secret,
            verifier=verifier,
        )
        oauth_tokens = get_access_token.get_token()

        return oauth_tokens

    async def mainloop(self) -> None:
        while True:
            self.get_date()

            if self.cnt_getEew >= 1:
                eewData = await api.kmoni.get_eew(self.dateNow)

                if eewData["status"] == 0x0101:
                    self.eew_repNum = eewData["data"]["raw"]["report_num"]
                    if (
                        self.eew_repNum_last != self.eew_repNum
                        and self.eew_repNum != ""
                        and eewData["data"]["raw"]["calcintensity"]
                        in ["3", "4", "5弱", "5強", "6弱", "6強", "7"]
                    ):
                        self.upload(
                            eewData["data"]["text"], eewData["data"]["raw"]["is_final"]
                        )
                        self.eew_repNum_last = self.eew_repNum
                else:
                    self.error(
                        errCode=eewData["status"],
                        line=self.frame.f_lineno,
                        errContent=eewData["data"],
                    )

                self.cnt_getEew = 0

            if self.cnt_getEqinfo >= 10:
                eqinfoData = await api.p2peqinfo.get_eqinfo()

                if eqinfoData["status"] == 0x0101:
                    self.eqinfo_id = eqinfoData["data"]["raw"][0]["id"]
                    if self.eqinfo_id_last != self.eqinfo_id:
                        self.upload(eqinfoData["data"]["text"], False)
                        self.eqinfo_id_last = self.eqinfo_id
                else:
                    self.error(
                        errCode=eqinfoData["status"],
                        line=self.frame.f_lineno,
                        errContent=eqinfoData["data"],
                    )

                self.cnt_getEqinfo = 0

            self.cnt_getEew += 1
            self.cnt_getEqinfo += 1

            await asyncio.sleep(1)

    def error(self, errCode, line, errContent) -> None:
        date = self.dateNow.strftime("%Y/%m/%d %H:%M:%S")
        print(f"[ERROR]\n{date}; {hex(errCode)}; Line: {str(line)}\n{errContent}\n")
        return None

    def get_date(self) -> None:
        self.dateNow = datetime.datetime.now()
        return None

    def gotNewdata(self) -> None:
        date = self.dateNow.strftime("%Y/%m/%d %H:%M:%S")
        print(f"[LOG]\n{date}; Earthquake information was retrieved.")
        return None

    def upload(self, content, eew_isFinal) -> None:
        if self.eew_tree != "":
            data = {"text": content, "repry": {"in_reply_to_tweet_id": self.eew_tree}}
        else:
            data = {"text": content}

        response = self.client.post("https://api.twitter.com/2/tweets", json=data)

        if response.status_code == 201:
            if eew_isFinal:
                self.eew_tree = ""
            else:
                data = json.loads(response.text)
                self.eew_tree = data["data"]["id"]
            print("Successfully distributed.\n")
        else:
            self.error(
                errCode=0x0221,
                line=self.frame.f_lineno,
                errContent=response.status_code,
            )

        return None
