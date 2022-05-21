import typing
import json
from os import path
from .exceptions import BadSearchTerm


class Config:
    def __init__(self, data_path: str, json_table_schema_path: str):
        self.json_table_schema_path = json_table_schema_path
        self.data_path = data_path
        self.fields: typing.Dict[str, int] = {}
        with open(
            file=self.json_table_schema_path, mode="r", encoding="utf-8"
        ) as schemafile:
            schema = json.loads(schemafile.read())
            for i, field in enumerate(schema.get("fields")):
                self.fields[field.get("name")] = i

    def get_index(self, field_name: str) -> int:
        try:
            return self.fields[field_name]
        except KeyError:
            raise BadSearchTerm(
                f"field name '{field_name}' does not exist in schema fields (Config.fields)"
            )
        except:
            raise
