#Information column
The **information column** is the billboard like thing standing outside Sticky. The goal is the show the upcoming events at Sticky with the time people are expected and the date of the event. It should give an easy overview for members of Sticky.

##Technical requirements
At first it will do if it could read out a YAML file with the events that should be put on the screen. I believe this should be the first version, it is probably already hard enough to get the thing started and be able to access it.

It would be nice the system (which is in fact an old laptop could be approached with something like *infozuil.local* on the Sticky network *Woestgaafsecure*. This should be accomplished by adding a hostname (like a printer does).

Using a simple ``ssh`` command we can easily update such a YAML file and edit the screen. Followed by update call of the script updating the screen.

There is a python script I believe but it would be easier to start over and just find out how to write something on the screen, and in which format. For the format of the screen we would like to put the date and time to the right of the screen whilst the activity itself is the line above it aligned to the left. To be consistent it would be nice it the time and date have a fixed format, hence no matter what the time is it should be outlined directly above or below the other activities. Using this format the activity can have a quite long name but if that isn't enough we should scroll or something.

##Future plans
In the future the above could be extended with a program that uses the public [Sticky activities calendar][calendar] and updates daily or if necessary with a command if a immediate update is required.

##Dependencies

##Installation

##License
The MIT License (MIT)

Copyright (c) 2014 Martijn Casteel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

[calendar]: http://www.google.com/calendar/ical/stickyutrecht.nl_thvhicj5ijouaacp1elsv1hceo@group.calendar.google.com/public/basic.ics
