import typing
import os
import urllib.request
from .config import Config
from ._parser import Parser
from .model import Building


class Client:
    def __init__(self, config: Config):
        self.config: Config = config

    @classmethod
    def from_env(cls):
        config = Config(
            data_path=os.getenv("FINADDR_DATA_PATH"),
            json_table_schema_path=os.getenv("FINADDR_JSON_TABLE_SCHEMA_PATH"),
        )
        return cls(config=config)

    @classmethod
    def with_remote_data(cls, data_url: str, json_table_schema_url: str):
        urllib.request.urlretrieve(url=data_url, filename="data.csv")
        urllib.request.urlretrieve(url=json_table_schema_url, filename="schema.json")
        return cls(
            config=Config(data_path="data.csv", json_table_schema_path="schema.json")
        )

    def search(self, **search_params) -> typing.List[Building]:
        parser = Parser(self.config)
        found = parser.search(**search_params)
        return found
