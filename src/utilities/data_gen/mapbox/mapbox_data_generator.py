import numpy as np
import os
import requests
import json
import time

# (lat, lon, name)
COORDINATES = [
    (48.1374, 11.5754, 'Marien platz'),
    (48.1755, 11.5518, 'Olympia'),
    (48.1340, 11.5676, 'Sendlinger Tor'),
    (48.1114, 11.4703, 'Klinikum Großhadern'),
    (48.2648, 11.6713, 'Garching-Forschungszentrum'),
    (48.2489, 11.6532, 'Garching'),
    (48.2474, 11.6310, 'Garching-Hochbrück'),
    (48.2123, 11.6279, 'Fröttmaning'),
    (48.2038, 11.6133, 'Kieferngarten'),
    (48.2012, 11.6146, 'Freimann'),
    (48.1832, 11.6077, 'Studentenstadt'),
    (48.1792, 11.5999, 'Alte Heide'),
    (48.1753, 11.6031, 'Nordfriedhof'),
    (48.1672, 11.5909, 'Dietlindenstraße'),
    (48.1632, 11.5869, 'Münchner Freiheit'),
    (48.1565, 11.5840, 'Giselastraße'),
    (48.3321, 10.8957, 'Universität'),
    (48.1436, 11.5779, 'Odeonsplatz'),
    (48.1257, 11.5506, 'Poccistraße'),
    (48.1170, 11.5358, 'Harras'),
    (48.1152, 11.5198, 'Westpark'),
    (48.1160, 11.5022, 'Holzapfelkreuth'),
    (48.1231, 11.4840, 'Haderner'),
    (48.1811, 11.5115, 'Moosach'),
    (48.1833, 11.5316, 'Olympia-Einkaufszentrum'),
    (48.1861, 11.5468, 'Oberwiesenfeld'),
    (48.1713, 11.5729, 'Scheidplatz'),
    (48.1667, 11.5782, 'Bonner Platz'),
    (48.1296, 11.5584, 'Goetheplatz'),
    (48.0768, 11.5120, 'Thalkirchen'),
    (48.0884, 11.4810, 'Fürstenried West'),
    (48.1330, 11.5317, 'Heimeranplatz'),
    (48.1363, 11.5532, 'Theresienwiese'),
    (48.1403, 11.5600, 'Hauptbahnhof'),
    (48.1392, 11.5662, 'Karlsplatz'),
    (48.1356, 11.5989, 'Max-Weber-Platz'),
    (48.1533, 11.6203, 'Arabellapark'),
    (48.1354, 11.5019, 'Laimer Platz'),
    (48.1360, 11.5382, 'Schwanthalerhöhe'),
    (48.1274, 11.6050, 'Ostbahnhof'),
    (48.1207, 11.6200, 'Innsbrucker Ring'),
    (48.1012, 11.6462, 'Neuperlach Zentrum'),
    (48.0890, 11.6451, 'Neuperlach Süd'),
    (48.1334, 11.6906, 'Messestadt'),
    (48.1287, 11.6835, 'Trudering'),
    (48.1124, 11.5878, 'Untersbergstraße'),
    (48.1129, 11.5928, 'Giesing'),
    (48.1155, 11.5797, 'Silberhornstraße'),
    (48.1266, 11.6338, 'Josephsburg'),
    (48.1198, 11.5768, 'Kolumbusplatz'),
    (48.1457, 11.5653, 'Königsplatz'),
    (48.1621, 11.5687, 'Hohenzollernplatz'),
    (48.2106, 11.5722, 'Milbertshofen'),
    (48.2115, 11.5132, 'Hasenbergl'),
    (48.1701, 11.5244, 'Westfriedhof'),
    (48.1479, 11.5570, 'Stiglmaierplatz'),
    (48.1130, 11.5716, 'Candidplatz'),
    (48.0972, 11.5793, 'Mangfallplatz'),
]
TRAFFIC_COEFS = [1.2, 1.3, 1.2, 1.1, 1.0, 1.1, 1.2, 1.3, 1.4, 1.3, 1.2, 1.1]

ACCESS_TOKEN = os.environ.get("MAPBOX_TOKEN") or ""


class Mapbox:
    access_token: str

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_endpoint(self, src, dest, profile):
        '''Constructs an HTTP endpoint URL to which you can send a GET request.'''
        param_coordinates = f"{src[1]},{src[0]};{dest[1]},{dest[0]}"
        endpoint = f'https://api.mapbox.com/directions-matrix/v1/mapbox/{profile}/{param_coordinates}?access_token={self.access_token}'
        return endpoint

    def get_duration_matrix(self, src, dest, profile='driving'):
        '''Returns the duration matrix for the given coordinate list and profile.'''
        endpoint = self.get_endpoint(src, dest, profile)
        response = requests.get(endpoint)
        return endpoint, json.loads(response.text)


def run(n: int = 5):
    coordinates = COORDINATES[:n]
    mapbox = Mapbox(ACCESS_TOKEN)
    duration = []
    for i in range(n):
        print(f"Source i={i}")
        duration_src = []
        for j in range(n):
            duration_src_dest = []
            time.sleep(1)  # Maximum 60 requests per minute
            endpoint, response = mapbox.get_duration_matrix(coordinates[i], coordinates[j])
            if 'durations' not in response:
                print('Mapbox access key not provided!')
                return
            duration_value = response['durations'][0][1]
            for coefficient in TRAFFIC_COEFS:
                duration_src_dest.append(duration_value * coefficient)
            duration_src.append(duration_src_dest)
        duration.append(duration_src)
    duration = np.array(duration)
    np.save(f"../../../../data/mapbox/matrix_{n}.npy", duration)


if __name__ == "__main__":
    run()
