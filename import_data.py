import pandas as pd
import re
import os

def read_UFAS_file_names(folder):
    file_names = os.listdir(folder)
    date_pattern = re.compile(r'\d{4}-\d{2}')
    filtered_file_names = [file for file in file_names if date_pattern.search(file)]
    return filter_file_names

def clean_UFAS_Data(filenames, fred_api_key):
    # Initialize Fred API for CPI data
    fred = Fred(api_key=fred_api_key)
    cpi_data = fred.get_series("CPIAUCSL").reset_index()
    cpi_data.columns = ['Date', 'CPI']

    # Read and clean salary data
    all_salaries = []
    for file in filenames:
        # Read Excel and clean column names
        df = pd.read_excel(file)
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Extract date from filename
        date_match = re.search(r'\d+-\d+', file)
        df['Date'] = date_match.group(0) if date_match else None

        all_salaries.append(df)

    # Combine all salary data
    salaries = pd.concat(all_salaries, ignore_index=True)

    # Create unique IDs for employees
    person_ids = salaries[['last_name', 'first_name']].drop_duplicates().reset_index(drop=True)
    person_ids['ID'] = person_ids.index + 1

    # Merge the data with unique IDs
    salary_data = salaries.merge(person_ids, on=['last_name', 'first_name'], how='left')

    # Adjust data and calculate additional fields
    salary_data['job_code'] = salary_data['job_code'].fillna(salary_data['jobcode'])
    salary_data['employee_category'] = salary_data['employee_category'].replace({
        "AS": "Academic Staff",
        "FA": "Faculty",
        "CJ": "University Staff", "CL": "University Staff", "CP": "University Staff",
        "ET1": "Employee-In-Training", "ET2": "Employee-In-Training",
        "ET3": "Employee-In-Training", "ET4": "Employee-In-Training",
        "LI": "Limited Appointee",
        "OT1": "Other", "OT2": "Other", "OT3": "Other",
        "OT4": "Other", "OT5": "Other", "OT6": "Other"
    })

    salary_data['annual_fte_adjusted_salary'] = salary_data.apply(
        lambda row: row['current_annual_contracted_salary'] * row['full_time_equivalent']
        if pd.isna(row['annual_fte_adjusted_salary']) else row['annual_fte_adjusted_salary'], axis=1
    )

    salary_data['FullTime'] = salary_data['full_time_equivalent'] == 1
    salary_data['JobGroup'] = salary_data['job_code'].str[:2]
    salary_data['JobNumber'] = salary_data['job_code'].str[2:]

    # Inflation adjustment
    salary_data = salary_data.merge(cpi_data, on='Date', how='left')
    cpi_2021 = cpi_data.loc[cpi_data['Date'] == '2021-11-01', 'CPI'].iloc[0]
    salary_data['2021_Index'] = cpi_2021 / salary_data['CPI']
    salary_data['FTE_Adjusted_Salary_2021_Dollars'] = salary_data['annual_fte_adjusted_salary'] * salary_data['2021_Index']

    # Return the cleaned DataFrame
    return salary_data


def job_group(jobcode):
    # Create a DataFrame for job groups
    category_codes = pd.DataFrame({
        'JobGroup': [code[:2] for code in jobcode]
    })

    categories = pd.DataFrame({
        'JobGroup': ["AE", "AD", "AN", "AR", "AT", "AV",
                     "CC", "CM", "CP", "DS", "EI", "EX",
                     "FA", "FN", "FP", "HR", "HS", "IC",
                     "IT", "LM", "OE", "PB", "PD", "RE",
                     "SC", "T0", "TL"],
        'JobGroupDescr': ["Academic Services and Student Experience",
                          "Administration", "Animal Care Services",
                          "Arts", "Athletics", "Advancement Services",
                          "Required by Statute", "Communications and Marketing",
                          "Compliance, Legal and Protection",
                          "Dining, Events, Hospitality Services, and Sales",
                          "Diversity, Equity, and Inclusion", "Executive",
                          "Faculty", "Finance", "Facilities and Capital Planning",
                          "Human Resources", "Health and Wellness Services",
                          "Instruction", "Information Technology",
                          "Libraries, Archives and Museums",
                          "Outreach and Community Engagement", "Public Broadcasting",
                          "Post Degree Training", "Research",
                          "Sponsored Programs, Grants and Contracts",
                          "Other", "Teaching and Learning"]
    })

    # Merge the data
    data = pd.merge(category_codes, categories, on="JobGroup", how="left")

    # Return the JobGroup descriptions
    return data['JobGroupDescr'].tolist()
