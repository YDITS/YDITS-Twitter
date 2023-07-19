#
# database.py | ydits_twitter | YDITS for Twitter
#
# Copyright (c) 2022-2023 よね/Yone
# licensed under the Apache License 2.0
#

import sqlite3


class Database:
    """データベース操作クラス"""

    def __init__(self, *, database_file: str) -> None:
        """
        Args:
            database_file (str): 使用するデータベースのファイルパス名
        """
        self.database_file = database_file
        self.create_table()
        return None

    def connect(self) -> sqlite3.Connection:
        """データベース接続"""
        return sqlite3.connect(self.database_file)

    def cursor(self, *, connect: sqlite3.Connection) -> sqlite3.Cursor:
        """データベースカーソルインスタンスを生成"""
        return connect.cursor()

    def save(self, *, connect: sqlite3.Connection) -> None:
        """データベース保存

        データベース操作内容のコミットおよびクローズを行う
        """
        connect.commit()
        connect.close()
        return None

    def create_table(self) -> None:
        """データベースのテーブル作成"""
        db_con = self.connect()
        db_cur = self.cursor(connect=db_con)
        db_cur.execute("CREATE TABLE IF NOT EXISTS twitterApiConfig(name, value)")
        self.save(connect=db_con)
        return None

    def get_twitter_token(self, *, name: str) -> list:
        db_con = self.connect()
        db_cur = self.cursor(connect=db_con)
        db_cur.execute(f"SELECT value FROM twitterApiConfig WHERE name=?", (name,))
        data = db_cur.fetchall()
        self.save(connect=db_con)
        return data

    def set_twitter_token(self, *, name: str, value: str) -> None:
        db_con = self.connect()
        db_cur = self.cursor(connect=db_con)
        db_cur.execute("INSERT INTO twitterApiConfig VALUES(?, ?)", (name, value))
        self.save(connect=db_con)
        return None
