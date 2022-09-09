# 游戏版本模块
# 版本搜查和文件下载
import pathlib

from .VersionSearch import version_table, available_versions

_game_instance_folder = pathlib.Path("./instances")
if not _game_instance_folder.exists():
    _game_instance_folder.mkdir()
