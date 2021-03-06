'''
The getscript contains the relevant code to load the upcoming activities from
Koala and extract the relevant information, for display on the zuil.

The getscript can be run independently, by using the command
:command:`zuil-get`, which calls :func:`main`.
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
ALIGN_CENTER = '^' + str(LINE_WIDTH)
UPDATE_TIME_FORMAT = '%d %B %X'
ACTIVITY_DATE_FORMAT = '%d %b'

def get_activities():
    '''
    Retrieve upcoming activities and parse the received data into the format to
    be used on the display.

    Returns:
        A list of (*name*, *date*) tuples and an optional string containing an
        error code. The list of events will be empty if events could not be
        retrieved.
    '''

    try:
        response = requests.get(API_URL)
    except requests.exceptions.ConnectionError as ex:
        logging.critical('Failed to connect: %s', ex)
        return [], 'Geen verbinding met Koala!'

    if response.status_code != 200:
        logging.error('HTTP error: %s',
                      response.status_code)
        logging.error('Response content: %s', response.text)
        return [], 'HTTP-fout: {}'.format(response.status_code)

    try:
        raw_events = response.json()
    except JSONDecodeError:
        logging.error('Invalid API output: %s', response.text)
        return [], 'Onzin binnengekregen!'
    result = []
    for event in raw_events:
        result.append((event['name'], build_when(event)))

    return result, ''

def no_secs(time):
    ''' Force a :class:`datetime.datetime` to a string, with the seconds removed. '''
    return time.strftime("%H:%M")

def build_when(event, today=None):
    '''
    Args:
        event (dict): a dict as returned by Koala's API.
        today (datetime.datetime): an optional 'now-moment' for testing
            consistency of date collapsing.

    Returns:
        A string that contains just enough information to inform the viewer
        when an event will take place.
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
''' The template for the first page, as used in :func:`make_rotation`. '''

def make_rotation(activities=None, motd=None, limit_activities=None):
    '''
    Retrieve activities and return a :class:`Rotation` that can be passed to the sendscript.

    Args:
        activities (list): a list of events retrieved from Koala, to bypass
            automatic retrieval in the function itself.
        motd (str): A status message to be shown on the first page, in the
            fifth and sixth lines. Will use default if None.
        limit_activities (int): the maximum number of events that may be shown.
            A negative value will remove that many values from the end. This
            value is only applied to automatically retrieved events, manually
            passed activities via the argument will always be used as-is.

    Returns:
        A :class:`Rotation` containing three events per :class:`Page`, and a
        title page containting the generation time and date.
    '''
    rota = Rotation()

    # Retrieve activities if we didn't get pre-retrieved ones.
    if not activities and activities is not []:
        activities, _ = get_activities()
        activities = activities[0:limit_activities]
        if not activities:
            logging.warning('No activities were left after limit.')

    # Split activities in groups of at most 3
    activity_groups = [activities[i:i+3] for i in range(0, len(activities), 3)]

    # Make a copy of the default page before modifying it
    info_lines = INFO_LINES[:]
    # Update 'last updated' and add first page
    now = format(datetime.datetime.now().strftime(
        UPDATE_TIME_FORMAT), ALIGN_RIGHT)
    info_lines[-1] = now

    if motd:
        status_lines = motd.split('\n')
        info_lines[4] = format(status_lines[0], ALIGN_CENTER)
        try:
            info_lines[5] = format(status_lines[1], ALIGN_CENTER)
        except IndexError:
            info_lines[5] = ''


    rota.pages.append(Page(info_lines))

    # Make pages with activities
    for pageno, group in enumerate(activity_groups):
        lines = [TOP_LINE]

        for activity in group: # activities are (name, date) tuples
            name = unidecode.unidecode(activity[0])
            lines.append(name)
            lines.append(format(activity[1], ALIGN_RIGHT))

        # Add empty lines until we've got 7 lines, and then page number
        for _ in range(7 - len(lines)):
            lines.append('')

        lines.append(format('{no}/{max}'.format(
            no=pageno+1, max=len(activity_groups)), ALIGN_RIGHT))

        rota.pages.append(Page(lines))

    return rota

def make_rotation_json(max_activities=None):
    ''' Convert the :class:`Rotation` returned by :func:`make_rotation` to a json string. '''
    return make_rotation(max_activities).to_json()

def main():
    '''
    :command:`zuil-get` entrypoint.

    :command:`zuil-get` retrieves the current activities, and outputs them in a
    JSON format parsable by :func:`infozuild.sendscript.Rotation.from_json`.
    '''
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
