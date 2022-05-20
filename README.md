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
from finaddr.model import Building
from finaddr.client import Client

client = Client.with_remote_data(
        data_url="http://address.com/data.csv",
        json_table_schema_url="http://address.com/schema.json",
)

results: typing.List[Building] = client.search(street="Viulukuja")

for r in results:
    print(r.__dict__)

```

## Configure client from environment

If you have already downloaded the data by other means you can also pass the paths in environment variables

1. create your code:

```python
import typing
from finaddr.model import Building
from finaddr.client import Client

client = Client.from_env()

results: typing.List[Building] = client.search(street="Viulukuja")

for r in results:
    print(r.__dict__)

```

2. export variables, start virtual environment, and run your code

```bash
$ export FINADDR_DATA_PATH="/path/to/data.csv"
$ export FINADDR_JSON_TABLE_SCHEMA_PATH="/path/to/schema.json"

$ source /path/to/your/project/virtualenv/bin/activate

(venv)$ python3 your_file.py
```


You can also filter results by other key's. Checkout finaddr.model.Building for accepted keys.