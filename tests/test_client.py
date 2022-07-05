import unittest
from os import path


from finaddr.finaddr import (
    Config,
    StreetNameAlphabeticalParser,
    Client,
    MissingSearchParam,
    InvalidParser,
)

resources_dir = path.join(path.dirname(__file__), "data")

TESTDATA = f"{resources_dir}/testdata.csv"
INDEXED_DATA = f"{resources_dir}/indexed_data"
TESTSCHEMA = f"{resources_dir}/schema.json"

good_config = Config(
    data_path=TESTDATA,
    indexed_data_folder_path=INDEXED_DATA,
    json_table_schema_path=TESTSCHEMA,
)

client = Client(
    good_config, parser=StreetNameAlphabeticalParser, should_index_data=True
)


class ConfigTest(unittest.TestCase):
    def test_bad_schema_path(self):
        with self.assertRaises(FileNotFoundError):
            bad_config = Config(
                data_path=TESTDATA,
                indexed_data_folder_path=INDEXED_DATA,
                json_table_schema_path="/non/existent/path/to/json.json",
            )

    def test_with_default_schema(self):
        config = Config(
            data_path=TESTDATA,
            indexed_data_folder_path=INDEXED_DATA,
            json_table_schema_path=None,
        )

    def test_incomplete_config(self):
        with self.assertRaises(TypeError):
            # Disable pylint for below line since 'no-value-for-parameter' is exactly
            # what's being tested here
            config = Config(  # pylint: disable=no-value-for-parameter
                data_path=TESTDATA
            )


class ClientTest(unittest.TestCase):
    def test_invalid_parser(self):
        """Try to pass invalid parser"""
        with self.assertRaises(InvalidParser):
            client = Client(config=good_config, parser="not a real parser")
            client.search(street="Viulukuja")

    def test_search(self):
        """
        Search for something that should be present in the test data
        """
        results = client.search(street="Viulukuja")
        self.assertTrue(len(results) > 0)

    def test_not_found_any(self):
        results = client.search(street="Viuhukuja")
        self.assertTrue(len(results) == 0)

    def test_search_with_bad_param(self):
        """
        Make a search with parser 'StreetNameAlphabeticalParser' using a bad search term
        """
        with self.assertRaises(MissingSearchParam):
            results = client.search(somekey="somevalue")
            # Should not print because above search should fail
            print(results)
