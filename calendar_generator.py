import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from ics import Calendar, Event
import holidays
from datetime import datetime, timedelta, date
import prompts
import pytz
from pytz import timezone


# Global Variables
MINDATE = datetime.today()
MINDATE = MINDATE.replace(hour=0, minute=0, second=0, microsecond=0)

# Load the .env file
_ = load_dotenv(find_dotenv())

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Set timezone
local_tz = timezone('America/Los_Angeles')

# Prompt the user for subject info

subject = input("What is the subject you want to learn? ")

while True:
    link_input = input("Do you have a link to a guiding resource? (yes/no): ").strip().lower()
    if link_input in {'yes', 'no'}:
        has_link = link_input == 'yes'  # Convert to a boolean
        break
    else:
        print("Please enter 'yes' or 'no'.")

link = None
if has_link == True:
    link = input("Please enter the link to the guiding resource: ")

# Prompt user for time commitment info

# Get start and end dates
while True:
    start_date_input = input("When do you want to start learning? (YYYY-MM-DD): ")
    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        if start_date < MINDATE:
            print(f"You entered {start_date}. The earliest date is {MINDATE}.")
            raise ValueError
        break
    except ValueError:
        print("Please enter a valid date [earliest date is today] (YYYY-MM-DD).")

while True:
    end_date_input = input("When is the latest that you want to finish learning? (YYYY-MM-DD): ")
    try:
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
        if end_date <= start_date:
            raise ValueError
        break
    except ValueError:
        print("Please enter a valid date [earliest date is after start date] (YYYY-MM-DD).")

# GET ACTIVE DAYS
while True:
    active_days_input = input("What days are you available to study? (e.g. 0 2 3 4 (where 0 = Monday, 1 = Tuesday, ..., 6 = Sunday)): ")
    try :
        active_days = list(map(int, active_days_input.split()))
        if not all(0 <= day <= 6 for day in active_days):
            raise ValueError
        break
    except ValueError:
        print("Please enter a combination of valid days (0 1 2 3 4 5 6).")
    

# CHECK HOLIDAYS
while True:
    holidays_input = input("Do you want to work on holidays? (yes/no): ").strip().lower()
    if holidays_input in {'yes', 'no'}:
        work_holidays = holidays_input == 'yes'  # Convert to a boolean
        break
    else:
        print("Please enter 'yes' or 'no'.")



# GET @ WHAT TIME TO STUDY
while True:
    start_time_input = input("What time do you want to start studying? (HH:MM): ")
    try:
        start_time = datetime.strptime(start_time_input, "%H:%M")
        break
    except ValueError:
        print("Please enter a valid time (HH:MM).")


# GET DAILY STUDY HOURS

while True:
    user_input_hours = input("How many hours do you want to study each day? (HH:MM): ")
    try:
        hours, minutes = map(int, user_input_hours.split(":"))

        if hours < 0 or minutes < 0 or minutes >= 60:
            raise ValueError("Invalid time format.")
        
        daily_study_minutes = hours * 60 + minutes
        time_left_in_day = (24 * 60) - (start_time.hour * 60 + start_time.minute)


        if daily_study_minutes <= 0 or daily_study_minutes > time_left_in_day:
            raise ValueError(f"Time exceeds the available time left in the day ({time_left_in_day // 60} hours and {time_left_in_day % 60} minutes).")

        break
    except ValueError as e:
        print(f"Error: {e}. Please enter a valid time in HH:MM format.")

# CALCULATE TOTAL # DAYS AVAILABLE
total_days = 0
count_date = start_date

while count_date <= end_date:
    if(count_date.weekday() in active_days):
        if work_holidays == True or count_date not in holidays.US():
            total_days += 1

    count_date += timedelta(days=1)




# OPENAI API CALL

# Include subject, link, and total_days in the prompt

model = "gpt-4o-mini"
temperature = 0.3
max_tokens = 1500


system_message = prompts.system_message
prompt = prompts.generate_prompt(subject, link, total_days, daily_study_minutes) 

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": prompt}
]

def get_tasks():
    completion = client.chat.completions.create(
        model = model,
        messages = messages,
        temperature = temperature,
        max_tokens = max_tokens,
    )

    return completion.choices[0].message.content



# FILL IN TASKS

# Extract tasks array from OpenAI's response
response_text = get_tasks()

# Namespace for safely evaluating tasks
namespace = {}

try:
    # Extract the actual array content using string manipulation
    start_index = response_text.find("[")
    end_index = response_text.rfind("]") + 1  # Include the closing bracket
    tasks_array_content = response_text[start_index:end_index]

    # Dynamically evaluate the tasks array content
    exec(f"tasks = {tasks_array_content}", namespace)
    tasks = namespace.get("tasks")

    if not tasks:
        raise ValueError("The response does not contain a valid `tasks` array.")

except Exception as e:
    print(f"Error extracting tasks: {e}")
    tasks = []  # Default to an empty list if extraction fails

# Check if tasks were successfully extracted
if not tasks:
    print("Failed to generate a tasks array. Exiting.")
    exit(1)

# Print tasks for debugging
print("Extracted tasks:")
for title, activities in tasks:
    print(f"- {title}:")
    for activity in activities:
        print(f"  - {activity}")


# CREATE CALENDAR

# Initialize the calendar
calendar = Calendar()

# Start adding tasks to the calendar
current_date = start_date
for title, task_list in tasks:
    # Skip non-active days
    while current_date.weekday() not in active_days or (
        not work_holidays and current_date in holidays.US()
    ):
        current_date += timedelta(days=1)

    # Create and add the event
    event = Event()
    event.name = title
    event.begin = datetime.combine(current_date, start_time.time(), tzinfo=local_tz)
    event.description = "\n".join(task_list)
    event.duration = timedelta(minutes=daily_study_minutes)
    calendar.events.add(event)

    # Move to the next active day
    current_date += timedelta(days=1)

# Save the calendar to a .ics file
calendar_path = f"calendars/{subject.replace(' ', '_')}_Learning_Calendar.ics"
with open(calendar_path, 'w') as file:
    file.writelines(calendar)

print(f"Calendar saved as {calendar_path}")




