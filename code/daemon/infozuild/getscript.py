'''
Loads the upcoming activities from Koala and outputs them in json.
'''
from __future__ import print_function
import argparse
import datetime
import logging
import json
try:
    from json.decoder import JSONDecodeError as JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

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

    try:
        raw_events = response.json()
    except JSONDecodeError:
        logging.error('Invalid API output: %s', response.text)
        return []
    result = []
    for event in raw_events:
        result.append((event['name'], event['start_date']))

    return result

PAGE_TEMPLATE = {
    'lines': [
        "        Welkom bij Sticky:",
        " Uw bron voor koekjes, koffie en",
        "        hulp bij practica",
        "",
        "Dagelijks geopend van 9-17 uur.",
        "",
        "Laatste update:",
        "  +++ OUT OF CHEESE ERROR +++", # replaced when script is run
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

def make_pages_dict(limit_activities=-1):
    '''
    Retrieve activities and build a dict that can be passed to the zuil.
    '''
    activities = get_activities()[0:limit_activities]
    if not activities:
        logging.warning('No activities were retrieved.')

    # Split activities in groups of at most 3
    activity_groups = [activities[i:i+3] for i in range(0, len(activities), 3)]
    pages = []

    # Add empty lines if page template has less than 8 lines
    for _ in range(8 - len(PAGE_TEMPLATE['lines'])):
        PAGE_TEMPLATE['lines'].append('')

    # Update 'last updated'-time
    now = format(datetime.datetime.now().strftime(
        DATETIME_FORMAT), ALIGN_RIGHT)
    PAGE_TEMPLATE['lines'][-1] = now

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

def make_pages_json(max_activities=-1):
    ''' Convert the pages dict to a json string. '''
    return json.dumps(make_pages_dict(max_activities))

def main():
    ''' Console script entry point. '''
    parser = argparse.ArgumentParser(
        description='Retrieve events from Koala and output in JSON format suitable for the zuil.'
        )
    parser.add_argument(
        '--output', '-o',
        help='output the resulting JSON not to stdout, but to a file. (File is overwritten)')
    parser.add_argument(
        '--limit', '-l', type=int, default=-1,
        help='limit the number of events displayed.')

    args = parser.parse_args()

    result = make_pages_json(args.limit)
    if args.output:
        with open(args.output, 'w') as outputfile:
            outputfile.write(result)
    else:
        print(result)

if __name__ == '__main__':
    main()
