# Finaddr

Finaddr is a library to query finnish addresses, buildings and postcodes from a separate offline database.

Download the static files package from avoindata: https://www.avoindata.fi/data/fi/dataset/postcodes

You'll need "json_table_schema.json" (schema) and "data/Finland_addresses_2022-05-12.csv" (data).

You have to include the static files in your project and refer to them from within your code. You may pass the path to the files as environment variable,
or even tell your client to download the files over HTTP(S) when loading the Client. (This is probably the easiest way if you want to maintain the files on your server)


## Install

```bash
pip install finaddr
```

## Configure with remote data (download data files over HTTP)

```python
import typing
from finaddr.finaddr import (
    Config,
    StreetNameAlphabeticalParser,
    Client,
)

config = Config(
    data_path="path/to/raw_data.csv",
    indexed_data_folder_path="/path/to/indexed_data_folder",
    json_table_schema_path="/path/to/schema.json",
)

# use should_index_data when setting things up. This will call the parser's
# index_data() method. This is a long running operation so be mindful when and where to do it.
# If data is already indexed by the selected parser then set should_index_data=False
client = Client(config=config, parser=StreetNameAlphabeticalParser, should_index_data=True)

results: typing.List[typing.Dict[str,str]] = client.search(street="Viulukuja", house_number="1")

for r in results:
    print(r)

```

## Configure client from environment

If you have already downloaded the data by other means you can also pass the paths in environment variables

1. create your code:

```python
import typing
from finaddr.finaddr import Client, StreetNameAlphabeticalParser

client = Client.from_env(parser=StreetNameAlphabeticalParser, should_index_data=False)

results: typing.List[typing.Dict[str,str]] = client.search(street="Viulukuja")

for r in results:
    print(r)

```

2. export variables, start virtual environment, and run your code

```bash
$ export FINADDR_DATA_PATH="/path/to/data.csv"
$ export FINADDR_INDEXED_DATA_FOLDER_PATH="/path/to/data_folder"
$ export FINADDR_JSON_TABLE_SCHEMA_PATH="/path/to/schema.json"

$ source /path/to/your/project/virtualenv/bin/activate

(venv)$ python3 your_file.py
```