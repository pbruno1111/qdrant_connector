from qdrant_connector.src.data.field import Field, FieldData


class EntityData:
    """
    helper class to create entity data
    """
    def __init__(self, entity_id, field_data: list[FieldData]) -> None:
        """
        create entity data
        :param entity_id: an entity id object
        :param field_data: list of field data to be stored in the entity
        """
        self.entity_id = entity_id
        self.field_data = field_data

    def __str__(self) -> str:
        """
        helper method to print the internals
        :return:
        """
        return f"entity_id: {str(self.entity_id)}, field_data: {str(self.field_data)}"


class EntityId:
    """
    helper class to create an entity id
    """
    def __init__(self, schema_id: str, object_id: str) -> None:
        """
        create entity id
        :param schema_id: the schema id to be used
        :param object_id: the object id to be used
        """
        self.schema_id = schema_id
        self.object_id = object_id


class Entity:
    """
    helper class to create an entity
    """
    def __init__(self, entity_id: EntityId, fields: list[Field]) -> None:
        """
        create an entity
        :param entity_id: an entity id object
        :param fields: list of fields to be available on the entity
        """
        self.entity_id = entity_id
        self.fields = fields


