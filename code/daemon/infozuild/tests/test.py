import imp
import unittest
import logging
import infozuild.getscript

class TestNotConnected(unittest.TestCase):
    ''' Test various scenarios where the daemon might not be able to retrieve events from Koala. '''

    def setUp(self):
        ''' Always reset the module after testing, so the next test has a clean state. '''
        self.addCleanup(self.resetGetscript)

    @staticmethod
    def resetGetscript():
        ''' Reload module state. '''
        imp.reload(infozuild.getscript)

    def testNoAPI(self):
        ''' Ensure that no exception is raised if the API cannot be reached. '''
        infozuild.getscript.API_URL = 'http://nope'
        logging.disable(logging.CRITICAL)
        self.assertEqual(infozuild.getscript.get_activities(), [])
        logging.disable(logging.NOTSET)

    def testAPIWeird(self):
        ''' Ensure no exception is raised if the API gives invalid (non-JSON) output. '''
        infozuild.getscript.API_URL = 'https://svsticky.nl'
        logging.disable(logging.ERROR)
        self.assertEqual(infozuild.getscript.get_activities(), [])
        logging.disable(logging.NOTSET)
