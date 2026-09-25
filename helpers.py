import datetime
from datetime import timedelta

#TIME CHOICES
def time_choices():
    start = datetime.datetime.strptime("7:00", "%H:%M")
    end = datetime.datetime.strptime("20:00","%H:%M")
    step = timedelta(minutes=30)
    time_choices_list = []
    current = start
    while current <= end:
        label = current.strftime("%H:%M")
        time_choices_list.append((label,label))
        current += step

    return time_choices_list
#TIME CALCULATING FUNCTION
def parse_session_time(start_time_str,duration_minutes):
    start_time_object = datetime.datetime.strptime(start_time_str,"%H:%M")
    end_time_object = start_time_object + timedelta(minutes=duration_minutes)
    return start_time_object.time(),end_time_object.time()
#CALCULATE DURATION
def duration_minutes_calculated(start_time,end_time):
    start = datetime.datetime.combine(datetime.date.today(),start_time)
    end = datetime.datetime.combine(datetime.date.today(),end_time)
    duration = end - start
    return duration.total_seconds()/60

#NAME ATTACH TO NUMBER OF SESSION
def package_lookup(tier_id):
    number_of_sess = {
        1:("Beginners",10),
        2:("Boxer",50),
        3:("Warrior",100),
        4:("Walk in", 1)
    }
    return number_of_sess[tier_id]

