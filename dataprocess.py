import numpy as np
import pandas as pd
import keyring
import import_data

fred_api_key = keyring.get_password("fredapi","fredapi")

faculty_instruction_research_jobgroups = [
    'Instruction', 'Animal Care Services', 'Faculty','Research']

non_teaching_titles_TLA = [
    'Teach, Learn, & Tech Spec II',
       'Teach, Learn, & Tech Spec I',
       'Cont Edu Prog Dir', 'Early Child Edu Asst Teacher',
       'Teach, Learn & Tech Spec III', 'Early Child Edu Teacher',
       'Teaching, Learning, & Tech Dir',
       'Cont Edu Specialist', 'Teaching, Learning, & Tech Mgr',
       'Instructional Administrator', 'Academic Assessment Dir (Inst)',
       'Education Technical Consultant', 'Academic Assessment Specialist',
       'Athletics Learning Specialist', 'Cont Edu Prog Mgr',
       'Cont Edu Prog Instructor', 'Cont Edu Prog Dir (C)',
       'Psychometrician',  'Music Coach',
       'Academic Assessment Manager', 'Early Child Edu Dir',
       'Academic Assessment Coord', 'Assistant Teaching Professor',
       'Tutor', 'Early Child Edu Assoc Dir',
       'Cont Edu Prog Dir (B)', 'Preceptor',
        'Cont Edu Prog Assoc Dir',
        'Instructional & Media Designer',
       'Teaching & Learning Developer']


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
    .division
    .unique())

salary_data['IsFacultyDivision'] = salary_data['division'].isin(faculty_division_list)
salary_data['IsFacResTeachingTitle'] = (
     salary_data['jobgroup'].isin(non_teaching_titles_TLA) &
        ~((salary_data['jobgroup'] == 'Teaching and Learning') &
        salary_data['title'].isin(faculty_instruction_research_jobgroups))

)




#Determine proprortions of each employment category
department_jobgroup_prop = (
    salary_data[['division','department','Date','jobgroup','full_time_equivalent']]
    .groupby([salary_data['division'],salary_data['department'], salary_data['Date'], salary_data['jobgroup']])
    .sum('full_time_equivalent'))

# Calculate total FTE per (division, department, Date)
department_jobgroup_prop['total_fte'] = (
    department_jobgroup_prop
    .groupby(['division', 'department', 'Date'])
    .sum('full_time_equivalent'))


# Calculate proportion
department_jobgroup_prop['fte_proportion'] = (
    department_jobgroup_prop['full_time_equivalent'] /
    department_jobgroup_prop['total_fte']
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

