import typing
import json
import os
import csv
import re
import requests

DEFAULT_SCHEMA = {
    "fields": [
        {
            "name": "building_id",
            "type": "string",
            "description": "Identifier for Finnish buildings",
        },
        {
            "name": "region",
            "type": "string",
            "description": "Identification number for Finnish regions. See: https://dvv.fi/tilastot-ja-luettelot, file Maakunnat.xlsx",
        },
        {
            "name": "municipality",
            "type": "string",
            "description": "Identification number for Finnish municipalities. See: http://tilastokeskus.fi/meta/luokitukset/kunta/001-2019/index.html",
        },
        {
            "name": "street",
            "type": "string",
            "description": "Street name: an identifying name given to a street",
        },
        {
            "name": "house_number",
            "type": "string",
            "description": "Unique number to each building in a street or area, with the intention of making it easier to locate a particular building",
        },
        {
            "name": "postal_code",
            "type": "string",
            "description": "Series of digits included in a postal address for the purpose of sorting mail.",
        },
        {
            "name": "latitude_wgs84",
            "type": "number",
            "description": "Coordinate latitude in the WGS 84 standard. The World Geodetic System (WGS) is a standard for use in cartography, geodesy, and navigation including GPS.",
        },
        {
            "name": "longitude_wgs84",
            "type": "number",
            "description": "Coordinate longitude in the WGS 84 standard. The World Geodetic System (WGS) is a standard for use in cartography, geodesy, and navigation including GPS.",
        },
        {
            "name": "building_use",
            "type": "integer",
            "description": "Intended use of building. The identification codes with the corresponding letter codes from stat.fi are: 0 The intended use of building is lacking, 1 Residental building or business premises (A - H), and 2 Production building or other building (J - N). See: http://www.stat.fi/meta/luokitukset/rakennus/001-2018-07-12/index_en.html",
        },
    ]
}


class MissingSearchParam(Exception):
    """Use this exception to indicate that a required search param
    was missing or its value was None or an empty string.

    Args:
        Exception ([type]): Instantiate this exception with a text that matches
        the usage description of this Exception
    """

    pass


class InvalidParser(Exception):
    """Use this exception to indicate that an invalid parser was provided

    Args:
        Exception ([type]): Instantiate this exception with a text that matches
        the usage description of this Exception
    """

    pass


class Config:
    def __init__(
        self,
        data_path: str,
        indexed_data_folder_path: str,
        json_table_schema_path: typing.Optional[str],
    ):
        self.json_table_schema_path = json_table_schema_path
        self._data_path = data_path
        self._indexed_data_folder_path = indexed_data_folder_path
        self._fields: typing.Dict[str, int] = {}
        if json_table_schema_path is not None:
            with open(
                file=self.json_table_schema_path, mode="r", encoding="utf-8"
            ) as schemafile:
                schema = json.loads(schemafile.read())
        else:
            schema = DEFAULT_SCHEMA
        for i, field in enumerate(schema.get("fields")):
            self._fields[field.get("name")] = i

    @property
    def data_path(self):
        return self._data_path

    @property
    def indexed_data_folder_path(self):
        return self._indexed_data_folder_path

    def get_index(self, field_name: str) -> int:
        return self._fields[field_name]


class BaseParser:
    """Base parser for parsing and searching from data. Can be inherited by custom parsers."""

    def __init__(self, config: Config):
        """Base parser for parsing and searching from data. Can be inherited by custom parsers.

        Args:
            config (Config): Contains necessary filepaths
        """
        self.config = config

    def _create_dict_from_row(self, row: typing.List[str]) -> typing.Dict[str, str]:
        result = {}
        for x in self.config._fields:
            result[x] = row[self.config.get_index(x)]
        return result

    def index_data(self):
        """This method should index data and it should not return anything.
        Override it to create your own indexing
        """
        pass

    def search(self, **search_params) -> typing.List[typing.Dict[str, str]]:
        """This method should search from (indexed or directly from) data depending
        on your approach.
        Override it to create your custom search.

        Returns:
            typing.List[typing.Dict[str, str]]: List of dictionaries containing data as per schema
        """
        return []


class StreetNameAlphabeticalParser(BaseParser):
    def _validate_letter(self, letter: str) -> bool:
        regex = re.compile("^[A-Za-z]{1}")
        if regex.match(letter):
            return True
        return False

    def _get_filepath_for(self, index_name: str):
        return f"{self.config.indexed_data_folder_path}/{index_name}.json"

    def _get_index_name_for(self, street_name: str):
        index_name = (
            street_name[0].upper()
            if self._validate_letter(street_name[0].upper())
            else "unknown"
        )
        return index_name

    def _index_data_alphabetically_by_street(self):
        """
        Organizes data into json files by street name in alphabetical order.
        """
        results = {}
        with open(file=self.config.data_path, newline="\n") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                street = row[self.config.get_index("street")]
                if not street:
                    continue
                index_name = self._get_index_name_for(street)
                letter = results.get(index_name, None)
                if isinstance(letter, list):
                    results[index_name].append(self._create_dict_from_row(row))
                else:
                    results[index_name] = [self._create_dict_from_row(row)]
        if not os.path.exists(self.config.indexed_data_folder_path):
            os.makedirs(self.config.indexed_data_folder_path)
        for x in results:
            with open(
                file=self._get_filepath_for(x),
                mode="w",
                encoding="utf-8",
            ) as jsonfile:
                json.dump(results[x], jsonfile, ensure_ascii=False)

    def index_data(self):
        self._index_data_alphabetically_by_street()

    def _check_row(self, row: typing.Dict[str, str], **search_params) -> bool:
        for s in search_params:
            if not row.get(s).lower() == search_params[s].lower():
                return False
        return True

    def _search_from_index(self, index_name, **search_params):
        results: typing.List[typing.Dict[str, str]] = []
        with open(
            self._get_filepath_for(index_name),
            mode="r",
            encoding="utf-8",
        ) as f:
            jsondata = json.loads(f.read())
            for row in jsondata:
                if self._check_row(row, **search_params):
                    results.append(row)
        return results

    def search(self, **search_params):
        street = search_params.get("street", None)
        if street:
            index_name = self._get_index_name_for(street)
            return self._search_from_index(index_name, **search_params)
        else:
            raise MissingSearchParam("'street' is missing from parameters")


def get_default_path_for(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), name)


class Client:
    """Client for searching finnish building data."""

    def __init__(
        self,
        config: Config,
        parser: typing.Type[BaseParser],
        should_index_data: bool = False,
    ):
        """Client for searching finnish building data.

        Args:
            config (Config): Configuration containing necessary filepaths
            parser (typing.Type[BaseParser]): Reference to parser class. Used class must inherit BaseParser
            should_index_data (bool, optional): Whether client should call parser's index_data() method (this is a long running operation). Defaults to False.

        Raises:
            InvalidParser: If parser is not subclass of BaseParser then this exception is raised.
        """
        try:
            if not issubclass(parser, BaseParser):
                raise InvalidParser("'parser' must be a subclass of BaseParser")
            self._parser = parser(config)
            if should_index_data:
                self._parser.index_data()
        except TypeError:
            raise InvalidParser("'parser' must be a subclass of BaseParser")

    @classmethod
    def from_env(cls, parser: typing.Type[BaseParser], should_index_data: bool = False):
        """Gets this class properties from environment variables

        Env:
            FINADDR_DATA_PATH: Reference to the raw CSV data file
            FINADDR_INDEXED_DATA_FOLDER_PATH: Reference to the folder where indexed data should be stored
            FINADDR_JSON_TABLE_SCHEMA_PATH: Reference to the schema file containing supported fields

        Args:
            parser (typing.Type[BaseParser]): Reference to parser class. Used class must inherit BaseParser
            should_index_data (bool, optional): Whether client should call parser's index_data() method (this is a long running operation). Defaults to False.

        Returns:
            [type]: Client
        """
        config = Config(
            data_path=os.getenv("FINADDR_DATA_PATH"),
            indexed_data_folder_path=os.getenv("FINADDR_INDEXED_DATA_FOLDER_PATH"),
            json_table_schema_path=os.getenv("FINADDR_JSON_TABLE_SCHEMA_PATH"),
        )
        return cls(config=config, parser=parser, should_index_data=should_index_data)

    @classmethod
    def with_data_from_uri(
        cls,
        data_uri: str,
        json_table_schema_uri: str,
        parser: typing.Type[BaseParser],
        should_index_data: bool = True,
    ):
        data = requests.get(data_uri, allow_redirects=True)
        with open(get_default_path_for("data.csv"), mode="wb") as f:
            f.write(data.content)
        schema = requests.get(json_table_schema_uri, allow_redirects=True)
        with open(get_default_path_for("schema.json"), mode="wb") as f:
            f.write(schema.content)

        config = Config(
            data_path=get_default_path_for("data.csv"),
            indexed_data_folder_path=get_default_path_for("indexed_data"),
            json_table_schema_path=get_default_path_for("schema.json"),
        )
        return cls(config=config, parser=parser, should_index_data=should_index_data)

    @classmethod
    def with_defaults(cls, parser: typing.Type[BaseParser]):
        config = Config(
            data_path=get_default_path_for("data.csv"),
            indexed_data_folder_path=get_default_path_for("indexed_data"),
            json_table_schema_path=get_default_path_for("schema.json"),
        )
        return cls(config=config, parser=parser, should_index_data=False)

    def search(self, **search_params) -> typing.List[typing.Dict[str, str]]:
        """Searches from data with the provided parser

        Returns:
            typing.List[typing.Dict[str, str]]: List of dictionaries containing data as per schema
        """
        return self._parser.search(**search_params)


# if __name__ == "__main__":

# client = Client.with_data_from_uri(
#     data_uri="https://yourstorage.blob.core.windows.net/public/Finland_addresses_2022-05-12.csv",
#     json_table_schema_uri="https://yourstorage.blob.core.windows.net/public/json_table_schema.json",
#     parser=StreetNameAlphabeticalParser,
#     should_index_data=True,
# )
# client = Client.with_defaults(parser=StreetNameAlphabeticalParser)
# results = client.search(street="somestreet", house_number="4")
# print(results)
