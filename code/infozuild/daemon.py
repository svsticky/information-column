'''
Daemon that will periodically update the zuil.

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

from apscheduler.schedulers.blocking import BlockingScheduler

from . import __version__, sendscript, getscript


logging.basicConfig(level=logging.INFO)

JOB_DEFAULTS = {
    'coalesce': True,   # If multiple updates have been missed, they can be replaced by a single one.
    'max_instances': 1  # Don't send multiple updates at the same time.
}

SCHEDULER = BlockingScheduler(job_defaults=JOB_DEFAULTS)
DEBUGGING = False

def update_zuil(host, controller_address, max_events, print_only=False):
    '''
    Wrapper method to retrieve events and update the zuil.

    Args:
        host (str): The hostname or IP address of the controller.
        controller_address (int): The controller index, usually 0.
        max_events (int): The maximum number of events to display. -1 to show
            all.
        print_only (bool): activate debugging and bypass actually updating the
            zuil, instead only printing the control string to debug.
    '''
    data = getscript.make_rotation(max_events)
    data.address = int(controller_address)
    logging.debug(data.to_json())
    controlstring = data.to_controlstring()

    if not print_only:
        sendscript.connect_and_send(host, controlstring)
    logging.debug(repr(controlstring.encode()))

def main():
    ''' :command:`zuild` entry point. '''
    global DEBUGGING

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
    max_events = args.limit or config.getint('Daemon', 'MaxEntries')

    logging.debug('Parameters: host %s, index %s, interval %s',
                  host, controller_address, update_interval)
    logging.debug('Limit %s, configfile %s', max_events, args.config)

    if args.once:
        update_zuil(host, controller_address, max_events) # Will exit after this

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
            update_zuil, trigger='cron', args=(host, controller_address, max_events),
            minute=update_interval, id='zuild.update')

        if not args.verbose:
            logging.getLogger().setLevel(logging.WARNING)
        SCHEDULER.start() # Blocking call

def quit_handler_cb(sig, *args):
    ''' Called when SIGINT, SIGTERM or SIGQUIT is received while in daemon mode.
    Attempt to shutdown somewhat cleanly by waiting for the currently executing jobs.'''

    logging.info('Shutting down, caught signal %s.', sig)
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
