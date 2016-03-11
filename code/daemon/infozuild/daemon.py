''' Daemon that will periodically update the zuil. '''
import logging
import configparser
import argparse
from os.path import expanduser

from apscheduler.schedulers.blocking import BlockingScheduler

from .getscript import make_pages_dict
from .sendscript import build_controlstring, connect_and_send


logging.basicConfig(level=logging.INFO)

JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 1
}

def update_zuil(host, controller_address, max_events):
    ''' Wrapper method to retrieve events and update the zuil. '''
    data = make_pages_dict(max_events)
    controlstring = build_controlstring(data, int(controller_address))
    connect_and_send(host, controlstring)

def main():
    ''' Console entry point. '''
    parser = argparse.ArgumentParser()

    parser.add_argument('--once', action='store_true',
                        help='update immediately and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='activate debugging output')

    parser.add_argument('--interval', type=int,
                        help='number of minutes to wait')
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
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug(args)

    config = configparser.ConfigParser()
    config.read(expanduser(args.config))
    host = args.host or config['ConnectionInfo']['Server']
    controller_address = args.index or config['ConnectionInfo']['Address']

    update_interval = '*/{}'.format(args.interval or config['Daemon']['Interval'])
    max_events = args.limit or config.getint('Daemon', 'MaxEntries')

    logging.debug('Parameters: host %s, index %s, interval %s',
                  host, controller_address, update_interval)
    logging.debug('Limit %s, configfile %s', max_events, args.config)

    if args.once:
        update_zuil(host, controller_address, max_events)

    else:
        scheduler = BlockingScheduler(job_defaults=JOB_DEFAULTS)
        scheduler.add_job(
            update_zuil, trigger='cron', args=(host, controller_address, max_events),
            hour='7-19', minute=update_interval)

        scheduler.start()

if __name__ == '__main__':
    main()
