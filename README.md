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

## Test/Use with local data

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
# Currently only StreetNameAlphabeticalParser can be used or you can write your own parser
# use should_index_data when setting things up. This will call the parser's
# index_data() method. This is a long running operation so be mindful when and where to do it.
# If data is already indexed by the selected parser then set should_index_data=False
client = Client(config=config, parser=StreetNameAlphabeticalParser, should_index_data=True)

results: typing.List[typing.Dict[str,str]] = client.search(street="Viulukuja", house_number="1")

for r in results:
    print(r)

```

## Use in Azure Functions with data downloaded from server

This approach works with azure functions. A function app should normally save data elsewhere but this example makes it download the data and schema
into the library folder itself.



You should use this/similar code in a TimerTrigger (that downloads any possible updates to your schema and indexes the data)

Timer - function.json
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "mytimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 1 * * Sun",
      "runOnStartup": true
    }
  ]
}
```
Timer - Trigger
```python

import datetime
import logging
import azure.functions as func
from finaddr.finaddr import Client, StreetNameAlphabeticalParser

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logging.info("Trying to download and index address data (%s)", utc_timestamp)

    client = Client.with_data_from_uri(
        data_uri="https://yourdomain.com/Finland_addresses_2022-05-12.csv",
        json_table_schema_uri="https://yourdomain.com/json_table_schema.json",
        parser=StreetNameAlphabeticalParser,
        should_index_data=True, # make sure above parser will index data
    )

    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logging.info("Data downloaded and indexed at %s", utc_timestamp)

```

HTTP Trigger - function.json
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": [
        "get"
      ],
      "route": "v1/find"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

HTTP Trigger - function:

```python
import logging

import azure.functions as func
from finaddr.finaddr import (
    Client,
    StreetNameAlphabeticalParser,
    MissingSearchParam,
)
import os
import json

client = Client.with_defaults(parser=StreetNameAlphabeticalParser)


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("Python HTTP trigger function processed a request.")

    try:
        results = client.search(**req.params)

        return func.HttpResponse(
            json.dumps(results),
            status_code=200,
        )
    except MissingSearchParam as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
        )


```
