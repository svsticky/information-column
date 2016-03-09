''' Daemon that will periodically update the zuil. '''
import logging
import configparser
from os.path import expanduser

from .getscript import make_pages_dict
from .sendscript import build_controlstring, connect_and_send

from apscheduler.schedulers.blocking import BlockingScheduler


logging.basicConfig(level=logging.INFO)

JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 1
}

def update_zuil(ip, controller_address):
    ''' Wrapper method to retrieve events and update the zuil. '''
    data = make_pages_dict()
    controlstring = build_controlstring(data, int(controller_address))
    connect_and_send(ip, controlstring)

def main():
    ''' Console entry point. '''
    config = configparser.ConfigParser()
    config.read(expanduser('~/.infozuil/daemon.ini'))
    ip = config['ConnectionInfo']['Server']
    controller_address = config['ConnectionInfo']['Address']

    scheduler = BlockingScheduler(job_defaults=JOB_DEFAULTS)
    scheduler.add_job(
        update_zuil, trigger='cron', args=(ip, controller_address),
        hour='7-19', minute='*')

    scheduler.start()

if __name__ == '__main__':
    main()
