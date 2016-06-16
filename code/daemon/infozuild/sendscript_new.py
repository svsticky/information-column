
#! /usr/bin/python
'''
Contains the relevant code to generate a controlstring and send it to the zuil.
'''
import datetime
import json
import logging
import math
import socket


def encode_value(value):
    ''' Convert a numeric value to an ascii character. '''
    return chr(value + 32)

def decode_value(character):
    ''' Convert an ascii character to a numeric value. (We probably won't need this.) '''
    return ord(character) - 32

def check_in_range(*items):
    ''' Verify all given arguments are within the given values.
    Format (name, value, min, max), max inclusive.'''
    for item in items:
        if item[1] not in range(item[2], item[3]+1):
            raise ValueError('Argument out of range: ', item[0], '=', item[1],
                             ', min=', item[2], ', max=', item[3])

## Control characters
SOH = chr(1)    # Start of heading
CR = chr(13)    # Carriage return
SO = chr(14)    # Bold Text - only usable for information panels
SYN = chr(22)   # Synchronisation
ESC = chr(27)   # Escape
FS = chr(28)    # Field Seperator
GS = chr(29)    # Blink

## Common components of control string
def start_controlstring(address):
    ''' Common header. '''
    return SOH + encode_value(address) + FS

## Controller-level operations.
class DisplayMode: # pylint: disable=too-few-public-methods, fixme
    ''' Sets the display mode (see manual, page 8) of the controller. '''

    # Known values:
    blank = 0       # Display will blank until restarted or re-enabled. Pages are kept.
    normal = 1      # Display will operate in normal mode.
    test_off = 2    # Disables test mode and allows entering of normal pages.
    test_halt = 3   # Test mode pauses on the visible page. TODO: Does this pause 'normal' pages?
    test_on = 4     # Enables test mode. Warning: deletes currently stored pages!
    output = 10     # Toggles, if connected, the output. (No idea if we use this.)
    modes = [blank, normal, test_off, test_halt, test_on, output]

    def __init__(self, mode, address=0):
        ''' Unfortunately trivial. '''
        if mode not in DisplayMode.modes:
            raise ValueError('Unknown DisplayMode:', mode)
        self.address = address
        self.mode = mode

    def to_controlstring(self):
        ''' Generate a control string from the known mode and given address. '''
        result = start_controlstring(self.address)
        result += ESC + 'D'
        result += encode_value(self.mode)
        result += FS + CR

        return result

def set_rtc(address=0, when=None):
    ''' Generates a controlstring that will set the controller's RTC to the given time. '''
    result = start_controlstring(address)
    result += ESC + 'T'

    enc = encode_value

    if not when:
        when = datetime.datetime.now()

    year = when.year - 1980
    if year not in range(0, 96):
        raise ValueError('Year out of range:', year)

    result += '{year}{month}{u}{day}{hour}{minute}{second}'.format(
        year=enc(year), month=enc(when.month), u=enc(0),
        day=enc(when.day), hour=enc(when.hour), minute=enc(when.minute),
        second=enc(when.second))

    result += FS + CR

    return result

## Page-related classes
class Page:
    ''' Contains the information for one screenful of text. '''
    attributes = ['blinkspeed', 'duration', 'schedular', 'brightness',
                  'scrolling', 'fading']

    def __init__(self, lines):
        ''' Initialize a new page with the given text-lines and default attributes. '''
        self.lines = lines

        self.blinkspeed = 4
        # pylint: disable=fixme
        self.duration = 10012 # TODO: define sane defaults
        self.schedular = None
        self.brightness = 2
        self.scrolling = True
        self.fading = False
        # All moving-text attributes are removed, because we can't use them anyway.

    # Attribute encoding
    def build_duration(self):
        ''' Return 4 characters representing the duration of this page. '''
        i = math.floor(self.duration / 26.7)

        # pylint: disable=invalid-name
        a = math.floor(i / 4096)
        i %= 4096
        b = math.floor(i / 256)
        i %= 256
        c = math.floor(i / 16)
        i %= 16
        d = i

        enc = encode_value
        result = enc(a) + enc(b) + enc(c) + enc(d)
        logging.debug('duration: %s %s %s %s', a, b, c, d)
        logging.debug(result)
        return result

    def build_schedular(self):
        ''' Return 7 characters respresenting the schedular, whatever it may be. '''
        enc = encode_value

        sch = self.schedular
        return '{}{}{}{}{}{}{}'.format(
            enc(sch.year), enc(sch.month), enc(0), enc(sch.day), enc(sch.hour),
            enc(sch.minute), enc(sch.second))

    # Encoding
    def to_controlstring(self):
        ''' Convert the page to a controlstring. This string must be used in a rotation! '''
        # Validate attributes are valid
        check_in_range(
            ('Line amount', len(self.lines), 0, 8),
            ('Blink speed', self.blinkspeed, 0, 4),
            ('Duration', self.duration, 1, 218450),
            ('Brightness', self.brightness, 0, 17)
            )

        result = ''
        for num, line in enumerate(self.lines):
            result += str(num) + line + FS

        num += 1

        if num < 8:
            for line in range(num, 8):
                result += str(line) + FS


        if self.blinkspeed:
            result += ESC + 'B' + encode_value(self.blinkspeed) + FS

        result += ESC + 'A' + self.build_duration() + FS

        if self.schedular:
            check_in_range(
                ('Year', self.schedular.year, 1980, 2075),
                ('Month', self.schedular.month, 1, 12),
                ('Day', self.schedular.day, 1, 31),
                ('Hour', self.schedular.hour, 0, 23),
                ('Minute', self.schedular.minute, 0, 59),
                ('Second', self.schedular.second, 0, 59)
            )
            result += ESC + 'P' + self.build_schedular() + FS

        if self.brightness:
            result += ESC + 'Q' + encode_value(self.brightness) + FS

        if self.scrolling:
            result += ESC + 'R' + encode_value(1) + FS
        if self.fading:
            result += ESC + 'S' + encode_value(1) + FS

        return result

    def to_json(self):
        ''' Dump all relevant attributes as a JSON string. '''
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_dict(self):
        ''' Dump all relevant attributes as a dict. '''
        result = {
            'lines': self.lines,
            }

        for attribute in type(self).attributes:
            attr_value = getattr(self, attribute)
            if attr_value:
                result[attribute] = attr_value

        return result

    # Decoding
    @classmethod
    def from_json(cls, jsonstring):
        ''' Initialize a page from a JSON-string. '''
        return cls.from_dict(json.loads(jsonstring))

    @classmethod
    def from_dict(cls, data):
        ''' Initialize a page from a dict of attributes. '''
        page = cls(data['lines'])
        for attribute in cls.attributes:
            if attribute in data:
                setattr(page, attribute, data[attribute])
        return page

class Rotation:
    ''' Contains the pages that should be displayed, and the controller address. '''
    def __init__(self, address=0, pages=[]):
        ''' Create a new Rotation. '''
        check_in_range(('Controller address', address, 0, 31))
        self.address = address
        self.pages = pages

    # Encoding
    def to_controlstring(self):
        ''' Convert the rotation to a controlstring that can be sent to the controller. '''
        check_in_range(('Address', self.address, 0, 31))

        result = start_controlstring(self.address)

        for page in self.pages:
            result += page.to_controlstring()

        result += SYN + CR

        return result

    def to_dict(self):
        ''' Dump all relevant attributes as a dict. '''
        return {
                'address': self.address,
                'pages': [page.to_dict() for page in self.pages]
            }

    def to_json(self):
        ''' Dump all relevant attributes as a JSON string. '''
        return json.dumps(self.to_dict(), sort_keys=True)

    # Decoding
    @classmethod
    def from_json(cls, jsonstring):
        ''' Initialize a rotation from a JSON-string. '''
        return cls.from_dict(json.loads(jsonstring))

    @classmethod
    def from_dict(cls, data):
        ''' Initialize a rotation from a dict with a list of pages and address. '''
        return cls(data['address'],
                   [Page.from_dict(page) for page in data['pages']])

## Communication with the zuil
def connect_and_send(ip, controlstring):
    ''' Open a connection and send the given control string. '''
    logging.info('Connecting to %s', ip)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((ip, 23))
    except OSError as ex:
        logging.error('Could not connect to %s: %s', ip, ex)
        return
    sock.recv(1024) # Necesssary to get rid of the *** mini blabla *** header!

    sock.sendall(controlstring.encode())
    sock.close()

def update_rtc(ip, address=0, when=None):
    ''' Generate a control string that will set the controller's RTC to the given time (or
    the system time if none, and immediately send it to the controller. '''
    logging.info('Starting RTC update.')
    controlstring = set_rtc(address, when)

    logging.info('Setting RTC.')
    connect_and_send(ip, controlstring)
    logging.info('RTC update complete.')

def update_displaymode(ip, mode, address=0):
    ''' Generate a controlstring that will set the display mode, and immediately send it.
    '''
    new_mode = DisplayMode(mode, address)
    controlstring = new_mode.to_controlstring()

    logging.info('Setting display mode %s', new_mode.mode)
    connect_and_send(ip, controlstring)
    logging.info('Mode setting complete.')
