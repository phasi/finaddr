import typing


class Building:
    def __init__(
        self,
        building_id: str,
        region: str,
        municipality: str,
        street: str,
        house_number: str,
        postal_code: str,
        latitude_wgs84: str,
        longitude_wgs84: str,
        building_use: int,
    ):
        self.building_id = building_id
        self.region = region
        self.municipality = municipality
        self.street = street
        self.house_number = house_number
        self.postal_code = postal_code
        self.latitude_wgs84 = latitude_wgs84
        self.longitude_wgs84 = longitude_wgs84
        self.building_use = building_use
