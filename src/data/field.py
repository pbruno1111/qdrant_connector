from typing import Any


class Field:
    """
    helper class to describe a field
    """

    def __init__(self, name: str, data_type: str = "") -> None:
        """
        create a field
        :param name: the name of the field
        :param data_type: the data type of the field
        """
        self.name = name
        self.data_type = data_type


class FieldData(Field):
    """
    helper class to describe field data
    """

    def __init__(self, name: str, data_type: str = "", value: Any = None) -> None:
        """
        create a field data
        :param name: name of the field data
        :param data_type: data type of field data
        :param value: the value of the field data
        """
        super().__init__(name, data_type)
        self.value = value

    def __str__(self) -> str:
        """
        helper method to print the internals
        :return:
        """
        return f"name: {self.name}, data_type: {self.data_type}, value: {self.value}"



