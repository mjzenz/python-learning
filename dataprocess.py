import numpy as np
import pandas as pd
import keyring
import import_data

fred_api_key = keyring.get_password("fredapi","fredapi")

filenames = import_data.read_ufas_file_names("data")
#Basic Data Cleaning
salary_data = import_data.clean_ufas_data(filenames, fred_api_key)

#Remove 0 FTE appointments
salary_data = salary_data.loc[salary_data.full_time_equivalent > .01]
salary_data["jobgroup"] = import_data.job_group(salary_data.jobcode)


#List of divisions with faculty appointments
faculty_division_list = (
    salary_data
    .loc[salary_data.employee_category == "Faculty"]
    .division)
#This doesn't work.
college_admin_departments_lists = (
    salary_data
    .loc[salary_data.division in faculty_division_list]
)
admin_ss_division_list = ['Div for Teaching and Learning',
       'Graduate School', 'General Educational Admin',
       'Recreation & Wellbeing', 'Collab Adv Learning & Teaching',
        'Division of Student Life', 'Wisconsin Union',  'Information Technology' ,
        'Enrollment Management', 'VC for Rsrch & Grad Education', 'General Services',
        'Facilities Planning & Mgmt']

dept_fte = (salary_data
            .groupby([salary_data['division'], salary_data['department'], salary_data['Date']])
            .sum('full_time_equivalent')
            .pivot_table(index = ['division', 'department'],columns = ['Date'], values = ['full_time_equivalent']))

