import os
import time
from typing import List, Tuple

import requests

N_NODES = 2  # Set it to 50
API_FILE_NAME = "api.txt"  # Google Maps API is not free
COORDINATES_FILE_NAME = "coordinates.txt"
OUTPUT_FOLDER_PATH = "../../../../data/google_api/static"

# Since Google Maps API returns slightly different data for a day, we just fetch one-hour data
FORECAST_HOURS_RANGE = range(0, 1)


def get_duration_from_response(request_url: str) -> List[int]:
    """
    Gets duration data for a specific source from a given request

    :param request_url: Request to send to Google Maps API
    :return: Duration data for a specific source
    """
    r = requests.get(request_url)
    duration_single_source = []
    elements = r.json()["rows"][0]["elements"]
    for element in elements:
        seconds = element["duration"]["value"]
        duration_single_source.append(seconds)
    return duration_single_source


def get_source_and_destination(
    coordinates: List[Tuple[float, float, str]],
    source_id: int,
    dest_id_lower: int,
    dest_id_upper: int,
) -> Tuple[str, str]:
    """
    Gets parts of the request to send from the given source, destinations and coordinates

    :param coordinates: Coordinates and names of specific places in Munich
    :param source_id: ID of the source location
    :param dest_id_lower: Lower bound on the destination id
    :param dest_id_upper: Upper bound on the destination id
    :return: Parts of the request to send where they are related to the source and destinations
    """
    source = f"{coordinates[source_id][0]}%2C{coordinates[source_id][1]}"
    destination = ""
    for idx in range(dest_id_lower, dest_id_upper):
        if idx != source_id:
            if destination:
                destination = f"{destination}%7C"
            x, y, _ = coordinates[idx]
            destination = f"{destination}{x}%2C{y}"
    return source, destination


def get_request(
    coordinates: List[Tuple[float, float, str]],
    source_id: int,
    dest_id_lower: int,
    dest_id_upper: int,
    api_key: str,
    forecast_hours: int,
):
    """
    Constructs the request to send to Google Maps API

    :param coordinates: Coordinates and names of specific places in Munich
    :param source_id: ID of the source location
    :param dest_id_lower: Lower bound on the destination id
    :param dest_id_upper: Upper bound on the destination id
    :param api_key: API key which is necessary for Google Maps API
    :param forecast_hours: The hour (time slice) in FORECAST_HOURS_RANGE
    :return: Request to send to Google Maps API
    """
    seconds = int(time.time()) + forecast_hours * 3600
    src, dest = get_source_and_destination(coordinates, source_id, dest_id_lower, dest_id_upper)
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    request_url = f"{url}mode=driving&departure_time={seconds}&origins={src}&destinations={dest}&key={api_key}"
    return request_url


"""
https://developers.google.com/maps/documentation/distance-matrix/usage-and-billing

While there is no maximum number of elements per day (EPD), the following usage limits are in place for the Distance
    Matrix API:
1.  Maximum of 25 origins or 25 destinations per request
2.  Maximum 100 elements per server-side request.
3.  Maximum 100 elements per client-side request.
4.  1000 elements per second (EPS), calculated as the sum of client-side and server-side queries.

Note: Distance Matrix requests specifying `departure_time` when `mode=driving` are limited to a maximum of 100
    elements per request. The number of origins times the number of destinations defines the number of elements.

Traffic information is used when all the following apply (these are the conditions required to receive the
    duration_in_traffic field in the Distance Matrix response):
The travel mode parameter is driving, or is not specified (driving is the default travel mode).
The request includes a valid departure_time parameter. The departure_time can be set to the current time or some
    time in the future. It cannot be in the past.
"""


def get_duration(
    api_key: str,
    coordinates: List[Tuple[float, float, str]],
    forecast_hours: int,
    jump: int = 10,
):
    """
    Gets duration matrix N by N in seconds for the first hour of the day

    :param api_key: API key which is necessary for Google Maps API
    :param coordinates: Coordinates and names of specific places in Munich
    :param forecast_hours: The hour (time slice) in FORECAST_HOURS_RANGE
    :param jump: The max number of destinations to fetch data per request, because of the restrictions on API
    :return: Duration matrix N by N in seconds for the given hour of the day
    """
    duration = [[0] * N_NODES for _ in range(N_NODES)]
    for source_id in range(N_NODES):
        for dest_id_lower in range(0, N_NODES, jump):
            dest_id_upper = min(dest_id_lower + jump, N_NODES)
            request_url = get_request(
                coordinates,
                source_id,
                dest_id_lower,
                dest_id_upper,
                api_key,
                forecast_hours,
            )
            idx = 0
            duration_single_source = get_duration_from_response(request_url)
            for dest_id in range(dest_id_lower, dest_id_upper):
                if source_id != dest_id:
                    duration[source_id][dest_id] = duration_single_source[idx]
                    idx += 1
            time.sleep(1)
    return duration


def get_coordinates() -> List[Tuple[float, float, str]]:
    """
    Gets coordinates and names of specific places in Munich

    :return: Coordinates and names of specific places in Munich
    """
    coordinates = []
    with open(COORDINATES_FILE_NAME) as file:
        lines = file.readlines()
        for line in lines:
            content = line.split()
            latitude = float(content[0])
            longitude = float(content[1])
            name = ""
            for word in content[2:]:
                if name:
                    name += " "
                name += word
            coordinates.append((latitude, longitude, name))
    coordinates = coordinates[:N_NODES]
    return coordinates


def get_api_key() -> str:
    """
    Gets the API key which is necessary for Google Maps API

    :return: API key which is necessary for Google Maps API
    """
    file = open(API_FILE_NAME)
    api_key = file.read()
    file.close()
    return api_key


def output_file(duration: List[List[float]], time_in_sec: int, forecast_hours: int) -> None:
    """
    Saves duration matrix for the given hour of the day

    :param duration: Duration matrix N by N in seconds for the given hour of the day
    :param time_in_sec: Current timestamp in seconds
    :param forecast_hours: The hour (time slice) in FORECAST_HOURS_RANGE
    """
    os.makedirs(f"{OUTPUT_FOLDER_PATH}/", exist_ok=True)
    output_file_name = f"{OUTPUT_FOLDER_PATH}/duration_{N_NODES}_{time_in_sec}_{forecast_hours}.txt"
    with open(output_file_name, "w") as file:
        file.writelines(" ".join(str(j) for j in i) + "\n" for i in duration)


def run() -> None:
    """
    Gets duration data from Google Maps API and saves duration matrix for the initial hour
    """
    api_key = get_api_key()
    coordinates = get_coordinates()
    time_in_sec = int(time.time())
    for forecast_hours in FORECAST_HOURS_RANGE:
        duration = get_duration(api_key, coordinates, forecast_hours)
        output_file(duration, time_in_sec, forecast_hours)
        print(f"forecast_hours = {forecast_hours}")
        print(duration)


if __name__ == "__main__":
    run()
