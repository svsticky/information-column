# Information column

The **information column** is the billboard-like device standing outside Sticky's chamber. The goal is to show the upcoming events at Sticky with its start/end dates and times. It should give an easy overview for members of Sticky.

## Technical requirements

* A Linux client device with
   * A wired network interface AND
   * A wireless interface
* A server to run the serverside code
* The information column

## Dependencies

### Client

* Perl (version unknown)
* libwww-perl
* ?

### Server

* Web server with PHP

## Future plans

* Rewrite of the client code in Python.
* Use of the [Koala](https://github.com/StickyUtrecht/constipated-koala) API as the source of  information, instead of a public Google Calendar feed.

## Installation
Install the client code on the client, and the serverside code on your server. Setup the network configuration of the client environment as described [here](config/network-config.md).

Use `gettext.pl` to retrieve the current information from the server, and `sendtozuil.pl /path/to/zuiltext` to upload `/path/to/zuiltext` to the information column. It will be instantly looped on the matrix display of the column.
