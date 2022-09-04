
import sys
from time import sleep
import requests
from bs4 import BeautifulSoup
import csv

def get_cancer_data(outfile_name: str, sleep_time: int):

    #   Helper method for making a request and getting cancer rate data.
    def findCancerData(url: str) -> list[float]:
        req = requests.get(url)
        if req.status_code != 200:
            print(f"Failed to access url {url} with status code {req.status_code}")
            return
        soup = BeautifulSoup(req.text, "html.parser")

        rates_per_hundred_thousand = []
        for y in range(2000,2019):
            item = soup.find("td", {"headers" : f"y{y} inc b_inc b_inc_r"})
            rates_per_hundred_thousand.append(float(item.text))
        return rates_per_hundred_thousand

    #   Display the status of the requests.
    def sleep_with_status():
        for num in range (0,sleep_time): 
            sleep(1) 
            print(f"Waiting {sleep_time - num} more seconds for next request{'.'*(1 + num % 3) + ' '*(3 - (1 + num % 3))}", end="\r")
        print(f"Making request." + " " * 30, end="\r")

    #   Find the cancer data for each borough. Sleeps the given time between
    #       each request to satisfy ethics expectation.
    bronx = ["bronx"] + findCancerData("https://www.health.ny.gov/statistics/cancer/registry/table2/tb2lungbronx.htm")
    sleep_with_status()
    brooklyn = ["brooklyn"] + findCancerData("https://www.health.ny.gov/statistics/cancer/registry/table2/tb2lungkings.htm")
    sleep_with_status()
    manhattan = ["manhattan"] + findCancerData("https://www.health.ny.gov/statistics/cancer/registry/table2/tb2lungnewyork.htm")
    sleep_with_status()
    queens = ["queens"] + findCancerData("https://www.health.ny.gov/statistics/cancer/registry/table2/tb2lungqueens.htm")
    sleep_with_status()
    stat_isl = ["staten island"] + findCancerData("https://www.health.ny.gov/statistics/cancer/registry/table2/tb2lungrichmond.htm")

    #   Put data into a list and export to the outfile csv.
    headers = ["borough"] + [f"{x}_rate_per_100k" for x in range(2000,2019)]
    data = [
        headers,
        bronx,
        brooklyn,
        manhattan,
        queens,
        stat_isl
    ]

    with open(outfile_name, "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)

get_cancer_data("CancerData.csv", 30)
