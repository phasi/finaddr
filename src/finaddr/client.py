import typing
import os
import urllib.request
from .config import Config
from ._parser import Parser
from .model import Building
import ssl


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
        with urllib.request.urlopen(url=data_url, context=ssl.SSLContext()) as data:
            with open(file="data.csv", mode="w", encoding="utf-8") as f:
                f.write(str(data.read(), encoding="utf-8"))
        with urllib.request.urlopen(
            url=json_table_schema_url, context=ssl.SSLContext()
        ) as schema:
            with open(file="schema.json", mode="w", encoding="utf-8") as f:
                f.write(str(schema.read(), encoding="utf-8"))

        return cls(
            config=Config(data_path="data.csv", json_table_schema_path="schema.json")
        )

    def search(self, **search_params) -> typing.List[Building]:
        """Search with key=value arguments

        Returns:
            typing.List[Building]: List of buildings that matched the search.
        """
        parser = Parser(self.config)
        found = parser.search(**search_params)
        return found
