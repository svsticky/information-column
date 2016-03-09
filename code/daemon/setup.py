''' Package information for infozuild. '''
from setuptools import setup

setup(
    name='infozuild',
    version='0.2.0',
    description='daemon and scripts for updating the infozuil',

    url='https://github.com/svsticky/information-column',
    author='Study Association Sticky',
    author_email='info@svsticky.nl',

    packages=['infozuild'],
    entry_points={
        'console_scripts': [
            'zuil-get=infozuild.getscript:main',
            'zuil-send=infozuild.sendscript:main',
            'zuild=infozuild.daemon:main',
            ],
        },
    install_requires=[
        'requests',
        'apscheduler',
    ],
    zip_safe=False
)