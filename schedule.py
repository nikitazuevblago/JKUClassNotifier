from datetime import datetime
import pytz
import requests
from ics import Calendar
from dotenv import load_dotenv

load_dotenv()


# Custom exceptions
class IncorrectCalendarURL(Exception):
    def __init__(self, message="URL doesn't contain .ics or iCal file"):
        super().__init__(message)


def get_current_date(time=False):
    # Define CET timezone
    cet_timezone = pytz.timezone("Europe/Berlin")

    # Get current time in CET
    if time:
        current_cet_date = datetime.now(cet_timezone)
    else:
        current_cet_date = datetime.now(cet_timezone).date()

    return current_cet_date


class Schedule():
    def __init__(self):
        self.current_date = get_current_date()


    def url_to_calendar(self, url):
        try:
            response = requests.get(url)
            calendar = Calendar(response.text)
            return calendar
        except:
            raise IncorrectCalendarURL


    def get_today_events(self, current_date, calendar):
        today_events = []

        for event in calendar.events:
            calendar_date = event.begin.date()
            if calendar_date==current_date:
                today_events.append(event)

        # Sorting events by time, from earliest
        today_events = sorted(today_events, key=lambda event: event.begin)
        
        return today_events


    def get_daily_schedule(self, url):
        calendar = self.url_to_calendar(url)
        today_events = self.get_today_events(self.current_date, calendar)
        # Template for the header
        header_template = (
            "📅 Servus!\n"
            "Here’s your schedule for {current_date}:\n\n"
        )
        
        # Template for each event (subject/class)
        event_template = (
            "━━━━━━━━━━━━━━━━━━\n"
            "🎯 Subject: {course_title}\n"
            "👨‍🏫 Instructor: {instructor}\n"
            "🗓 Time: {start_time} – {end_time}\n"
            "🏫 Room: {location}\n"
        )
        
        # Start the message with the header
        message = header_template.format(current_date=self.current_date)
        
        # Add each event to the message
        for event in today_events:
            # Extract details from ICS event
            summary = event.name  # e.g. "KV Responsible AI / Martina Mara / (510101/2024W)"
            parts = summary.split(" / ")
            
            if len(parts) >= 2:
                course_title = parts[0].strip()
                instructor = parts[1].strip()
            else:
                # If the format is different or incomplete
                course_title = summary.strip()
                instructor = "N/A"
            
            start_time = event.begin.format('HH:mm')
            end_time = event.end.format('HH:mm')
            location = event.location if event.location else "N/A"
            
            message += event_template.format(
                course_title=course_title,
                instructor=instructor,
                start_time=start_time,
                end_time=end_time,
                location=location
            )
        
        return message