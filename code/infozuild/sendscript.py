'''
The sendscript contains the relevant code to generate a controlstring from a
list of lines and send it to the zuil.
'''

import argparse
import configparser
import datetime
import json
import logging
import math
import os
import socket
import sys

from . import __version__


def encode_value(value):
    ''' Convert a numeric value to an ascii character. '''
    return chr(value + 32)

def decode_value(character):
    ''' Convert an ascii character to a numeric value. '''
    return ord(character) - 32

def check_in_range(*items):
    '''
    Takes a number of (`name`, `value`, `min`, `max`) tuples and verifies
    that all `min` <= `value` <= `max`.

    Raises:
        ValueError if a value that is outside the given range is found. Any
        additional values are not checked.
    '''
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
    ''' Generates the common header. '''
    return SOH + encode_value(address) + FS

## Controller-level operations.
class DisplayMode:
    ''' Represents an instruction to set the controller's display mode. '''

    # Known values:
    blank = 0
    normal = 1
    test_off = 2
    test_halt = 3
    test_on = 4
    output = 10

    _modes = [blank, normal, test_off, test_halt, test_on, output]

    def __init__(self, mode, address=0):
        ''' Verify that *mode* is valid and set up a DisplayMode instruction. '''
        if mode not in DisplayMode._modes:
            raise ValueError('Unknown DisplayMode:', mode)
        self.address = int(address)
        self.mode = mode

    def to_controlstring(self):
        '''
        Generate a control string from the known mode and address.

        Returns:
            A string that may be sent to the controller to set the display
            mode.
        '''

        result = start_controlstring(self.address)
        result += ESC + 'D'
        result += encode_value(self.mode)
        result += FS + CR

        return result

def set_rtc(address=0, when=None):
    '''
    Generate an instruction to set the controller's RTC (Real Time Clock) to
    the given time and date.

    Args:
        address: an optional integer specifying which controller to update.
            Should be left on zero.
        when: an optional :class:`datetime.datetime` instance that contains the
            new values for the RTC. The system date and time will be used if
            omitted.

    Returns:
        A string that may be sent to the controller to update the clock.

    The RTC can be used in control strings with the special values as documented in Protocol.md.
    '''

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
    '''
    Represents one screenful of text. All attributes may be `None` to inherit
    the setting used by the previous Page.

    Attributes:
        lines:
            a list of strings containing the text to display. Should contain 8
            strings when sending.

        blinkspeed:
            an optional integer controlling the duration of the transition to
            the next page, in half-seconds. 0 <= `blinkspeed` <= 4.

        duration:
            an optional integer controlling the time the controller waits until
            advancing to the next page, in milliseconds. Due to a quirk in the
            encoding, the set value will be rounded to ``floor(duration/26.7)``
            on sending. 0 <= `duration` <= 218450.

        brightness:
            an optional integer controlling the brightness of the leds for this
            page. 0 <= `brightness` <= 17.

        scrolling:
            A boolean that will, if `True`, make the letters on the page scroll in from above.

        fading:
            A boolean that will, if `True`, make the contents of the page fade in and out.
    '''
    _attributes = ['blinkspeed', 'duration', 'schedular', 'brightness',
                   'scrolling', 'fading']

    def __init__(self, lines=None):
        ''' Initialize a new page with the given text and default attributes. '''
        self.lines = lines or []
        self.blinkspeed = 1
        self.duration = 10000
        self.schedular = None
        self.brightness = 17
        self.scrolling = False
        self.fading = False

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
        ''' Return 7 characters respresenting the schedular, whatever it may be. (Unused)'''
        enc = encode_value

        sch = self.schedular
        return '{}{}{}{}{}{}{}'.format(
            enc(sch.year), enc(sch.month), enc(0), enc(sch.day), enc(sch.hour),
            enc(sch.minute), enc(sch.second))

    # Encoding
    def to_controlstring(self):
        '''
        Convert the page to a controlstring.

        Returns:
            A string that may be included in the controlstring of a :class:`Rotation`.
        Raises:
            ValueError if any attributes are out of range.
        '''

        # Validate attributes
        check_in_range(
            ('Line amount', len(self.lines), 0, 8),
            ('Blink speed', self.blinkspeed, 0, 4),
            ('Duration', self.duration, 1, 218450),
            ('Brightness', self.brightness, 0, 17)
            )

        result = ''
        num = 0
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

        for attribute in self._attributes:
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
        for attribute in cls._attributes:
            if attribute in data:
                setattr(page, attribute, data[attribute])
        return page

class Rotation:
    '''
    Contains a set of :class:`Page`\\ s that should be displayed, and the
    controller address.

    Attributes:
        pages:
            A :class:`list` of :class:`Page`\\ s which will be shown in the
            given order.
        address:
            An integer that controls the address of the controller that will be
            updated, usually zero.
    '''
    def __init__(self, address=0, pages=None):
        ''' Create a new Rotation. '''
        check_in_range(('Controller address', address, 0, 31))
        self.address = address

        if pages is not None:
            self.pages = pages
        else:
            self.pages = []

    # Encoding
    def to_controlstring(self):
        ''' Convert the Rotation to a controlstring that can be sent to the controller. '''
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
        ''' Initialize a Rotation from a JSON-string. '''
        return cls.from_dict(json.loads(jsonstring))

    @classmethod
    def from_dict(cls, data):
        ''' Initialize a Rotation from a dict with a list of pages and address. '''
        return cls(data['address'],
                   [Page.from_dict(page) for page in data['pages']])

## Communication with the zuil
def connect_and_send(host, controlstring):
    ''' Open a connection to *host* and send the given control string. '''
    logging.info('Connecting to %s', host)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((host, 23))
    except OSError as ex:
        logging.error('Could not connect to %s: %s', host, ex)
        return
    sock.recv(1024) # Necesssary to get rid of the *** mini blabla *** header!

    sock.sendall(controlstring.encode())
    sock.close()

def update_rtc(host, address=0, when=None):
    ''' Generate a control string that will set the controller's RTC to the given time (or
    the system time if None), and immediately send it to the controller. '''

    logging.info('Starting RTC update.')
    controlstring = set_rtc(address, when)

    logging.info('Setting RTC.')
    logging.debug(repr(controlstring))
    connect_and_send(host, controlstring)
    logging.info('RTC update complete.')

def update_displaymode(host, mode, address=0):
    ''' Generate a controlstring that will set the display mode, and immediately send it. '''
    new_mode = DisplayMode(mode, address)
    controlstring = new_mode.to_controlstring()

    logging.info('Setting display mode %s', new_mode.mode)
    logging.debug(repr(controlstring))
    connect_and_send(host, controlstring)
    logging.info('Mode setting complete.')

## Script
def main():
    ''' :command:`zuil-send` entrypoint. '''
    config = configparser.ConfigParser()

    configdir = os.path.expanduser('~/.infozuil')
    configpath = os.path.join(configdir, 'send.cfg')
    if not os.path.isdir(configdir) or not os.path.isfile(configpath):
        logging.critical('Configfile does not exist, please create send.cfg in ~/.infozuil')
        os.mkdir(configdir)
        sys.exit(1)
    config.read(configpath) # Read the configuration file

    host = config['ConnectionInfo']['server']
    address = int(config['ConnectionInfo']['address'])

    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version',
                        version='infozuild {}'.format(__version__))
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='activate debug logging')

    # Other modes:
    parser.add_argument('--displaymode', type=int, default=None,
                        help='set a display mode (overrides text update)')
    parser.add_argument('--update-rtc', action='store_true',
                        help='update the RTC to the current time (overrides text update)')

    # Text update
    parser.add_argument('--file', '-f', default=None,
                        help='rotation file to read, stdin if not specified.')
    parser.add_argument('--output', '-o', default=None,
                        help='output resulting controlstring to file, as well as sending')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.displaymode is not None:
        update_displaymode(host, args.displaymode, address)
    elif args.update_rtc:
        update_rtc(host, address)
    else:
        script_set_text(args, host, address)

def script_set_text(args, host, address):
    ''' Send a new :class:`Rotation` to the zuil. Called from :func:`main`.'''
    if args.file:
        try:
            with open(args.file, 'r') as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            logging.critical('Could not open file %s, exiting', args.file)
            sys.exit(1)

    else:
        read_data = sys.stdin.read()
        data = json.loads(read_data)

    rotation = Rotation.from_dict(data)
    rotation.address = address
    controlstring = rotation.to_controlstring()

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write(controlstring)

    connect_and_send(host, controlstring)
