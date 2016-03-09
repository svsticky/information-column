''' Daemon that will periodically update the zuil. '''
import logging
import configparser
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
    config = configparser.ConfigParser()
    config.read(expanduser('~/.infozuil/daemon.ini'))
    host = config['ConnectionInfo']['Server']
    controller_address = config['ConnectionInfo']['Address']

    update_interval = '*/{}'.format(config['Daemon']['Interval'])
    max_events = config.getint('Daemon', 'MaxEntries')

    scheduler = BlockingScheduler(job_defaults=JOB_DEFAULTS)
    scheduler.add_job(
        update_zuil, trigger='cron', args=(host, controller_address, max_events),
        hour='7-19', minute=update_interval)

    scheduler.start()

if __name__ == '__main__':
    main()
