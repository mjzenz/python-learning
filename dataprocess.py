import numpy as np
import pandas as pd
import keyring
import import_data

fredapi_key = "key"


filenames = import_data.read_ufas_file_names("data")
salary_data = import_data.clean_ufas_data(filenames, fredapi_key)
# Example usage
files = ["2021_12.xlsx", "2022_06.xlsx", "2024_01.xlsx"]
fred_api_key = "YOUR_FRED_API_KEY"
cleaned_data = clean_UFAS_Data(files, fred_api_key)
print(cleaned_data.head())

