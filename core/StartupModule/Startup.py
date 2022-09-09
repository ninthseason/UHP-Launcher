from core.ConfigModule import jvm_config
from core.ConfigModule import minecraft_config

from . import config_to_string


def start_up_script() -> str:
    """
    获取启动脚本

    :return: 启动脚本
    """
    return config_to_string(jvm_config.items()) + " " + config_to_string(minecraft_config.items())
