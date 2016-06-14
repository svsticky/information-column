
#! /usr/bin/python
'''
Contains the relevant code to generate a controlstring and send it to the zuil.
'''
import datetime


def encode_value(value):
    ''' Convert a numeric value to an ascii character. '''
    return chr(value + 32)

def decode_value(character):
    ''' Convert an ascii character to a numeric value. (We probably won't need this.) '''
    return ord(character) - 32

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
class DisplayMode:
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
        pass

    def to_controlstring(self):
        ''' Convert the page to a controlstring. This string must be used in a rotation! '''
        pass

class Rotation:
    ''' Contains the pages that should be displayed, and some attributes. '''
    def __init__(self):
        pass

    def to_controlstring(self, address):
        ''' Convert the rotation to a controlstring that can be sent to the controller. '''
        pass

