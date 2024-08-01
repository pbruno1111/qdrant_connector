from enum import Enum, auto


class ConnType(Enum):
    """
    enum for qdrant connection types
    """
    MEMORY = auto()
    LOCAL = auto()
    CLOUD = auto()


class QdrantConnectionParams:
    """
    a helper class for the qdrant connection
    """

    def __init__(self, conn_type: ConnType, url: str = "", ) -> None:
        """
        set the required connection params
        :param conn_type: the connection type, could be in-memory, local and cloud
        :param url: the connection url
        """
        self._type = conn_type
        self.url = url
        if self._type == ConnType.MEMORY:
            self.url = ":memory:"


