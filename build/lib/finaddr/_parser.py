import typing
from .config import Config
import csv
from .model import Building


class Parser:
    def __init__(self, config: Config):
        self.config = config

    def _search(
        self, row: typing.List[str], **search_params
    ) -> typing.Optional[Building]:
        for s in search_params:
            if not row[self.config.get_index(s)].lower() == search_params[s].lower():
                return None
        return Building(
            building_id=row[self.config.get_index("building_id")],
            region=row[self.config.get_index("region")],
            municipality=row[self.config.get_index("municipality")],
            street=row[self.config.get_index("street")],
            house_number=row[self.config.get_index("house_number")],
            postal_code=row[self.config.get_index("postal_code")],
            latitude_wgs84=row[self.config.get_index("latitude_wgs84")],
            longitude_wgs84=row[self.config.get_index("longitude_wgs84")],
            building_use=row[self.config.get_index("building_use")],
        )

    def search(self, **search_params):
        results = []
        with open(file=self.config.data_path, newline="\n") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                result = self._search(row, **search_params)
                if result:
                    results.append(result)
        return results
