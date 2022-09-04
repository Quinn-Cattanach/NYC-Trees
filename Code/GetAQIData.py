import requests
import numpy as np
import pandas as pd
import csv

#   Directory of locations with their corresponding borrough.
directory = {
    "staten island" : {
        "Southern SI",
        "Northern SI",
        "Willowbrook",
        "South Beach and Willowbrook (CD2)",
        "Port Richmond",
        "Tottenville and Great Kills (CD3)",
        "Stapleton - St. George",
        "South Beach - Tottenville",
        "St. George and Stapleton (CD1)"
    },
    "bronx" : {
        "Bronx",
        "South Bronx"
    },
    "queens" : {
        "Hillcrest and Fresh Meadows (CD8)",
        "Southeast Queens",
        "South Ozone Park and Howard Beach (CD10)",
        "Kew Gardens and Woodhaven (CD9)",
        "Rockaway and Broad Channel (CD14)",
        "Jamaica and Hollis (CD12)",
        "Bayside and Little Neck (CD11)",
        "Rockaways",
        "Flushing and Whitestone (CD7)",
        "Southwest Queens",
        "Ridgewood and Maspeth (CD5)",
        "Queens Village (CD13)",
        "Bayside Little Neck-Fresh Meadows",
        "Jamaica",
        "Fresh Meadows",
        "Rego Park and Forest Hills (CD6)"
    },
    "manhattan" : {
        "Chelsea-Village",
        "Upper East Side-Gramercy",
        "Union Square-Lower Manhattan",
    }
}

#   Gets and then extracts data from the air quality api.
def get_aqi_data(outfile_name: str):

    #   Make request.
    response = requests.get("https://data.cityofnewyork.us/resource/c3uy-2p5r.json")
    data = response.json()

    #   Skeleton for data.
    aqi_data = {
        "bronx": {},
        "manhattan": {},
        "queens": {},
        "staten island": {},
    }

    #   extract data
    for item in data:
        #   Find the borough of the location.
        location_name = item["geo_place_name"].strip()
        borough = None
        for key in directory.keys():
            if location_name in directory[key]:
                borough = key
                break
        if borough == None:
            print(f"\"{location_name}\" not found in borough directory.")
            continue

        period = item["time_period"]
        measurement_name = item["name"]
        aqi_value = round(float(item["data_value"]), 2)

        #   Filter to only annual averages.
        if ("annual average" in period.lower()) and (measurement_name == "Fine Particulate Matter (PM2.5)"):
            year = int(period.split()[-1])
            if year in aqi_data[borough]:
                np.append(aqi_data[borough][year], aqi_value)
            else:
                aqi_data[borough][year] = np.array([aqi_value])
    
    #   Average the aqui values in each borough.
    for key in aqi_data.keys():
        aqi_data[key] = [(year, round(float(aqi_data[key][year].mean()), 2)) for year in aqi_data[key]]
        aqi_data[key].sort(key=lambda year: year[0])

    #   Format csv data.
    headers = ["borough"] + [f"{year}_avg_part_matter_mcg/m^3" for year, _ in aqi_data["bronx"]]
    csv_data = [
        headers
    ]
    for key in aqi_data.keys():
        csv_data.append([key] + [value for _, value in aqi_data[key]])

    #   Write to csv.
    with open(outfile_name, "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(csv_data)

get_aqi_data("AirQuality.csv")




