sendscript
==========

.. automodule:: infozuild.sendscript
    :members:

The RTC
-------
Some substrings, when used in the text on a page, will be automatically
replaced with something else:

======== ===============================================
Original Replacement
======== ===============================================
``%M``   Numeric month (01 for January, etc.)
``%D``   Numeric day in month
``%H``   Hour (24-hour clock)
``%m``   Minute
``%S``   Second
``%R``   Hourglass glyph indicating time until next page
======== ===============================================

.. _display_modes:

Display modes
-------------
The following display modes are listed in the manual:

00. *Blank*. The display will blank until the mode is changed to *normal* or
    *test on*. New pages can be entered while the display is blanked, and the
    currently stored pages are kept.
01. *Normal*. The controller will operate as usual, displaying the pages loaded
    earlier. Setting this mode multiple times does not seem to have any special
    effect.
02. *Test off*. Setting this mode will disable the testing sequence and blank
    the display, and allow for new pages to be entered.
03. *Test pause*. Setting this mode will pause the rotation of test pages on
    the current page. Setting this mode does not pause the rotation of normal
    pages.
04. *Test on*. Setting this mode enables testing mode, which makes the
    controller show some pre-defined pages to turn on all leds and such. When
    test mode is enabled, all previously stored pages are forgotten!

10. *Output*. According to the manual, setting this mode will toggle some kind
    of hardware output on the controller board. We don't seem to use this and
    it has not been tested.

