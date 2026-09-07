"""

YDITS for Twitter

Copyright (C) 2022-2026 よね/Yone
Licensed under the Apache License 2.0.

https://github.com/YDITS/YDITS-Twitter

"""

import asyncio
import datetime
import inspect
import json
from typing import Any

from requests_oauthlib import OAuth1Session

import ydits_twitter
from ydits_twitter import config
from ydits_twitter.database import Database
from ydits_twitter.api import kmoni, p2peqinfo, twitter


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

        self.client = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        print("\n>Waiting for EEW and earthquake information.", end="\n\n")

        asyncio.run(self.mainloop())

        return

    def connection_setup(
        self,
        *,
        consumer_key: str,
        consumer_secret: str,
    ) -> dict[str, str]:
        print("[INFO] アプリ連携が必要です。")

        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        request_token = twitter.RequestToken(oauth=oauth)
        tokens = request_token.get_token()
        if tokens is None:
            print("[ERROR] Consumer Key もしくは Consumer Secret Key が不正です。")
            exit()

        owner_key = tokens["oauth_token"]
        owner_secret = tokens["oauth_token_secret"]

        authorization = twitter.Authorization(oauth=oauth)
        authorization_url = authorization.get_url()
        print("下記の連携用URLにアクセスして，アプリ連携をしてください。")
        print(f"{authorization_url}")
        verifier = input("認証ボタンをクリック後，表示された認証PINコードを入力> ")

        get_access_token = twitter.AccessToken(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            owner_key=owner_key,
            owner_secret=owner_secret,
            verifier=verifier,
        )
        oauth_tokens = get_access_token.get_token()
        if oauth_tokens is None:
            exit()

        return oauth_tokens

    async def mainloop(self) -> None:
        while True:
            self.get_date()

            if self.cnt_getEew >= 1:
                eewData = await kmoni.get_eew(self.dateNow)

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
                        line=self.frame.f_lineno if self.frame is not None else 0,
                        errContent=eewData["data"],
                    )

                self.cnt_getEew = 0

            if self.cnt_getEqinfo >= 10:
                eqinfoData = await p2peqinfo.get_eqinfo()

                if eqinfoData["status"] == 0x0101:
                    self.eqinfo_id = eqinfoData["data"]["raw"][0]["id"]
                    if self.eqinfo_id_last != self.eqinfo_id:
                        self.upload(eqinfoData["data"]["text"], False)
                        self.eqinfo_id_last = self.eqinfo_id
                else:
                    self.error(
                        errCode=eqinfoData["status"],
                        line=self.frame.f_lineno if self.frame is not None else 0,
                        errContent=eqinfoData["data"],
                    )

                self.cnt_getEqinfo = 0

            self.cnt_getEew += 1
            self.cnt_getEqinfo += 1

            await asyncio.sleep(1)

    def error(self, errCode: int, line: int, errContent: object) -> None:
        date = self.dateNow.strftime("%Y/%m/%d %H:%M:%S")
        print(f"[ERROR]\n{date}; {hex(errCode)}; Line: {str(line)}\n{errContent}\n")
        return

    def get_date(self) -> None:
        self.dateNow = datetime.datetime.now()
        return

    def gotNewdata(self) -> None:
        date = self.dateNow.strftime("%Y/%m/%d %H:%M:%S")
        print(f"[LOG]\n{date}; Earthquake information was retrieved.")
        return

    def upload(self, content: str, eew_isFinal: bool) -> None:
        data: dict[str, str | dict[str, str]]
        if self.eew_tree != "":
            data = {"text": content, "reply": {"in_reply_to_tweet_id": self.eew_tree}}
        else:
            data = {"text": content}

        response = self.client.post("https://api.twitter.com/2/tweets", json=data)

        if response.status_code == 201:
            if eew_isFinal:
                self.eew_tree = ""
            else:
                response_data: dict[str, Any] = json.loads(response.text)
                self.eew_tree = response_data["data"]["id"]
            print("Successfully distributed.\n")
        else:
            self.error(
                errCode=0x0221,
                line=self.frame.f_lineno if self.frame is not None else 0,
                errContent=response.status_code,
            )

        return


def main() -> None:
    show_logo()

    try:
        database = Database(database_file=config.DATABASE_FILE_PATH)
        access_token = database.get_twitter_token(name="accessToken")
        access_tokenr_secret = database.get_twitter_token(name="accessTokenSecret")

    except Exception as error:
        print(f"[ERROR] データベースの読み込みに失敗しました。\n{error}")
        return

    if access_token:
        access_token = access_token[0][0]
    else:
        access_token = None

    if access_tokenr_secret:
        access_tokenr_secret = access_tokenr_secret[0][0]
    else:
        access_tokenr_secret = None

    YditsTwitter(
        consumer_key=config.TWITTER_API["CONSUMER_KEY"],
        consumer_secret=config.TWITTER_API["CONSUMER_SECRET"],
        access_token=access_token,
        access_token_secret=access_tokenr_secret,
        database=database,
    )


def show_logo() -> None:
    print(
        f"{ydits_twitter.__title__}  Ver. {ydits_twitter.__version__}\n"
        f"{ydits_twitter.__copyright__}\n\n"
        "--------------------------------\n"
    )


if __name__ == "__main__":
    main()
