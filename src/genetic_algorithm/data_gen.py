

import math

depot_coordinates = (48.137529134126616, 11.575577233934517)
per_km_time = 5 # minutes 

coordinate_list = [
    (48.1374, 11.5754), # depot
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
    (48.0972, 11.5793)
]


def guess_traffic_density():
    """
    Gets traffic density for each hour in [9, 21)

    :return: Traffic density for each hour in [9, 21)
    """
    density = 1
    increment_rate = 0.03
    hourly_density_list = []

    for hour in range(9, 21):
        hour_index = hour - 7

        density = density*(1 + hour_index*increment_rate)

        hourly_density_list.append(density)

        density = 1

    return hourly_density_list


def get_tdttm(initial_tts):
    """
    Calculates dynamic duration data from static one for a specific source

    :param initial_tts: Duration time data for a specific source for the initial hour
    :param hourly_traffic_densities: Traffic density for each hour in [9, 21)
    :return: Dynamic duration time data for a specific source
    """
    hourly_density_list = guess_traffic_density()

    tdttm = []

    for initial_tt in initial_tts:

        current_tt_list = [] # generated based on real tt data

        current_tt_list.append(initial_tt)

        for hourly_density in hourly_density_list:

            current_tt_list.append(initial_tt*hourly_density)

        tdttm.append(current_tt_list)

    return tdttm


def degreesToRadians(degrees):
    """
    Makes degrees to radians conversion

    :param degrees: A value in degrees
    :return: A value in radians
    """
    return degrees * math.pi / 180


def distanceInKmBetweenEarthCoordinates(lat1, lon1, lat2, lon2):
    """
    Gets km distance between given two locations

    :param source: Coordinates of the source location
    :param destination: Coordinates of the destination location
    :return: Distance between given two locations
    """
    earthRadiusKm = 6371

    dLat = degreesToRadians(lat2-lat1)
    dLon = degreesToRadians(lon2-lon1)

    lat1 = degreesToRadians(lat1)
    lat2 = degreesToRadians(lat2)

    a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));

    return earthRadiusKm * c


def get_dist_data():
    """
    Gets dynamic duration time data

    :param per_km_time: Multiplier to calculate duration from distance in km
    :return: Dynamic duration time data
    """
    dist_list = []
    tt_list = []

    for coordinate in coordinate_list:
        current_distance_list = []
        current_tt_list = []
        for other_coordinate in coordinate_list:
            cur_dist = distanceInKmBetweenEarthCoordinates(coordinate[0], coordinate[1], other_coordinate[0], other_coordinate[1])
            current_distance_list.append(cur_dist)
            current_tt_list.append(cur_dist*per_km_time)
        dist_list.append(current_distance_list)
        tt_list.append(current_tt_list)

    final_tt_list = []

    for dist_list in tt_list:
        updated_dist_list = get_tdttm(dist_list)
        final_tt_list.append(updated_dist_list)

    return final_tt_list


if __name__ == '__main__':
    dist_data = get_dist_data()
