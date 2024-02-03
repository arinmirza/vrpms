import math
from typing import List, Tuple

EARTH_RADIUS_KM = 6371
DENSITY = 1
INCREMENT_RATE = 0.03

COORDINATE_LIST = [
    (48.1374, 11.5754),  # depot
    (48.1755, 11.5518),
    (48.1340, 11.5676),
    (48.1114, 11.4703),
    (48.2648, 11.6713),
    (48.2489, 11.6532),
    (48.2474, 11.6310),
    (48.2123, 11.6279),
    (48.2038, 11.6133),
    (48.2012, 11.6146),
    (48.1832, 11.6077),
    (48.1792, 11.5999),
    (48.1753, 11.6031),
    (48.1672, 11.5909),
    (48.1632, 11.5869),
    (48.1565, 11.5840),
    (48.3321, 10.8957),
    (48.1436, 11.5779),
    (48.1257, 11.5506),
    (48.1170, 11.5358),
    (48.1152, 11.5198),
    (48.1160, 11.5022),
    (48.1231, 11.4840),
    (48.1811, 11.5115),
    (48.1833, 11.5316),
    (48.1861, 11.5468),
    (48.1713, 11.5729),
    (48.1667, 11.5782),
    (48.1296, 11.5584),
    (48.0768, 11.5120),
    (48.0884, 11.4810),
    (48.1330, 11.5317),
    (48.1363, 11.5532),
    (48.1403, 11.5600),
    (48.1392, 11.5662),
    (48.1356, 11.5989),
    (48.1533, 11.6203),
    (48.1354, 11.5019),
    (48.1360, 11.5382),
    (48.1274, 11.6050),
    (48.1207, 11.6200),
    (48.1012, 11.6462),
    (48.0890, 11.6451),
    (48.1334, 11.6906),
    (48.1287, 11.6835),
    (48.1124, 11.5878),
    (48.1129, 11.5928),
    (48.1155, 11.5797),
    (48.1266, 11.6338),
    (48.1198, 11.5768),
    (48.1457, 11.5653),
    (48.1621, 11.5687),
    (48.2106, 11.5722),
    (48.2115, 11.5132),
    (48.1701, 11.5244),
    (48.1479, 11.5570),
    (48.1130, 11.5716),
    (48.0972, 11.5793),
]


def guess_traffic_density() -> List[float]:
    """
    Gets traffic density for each hour in [9, 21)

    :return: Traffic density for each hour in [9, 21)
    """
    hourly_density_list = []
    for hour in range(9, 21):
        hour_index = hour - 7
        density_hour = DENSITY * (1 + hour_index * INCREMENT_RATE)
        hourly_density_list.append(density_hour)
    return hourly_density_list


def degrees_to_radians(degrees: float) -> float:
    """
    Makes degrees to radians conversion

    :param degrees: A value in degrees
    :return: A value in radians
    """
    return degrees * math.pi / 180


def distance_in_km_between_coordinates(source: Tuple[float, float], destination: Tuple[float, float]) -> float:
    """
    Gets km distance between given two locations

    :param source: Coordinates of the source location
    :param destination: Coordinates of the destination location
    :return: Distance between given two locations
    """
    lat1, lon1 = source
    lat2, lon2 = destination
    d_lat = degrees_to_radians(lat2 - lat1)
    d_lon = degrees_to_radians(lon2 - lon1)
    lat1 = degrees_to_radians(lat1)
    lat2 = degrees_to_radians(lat2)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.sin(d_lon / 2) * math.sin(d_lon / 2) * math.cos(
        lat1
    ) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def get_time_data(per_km_time: float = 5) -> List[List[List[float]]]:
    """
    Gets dynamic duration time data

    :param per_km_time: Multiplier to calculate duration from distance in km
    :return: Dynamic duration time data
    """
    hourly_traffic_densities = guess_traffic_density()
    time_data = []
    for src_coordinate in COORDINATE_LIST:
        time_data_src = []
        for dest_coordinate in COORDINATE_LIST:
            time_data_src_dest = []
            dist_km = distance_in_km_between_coordinates(src_coordinate, dest_coordinate)
            static_duration = dist_km * per_km_time
            for density in hourly_traffic_densities:
                dynamic_duration = density * static_duration
                time_data_src_dest.append(dynamic_duration)
            time_data_src.append(time_data_src_dest)
        time_data.append(time_data_src)
    return time_data


def run(per_km_time: float = 5) -> None:
    """
    Calculates dynamic duration data of common dataset and prints it

    :param per_km_time: Multiplier to calculate duration from distance in km
    """
    time_data = get_time_data(per_km_time)
    print(time_data)


if __name__ == "__main__":
    run()
