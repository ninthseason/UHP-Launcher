import json
import pathlib


class Config:
    def __init__(self, path: str):
        self.config = {}
        self.path = pathlib.Path(path)
        self.load()

    def save(self) -> None:
        """
        保存配置

        :return: None
        """

        if not self.path.parent.exists():
            self.path.parent.mkdir()
        with open(self.path, "w") as f:
            json.dump(self.config, f)

    def load(self) -> None:
        """
        从文件加载配置

        :return: None
        """

        if self.path.exists():
            with open(self.path, "r") as f:
                self.config = json.load(f)

    def update(self, config: dict) -> None:
        """
        (批量)更新配置

        :param config:
        :return:
        """
        self.config.update(config)
        self.save()

    def set(self, key, value) -> None:
        """
        设置单项配置

        :param key: 键
        :param value: 值
        :return:
        """
        self.config.update({key: value})
        self.save()

    def get(self, key) -> None:
        """
        获取单项配置

        :param key: 键
        :return:
        """
        return self.config.get(key, None)

    def empty(self) -> bool:
        """
        检查配置表是否为空

        :return: boolean
        """
        return True if len(self.config) == 0 else False

    def load_default(self, config: dict) -> None:
        """
        设置默认模板

        配置文件 覆盖 默认模板 => 配置

        如: 默认模板:{var1： 1, var2: 2}, 配置文件:{var1: 3}

        生成配置: {var1: 3, var2: 2}

        :param config: 默认模板
        :return: None
        """
        self.load()
        config.update(self.config)
        self.config = config
        self.save()

    def items(self) -> dict:
        """
        获取字典形式的配置

        :return: dict
        """
        return self.config


class DynamicConfig:
    """
    动态配置

    与普通配置的不同点在于操作值前会重新读取一遍文件
    以此获取到文件的更改
    """

    def __init__(self, path: str):
        self.config = {}
        self.path = pathlib.Path(path)
        self.load()

    def save(self):
        if not self.path.parent.exists():
            self.path.parent.mkdir()
        with open(self.path, "w") as f:
            json.dump(self.config, f)

    def load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                self.config = json.load(f)

    def update(self, config: dict):
        self.load()
        self.config.update(config)
        self.save()

    def set(self, key, value):
        self.load()
        self.config.update({key: value})
        self.save()

    def get(self, key):
        self.load()
        return self.config.get(key, None)

    def empty(self):
        return True if len(self.config) == 0 else False

    def load_default(self, config: dict):
        self.load()
        config.update(self.config)
        self.config = config
        self.save()

    def items(self):
        return self.config


class LazyConfig:
    """
    懒惰配置

    与普通配置不同点在于不会自动保存配置项
    需要手动调用save()以持久化数据
    """

    def __init__(self, path: str):
        self.config = {}
        self.path = pathlib.Path(path)
        self.load()

    def save(self):
        if not self.path.parent.exists():
            self.path.parent.mkdir()
        with open(self.path, "w") as f:
            json.dump(self.config, f)

    def load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                self.config = json.load(f)

    def update(self, config: dict):
        self.config.update(config)

    def set(self, key, value):
        self.config.update({key: value})

    def get(self, key):
        return self.config.get(key, None)

    def empty(self):
        return True if len(self.config) == 0 else False

    def load_default(self, config: dict):
        self.load()
        config.update(self.config)
        self.config = config

    def items(self):
        return self.config
