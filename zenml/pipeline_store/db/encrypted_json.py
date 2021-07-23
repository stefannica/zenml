import json

from sqlalchemy import JSON


class JSONEncryptedType(JSON):
    """
    We have to use this so that JSON can be encrypted. See this issue for
    details: https://github.com/kvesteri/sqlalchemy-utils/issues/177
    """

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        json_serializer = dialect._json_serializer or json.dumps
        return json_serializer(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        json_deserializer = dialect._json_deserializer or json.loads
        return json_deserializer(value)
