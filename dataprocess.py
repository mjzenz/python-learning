import numpy as np
import pandas as pd
import keyring
import import_data

fred_api_key = keyring.get_password("fredapi","fredapi")

filenames = import_data.read_ufas_file_names("data")

#Basic Data Cleaning
salary_data = import_data.clean_ufas_data(filenames, fred_api_key)

#Remove 0 FTE appointments
