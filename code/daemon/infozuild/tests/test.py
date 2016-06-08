''' Contains various tests to verify zuild works as intended. '''
import datetime
import imp
import logging
import unittest

import dateutil.parser
import infozuild.getscript
from infozuild.getscript import no_secs

class TestNotConnected(unittest.TestCase):
    ''' Test various scenarios where the daemon might not be able to retrieve events from Koala. '''

    def setUp(self):
        ''' Always reset the module after testing, so the next test has a clean state. '''
        self.addCleanup(self.reset_getscript)

    @staticmethod
    def reset_getscript():
        ''' Reload module state. '''
        imp.reload(infozuild.getscript)

    def test_no_api(self):
        ''' Ensure that no exception is raised if the API cannot be reached. '''
        infozuild.getscript.API_URL = 'http://nope'
        logging.disable(logging.CRITICAL)
        self.assertEqual(infozuild.getscript.get_activities(), [])
        logging.disable(logging.NOTSET)

    def test_api_weird(self):
        ''' Ensure no exception is raised if the API gives invalid (non-JSON) output. '''
        infozuild.getscript.API_URL = 'https://svsticky.nl'
        logging.disable(logging.ERROR)
        self.assertEqual(infozuild.getscript.get_activities(), [])
        logging.disable(logging.NOTSET)

class TestWhenBuilder(unittest.TestCase):
    ''' Test whether getscript.build_when behaves as specified. '''

    today = datetime.date(2016, 6, 8) # Comparison date for today-checking
    tomorrow = datetime.date(2016, 6, 9)

    def test_legacy(self):
        ''' Tests legacy event '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08'
        }
        start = dateutil.parser.parse(event['start_date'])
        self.assertEqual(
            infozuild.getscript.build_when(event), str(start.date()))

    def test_all_single_day(self):
        ''' Tests single-day full-day event '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'end_date' : '2016-06-08'
        }
        start = dateutil.parser.parse(event['start_date'])

        self.assertEqual(
            infozuild.getscript.build_when(event, self.tomorrow), str(start.date()))

    def test_singleday_starttime(self):
        ''' Tests a single-day event with start-time but without end '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08T12:34:00+02:00',
            'end_date' : '2016-06-08'
        }
        start = dateutil.parser.parse(event['start_date'])

        self.assertEqual(
            infozuild.getscript.build_when(event, self.today), no_secs(start.time()))
        self.assertEqual(
            infozuild.getscript.build_when(event, self.tomorrow),
            "{} {}".format(start.date(), no_secs(start.time())))

    def test_singleday_startendtimes(self):
        ''' Tests a single day event with both start and end-times '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08T12:34:00+02:00',
            'end_date' : '2016-06-08T13:37:00+02:00'
        }
        start = dateutil.parser.parse(event['start_date'])
        end = dateutil.parser.parse(event['end_date'])

        self.assertEqual(
            infozuild.getscript.build_when(event, self.today),
            "{}~{}".format(no_secs(start.time()), no_secs(end.time())))

        self.assertEqual(
            infozuild.getscript.build_when(event, self.tomorrow),
            "{} {}~{}".format(start.date(), no_secs(start.time()),
                              no_secs(end.time())))

    def test_multiday_allday(self):
        ''' Tests multiday all-day event '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'end_date' : '2016-06-09'
        }
        start = dateutil.parser.parse(event['start_date'])
        end = dateutil.parser.parse(event['end_date'])

        self.assertEqual(
            infozuild.getscript.build_when(event, self.today),
            "{}~{}".format(start.date(), end.date()))

    def test_multiday_starttime(self):
        ''' Tests a multiday event with start-time but without end-time '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08T12:34:00+02:00',
            'end_date' : '2016-06-09'
        }
        start = dateutil.parser.parse(event['start_date'])
        end = dateutil.parser.parse(event['end_date'])

        self.assertEqual(
            infozuild.getscript.build_when(event),
            "{} {}~{}".format(start.date(), no_secs(start.time()), end.date()))

    def test_multiday_startendtime(self):
        ''' Tests a multi-day event with both start- and end-times '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08T12:34:00+02:00',
            'end_date' : '2016-06-09T13:37:00+02:00'
        }
        start = dateutil.parser.parse(event['start_date'])
        end = dateutil.parser.parse(event['end_date'])

        self.assertEqual(
            infozuild.getscript.build_when(event),
            "{} {} ~ {} {}".format(
                start.date(), no_secs(start.time()),
                end.date(), no_secs(end.time())))
