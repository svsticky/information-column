#! /usr/bin/python

from pprint import pprint;
import sys, getopt, json, configparser
from math import floor;

Config = configparser.ConfigParser();

def ConfigSectionMap(section): # Get the keys of a certain section
    dict1 = {} # Initialize the dictionary
    options = Config.options(section) # Get the options
    for option in options: # foreach option
        try:
            dict1[option] = Config.get(section, option) # set the key to this value
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def ValueCharacter(value):
    return chr(value+32)

def main(argv):
    Config.read("./settings/main.cfg"); # Read the configuration file

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

    ip = ConfigSectionMap("ConnectionInfo")['server'] # get the IP on which to connect
    address = int(ConfigSectionMap("ConnectionInfo")['address']) # Get the address of the controller

    print("Attempting to connect to {0} controller on port {1}".format(ip, address))

    controlstring = "%s%s\n" % (soh, chr(address+32))

    controlstring += ReadPages(data["pages"]);
    controlstring += "%s%s%s" % (fs, syn, cr)

    if (writeToOutput and output != ''):
        f = open(output, 'w')
        f.write(controlstring)
        f.close()
    else:
        print(controlstring)
    TimeValue("  7'")
    TimeValue(" !'&")


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
    return "%sB%s%s\n" % (esc, ValueCharacter(v), fs)

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
    return "%sA%s%s%s%s\n" % (esc, ValueCharacter(vA), ValueCharacter(vB), ValueCharacter(vC), ValueCharacter(vD))

def BetterReadtime(value):
    valA = floor(value/4096);
    value %= 4096;
    valB = floor(value/256);
    value %= 256;
    valC = floor(value/16);
    value %= 16;
    valD = floor(value);

    print("%s %s %s %s" % (valA, valB, valC, valD))

    v = 2048*valA + 256 * valB + 16*valC + valD;
    print(v);

    return Readtime(int(valA), int(valB), int(valC), int(valD));

def TimeValue(value):
    for char in value:
        print(int(char));

def Brightness(value):
    v = int(value);
    if ( v < 1 or v > 17):
        raise NameError("Value must be between 1 and 17");
    return "%sQ%s%s\n" % (esc, ValueCharacter(v), fs);

def Scroll(value):
    v = int(value);
    if (v < 0 or v > 1):
        raise NameError("Value must be either 0 or 1");
    return "%sR%s%s\n" % (esc, ValueCharacter(v), fs);

def Fading(value):
    v = int(value)

def ReadPages(pages):
    string = "";
    for page in pages:
        string += ReadPage(page)
    return string;

def ReadPage(page):
    p = "";
    for x in range(0,8):
        p += "%s%s%s\n" % (fs, x, page["lines"][x])
    p += "%s\n" % (fs)
    p += BetterReadtime(page["time"]/26.7);
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
