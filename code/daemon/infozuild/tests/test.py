''' Contains various tests to verify zuild works as intended. '''
import datetime
import imp
import logging
import unittest

import infozuild.getscript

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
        self.assertEqual(
            infozuild.getscript.build_when(event), event['start_date'])

    def test_all_single_day(self):
        ''' Tests single-day full-day event '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'end_date' : '2016-06-08'
        }
        self.assertEqual(
            infozuild.getscript.build_when(event, self.tomorrow), event['start_date'])

    def test_singleday_starttime(self):
        ''' Tests a single-day event with start-time but without end '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'start_time' : '12:34',
            'end_date' : '2016-06-08'
        }
        self.assertEqual(
            infozuild.getscript.build_when(event, self.today), event['start_time'])
        self.assertEqual(
            infozuild.getscript.build_when(event, self.tomorrow),
            "{} {}".format(event['start_date'], event['start_time']))

    def test_singleday_startendtimes(self):
        ''' Tests a single day event with both start and end-times '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'start_time' : '12:34',
            'end_time' : '13:37',
            'end_date' : '2016-06-08'
        }
        self.assertEqual(
            infozuild.getscript.build_when(event, self.today),
            "{}~{}".format(event['start_time'], event['end_time']))

        self.assertEqual(
            infozuild.getscript.build_when(event, self.tomorrow),
            "{} {}~{}".format(event['start_date'], event['start_time'],
                              event['end_time']))

    def test_multiday_allday(self):
        ''' Tests multiday all-day event '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'end_date' : '2016-06-09'
        }
        self.assertEqual(
            infozuild.getscript.build_when(event, self.today),
            "{}~{}".format(event['start_date'], event['end_date']))

    def test_multiday_starttime(self):
        ''' Tests a multiday event with start-time but without end-time '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'start_time' : '12:34',
            'end_date' : '2016-06-09'
        }
        self.assertEqual(
            infozuild.getscript.build_when(event),
            "{} {}~{}".format(event['start_date'], event['start_time'], event['end_date']))

    def test_multiday_startendtime(self):
        ''' Tests a multi-day event with both start- and end-times '''
        event = {
            'name' : 'Honking',
            'start_date' : '2016-06-08',
            'start_time' : '12:34',
            'end_time' : '13:37',
            'end_date' : '2016-06-09'
        }
        self.assertEqual(
            infozuild.getscript.build_when(event),
            "{} {} ~ {} {}".format(
                event['start_date'], event['start_time'],
                event['end_date'], event['end_time']))
