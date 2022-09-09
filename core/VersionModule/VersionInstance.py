import hashlib
import json
import os
import pathlib
import zipfile

from tqdm.asyncio import tqdm

from core.DownloadModule.AsyncDownloader import DownloadManager


class VersionInstance:
    def __init__(self, version_json: dict, root_path: str):
        self.version_json = version_json
        self.root_path = pathlib.Path(root_path).absolute()
        if not self.root_path.exists():
            self.root_path.mkdir()
        # 游戏库的下载地址和路径及文件哈希值
        self.mc_libraries_urls = []
        self.mc_libraries_paths = []
        self.mc_libraries_hashes = []
        # fabric库的下载地址和路径
        self.fabric_libraries_urls = []
        self.fabric_libraries_paths = []
        # 动态链接库的下载地址和路径
        self.dll_urls = []
        self.dll_paths = []
        self.dll_hashes = []
        # 游戏主文件的下载地址和路径
        self.client_url = version_json["downloads"]["client"]["url"]
        self.client_path = self.root_path.joinpath(version_json["id"] + ".jar").absolute()
        if not self.root_path.joinpath(version_json["id"] + ".json").exists():
            with self.root_path.joinpath(version_json["id"] + ".json").open("w") as f:
                json.dump(self.version_json, f)
        self.client_hash = version_json["downloads"]["client"]["sha1"]
        # natives路径
        self.nativesPath = self.root_path.joinpath(f"natives")
        # assets相关
        self.assetsPath = self.root_path.joinpath("assets")
        self.assetsVersion = version_json["assets"]
        self.assetsHash = version_json["assetIndex"]["sha1"]
        self.assetsUrl = version_json["assetIndex"]["url"]
        # 完成以上各种列表的装填
        for entry in version_json['libraries']:
            # 过滤为 用于windows的非动态链接库
            if (("downloads" in entry) and (len(entry["downloads"]) == 1)) and (("rules" not in entry) or (len(entry["rules"]) == 2)):
                self.mc_libraries_urls.append(entry["downloads"]["artifact"]["url"])
                self.mc_libraries_paths.append(str(self.root_path.joinpath("libraries/" + entry["downloads"]["artifact"]["path"])))
                self.mc_libraries_hashes.append(entry["downloads"]["artifact"]["sha1"])
            # 过滤为 用于windows的动态链接库
            elif ("downloads" in entry) and (len(entry["downloads"]) == 2) and (("rules" not in entry) or (len(entry["rules"]) == 2)):
                self.dll_urls.append(entry["downloads"]["classifiers"]["natives-windows"]["url"])
                self.dll_paths.append(str(self.root_path.joinpath("libraries/" + entry["downloads"]["classifiers"]["natives-windows"]["path"])))
                self.dll_hashes.append(entry["downloads"]["classifiers"]["natives-windows"]["sha1"])
            # 过滤为 fabric条目
            elif "downloads" not in entry:
                sep = entry['name'].split(":")  # 切分为 一半路径、文件名、版本号
                # secondPath - 次级地址，基于.minecraft的相对地址
                s_path = sep[0].replace('.', '/') + "/" + sep[1] + "/" + sep[2] + "/" + sep[1] + "-" + sep[2] + ".jar"
                self.fabric_libraries_paths.append(str(self.root_path.joinpath("libraries/" + s_path)))
                self.fabric_libraries_urls.append(entry["url"] + s_path)

    # 获取cp
    def get_cp(self) -> str:
        return "\"" + str(self.client_path) + ";" + ";".join(self.mc_libraries_paths) + ";" + ";".join(self.fabric_libraries_paths) + "\""

    # 获取游戏id
    def get_id(self) -> str:
        return f'"{self.version_json["id"]}"'

    # 获取assets索引（版本号）
    def get_assets_index(self) -> str:
        return self.assetsVersion

    # 返回游戏主类
    def get_main_class(self):
        return self.version_json["mainClass"]

    # 返回动态链接库路径
    def get_natives(self):
        return self.nativesPath

    async def check_file(self, auto_download: bool = False, check_hash: bool = True):
        # 不存在的文件
        nonexistent_files = []
        nonexistent_files_urls = []
        # 错误的文件
        wrong_files = []
        wrong_files_urls = []
        # 验证mc原版文件和动态链接库文件
        for path, fileHash, url in zip(self.mc_libraries_paths + self.dll_paths,
                                       self.mc_libraries_hashes + self.dll_hashes,
                                       self.mc_libraries_urls + self.dll_urls):
            # 验证存在性
            if os.path.isfile(path):
                # 验证hash
                if check_hash:
                    with open(path, "rb") as jar:
                        # 对比哈希值，若不匹配则记录
                        if hashlib.sha1(jar.read()).hexdigest() != fileHash:
                            wrong_files.append(path)
                            wrong_files_urls.append(url)
            # 不存在文件则直接记录
            else:
                nonexistent_files.append(path)
                nonexistent_files_urls.append(url)
        # 验证fabric文件 只能验证是否存在，无法验证hash值
        for path, url in zip(self.fabric_libraries_paths, self.fabric_libraries_urls):
            if not os.path.isfile(path):
                nonexistent_files.append(path)
                nonexistent_files_urls.append(url)

        # 自动下载模块
        if auto_download:
            # 创建下载器对象
            net_d = DownloadManager(dict(zip(nonexistent_files_urls + wrong_files_urls, nonexistent_files + wrong_files)))
            # 开始下载
            await net_d.start()
            self.extract_dll()

        return nonexistent_files, wrong_files

    # 游戏主文件验证及自动下载
    async def check_minecraft_client(self, auto_download: bool = False, check_hash: bool = True):
        # 验证存在
        res = True
        if os.path.isfile(self.client_path):
            # 验证hash
            if check_hash:
                with open(self.client_path, "rb") as jar:
                    if hashlib.sha1(jar.read()).hexdigest() != self.client_hash:
                        res = False
        else:
            res = False
        # 自动下载模块
        if not res and auto_download:
            await DownloadManager.download_unit(self.client_url, str(self.client_path))
        return res

    # 游戏资源文件索引验证及下载
    async def check_assets(self, auto_download: bool = False, check_hash: bool = True):
        path = self.assetsPath.joinpath("indexes/" + self.assetsVersion + ".json")
        # 验证存在
        res = True
        if os.path.isfile(path):
            # 验证hash
            if check_hash:
                with open(path, "rb") as Json:
                    if hashlib.sha1(Json.read()).hexdigest() != self.assetsHash:
                        res = False
        else:
            res = False
        # 自动下载模块
        if not res and auto_download:
            await DownloadManager.download_no_bar(self.assetsUrl, str(path))
        return res

    # 将dll从jar包中解压出来
    def extract_dll(self):
        for jar in self.dll_paths:
            with zipfile.ZipFile(jar) as Jar:
                for i in Jar.namelist():
                    if i[-4:] == ".dll":
                        Jar.extract(i, self.nativesPath)


class Assets:
    def __init__(self, index_path: str, root_path: str):
        # 读取索引json
        with open(index_path, "rb") as index:
            self.objects = json.load(index)["objects"]
        # 设置.minecraft根目录路径
        self.objectsPath = f"{root_path}/assets/objects"

    async def check_objects(self, auto_download: bool = False, check_hash: bool = True):
        nonexistent_files = []
        nonexistent_files_urls = []
        wrong_files = []
        wrong_files_urls = []

        with tqdm(total=len(self.objects)) as process:
            for i in self.objects:
                file_hash = self.objects[i]["hash"]
                # 基于objects的次级目录
                s_path = f"{file_hash[:2]}/{file_hash}"
                # 文件目录
                path = f"{self.objectsPath}/{s_path}"
                if os.path.isfile(path):
                    if check_hash:
                        with open(path, "rb") as file:
                            if hashlib.sha1(file.read()).hexdigest() != file_hash:
                                wrong_files.append(path)
                                wrong_files_urls.append(f"http://resources.download.minecraft.net/{s_path}")
                else:
                    nonexistent_files.append(path)
                    nonexistent_files_urls.append(f"http://resources.download.minecraft.net/{s_path}")
                process.update(1)
        if auto_download:
            # 创建下载器对象
            net_d = DownloadManager(dict(zip(nonexistent_files_urls + wrong_files_urls, nonexistent_files + wrong_files)))
            # 开始下载
            await net_d.start()

        return nonexistent_files, wrong_files
