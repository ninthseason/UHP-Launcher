import json
import logging
import pathlib

import httpx
from tqdm import tqdm


class MicrosoftLogin:
    # https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf
    request_client = httpx.Client()

    class LoginInfo:
        def __init__(self, mine_token=None, uuid=None, name=None):
            self.cache_path = pathlib.Path("./cache/login.cache")
            self.mine_token = mine_token
            self.uuid = uuid
            self.name = name

        def save(self) -> "MicrosoftLogin.LoginInfo":
            with open(self.cache_path, "w") as file:
                json.dump({"mine_token": self.mine_token, "uuid": self.uuid, "name": self.name}, file)
            return self

        def load(self) -> "MicrosoftLogin.LoginInfo":
            if not self.cache_path.exists():
                logging.warning("未找到登录缓存文件，无法缓存登录，请手动登录")
                return self
            with open(self.cache_path, "r") as file:
                _: dict = json.load(file)
                self.mine_token = _.get("mine_token", "")
                self.uuid = _.get("uuid", "")
                self.name = _.get("name", "")
                return self

    @staticmethod
    def of(access_code: str, save=True) -> "MicrosoftLogin.LoginInfo":
        process_bar = tqdm(total=4)
        token = MicrosoftLogin.get_token_by_access_code(access_code)
        process_bar.update(1)
        xbl_token = MicrosoftLogin.xbl(token)
        process_bar.update(1)
        xsl_token, uhs = MicrosoftLogin.xsl(xbl_token)
        process_bar.update(1)
        mine_token = MicrosoftLogin.minecraft(xsl_token, uhs)
        process_bar.update(1)
        uuid, name = MicrosoftLogin.get_uuid(mine_token)
        if save:
            return MicrosoftLogin.LoginInfo(mine_token, uuid, name).save()
        else:
            return MicrosoftLogin.LoginInfo(mine_token, uuid, name)

    @staticmethod
    def with_cache() -> "MicrosoftLogin.LoginInfo":
        return MicrosoftLogin.LoginInfo().load()

    @staticmethod
    def get_token_by_access_code(i):
        context = {"client_id": "00000000402b5328",
                   "code": i,
                   "grant_type": "authorization_code",
                   "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
                   "scope": "service::user.auth.xboxlive.com::MBI_SSL"}

        response = MicrosoftLogin.request_client.post("https://login.live.com/oauth20_token.srf", data=context)
        # print(response.content)
        return response.json().get("access_token")

    @staticmethod
    def xbl(i):
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        context = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": i
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }
        response = MicrosoftLogin.request_client.post("https://user.auth.xboxlive.com/user/authenticate", json=context, headers=headers)
        # print(response.content)
        return response.json().get("Token")

    @staticmethod
    def xsl(i):
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        context = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    i
                ]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }
        response = MicrosoftLogin.request_client.post("https://xsts.auth.xboxlive.com/xsts/authorize", json=context, headers=headers)
        # print(response.content)
        response = response.json()
        return response.get("Token"), response.get("DisplayClaims").get("xui")[0].get("uhs")

    @staticmethod
    def minecraft(token, uhs):
        headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        context = {
            "identityToken": f"XBL3.0 x={uhs};{token}"
        }
        response = MicrosoftLogin.request_client.post("https://api.minecraftservices.com/authentication/login_with_xbox", json=context, headers=headers)
        # print(response.content)
        return response.json().get("access_token")

    @staticmethod
    def get_uuid(i):
        headers = {"Authorization": f"Bearer {i}"}
        res = MicrosoftLogin.request_client.get("https://api.minecraftservices.com/minecraft/profile", headers=headers)
        res = res.json()
        return res.get("id"), res.get("name")


if __name__ == '__main__':
    a = MicrosoftLogin.of("M.R3_BAY.57e045d0-603b-e140-d0d3-d96bdd99cc77")
    print(a)
