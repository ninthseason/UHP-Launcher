import asyncio
import json
import pathlib

from core.ConfigModule import launcher_config
from core.VersionModule.VersionInstance import VersionInstance, Assets

version_id = launcher_config.get('version')
path = pathlib.Path(f"./versions/{version_id}.json")
with path.open("r") as f:
    version_json = VersionInstance(json.load(f), f"./instances/{version_id}/")
    asyncio.run(version_json.check_file(True))
    asyncio.run(version_json.check_minecraft_client(True))
    asyncio.run(version_json.check_assets(True))
    version_assets = Assets(f"./instances/{version_id}//assets/indexes/{version_json.get_assets_index()}.json", f"./instances/{version_id}/")
    asyncio.run(version_assets.check_objects(True))
