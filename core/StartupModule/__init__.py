# 启动模块
# 整合各项配置，生成启动脚本

def config_to_string(config: dict) -> str:
    """
    将配置文件转换为脚本参数

    :param config: 配置文件 如 jvm_config, minecraft_config
    :return: 参数字符串
    """
    return " ".join([config[i] for i in config])
