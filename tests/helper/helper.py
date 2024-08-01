import string
import random
import uuid

from qdrant_connector.src.data.entity import EntityId, Entity, EntityData
from qdrant_connector.src.data.field import Field, FieldData


class TestHelper:
    """
    helper class to create various randomized data
    """
    @classmethod
    def str_generator(cls, size=6, chars=string.ascii_uppercase + string.digits):
        """
        create a randomized string with given length
        :param size: the length of the string
        :param chars: the list of characters to be used, default is all alphanumerics
        :return: the randomized string
        """
        return ''.join(random.choice(chars) for _ in range(size))

    @classmethod
    def type_generator(cls):
        """
        create a random data type
        :return: the random data type
        """
        return random.choice(['int', 'float', 'str', 'vector'])

    @classmethod
    def vector_generator(cls):
        """
        create a 10 length random vector
        :return: the randomized vector
        """
        return [random.uniform(0.1, 1.0) for _ in range(10)]

    @classmethod
    def value_generator(cls, data_type=None):
        """
        create a random value
        :param data_type: the data type of the value
        :return: the random value
        """
        if data_type == 'int':
            return random.randint(1,100)
        elif data_type == 'float':
            return random.uniform(0.1, 1.0)
        elif data_type == 'str':
            return cls.str_generator(size=10)
        else:
            return cls.vector_generator()

    @classmethod
    def create_random_entity_id(cls, id_type='int'):
        """
        create a random entity id object
        :param id_type: the id type to be used, int or uuid
        :return: the random object
        """
        if id_type == 'int':
            return EntityId(object_id=str(random.randint(1,1000)), schema_id=str(random.randint(1,10000)))
        else:
            return EntityId(object_id= str(uuid.uuid4()), schema_id= str(uuid.uuid4()))

    @classmethod
    def create_random_entity(cls):
        """
        create a random entity object
        :return: the random object
        """
        fields = [cls.create_random_field() for _ in range(10)]
        return Entity(entity_id=cls.create_random_entity_id(id_type='int'), fields=fields)

    @classmethod
    def create_random_field(cls):
        """
        create a random field object
        :return: the random object
        """
        name = cls.str_generator(size=5)
        data_type = cls.type_generator()
        return Field(name=name, data_type=data_type)

    @classmethod
    def create_random_field_data(cls):
        """
        create a random field data object
        :return: the random object
        """
        field = cls.create_random_field()
        value = cls.value_generator(data_type=field.data_type)
        return FieldData(name=field.name, data_type=field.data_type, value=value)

    @classmethod
    def create_random_entity_data(cls):
        """
        create a random entity data object
        :return: the random object
        """
        field_data_list = [cls.create_random_field_data() for _ in range(10)]
        return EntityData(entity_id=cls.create_random_entity_id(), field_data=field_data_list)
