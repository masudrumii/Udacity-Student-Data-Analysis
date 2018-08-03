####################################################################
#################### 1. Questions      #############################
####################################################################

# How do students who pass projects different from who doesn't ?



####################################################################
#################### 2. Data Wrangling #############################
####################################################################

import unicodecsv
from datetime import datetime as dt
from collections import defaultdict
import numpy as np

def read_csv(dataSet):
    #dataSet : CSV file name as input
    #Returns as a dictionary
    with open(dataSet, 'rb') as filestream:
        reader = unicodecsv.DictReader(filestream)
        dataDict = list(reader)
    return dataDict

def unique_students(dataset):
    #dataset : takes dictionary generated from read_csv() function
    #Retuns the set of account_key, which is unique student account list
    studentSet = set()
    for data in dataset:
        studentSet.add(data['account_key'])
    return studentSet


# CSV dataset (files)
enrollmentData = 'enrollments.csv'
daily_engagementData = 'daily_engagement.csv'
project_submission = 'project_submissions.csv'


#reading csv files by using read_csv() function
enrollments = read_csv(enrollmentData)
daily_engagements = read_csv(daily_engagementData)
project_submissions = read_csv(project_submission)



##########################################################
########## Data Cleaning #################################
##########################################################
# Fixing dictionary key name
for daily_record in daily_engagements:    
    daily_record['account_key'] = daily_record['acct']
    del daily_record['acct']


#Takes a date as a string, and returns a Python datetime object.
#If there is no date given, returns None

def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')

#Takes a string which is either an empty string or represents an integer,
#and returns an int or None

def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)


# Clean up the data types in the enrollments table
for enrollment in enrollments:
    enrollment['account_key'] = parse_maybe_int(enrollment['account_key'])
    enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
    enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
    enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
    enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
    enrollment['join_date'] = parse_date(enrollment['join_date'])

#print(enrollments[0])

# Clean up the data types in daily_engagements table
for daily_record in daily_engagements:
    daily_record['utc_date'] = parse_date(daily_record['utc_date'])
    daily_record['num_courses_visited'] = parse_maybe_int(float(daily_record['num_courses_visited']))
    daily_record['total_minutes_visited'] = float(daily_record['total_minutes_visited'])
    daily_record['projects_completed'] = parse_maybe_int(float(daily_record['projects_completed']))
    daily_record['account_key'] = parse_maybe_int(daily_record['account_key'])
    daily_record['lessons_completed'] = parse_maybe_int(float(daily_record['lessons_completed']))

#print(daily_engagements[0])

# Clean up the data types in project_submissions table

for project in project_submissions:
    project['creation_date'] = parse_date(project['creation_date'])
    project['completion_date'] = parse_date(project['completion_date'])
    project['account_key'] = parse_maybe_int(project['account_key'])
    project['lesson_key'] = parse_maybe_int(project['lesson_key'])


enrollments_num_rows = len(enrollments)
#print('Total Enrollments : ', enrollments_num_rows)
enrollments_unique_students = len(unique_students(enrollments))
#print('Unique students in enrollments : ', enrollments_unique_students)


daily_engagement_num_rows = len(daily_engagements)
#print('Total daily Engagement : ', daily_engagement_num_rows)
engagement_unique_students = unique_students(daily_engagements)
num_of_daily_unique_students = len(engagement_unique_students)
#print('Unique students in daily engagement :', num_of_daily_unique_students)


project_submission_num_rows = len(project_submissions)
#print('Total project submitted : ', project_submission_num_rows)
project_submission_unique_students = len(unique_students(project_submissions))
#print('Unique Students submitted projects : ', project_submission_unique_students)

udacity_test_accounts = set()

for enrollment in enrollments:
    if enrollment['is_udacity']:
        udacity_test_accounts.add(enrollment['account_key'])

#print('Total udacity test accounts : ', len(udacity_test_accounts))
    
def remove_udacity_test_account(data):
    non_udacity_data = []
    for data_point in data:
        if data_point['account_key'] not in udacity_test_accounts:
            non_udacity_data.append(data_point)
    return non_udacity_data

non_udacity_enrollments = remove_udacity_test_account(enrollments)
non_udacity_engagements = remove_udacity_test_account(daily_engagements)
non_udacity_project_submissions = remove_udacity_test_account(project_submissions)

#print(len(non_udacity_enrollments))
#print(len(non_udacity_engagements))
#print(len(non_udacity_project_submissions))


############################################################################
#################### 3. Data Exploration ###################################
############################################################################


paid_students = {}

for enrollment in non_udacity_enrollments:
    if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']

        if account_key not in paid_students or \
               enrollment_date > paid_students[account_key]:
            paid_students[account_key] = enrollment_date

print('Total paid students : ', len(paid_students))


# Takes a student's join date and the date of a specific engagement record,
# and returns True if that engagement record happened within one week
# of the student joining
def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7 and time_delta.days >= 0


def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data


paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments)
paid_engagement = remove_free_trial_cancels(non_udacity_engagements)
paid_submissions = remove_free_trial_cancels(non_udacity_project_submissions)

print('Paid enrollments : ', len(paid_enrollments))
print('Paid engagements : ', len(paid_engagement ))
print('Paid Submissions : ', len(paid_submissions))


for engagement_record in paid_engagement:
    if engagement_record['num_courses_visited'] > 0:
        engagement_record['has_visited'] = 1
    else:
        engagement_record['has_visited'] = 0



paid_engagement_in_first_week = []

for engagement_record in paid_engagement:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_date = engagement_record['utc_date']

    if within_one_week(join_date, engagement_date):
        paid_engagement_in_first_week.append(engagement_record)

print('\nPaid engagement in first week : ', len(paid_engagement_in_first_week))

def create_group_value_list(data):
    total_values = []
    for data_point in data.values():
        total_values.append(data_point)
    return total_values

def group_data(data, key_name):
    group_information = defaultdict(list)
    
    for data_point in data:
        data_key = data_point[key_name]
        group_information[data_key].append(data_point)
    return group_information




def describe_data(data):
    print('Mean : ', np.mean(data))
    print('Standard deviation : ',np.std(data))
    print('Minimum : ', np.min(data))
    print('Maximum : ', np.max(data))
    

def sum_group_items(data, key_name):
    group_information = {}

    for account_key, information in data.items():
        sum_data = 0
        for data_point in information:
            sum_data += data_point[key_name]
        group_information[account_key] = sum_data
    return group_information




engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')

print('\nFirst week students spending time information -- ')
total_minutes_by_account = sum_group_items(engagement_by_account, 'total_minutes_visited')
total_minutes = create_group_value_list(total_minutes_by_account)
describe_data(total_minutes)    


print('\nFirst week lessons completion information -- ')
total_lessons_by_account = sum_group_items(engagement_by_account, 'lessons_completed')
total_lessons = create_group_value_list(total_lessons_by_account)
describe_data(total_lessons)

print('\nDays visited by account -- ')
total_days_visited_by_account = sum_group_items(engagement_by_account, 'has_visited')
total_days = create_group_value_list(total_days_visited_by_account)
describe_data(total_days)



#Check how many students passed on specific projet

subway_project_lesson_keys = [746169184, 3176718735]

pass_subway_project = set()

for submission in paid_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating']
    
    if project in subway_project_lesson_keys and \
           (rating == 'PASSED' or rating == 'DISTINCTION'):
        pass_subway_project.add(submission['account_key'])

print('\nStudents passed on Subway Project : ', len(pass_subway_project))


passing_engagement = []
non_passing_engagement = []

for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] in pass_subway_project:
        passing_engagement.append(engagement_record)
    else:
        non_passing_engagement.append(engagement_record)


print('\nPassing Engagement : ', len(passing_engagement))
print('Non Passing Engagement  : ', len(non_passing_engagement))


passing_engagement_by_account = group_data(passing_engagement, 'account_key')
non_passing_engagement_by_account = group_data(non_passing_engagement, 'account_key')


print('\nNon-passing students. Minutes visited in First Week ')
non_passing_minutes = sum_group_items(non_passing_engagement_by_account, 'total_minutes_visited')
non_passing_total_minutes = create_group_value_list(non_passing_minutes)
describe_data(non_passing_total_minutes)


print('\nPassing students. Minutes visited in First Week :')
passing_minutes = sum_group_items(passing_engagement_by_account, 'total_minutes_visited')
passing_total_minutes = create_group_value_list(passing_minutes)
describe_data(passing_total_minutes)


print('\nNon-passing students. Lessons Completed in First Week ')
non_passing_lessons_completed = sum_group_items(non_passing_engagement_by_account, 'lessons_completed')
non_passing_total_lessons = create_group_value_list(non_passing_lessons_completed)
describe_data(non_passing_total_lessons)

print('\nPassing students. Lessons Completed in First Week :')
passing_lessons_completed = sum_group_items(passing_engagement_by_account, 'lessons_completed')
passing_total_lessons = create_group_value_list(passing_lessons_completed)
describe_data(passing_total_lessons)


print('\nNon-passing students. Days visited in First Week ')
non_passing_lessons_visited = sum_group_items(non_passing_engagement_by_account, 'has_visited')
non_passing_total_lessons_visited = create_group_value_list(non_passing_lessons_visited)
describe_data(non_passing_total_lessons_visited)


print('\nPassing students. Days visited in First Week :')
passing_lessons_visited = sum_group_items(passing_engagement_by_account, 'has_visited')
passing_total_lessons_visited = create_group_value_list(passing_lessons_visited)
describe_data(passing_total_lessons_visited)


