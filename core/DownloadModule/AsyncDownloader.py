import asyncio
import json
import pathlib

import httpx
from tqdm.asyncio import tqdm


class DownloadManager:
    def __init__(self, download_table: dict = None, connections: int = 8):
        """
        协程下载管理器

        :param download_table: 下载表 {url: path, ...}
        :param connections: 最大连接数
        """
        if download_table is None:
            download_table = {}
        self.download_table: dict = download_table
        if connections <= 0:
            connections = 8
        self.connections = connections

    def submit(self, unit: dict) -> None:
        """
        向下载表中新增/更新若干条目

        :param unit: {url: path, ...}
        :return: None
        """
        self.download_table.update(unit)

    def clear(self) -> None:
        """
        清空下载表

        :return: None
        """
        self.download_table = {}

    async def start(self):
        """
        开始下载下载表中的内容，同时清空下载表
        """
        tasks = []
        for idx, (source, target) in enumerate(self.download_table.items()):
            tasks.append(self.download_unit(source, target))
            if idx % self.connections == 0:
                for _ in asyncio.as_completed(tasks):
                    await _
                tasks = []
        if len(tasks) > 0:
            for _ in asyncio.as_completed(tasks):
                await _
        self.clear()

    @staticmethod
    async def download_unit(source: str, target: str):
        """
        下载单元。用于创建一个协程下载对象。下载一个二进制文件。

        :param source: 文件url
        :param target: 保存地址
        """
        # TODO 需要优化。使一个AsyncClient负责下载多个文件，减少tcp握手次数，提高下载速度。
        # AsyncClient 是可以保持TCP连接的，请求服务器的多个资源无需重新握手
        # 现在对每个资源都开一个 AsyncClient，显然是很浪费的，且未利用到 AsyncClient 的优势
        if not pathlib.Path(target).parent.exists():
            pathlib.Path(target).parent.mkdir(parents=True)
        with open(target, "wb") as file:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", source) as response:
                    total = int(response.headers['Content-Length'])
                    with tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B") as progress:
                        num_bytes_downloaded = response.num_bytes_downloaded
                        async for chunk in response.aiter_bytes():
                            file.write(chunk)
                            progress.set_description(source)
                            progress.update(response.num_bytes_downloaded - num_bytes_downloaded)
                            num_bytes_downloaded = response.num_bytes_downloaded

    @staticmethod
    async def download_no_bar(source: str, target: str):
        """
        无进度条下载。用于下载文本文件。如 json

        因为 json 响应无 Content-Length 头部，无法判断大小，故无法使用进度条下载

        :param source: 文件url
        :param target: 保存地址
        """
        if not pathlib.Path(target).parent.exists():
            pathlib.Path(target).parent.mkdir(parents=True)
        with open(target, "w") as file:
            async with httpx.AsyncClient() as client:
                response = await client.get(source)
                json.dump(response.json(), file)


if __name__ == '__main__':
    async def main():
        download = DownloadManager({
            "http://ipv4.download.thinkbroadband.com/512MB.zip": f"test-{0}.zip",
            "http://ipv4.download.thinkbroadband.com/200MB.zip": f"test-{1}.zip",
            "http://ipv4.download.thinkbroadband.com/100MB.zip": f"test-{2}.zip",
        })
        await download.start()


    asyncio.run(main())
