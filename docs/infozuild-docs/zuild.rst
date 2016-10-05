zuild
=====

Name
----
``zuild``, a daemon for automatically displaying events on the zuil

Synopsis
--------
.. code-block:: bash

    zuild [--help|-h]
        | --version
        | [--noop] [--once] [--verbose|-v]
          [--interval INTERVAL] [--limit LIMIT | -l LIMIT]
          [--config CONFIG] [--host HOST] [--index INDEX]

Description
-----------
:command:`zuild` is the main script used to update the contents of the
information column. The script starts a scheduler which will retrieve a list of
events at regular intervals, and then update the display with the new events.
The script will indicate exceptional circumstances (connection loss, invalid
retrieved data) by printing messages to standard error, and by showing an error
on the first page.

The daemon has two main modes of operation: "once" and "continuous".
"Once"-mode essentially removes all scheduling functionality and just sends
a single update to the zuil. "Continuous" is the default mode, and will update
(by default) every 5 minutes.

If the content contains :ref:`timecodes` codes, the value of the RTC will be used. This value is not automatically updated, but may be set using :option:`zuil-send --update-rtc`.

The behaviour of the script can be modified by either using command line
options, or by using a configuration file. Both ways are described below.


Configuration File
------------------

Options
-------
.. program:: zuild

.. option:: --help, -h

    Print a short help message describing the available options and exit.

.. option:: --version

    Print the current version of the ``infozuild`` package and exit.

.. option:: --once

    Disable scheduling of updates, retrieve events and update the display once, and exit.

.. option:: --verbose, -v

    Enable display of debugging output on standard error. Information displayed
    includes the results of combining command line options and the
    configuration file, the pages that will be sent to the controller (in
    parsable JSON), and connection status.

.. option:: --interval <interval>

    Specify the number of minutes to wait between updates, if not running with :option:`--once`.

.. option:: --limit <limit>, -l <limit>

    Specify the maximum number of events to show on the pages. If this number is negative, ``abs(limit)`` events will be removed from the end. The default is to display all events.

.. option:: --config <config>

    Specify an alternative configuration file to load. The default location is ``~/.infozuil/daemon.ini``.

.. option:: --host <host>

    Specify an alternative hostname or IP address to send the updates to. Default is ``infozuil.students.cs.uu.nl``, resolving to ``131.211.83.245``.

.. option:: --index <index>

    Specify an alternative controller index to update, probably only useful for controllers with multiple signs connected.

.. option:: --noop

    Do everything except for sending the updates to the controller, for debugging purposes. Best used combined with :option:`--verbose`, to be able to see the content that would be sent.

Debugging
---------
If the daemon is invoked with the following command, the Python interpreter
will activate after the script ends, enabling inspection of variables and
general poking at things:

.. code-block:: bash

    python -i -m infozuild.daemon -v [--once]

The main variable of interest here would be ``MANAGER``, a :class:`infozuild.daemon.ZuilManager`.

See Also
--------
:ref:`zuil-get`, :ref:`zuil-send`
