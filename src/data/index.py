from typing import Any


class IndexConfig:
    """
    helper class describing an index config
    """

    def __init__(self, index_name: str, config_data: dict[str, Any]) -> None:
        """
        create an index config
        :param index_name: the name of the config
        :param config_data: any config data that should be stored as a kv pair
        """
        self.index_name = index_name
        self.config_data = config_data
