import requests
import json

#OpenSky API endpoint
url = "https://opensky-network.org/api/states/all"

#request data from OpenSky API
response = requests.get(url)

#Check if the request was successful
if response.status_code == 200:
    data = response.json()

    #get first 5 aircraft states
    states = data['states'][:5]

    for state in states:
        callsign = state[1]
        longitude = state[5]
        latitude = state[6]
        altitude = state[7]

        print(f"Callsign: {callsign}, Longitude: {longitude}, Latitude: {latitude}, Altitude: {altitude} meters")
else:
    print(f"Error: {response.status_code} - Unable to fetch data from OpenSky API")
    