getscript
=========

.. automodule:: infozuild.getscript
    :members:
    :undoc-members:


Behaviour of build_when
-----------------------
Because it's unnecessary and annoying to show more information than needed,
:func:`build_when` will check the date information of the events against
a number of scenarios in order to determine what actually needs to be shown.

The following assumptions can be made (as they are enforced by Koala):

* `start_date` will always be present.
* `end_time` will never be present without `start_time`.

The following scenarios are likely:

1. `end_date` absent: legacy event, just show `start_date`.

`end_date` same as `start_date`:

2. No times: new(er) all-day event, just show `start_date`
3. `start_time` set, `end_time` absent:
     Event without known end, show `start_time` and `start_date` if not today
4. Both times set:
     Show `start_date` (if not today), `start_time` and `end_time`.

`end_date` NOT the same as `start_date` ("multi-day event"):

5. No times: multi-day all-day event, ``start_date~end_date``
6. Start_time: ``start_date start_time~end_date``
7. Both times: ``start_date start_time~end_date end_time``
