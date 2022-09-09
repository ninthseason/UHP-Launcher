# 版本相关界面
# 版本选择、版本添加
import asyncio

from prompt_toolkit.layout import ConditionalContainer, VSplit, HSplit, VerticalAlign, HorizontalAlign, DynamicContainer
from prompt_toolkit.widgets import Button, TextArea, Label

from core.VersionModule import available_versions
from core.VersionModule import version_table
from core.VersionModule.VersionSearch import VersionTable


class VersionMenu:
    """
    版本菜单，用于选择版本
    """
    def __init__(self, main_container):
        self.main_container = main_container

        self.return_btn = Button("Return", width=70, left_symbol="|", right_symbol="|",
                                 handler=self.main_container.switch_to(self.main_container.menu, self.main_container.main_menu.play_btn))
        self.version_buttons = []
        self.add_version_btn = Button("Add Version", width=70, left_symbol="|", right_symbol="|",
                                      handler=self.main_container.switch_to(self.main_container.add_version_menu, self.main_container.add_version.search_box))
        self.update_list()

        self.menu = ConditionalContainer(
            VSplit([HSplit([DynamicContainer(self.versions)], padding=0, align=VerticalAlign.CENTER)], align=HorizontalAlign.CENTER), False)

    def update_list(self):
        self.version_buttons = [self.return_btn]
        for i in available_versions:
            self.version_buttons.append(Button(text=i, width=70, left_symbol="|", right_symbol="|", handler=self.main_container.choose_version(i)))
        self.version_buttons.append(self.add_version_btn)

    def versions(self):
        return HSplit(self.version_buttons)


class VersionAddMenu:
    """
    版本添加菜单，用于添加版本

    仅下载<version>.json文件，不会下载游戏文件，游戏文件在启动游戏时检查并下载
    """
    def __init__(self, main_container):
        self.main_container = main_container

        self.versions = HSplit(children=[])
        self.search_box = TextArea(multiline=False, style="class:version-search-box")
        self.search_box.accept_handler = self.search
        self.menu = ConditionalContainer(VSplit([HSplit(
            [
                VSplit([Label("Input version id.    e.g 1.18"),
                        Button("Return", handler=self.main_container.switch_to(self.main_container.menu, self.main_container.main_menu.play_btn))]),
                self.search_box,
                DynamicContainer(lambda: self.versions)
            ],
            padding=0, align=VerticalAlign.CENTER)], align=HorizontalAlign.CENTER), False)

    def search(self, buffer):
        search_id = buffer.text

        versions: list[VersionTable.VersionManifest] = version_table.search(search_id)
        version_buttons = []
        for i, v in enumerate(versions):
            version_buttons.append(Button(v.id, width=70, handler=self.version_choose_handler(v)))
            if i >= 15:
                break
        self.versions = HSplit(children=version_buttons)

    def version_choose_handler(self, version_manifest):
        def handler():
            async def task():
                await version_manifest.download()
                self.main_container.version.update_list()

            if version_manifest.id not in available_versions:
                asyncio.get_event_loop().create_task(task())
            self.main_container.switch_to(self.main_container.menu, self.main_container.main_menu.play_btn)()

        return handler
