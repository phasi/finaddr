import unittest
from os import path

from finaddr.config import Config
from finaddr.client import Client

resources_dir = path.join(path.dirname(__file__), "data")


class ClientTest(unittest.TestCase):
    def test_search(self):
        config = Config(
            data_path=f"{resources_dir}/testdata.csv",
            json_table_schema_path=f"{resources_dir}/schema.json",
        )
        client = Client(config)
        results = client.search(street="Viulukuja")
        self.assertTrue(len(results) > 0)
