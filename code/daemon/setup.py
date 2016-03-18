''' Package information for infozuild. '''
from setuptools import setup
from infozuild import __version__

setup(
    name='infozuild',
    version=__version__,
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
    tests_require=[
        'nose2',
        'pylint',
    ],
    test_suite='nose2.collector.collector',
    include_package_data=True,
    zip_safe=False
)
