from datetime import datetime

# Course data with LEC and LAB schedules
course_data = {
    "ENGG*3390*0101": {
        "LEC": [("Tuesday", "1:00 PM - 2:20 PM"), ("Thursday", "1:00 PM - 2:20 PM")],
        "LAB": [("Friday", "11:30 AM - 1:20 PM")]
    },
    "ENGG*3390*0102": {
        "LEC": [("Tuesday", "1:00 PM - 2:20 PM"), ("Thursday", "1:00 PM - 2:20 PM")],
        "LAB": [("Thursday", "8:30 AM - 10:20 AM")]
    },
    "ENGG*3390*0103": {
        "LEC": [("Tuesday", "1:00 PM - 2:20 PM"), ("Thursday", "1:00 PM - 2:20 PM")],
        "LAB": [("Wednesday", "9:30 AM - 11:20 AM")]
    },
    "ENGG*3390*0201": {
        "LEC": [("Tuesday", "10:00 AM - 11:20 AM"), ("Thursday", "10:00 AM - 11:20 AM")],
        "LAB": [("Friday", "11:30 AM - 1:20 PM")]
    },
    "ENGG*3390*0203": {
        "LEC": [("Tuesday", "10:00 AM - 11:20 AM"), ("Thursday", "10:00 AM - 11:20 AM")],
        "LAB": [("Wednesday", "9:30 AM - 11:20 AM")]
    },
    "ENGG*3390*0204": {
        "LEC": [("Tuesday", "10:00 AM - 11:20 AM"), ("Thursday", "10:00 AM - 11:20 AM")],
        "LAB": [("Thursday", "12:30 PM - 2:20 PM")]
    },
    "ENGG*3450*0101": {
        "LEC": [("Monday", "12:30 PM - 1:20 PM"), ("Wednesday", "12:30 PM - 1:20 PM"), ("Friday", "12:30 PM - 1:20 PM")],
        "LAB": [("Monday", "3:30 PM - 5:20 PM")]
    },
    "ENGG*3450*0102": {
        "LEC": [("Monday", "12:30 PM - 1:20 PM"), ("Wednesday", "12:30 PM - 1:20 PM"), ("Friday", "12:30 PM - 1:20 PM")],
        "LAB": [("Wednesday", "3:30 PM - 5:20 PM")]
    },
    "ENGG*3450*0103": {
        "LEC": [("Monday", "12:30 PM - 1:20 PM"), ("Wednesday", "12:30 PM - 1:20 PM"), ("Friday", "12:30 PM - 1:20 PM")],
        "LAB": [("Friday", "3:30 PM - 5:20 PM")]
    },
    "ENGG*3450*0201": {
        "LEC": [("Monday", "8:30 AM - 9:20 AM"), ("Wednesday", "8:30 AM - 9:20 AM"), ("Friday", "8:30 AM - 9:20 AM")],
        "LAB": [("Monday", "3:30 PM - 5:20 PM")]
    },
    "ENGG*3450*0202": {
        "LEC": [("Monday", "8:30 AM - 9:20 AM"), ("Wednesday", "8:30 AM - 9:20 AM"), ("Friday", "8:30 AM - 9:20 AM")],
        "LAB": [("Wednesday", "3:30 PM - 5:20 PM")]
    },
    "ENGG*3450*0203": {
        "LEC": [("Monday", "8:30 AM - 9:20 AM"), ("Wednesday", "8:30 AM - 9:20 AM"), ("Friday", "8:30 AM - 9:20 AM")],
        "LAB": [("Friday", "3:30 PM - 5:20 PM")]
    },
    "ENGG*3640*0101": {
        "LEC": [("Monday", "1:30 PM - 2:20 PM"), ("Wednesday", "1:30 PM - 2:20 PM"), ("Friday", "1:30 PM - 2:20 PM")],
        "LAB": [("Monday", "2:30 PM - 5:20 PM")]
    },
    "ENGG*3640*0102": {
        "LEC": [("Monday", "1:30 PM - 2:20 PM"), ("Wednesday", "1:30 PM - 2:20 PM"), ("Friday", "1:30 PM - 2:20 PM")],
        "LAB": [("Wednesday", "2:30 PM - 5:20 PM")]
    },
    "ENGG*3640*0103": {
        "LEC": [("Monday", "1:30 PM - 2:20 PM"), ("Wednesday", "1:30 PM - 2:20 PM"), ("Friday", "1:30 PM - 2:20 PM")],
        "LAB": [("Friday", "2:30 PM - 5:20 PM")]
    },
    "ENGG*3700*0101": {
        "LEC": [("Tuesday", "11:30 AM - 12:50 PM"), ("Thursday", "11:30 AM - 12:50 PM")],
        "LAB": [("Friday", "2:30 PM - 4:20 PM")]
    },
    "ENGG*3700*0102": {
        "LEC": [("Tuesday", "11:30 AM - 12:50 PM"), ("Thursday", "11:30 AM - 12:50 PM")],
        "LAB": [("Wednesday", "2:30 PM - 4:20 PM")]
    },
    "ENGG*3700*0103": {
        "LEC": [("Tuesday", "11:30 AM - 12:50 PM"), ("Thursday", "11:30 AM - 12:50 PM")],
        "LAB": [("Wednesday", "9:30 AM - 11:20 AM")]
    },
    "ENGG*4450*0101": {
        "LEC": [("Tuesday", "4:00 PM - 5:20 PM"), ("Thursday", "4:00 PM - 5:20 PM")],
        "LAB": [("Friday", "2:30 PM - 4:20 PM")]
    },
    "ENGG*4450*0102": {
        "LEC": [("Tuesday", "4:00 PM - 5:20 PM"), ("Thursday", "4:00 PM - 5:20 PM")],
        "LAB": [("Wednesday", "7:00 PM - 8:50 PM")]
    },
    "ENGG*4450*0103": {
        "LEC": [("Tuesday", "4:00 PM - 5:20 PM"), ("Thursday", "4:00 PM - 5:20 PM")],
        "LAB": [("Wednesday", "3:30 PM - 5:20 PM")]
    },
    "HIST*1250*01": {
        "LEC": [("Tuesday", "5:30 PM - 6:50 PM"), ("Thursday", "5:30 PM - 6:50 PM")]
    }
}

# User preferences for each day's availability
preferred_times = {
    "Monday": "8:00 AM - 5:00 PM",
    "Tuesday": "9:00 AM - 4:00 PM",
    "Wednesday": "8:00 AM - 6:00 PM",
    "Thursday": "10:00 AM - 3:00 PM",
    "Friday": "9:00 AM - 12:00 PM"
}


def parse_time(time_str):
    return datetime.strptime(time_str, "%I:%M %p")

def check_time_overlap(event1, event2):
    day1, time_range1 = event1
    day2, time_range2 = event2
    return day1 == day2 and not (
        parse_time(time_range1.split(" - ")[1]) <= parse_time(time_range2.split(" - ")[0]) or
        parse_time(time_range2.split(" - ")[1]) <= parse_time(time_range1.split(" - ")[0])
    )

def fits_schedule(event, availability):
    day, time_range = event
    if day not in availability:
        return False
    start, end = [parse_time(t) for t in time_range.split(" - ")]
    avail_start, avail_end = [parse_time(t) for t in availability[day].split(" - ")]
    return avail_start <= start and end <= avail_end

def has_conflicts(events1, events2):
    return any(check_time_overlap(e1, e2) for e1 in events1 for e2 in events2)

def find_valid_schedule(course_data, preferred_times):
    selected = {}
    scheduled_events = []
    courses = sorted(course_data.items(), key=lambda x: len(x[1]))
    
    for course_name, sections in courses:
        best_section = None
        best_score = -1
        
        for section_code, times in sections.items():
            events = []
            if "LEC" in times:
                events.extend(times["LEC"])
            if "LAB" in times:
                events.extend(times["LAB"])
            
            if has_conflicts(events, scheduled_events):
                continue
            
            score = sum(1 for event in events if fits_schedule(event, preferred_times))
            if score > best_score:
                best_score = score
                best_section = (section_code, events)
        
        if best_section:
            selected[course_name] = best_section[0]
            scheduled_events.extend(best_section[1])
        else:
            return None
    
    return selected

def print_schedule(course_data, selected_sections):
    if not selected_sections:
        print("No valid schedule found!")
        return
    
    by_day = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    
    for course, section in selected_sections.items():
        times = course_data[course][section]
        for event_type in ["LEC", "LAB"]:
            if event_type in times:
                for day, time in times[event_type]:
                    by_day[day].append((time, f"{course} ({section} - {event_type})"))
    
    for day, events in by_day.items():
        if events:
            print(f"\n{day}:")
            for time, course in sorted(events, key=lambda x: parse_time(x[0].split(" - ")[0])):
                print(f"  {time}: {course}")

selected = find_valid_schedule(course_data, preferred_times)
print_schedule(course_data, selected)







