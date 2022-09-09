# 配置模块
# 提供全局配置信息和数据持久化

import pathlib

from . import BasicConfig

_config_folder = pathlib.Path("./config")
if not _config_folder.exists():
    _config_folder.mkdir()

jvm_config = BasicConfig.DynamicConfig("./config/jvmConfig.json")
jvm_config.load_default({
    'JavawPath': '',  # Java路径                          # 要引号
    'HeapDumpPath': '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump',  # 堆路径
    'DosName': '-Dos.name="Windows10"',  # 主机名 如windows10         # 要引号
    'DosVersion': '-Dos.version=10.0',  # 主机版本 如10.0
    'LibraryPath': '-Djava.library.path=',  # 库路径       # 要引号
    'cp': '-cp ',  # 所有依赖库                             # 要引号
    'Xmn': '-Xmn1024m',  # 最小内存
    'Xmx': '-Xmx2048m',  # 最大内存
    # 高级参数
    'UseG1GC': '-XX:+UseG1GC',
    'UseAdaptiveSizePolicy': '-XX:-UseAdaptiveSizePolicy',
    'OmitStackTraceInFastThrow': '-XX:-OmitStackTraceInFastThrow',
    'ignoreInvalidMinecraftCertificates': '-Dfml.ignoreInvalidMinecraftCertificates=True',
    'ignorePatchDiscrepancies': '-Dfml.ignorePatchDiscrepancies=True',
    # 固定项
    'LauncherBrand': '-Dminecraft.launcher.brand=UHP',
    'LauncherVersion': '-Dminecraft.launcher.version=001',
})

minecraft_config = BasicConfig.DynamicConfig("./config/minecraftConfig.json")
minecraft_config.load_default({
    'launcher': '',  # 主类入口点
    'username': '',  # 用户名
    'version': '',  # 游戏版本    # 要引号
    'gameDir': '',  # 游戏目录 version文件夹内的游戏文件夹   # 要引号
    'assetsDir': '',  # 资源路径 .minecraft文件夹内   # 要引号
    'assetIndex': '',  # 资源索引
    'uuid': '',
    'accessToken': '',
    'userType': 'Legacy',  # 用户类型 （不知道是什么玩意）
    'width': '854',  # 窗口宽
    'height': '480',  # 窗口高
    # 固定项
    'versionType': '--versionType UHP',
})

launcher_config = BasicConfig.DynamicConfig("./config/launcher.config")
launcher_config.load_default({
    "agreement_remind": True,
    "mine_token": "",
    "uuid": "",
    "name": "Login",
    "version": "Version"
})
