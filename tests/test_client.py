import unittest
from os import path

from finaddr.config import Config
from finaddr.client import Client
from finaddr.exceptions import BadSearchTerm

resources_dir = path.join(path.dirname(__file__), "data")

TESTDATA = f"{resources_dir}/testdata.csv"
TESTSCHEMA = f"{resources_dir}/schema.json"

good_config = Config(
    data_path=TESTDATA,
    json_table_schema_path=TESTSCHEMA,
)

client = Client(good_config)


class ClientTest(unittest.TestCase):
    def test_search(self):
        """
        Search for something that should be present in the test data
        """
        results = client.search(street="Viulukuja")
        self.assertTrue(len(results) > 0)

    def test_not_found_any(self):
        results = client.search(street="somethingthatdoesnotexist")
        self.assertTrue(len(results) == 0)

    def test_search_with_bad_param(self):
        """
        Make a search using a bad search term
        """
        with self.assertRaises(BadSearchTerm):
            results = client.search(somekey="somevalue")
            # Should not print because above search should fail
            print(results)
