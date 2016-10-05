'''
infozuild.daemon provides functions that will periodically update the zuil.

The daemon uses APScheduler to schedule regular updates, by using the functions
found in :mod:`infozuild.getscript` and :mod:`infozuild.sendscript` via :func:`update_zuil`.

The following signals will be handled:
    * SIGUSR1: schedule an update job to be executed immediately.
    * SIGUSR2: toggle the logging level between INFO and DEBUG.
    * SIGINT, SIGTERM, SIGQUIT: Cleanly wait for running jobs to end, and stop the daemon.
'''
import logging
import configparser
import argparse
import signal
import os.path
from os.path import expanduser
import random

from apscheduler.schedulers.blocking import BlockingScheduler
import fortune

from . import __version__, sendscript, getscript


logging.basicConfig(level=logging.INFO)

JOB_DEFAULTS = {
    'coalesce': True,   # If multiple updates have been missed, replace with only one.
    'max_instances': 1  # Don't send multiple updates at the same time.
}

FORTUNES = os.path.join(os.path.dirname(__file__), 'motds.txt')
FORTUNE_FREQUENCY = 0.05
DEFAULT_STATUS = 'Dagelijks geopend van 9-17 uur.'
SCHEDULER = BlockingScheduler(job_defaults=JOB_DEFAULTS)
MANAGER = None
DEBUGGING = False

class ZuilManager:
    '''
    The ZuilManager keeps track of what to display on the Zuil, by caching a
    list of events and responding to update requests.

    Using a manager allows us to not lose all events when Koala cannot be
    reached, but show an informative message and reuse the old events instead.
    Shutdown messages and rotating MOTDs are also inserted by the manager.

    Args:
        host (str): The hostname or IP address of the controller.
        controller_address (int): The controller index, usually 0.
        max_events (int): The maximum number of events to display. None to show
            all.
        print_only (bool): activate debugging and bypass actually updating the
            zuil, instead only printing the control string to debug.
    '''

    def __init__(self, host, controller_address, max_events, print_only=False):
        '''
        On start, save arguments and confirm that we can load the MOTDs.
        '''
        self.host = host
        self.controller_address = int(controller_address)
        self.max_events = max_events
        self.print_only = print_only

        self.events = []
        self.status = 'infozuild {}'.format(__version__)

        self.fortunes = None
        try:
            fortune.make_fortune_data_file(FORTUNES, quiet=True)
            self.fortunes = FORTUNES
        except FileNotFoundError:
            logging.warning('Failed to load status messages.')

    def generate_status(self):
        ''' Determine what message will be shown as status if no error. '''
        if self.fortunes and random.random() < FORTUNE_FREQUENCY:
            try:
                return fortune.get_random_fortune(self.fortunes)
            except ValueError:
                logging.error('Fortune file failed, disabled.')
                self.fortunes = None
        return DEFAULT_STATUS

    def update_activities(self):
        '''
        Attempt to update the cache of events, keep the old events in case of
        an error, and refresh the display with the possibly new content.
        '''
        new_events, error = getscript.get_activities()
        if not error:
            self.events = new_events
        self.status = error # Will clear old error if it is resolved.

        if not self.events and not error:
            self.status = 'Geen activiteiten gevonden.'

        self.refresh_zuil()

    def handle_shutdown(self):
        ''' Immediately update the zuil with a new status message indicating
        the pi is powering off.'''

        self.status = 'De zuil staat nu uit.\nPower-cycle voor nieuwe inhoud.'
        self.refresh_zuil()

    def make_rotation(self):
        '''
        Build the rotation that will be sent to the zuil. Exposed for debugging purposes.
        '''
        rota = getscript.make_rotation(
            self.events, self.status or self.generate_status(), self.max_events)
        rota.address = self.controller_address
        logging.debug(rota.to_json())

        return rota

    def refresh_zuil(self):
        '''
        Create a new :class:`Rotation`, populate it with the earlier retrieved
        events, and send it to the controller to be displayed.
        '''

        controlstring = self.make_rotation().to_controlstring()
        if not self.print_only:
            sendscript.connect_and_send(self.host, controlstring)
        logging.debug(repr(controlstring.encode()))

def main():
    ''' :command:`zuild` entry point. '''
    global DEBUGGING
    global MANAGER

    # Parse command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version',
                        version='infozuild {}'.format(__version__))

    parser.add_argument('--once', action='store_true',
                        help='update immediately and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='activate debugging output')

    parser.add_argument('--interval', type=int,
                        help='number of minutes to wait between updates')
    parser.add_argument('--limit', '-l', type=int, default=None,
                        help='maximum number of events to show')
    parser.add_argument('--config', default='~/.infozuil/daemon.ini',
                        help='configuration file to read')
    parser.add_argument('--host', default=None,
                        help='controller ip or hostname')
    parser.add_argument('--index', type=int, default=None,
                        help='controller index')
    parser.add_argument('--noop', '-n', action='store_true',
                        help='do not actually send content to the controller')

    args = parser.parse_args()

    if args.verbose:
        DEBUGGING = True
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug(args)

    # Read config file(s)
    config = configparser.ConfigParser()
    read_configs = config.read(
        [
            os.path.join(os.path.dirname(__file__), 'daemon.ini'),
            expanduser(args.config)
            ])

    logging.debug('Read configs: %s', read_configs)

    host = args.host or config['ConnectionInfo']['Server']
    controller_address = args.index or config['ConnectionInfo']['Address']

    update_interval = '*/{}'.format(args.interval or config['Daemon']['Interval'])
    max_events = args.limit or config.getint('Daemon', 'MaxEntries', fallback=None)

    logging.debug('Parameters: host %s, index %s, interval %s',
                  host, controller_address, update_interval)
    logging.debug('Limit %s, configfile %s, noop %s', max_events, args.config, args.noop)

    MANAGER = ZuilManager(host, controller_address, max_events, args.noop)

    if args.once:
        MANAGER.update_activities() # Script will exit after this.

    else:
        # Register signal handlers
        signal.signal(signal.SIGTERM, quit_handler_cb)
        signal.signal(signal.SIGINT, quit_handler_cb)
        try:
            signal.signal(signal.SIGQUIT, quit_handler_cb)
            signal.signal(signal.SIGUSR1, update_now_cb)
            signal.signal(signal.SIGUSR2, toggle_loglevel_cb)
        except ValueError:
            pass # Unavailable on Windows

        # Register update job
        SCHEDULER.add_job(
            MANAGER.update_activities, trigger='cron',
            minute=update_interval, id='zuild.update')

        if not args.verbose:
            logging.getLogger().setLevel(logging.WARNING)

        # Display version
        MANAGER.refresh_zuil()
        SCHEDULER.start() # Blocking call

def quit_handler_cb(sig, *args):
    ''' Called when SIGINT, SIGTERM or SIGQUIT is received while in daemon mode.
    Attempt to shutdown somewhat cleanly by waiting for the currently executing jobs.'''

    logging.info('Shutting down, caught signal %s.', sig)
    MANAGER.handle_shutdown()
    SCHEDULER.shutdown()

def update_now_cb(*args):
    ''' Called on SIGUSR1, add a 'update-zuil'-job scheduled to execute immediately. '''
    job = SCHEDULER.get_job('zuild.update')
    SCHEDULER.add_job(job.func, args=job.args, kwargs=job.kwargs,
                      name='manual_update', id='zuild.manual')

def toggle_loglevel_cb(*args):
    ''' Called on SIGUSR2, toggles the loglevel between DEBUG and WARNING. '''
    global DEBUGGING
    if DEBUGGING:
        logging.getLogger().setLevel(logging.WARNING)
        DEBUGGING = False
    else:
        logging.getLogger().setLevel(logging.DEBUG)
        DEBUGGING = True
    logging.warning('Loglevel set to %s', 'debug' if DEBUGGING else 'warn')

if __name__ == '__main__':
    main()
