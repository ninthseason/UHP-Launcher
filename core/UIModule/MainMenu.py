# 主菜单
from prompt_toolkit.layout import ConditionalContainer, VSplit, HSplit, VerticalAlign, HorizontalAlign
from prompt_toolkit.widgets import Button

from core.ConfigModule import launcher_config


class MainMenu:
    def __init__(self):
        self.login_btn = Button(text=launcher_config.get("name"), width=40)
        self.version_btn = Button(text=launcher_config.get("version"), width=40)
        self.setting_btn = Button(text="Settings", width=40)
        self.play_btn = Button(text="Play", width=40)

        self.menu = ConditionalContainer(VSplit([HSplit([
            self.login_btn,
            self.version_btn,
            self.setting_btn,
            self.play_btn,
        ], padding=1, align=VerticalAlign.CENTER)], align=HorizontalAlign.CENTER), True)
