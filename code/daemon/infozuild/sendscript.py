#! /usr/bin/python
'''
Contains the relevant code to generate a controlstring and send it to the zuil.
'''

import configparser
import getopt
import json
import logging
import os.path
import socket
import sys
from math import floor

Config = configparser.ConfigParser()

def ValueCharacter(value):
    return chr(value+32)

def main(argv=sys.argv[1:]):
    ''' Console script entrypoint '''
    configdir = os.path.expanduser('~/.infozuil')
    configpath = os.path.join(configdir, 'send.cfg')
    if not os.path.isdir(configdir) or not os.path.isfile(configpath):
        logging.critical('Configfile does not exist, please create send.cfg in ~/.infozuil')
        os.mkdir(configdir)
        sys.exit(1)
    Config.read(configpath) # Read the configuration file

    file = ''
    output = ''
    writeToOutput = False

    try:
        opts, args = getopt.getopt(argv, "hf:o:", ["file=", "output="])
    except getopt.GetoptError:
        print('sendscript.py -f <json file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('sendscript.py -f <json file>')
            sys.exit()
        elif opt in ("-f", "--file"):
            file = arg
        elif opt in ("-o", "--output"):
            output = arg
            writeToOutput = True

    if file == '':
        file = 'test.json'
    try:
        with open(file) as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        logging.critical('Could not open file %s, exiting', file)
        sys.exit(1)

    ip = Config["ConnectionInfo"]['server'] # get the IP on which to connect
    address = int(Config["ConnectionInfo"]['address']) # Get the address of the controller

    logging.info("Attempting to connect to %s controller on port %s", ip, address)
    controlstring = build_controlstring(data, address)

    if writeToOutput and output != '':
        f = open(output, 'w')
        f.write(controlstring)
        f.close()

    connect_and_send(ip, controlstring)

def build_controlstring(data, address):
    '''
    Build a controlstring that can be sent to the zuil from a data object and controller address.

    Controller address is not an IP!
    '''
    result = '{}{}'.format(soh, chr(address+32))
    result += ReadPages(data["pages"])
    result += '{}{}{}'.format(fs, syn, cr)
    result += str(TimeValue("  7'"))
    result += str(TimeValue(" !'&"))
    return result

def connect_and_send(ip, controlstring):
    ''' Open a connection and send the control string. '''
    logging.info('Connecting to %s', ip)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, 23))
    except OSError as ex:
        logging.error('Could not connect to %s: %s', ip, ex)
        return
    sock.recv(1024) # Necesssary to get rid of the *** mini blabla *** header!

    sock.sendall(controlstring.encode())
    sock.close()

# Define standard values for the protocol.
soh = chr(1)  # Start of Heading
cr  = chr(13) # Carriage Return
so  = chr(14) # Bold Text - only usable for information panels
syn = chr(22) # Synchronisation
esc = chr(27) # Escape
fs  = chr(28) # Field Seperator
gs  = chr(29) # Blink
# End of definition of standard values.

def BlinkSpeed(value):
    v = int(value)
    if v < 0 or v > 4:
        raise NameError('Value must be between 0 and 4')
    return "%sB%s%s" % (esc, ValueCharacter(v), fs)

def Readtime(valueA, valueB, valueC, valueD):
    vA = int(valueA)
    vB = int(valueB)
    vC = int(valueC)
    vD = int(valueD)
    if any(x < 0 or x > 50 for x in (vA, vB, vC, vD)):
        raise NameError('Values for readtime must be between 0 and 50.')
    return "%sA%s%s%s%s" % (
        esc, ValueCharacter(vA), ValueCharacter(vB), ValueCharacter(vC), ValueCharacter(vD))

def BetterReadtime(value):
    valA = floor(value/4096)
    value %= 4096
    valB = floor(value/256)
    value %= 256
    valC = floor(value/16)
    value %= 16
    valD = floor(value)

    logging.debug("Readtime: %s %s %s %s", valA, valB, valC, valD)

    v = 2048*valA + 256 * valB + 16*valC + valD
    logging.debug('Readtime: %s', v)

    return Readtime(int(valA), int(valB), int(valC), int(valD))

def TimeValue(value):
    i = len(value)-1
    ii = 0
    s = 0
    while i >= 0:
        s += pow(16, ii) * (ord(value[i])-32)
        i -= 1
        ii += 1
    logging.debug('Timevalue %s', s)
    return s

def Brightness(value):
    v = int(value)
    if v < 1 or v > 17:
        raise NameError("Value must be between 1 and 17")
    return "%sQ%s%s" % (esc, ValueCharacter(v), fs)

def Scroll(value):
    v = int(value)
    if v < 0 or v > 1:
        raise NameError("Value must be either 0 or 1")
    return "%sR%s%s" % (esc, ValueCharacter(v), fs)

def Fading(value):
    v = int(value)

def ReadPages(pages):
    string = ""
    for page in pages:
        string += ReadPage(page)
    return string

def ReadPage(page):
    p = ""
    for x in range(0, 8):
        try:
            p += "%s%s%s" % (fs, x, page["lines"][x])
        except IndexError: #out of lines
            p += "%s%s%s" % (fs, x, "")
    p += "%s" % (fs)
    p += BetterReadtime(page["time"]/26.7)
    return p


#Default format:
# (addressing)                       --> Address string for one controller
# 1 < x <= 8                         --> Pages 1 until 8
#   (page x: line 1 text)            --> Text of page 1, first line until the eight line
#   (page x: line 8 text)
#   (page attributes)                --> Attributes of this page (blinktime, readtime, schedular)
#   (information panel attributes)   --> Additional for information panel! (scroll- and fading effect)
#   (moving message attributes)      --> Additional for moving messages! (moving speed, text width
# (synchronisation)                  --> Synchronisation character
# (carriage return)                  --> Termination character
# The controller, page, information panel and moving message attributes are ESC commands.


if __name__ == "__main__":
    main(sys.argv[1:])
