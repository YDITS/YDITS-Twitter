"""

twitter.py | ydits_twitter/api | YDITS for Twitter

Copyright (c) 2022-2023 よね/Yone
licensed under the Apache License 2.0

"""

import requests_oauthlib
from requests_oauthlib import OAuth1Session


class RequestToken:
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"

    def __init__(self, *, oauth: OAuth1Session) -> None:
        self.oauth = oauth
        return None

    def get_token(self) -> None | dict:
        try:
            response = self.oauth.fetch_request_token(self.request_token_url)
        except ValueError:
            print(
                "[ERROR] There may have been an issue with the consumer_key or consumer_secret you entered."
            )
            return None

        return response


class Authorization:
    base_authorization_url = "https://api.twitter.com/oauth/authorize"

    def __init__(self, *, oauth: OAuth1Session) -> None:
        self.oauth = oauth
        return None

    def get_url(self) -> str:
        authorization_url = self.oauth.authorization_url(self.base_authorization_url)
        return authorization_url


class AccessToken:
    access_token_url = "https://api.twitter.com/oauth/access_token"

    def __init__(
        self,
        *,
        consumer_key: str,
        consumer_secret: str,
        owner_key: str,
        owner_secret: str,
        verifier: str
    ) -> None:
        self.oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=owner_key,
            resource_owner_secret=owner_secret,
            verifier=verifier,
        )

    def get_token(self) -> None | dict:
        try:
            oauth_tokens = self.oauth.fetch_access_token(self.access_token_url)

        except requests_oauthlib.oauth1_session.TokenRequestDenied:
            print("[ERROR] 認証PINコードが確認できませんでした。")
            return None

        else:
            print("[OK] 認証PINコードが確認できました。")

        return oauth_tokens
