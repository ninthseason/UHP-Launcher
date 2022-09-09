# 主容器
# 包含所有用到的界面
# 负责界面的切换和部分按钮的回调
import asyncio
import json
import os
import pathlib
import subprocess

from prompt_toolkit import Application
from prompt_toolkit.filters.utils import to_filter
from prompt_toolkit.layout import VSplit

from core.ConfigModule import launcher_config, jvm_config, minecraft_config
from core.LoginModule.MicrosoftLogin import MicrosoftLogin
from core.StartupModule.Startup import start_up_script
from core.VersionModule.VersionInstance import VersionInstance, Assets
from .LoginDialog import LoginDialog
from .MainMenu import MainMenu
from .VersionMenu import VersionMenu, VersionAddMenu


# TODO 需要重构
class ApplicationContainer:
    def __init__(self):
        self.app = None

        self.main_menu = MainMenu()
        self.menu = self.main_menu.menu

        self.login = LoginDialog()
        self.login.ok_btn.handler = self.login_new_account
        self.login.cancel_btn.handler = self.switch_to(self.menu, self.main_menu.play_btn)
        self.main_menu.login_btn.handler = self.switch_to(self.login.dialog, self.login.textarea)

        self.add_version = VersionAddMenu(self)
        self.add_version_menu = self.add_version.menu

        self.version = VersionMenu(self)
        self.version_menu = self.version.menu
        self.main_menu.version_btn.handler = self.switch_to(self.version_menu, self.version.return_btn)

        self.main_menu.setting_btn.handler = lambda: os.system("explorer.exe %s" % pathlib.Path("./config").absolute())
        self.main_menu.play_btn.handler = self.startup

        self.container = VSplit([self.menu, self.login.dialog, self.version_menu, self.add_version_menu])
        self.default_focus = self.main_menu.play_btn

    def hide_all(self):
        for i in self.container.children:
            i.filter = to_filter(False)

    @staticmethod
    def show(widget):
        widget.filter = to_filter(True)

    def login_new_account(self):
        access_code = self.login.textarea.text
        access_code = access_code.strip()
        if access_code != "":
            login_info = MicrosoftLogin.of(access_code)
            self.main_menu.login_btn.text = login_info.name
            launcher_config.set("name", login_info.name)
            launcher_config.set("uuid", login_info.uuid)
            launcher_config.set("mine_token", login_info.mine_token)
        self.switch_to(self.menu, self.main_menu.play_btn)()
        # self.app.reset()

    def choose_version(self, version):
        def handle():
            launcher_config.set("version", version)
            self.main_menu.version_btn.text = version
            self.switch_to(self.menu, self.main_menu.play_btn)()

        return handle

    @staticmethod
    def startup():
        version_id = launcher_config.get('version')
        with pathlib.Path(f"./versions/{version_id}.json").open("r") as f:
            version_json = VersionInstance(json.load(f), f"./instances/{version_id}/")

            async def check_and_download_and_start():
                await version_json.check_file(True, True)
                await version_json.check_file(True, True)
                await version_json.check_minecraft_client(True, True)
                await version_json.check_assets(True, True)
                assets = Assets(f"./instances/{version_id}//assets/indexes/{version_json.get_assets_index()}.json", f"./instances/{version_id}/")
                await assets.check_objects(True, True)

                jvm_config.set("LibraryPath", f"-Djava.library.path={version_json.get_natives()}")
                jvm_config.set("cp", f"-cp {version_json.get_cp()}")
                minecraft_config.set("launcher", version_json.get_main_class())
                minecraft_config.set("version", f"--version {version_json.get_id()}")
                minecraft_config.set("gameDir", f'--gameDir "./instances/{version_id}"')
                minecraft_config.set("assetsDir", f'--assetsDir "./instances/{version_id}/assets"')
                minecraft_config.set("assetIndex", f"--assetIndex {version_json.get_assets_index()}")
                minecraft_config.set("uuid", f'--uuid {launcher_config.get("uuid")}')
                minecraft_config.set("accessToken", f'--accessToken {launcher_config.get("mine_token")}')
                print("游戏启动中，请耐心等候")
                subprocess.Popen(start_up_script())

            asyncio.get_event_loop().create_task(check_and_download_and_start())

    def switch_to(self, window, focus) -> callable:
        def switch():
            self.hide_all()
            self.show(window)
            self.app.layout.focus(focus)

        return switch

    def set_app(self, app: Application):
        self.app = app
