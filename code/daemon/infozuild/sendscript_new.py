
#! /usr/bin/python
'''
Contains the relevant code to generate a controlstring and send it to the zuil.
'''
import datetime
import math


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

    def __init__(self, mode):
        ''' Unfortunately trivial. '''
        if mode not in DisplayMode.modes:
            raise ValueError('Unknown DisplayMode:', mode)
        self.mode = mode

    def to_controlstring(self, address):
        ''' Generate a control string from the known mode and given address. '''
        result = start_controlstring(address)
        result += ESC + 'D'
        result += encode_value(self.mode)
        result += FS + CR

        return result

def set_rtc(address, when=None):
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
    def __init__(self, lines):
        ''' Initialize a new page with the given text-lines and default attributes. '''
        self.lines = lines

        self.blinkspeed = 4
        # pylint: disable=fixme
        self.duration = 10012 # TODO: define sane defaults
        self.schedular = datetime.datetime.now()
        self.brightness = 2
        self.scrolling = True
        self.fading = False

        # All moving-text attributes are removed, because we can't use them anyway.

    def build_duration(self):
        ''' Return 4 characters representing the duration of this page. '''
        i = self.duration

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
        return result

    def build_schedular(self):
        ''' Return 7 characters respresenting the schedular, whatever it may be. '''
        enc = encode_value

        sch = self.schedular
        return '{}{}{}{}{}{}{}'.format(
            enc(sch.year), enc(sch.month), enc(0), enc(sch.day), enc(sch.hour),
            enc(sch.minute), enc(sch.second))

    def to_controlstring(self):
        ''' Convert the page to a controlstring. This string must be used in a rotation! '''
        # Validate attributes are valid
        check_in_range(
            ('Blink speed', self.blinkspeed, 0, 4),
            ('Duration', self.duration, 1, 218450),
            ('Brightness', self.brightness, 1, 17),
            ('Year', self.schedular.year, 1980, 2075),
            ('Month', self.schedular.month, 1, 12),
            ('Day', self.schedular.day, 1, 31),
            ('Hour', self.schedular.hour, 0, 23),
            ('Minute', self.schedular.minute, 0, 59),
            ('Second', self.schedular.second, 0, 59)
            )

        result = ''
        for num, line in enumerate(self.lines):
            result += str(num) + line + FS

        if self.blinkspeed:
            result += ESC + 'B' + encode_value(self.blinkspeed) + FS

        result += ESC + 'A' + self.build_duration() + FS

        if self.schedular:
            result += ESC + 'P' + self.build_schedular() + FS

        result += ESC + 'Q' + encode_value(self.brightness) + FS

        if self.scrolling:
            result += ESC + 'R' + encode_value(1) + FS
        if self.fading:
            result += ESC + 'S' + encode_value(1) + FS

        return result

    def to_json(self):
        ''' Dump all relevant attributes as a JSON object. '''
        pass

class Rotation:
    ''' Contains the pages that should be displayed, and the controller address. '''
    def __init__(self, address):
        self.address = address
        self.pages = []

    def to_controlstring(self):
        ''' Convert the rotation to a controlstring that can be sent to the controller. '''
        check_in_range(('Address', self.address, 0, 31))

        result = start_controlstring(self.address)

        for page in self.pages:
            result += page.to_controlstring()

        result += SYN + CR

        return result

    def to_json(self):
        ''' Dump all relevant attributes as a JSON object. '''
        pass

## Functions to manipulate lines,
