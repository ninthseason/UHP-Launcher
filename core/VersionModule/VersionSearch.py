# 获取 Minecraft 版本信息
# https://launchermeta.mojang.com/mc/game/version_manifest.json
import asyncio
import pathlib

import httpx

from core.DownloadModule.AsyncDownloader import DownloadManager

version_json_folder = pathlib.Path("./versions")


class VersionTable:
    """
    版本总表，用于获取全部版本，提供搜索功能
    """
    def __init__(self, source="https://launchermeta.mojang.com/mc/game/version_manifest.json"):
        self.source = source
        self.version_table = None

    class VersionManifest:
        """
        版本条目，包含特定版本的信息，用于下载<version>.json
        """
        def __init__(self, _id: str = None, _type: str = None, url: str = None, time: str = None, release_time: str = None):
            self.id = _id
            self.type = _type
            self.url = url
            self.time = time
            self.release_time = release_time

        async def download(self):
            """
            下载 version.json

            :return:
            """
            if self.id is None:
                return
            file_path = version_json_folder.joinpath(f"{self.id}.json")
            await DownloadManager.download_no_bar(self.url, str(file_path))
            update_available_version()

        def __str__(self):
            return f"id: {self.id}\ntype: {self.type}\nurl: {self.url}\ntime: {self.time}\nrelease_time: {self.release_time}"

    async def fetch(self) -> dict:
        """
        获取 version manifest 总表

        :return: version manifest 总表
        """
        if self.version_table is not None:
            return self.version_table
        async with httpx.AsyncClient() as client:
            self.version_table = (await client.get(self.source)).json()['versions']
            return self.version_table

    def search(self, version_id: str) -> list["VersionTable.VersionManifest"]:
        """
        获取特定版本的 version manifest

        :param version_id: 版本号 如: 1.19.1-rc1 或 22w24a
        :return: VersionManifest 对象
        """
        return [VersionTable.VersionManifest(entry['id'], entry['type'], entry['url'], entry['time'], entry['releaseTime'])
                for entry in self.version_table if version_id in entry.get('id', '')]


version_table = VersionTable()
# asyncio.get_event_loop().create_task(version_table.fetch())
asyncio.run(version_table.fetch())

_version_json_folder = pathlib.Path("./versions")
if not _version_json_folder.exists():
    _version_json_folder.mkdir()


def update_available_version():
    available_versions.clear()
    for file in _version_json_folder.iterdir():
        if file.name[-5:] == ".json":
            available_versions.append(file.name[:-5])


available_versions = []
update_available_version()

if __name__ == '__main__':
    import asyncio


    async def main():
        v = VersionTable()
        await v.fetch()

        v_m = v.search("1.19.1")
        print(v_m)


    asyncio.run(main())
