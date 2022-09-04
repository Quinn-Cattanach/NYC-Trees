
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests

#   2005 and 2015 Tree Census Headers that are needed.
#   Makes cleaning code more reusable, and can be expanded to even more censuses
#   by creating new classes.
class TC2005:
    borough_name = "boroname"
    tree_diameter_at_breast_height = "tree_dbh"
    species_latin_name = "spc_latin"
    species_common_name = "spc_common"
    status = "status"
class TC2015:
    borough_name = "boroname"
    tree_diameter_at_breast_height = "tree_dbh"
    species_latin_name = "spc_latin"
    species_common_name = "spc_common"
    status = "health"

#   Boroughs of NYC, ordered.
boroughs = [
    "bronx",
    "brooklyn",
    "manhattan",
    "queens",
    "staten island"
]

#   Helper function to fix mismatched types and formats for borough names "Bronx" / 1 / "1":
def correct_borough(item: any, dtype: type = str) -> any:
    
    item = str(item).strip().lower()
    if item in boroughs:
        if dtype is int:
            return boroughs.index(item) + 1
        if dtype is str:
            return item
    else:
        if item.isdigit():
            if dtype is int:
                return int(item)
            if dtype is str:
                return boroughs[int(item) - 1]
        else:
            print(f"Warning: Borough not found: {item} type: {type(item)}.")

#   Cleans and exports a JSON with manipulated data
def clean_tree_census(filename: str, Headers: type, exportFilename: str = None, include_dead = False) -> pd.DataFrame:

    clean_data = {}

    with open(filename, "r") as infile:
        df = pd.read_csv(infile, low_memory=False)

    #   Correct borrough data
    col = []
    for item in df[Headers.borough_name]:
        col.append(correct_borough(item))
    df[Headers.borough_name] = col

    #   Remove dead and dying trees.
    if not include_dead:
        df = df[(df[Headers.status] == "Good") | (df[Headers.status] == "Excellent") | (df[Headers.status] == "Poor")]

    #   Copy over necessary data.
    ndf = pd.DataFrame({
        "Borough": df[Headers.borough_name],
        "Genus": df[Headers.species_latin_name],
        "Common_Name": df[Headers.species_common_name],
        "Diameter_Inches": df[Headers.tree_diameter_at_breast_height]
    })

    # Deallocate df since very large.
    df = None

    #   Convert scientific name to just its Genus. If is nan, convert to "unknown"
    def getGenus(x) -> str:
        if not pd.isna(x):
            return x.lower().split()[0]
        else:
            return "unknown"
    ndf["Genus"] = ndf["Genus"].apply(getGenus)

    #   Get number of trees in each biological Genus.
    #   Different families can have different rates of sequestration.
    counts = ndf.groupby(["Borough","Genus"], as_index=False)["Common_Name"].count()
    for _, row in counts.iterrows():
        if row["Borough"] in clean_data and "tree_types" in clean_data[row["Borough"]]:
            clean_data[row["Borough"]]["tree_types"][row["Genus"]] = row["Common_Name"]
        else:
            clean_data[row["Borough"]] = {
                "tree_types" : {
                    row["Genus"] : row["Common_Name"]
                }
            }

    #   Total number of trees in borough.
    sums = counts.groupby("Borough", as_index=False)["Common_Name"].sum()
    for _,v in sums.iterrows():
        clean_data[v["Borough"]]["total_num_trees"] = v["Common_Name"]

    #   Get diameter at breast height of each tree. 
    #   This is useful, as trees with a greater diameter typically sequester more carbon.
    diameters = ndf.groupby("Borough", as_index=False)["Diameter_Inches"].mean().round(2)
    for _,v in diameters.iterrows():
        clean_data[v["Borough"]]["average_diameter_inches"] = v["Diameter_Inches"]

    #   Get area of each borrough; calculate average number of trees per square mile.
    req = requests.get("https://en.wikipedia.org/wiki/Boroughs_of_New_York_City")
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, "html.parser")
        index = 0
        for i in soup.find_all("tr", {"style":"background:#f9f9f9;"}):
            area = float(i.find_all("td")[4].text.strip())
            clean_data[boroughs[index]]["area_sq_mi"] = area
            clean_data[boroughs[index]]["avg_num_trees_per_sq_mi"] = round(clean_data[boroughs[index]]["total_num_trees"] / area, 2)
            index += 1

    #   Get trees per square mile.

    #   Export if filename passed:
    if exportFilename != None:
        with open(exportFilename, "w") as outfile:
            json.dump(clean_data, outfile)

clean_tree_census("Sources/2005_Street_Tree_Census.csv", TC2005, "TreeOutfile2005.json")
clean_tree_census("Sources/2015StreetTreesCensus_TREES.csv", TC2015, "TreeOutfile2015.json")