'''
Loads the upcoming activities from Koala and outputs them in json.
'''
from __future__ import print_function
import datetime
import json
import logging
import requests


LINE_WIDTH = 32
TOP_LINE = '----- Komende Activiteiten -----'
API_URL = 'https://koala.svsticky.nl/api/activities'

ALIGN_RIGHT = '>' + str(LINE_WIDTH)
DATETIME_FORMAT = '%d-%m-%Y %X'
def get_activities():
    '''
    Retrieve upcoming activities and return a list of (name, start_date) tuples.
    Return an empty list if events could not be retrieved.
    '''
    try:
        response = requests.get(API_URL)
    except requests.exceptions.ConnectionError as ex:
        logging.critical('Failed to connect: %s', ex)
        return []
    if response.status_code != 200:
        logging.error('Could not retrieve activities: %s',
                      response.status_code)
        logging.error('Response content: %s', response.text)
        return []

    raw_events = response.json()
    result = []
    for event in raw_events:
        result.append((event['name'], event['start_date']))

    return result

PAGE_TEMPLATE = {
    'lines': [
        "        Welkom bij Sticky.",
        " Uw bron voor koekjes, koffie en",
        "         hulp bij practica",
        "",
        "",
        "",
        "Laatste update:",
        format(datetime.datetime.now().strftime(
            DATETIME_FORMAT), ALIGN_RIGHT)
    ],
    "time": 10012,
    "blink": 5,
    "schedular": {
        "year": 2014,
        "month": 11,
        "day": 11,
        "hours": 14,
        "minutes": 10,
        "seconds": 50
    },
    "brightness": 2,
    "scroll": 1,
    "fading": 0,
    "moving": {
        "speed": 10,
        "width": 2
    }
}

def make_pages_dict():
    '''
    Retrieve activities and build a dict that can be passed to the zuil.
    '''
    activities = get_activities()
    if not activities:
        logging.warning('No activities were retrieved.')

    # Split activities in groups of at most 3
    activity_groups = [activities[i:i+3] for i in range(0, len(activities), 3)]
    pages = []
    pages.append(PAGE_TEMPLATE)
    for group in activity_groups:
        newpage = PAGE_TEMPLATE.copy()
        lines = []
        lines.append(TOP_LINE)
        for activity in group:
            # Activities are (name, date) tuples
            lines.append(activity[0])
            lines.append(format(activity[1], ALIGN_RIGHT)) # right-align
        for _ in range(8 - len(lines)):
            lines.append('')
        newpage['lines'] = lines
        pages.append(newpage)

    return {'pages': pages}

def make_pages_json():
    ''' Convert the pages dict to a json string. '''
    return json.dumps(make_pages_dict())

if __name__ == '__main__':
    print(make_pages_json())