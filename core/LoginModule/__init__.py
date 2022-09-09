# 微软登录模块
from pathlib import Path

cache_folder = Path("./cache")
if not cache_folder.exists():
    cache_folder.mkdir()
