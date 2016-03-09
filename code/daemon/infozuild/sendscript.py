#! /usr/bin/python

import socket
from pprint import pprint
import sys, getopt, json, configparser
from math import floor

Config = configparser.ConfigParser()

def ValueCharacter(value):
    return chr(value+32)

def main(argv=sys.argv[1:]):
    Config.read("./settings/main.cfg") # Read the configuration file

    file = ''
    output = ''
    writeToOutput = False

    try:
        opts, args = getopt.getopt(argv, "hf:o:", ["file=","output="])
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

    if (file == ''):
        file = 'test.json'
    with open(file) as data_file:
        data = json.load(data_file)

    ip = Config["ConnectionInfo"]['server'] # get the IP on which to connect
    address = int(Config["ConnectionInfo"]['address']) # Get the address of the controller

    print("Attempting to connect to {0} controller on port {1}".format(ip, address))

    controlstring = "%s%s" % (soh, chr(address+32))

    controlstring += ReadPages(data["pages"])
    controlstring += "%s%s%s" % (fs, syn, cr)

    if (writeToOutput and output != ''):
        f = open(output, 'w')
        f.write(controlstring)
        f.close()
    tv1 = TimeValue("  7'")
    tv2 = TimeValue(" !'&")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 23))
    sock.recv(1024) # Necesssary to get rid of the *** mini blabla *** header!

    sock.sendall(controlstring.encode())
    sock.sendall(str(tv1).encode())
    sock.sendall(str(tv2).encode())
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
    if (v < 0 or v > 4):
        raise NameError('Value must be between 0 and 4')
    return "%sB%s%s" % (esc, ValueCharacter(v), fs)

def Readtime(valueA, valueB, valueC, valueD):
    vA = int(valueA)
    vB = int(valueB)
    vC = int(valueC)
    vD = int(valueD)
    if (vA < 0 or vA > 50):
        raise NameError('Value must be between 0 and 50')
    if (vB < 0 or vB > 50):
        raise NameError('Value must be between 0 and 50')
    if (vC < 0 or vC > 50):
        raise NameError('Value must be between 0 and 50')
    if (vD < 0 or vD > 50):
        raise NameError('Value must be between 0 and 50')
    return "%sA%s%s%s%s" % (esc, ValueCharacter(vA), ValueCharacter(vB), ValueCharacter(vC), ValueCharacter(vD))

def BetterReadtime(value):
    valA = floor(value/4096)
    value %= 4096
    valB = floor(value/256)
    value %= 256
    valC = floor(value/16)
    value %= 16
    valD = floor(value)

    print("%s %s %s %s" % (valA, valB, valC, valD))

    v = 2048*valA + 256 * valB + 16*valC + valD
    print(v)

    return Readtime(int(valA), int(valB), int(valC), int(valD))

def TimeValue(value):
    i = len(value)-1
    ii = 0
    s = 0
    while i >= 0:
        s += pow(16, ii) * (ord(value[i])-32)
        i -=1
        ii += 1
        pass
    print(s)
    return s

def Brightness(value):
    v = int(value)
    if ( v < 1 or v > 17):
        raise NameError("Value must be between 1 and 17")
    return "%sQ%s%s" % (esc, ValueCharacter(v), fs)

def Scroll(value):
    v = int(value)
    if (v < 0 or v > 1):
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
    for x in range(0,8):
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
