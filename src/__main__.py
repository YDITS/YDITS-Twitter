"""

__main__.py | YDITS for Twitter

Copyright (c) 2022-2023 YDITS, よね/Yone
Licensed under the Apache License 2.0

"""

import os

import ydits_twitter
from data import config
from ydits_twitter.database import Database


class App:
    def __init__(self) -> None:
        self.clear_console()

        print(
            f"{ydits_twitter.__title__}\n"
            f"{ydits_twitter.__copyright__}\n\n"
            "--------------------\n"
        )

        try:
            database = Database(database_file=config.DATABASE_FILE_PATH)
            access_token = database.get_twitter_token(name="accessToken")
            access_tokenr_secret = database.get_twitter_token(name="accessTokenSecret")

        except Exception as error:
            print(f"[ERROR] データベースの読み込みに失敗しました。\n{error}")
            return None

        if (access_token is not None) and (access_token != []):
            access_token = access_token[0][0]
        else:
            access_token = None

        if (access_tokenr_secret is not None) and (access_tokenr_secret != []):
            access_tokenr_secret = access_tokenr_secret[0][0]
        else:
            access_tokenr_secret = None

        ydits_twitter.YditsTwitter(
            consumer_key=config.TWITTER_API["consumerKey"],
            consumer_secret=config.TWITTER_API["consumerSecret"],
            access_token=access_token,
            access_token_secret=access_tokenr_secret,
            database=database,
        )

        return None

    def clear_console(self) -> int:
        if os.name in ("nt", "dos"):
            return os.system(command="cls")
        else:
            return os.system(command="clear")


if __name__ == "__main__":
    App()
