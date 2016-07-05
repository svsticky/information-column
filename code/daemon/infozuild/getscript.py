'''
Loads the upcoming activities from Koala and outputs them in json.
'''
from __future__ import print_function
import argparse
import datetime
import logging
try:
    from json.decoder import JSONDecodeError as JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import dateutil.parser
import requests
import unidecode

from .sendscript import Page, Rotation


LINE_WIDTH = 32
TOP_LINE = '  --- Komende Activiteiten ---  '
API_URL = 'https://koala.svsticky.nl/api/activities'

ALIGN_RIGHT = '>' + str(LINE_WIDTH)
UPDATE_TIME_FORMAT = '%d %B %X'
ACTIVITY_DATE_FORMAT = '%d %b'

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
        result.append((event['name'], build_when(event)))

    return result

def no_secs(time):
    ''' Remove seconds and force to string because they don't matter '''
    return time.strftime("%H:%M")

def build_when(event, today=None):
    '''
    Builds a string that hopefully contains just the right amount of info to
    inform the viewer when an event will take place.
    - start_date will always be present
    - end_time will never be present without start_time

    The following scenarios are likely:
     1. end_date absent: legacy event, just show the date

    end_date same as start_date:
     2. No times: new(er) all-day event, just show the date
     3. Start_time set, end_time absent:
         Event without end, show start_time and date if not today
     4. Both times set:
         show date (if not today), start_ and end_time.

    end_date NOT the same as start_date:
     5. No times: multi-day all-day event, always show both dates
     6. Start_time: [s_date] [s_time]~[e_date]
     7. Both times: [s_date] [s_time]~[e_date] [e_time]
    '''
    start = dateutil.parser.parse(event['start_date'])
    start_date = start.date().strftime(ACTIVITY_DATE_FORMAT)
    start_time = no_secs(start)

    if 'end_date' not in event: #1
        return start_date

    end = dateutil.parser.parse(event['end_date'])
    end_date = end.date().strftime(ACTIVITY_DATE_FORMAT)
    end_time = no_secs(end)

    if not today:
        today = datetime.date.today()

    starts_today = today == start.date()
    multiday = start.date() != end.date()

    start_date_n2d = start_date + ' ' if not starts_today else '' # n2d == not today

    if not multiday:
        if 'T' not in event['start_date']: #2
            return start_date

        if 'T' not in event['end_date']: #3
            return "{}{}".format(start_date_n2d, start_time)

        else: #4
            return "{}{}~{}".format(start_date_n2d, start_time, end_time)

    if 'T' not in event['start_date']: #5
        return "{}~{}".format(start_date, end_date)

    if 'T' not in event['end_date']: #6
        return "{} {}~{}".format(start_date, start_time, end_date)

    return "{} {} ~ {} {}".format(start_date, start_time, end_date, end_time) #7

# The template for the first page, as used in make_rotation
INFO_LINES = [
    "        Welkom bij Sticky:",
    " Uw bron voor koekjes, koffie en",
    "        hulp bij practica",
    "",
    "Dagelijks geopend van 9-17 uur.",
    "",
    "Laatste update:",
    "  +++ OUT OF CHEESE ERROR +++", # replaced when script is run
    ]

def make_rotation(limit_activities=None):
    '''
    Retrieve activities and build a Rotation that can be passed to the sendscript.
    '''
    rota = Rotation()

    activities = get_activities()[0:limit_activities]
    if not activities:
        logging.warning('No activities were retrieved.')

    # Split activities in groups of at most 3
    activity_groups = [activities[i:i+3] for i in range(0, len(activities), 3)]

    # Update 'last updated' and add first page
    now = format(datetime.datetime.now().strftime(
        UPDATE_TIME_FORMAT), ALIGN_RIGHT)
    INFO_LINES[-1] = now

    rota.pages.append(Page(INFO_LINES))

    # Make pages with activities
    for pageno, group in enumerate(activity_groups):
        lines = [TOP_LINE]

        for activity in group: # activities are (name, date) tuples
            name = unidecode.unidecode(activity[0])
            lines.append(name)
            lines.append(format(activity[1], ALIGN_RIGHT))

        for _ in range(7 - len(lines)):
            lines.append('')

        lines.append(format('{no}/{max}'.format(
            no=pageno+1, max=len(activity_groups)), ALIGN_RIGHT))

        rota.pages.append(Page(lines))

    return rota

def make_rotation_json(max_activities=None):
    ''' Convert the pages dict to a json string. '''
    return make_rotation(max_activities).to_json()

def main():
    ''' Console script entry point. '''
    parser = argparse.ArgumentParser(
        description='Retrieve events from Koala and output in JSON format suitable for the zuil.'
        )
    parser.add_argument(
        '--output', '-o',
        help='output the resulting JSON not to stdout, but to a file. (File is overwritten)')
    parser.add_argument(
        '--limit', '-l', type=int, default=None,
        help='limit the number of events displayed.')

    args = parser.parse_args()

    result = make_rotation_json(args.limit)
    if args.output:
        with open(args.output, 'w') as outputfile:
            outputfile.write(result)
    else:
        print(result)

if __name__ == '__main__':
    main()
