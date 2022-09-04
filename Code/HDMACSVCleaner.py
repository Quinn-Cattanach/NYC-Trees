
import csv;
from enum import *;
import sys;
import re;
import numpy as np;
import pandas as pd;

class FilenameChecker:

    def __init__(self):
        pass

    def patchFilename(
        filename: str,
        expectedExtension: str
    ):
        pattern = r"\w+\." + expectedExtension

        if re.fullmatch(pattern, filename):
            return filename
        else:
            filename = re.sub(
                r"\s",
                "_",
                filename
            )
            filename = re.sub(
                r"\W",
                "?",
                filename
            )
            filename = re.sub(
                r"\.",
                ":",
                filename
            )
            filename += "." + expectedExtension



class HDMAReader:

    def __init__(self):
        pass

    def generateCSV (
        filename: str,
        options: list = None,
        delimiter: str = ",",
        quotechar: str = "\""
    ):
        pass

    class CSVOption(Enum):
        includeDamagedData = 0

    class HDMAHeader(Enum):
        id = "respondent_id"
        agency = "agency_name"

print(HDMAReader.CSVOption.includeDamagedData.__class__)

