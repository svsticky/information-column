''' Package information for infozuild. '''
from setuptools import setup

setup(
    name='infozuild',
    version='0.1.0',
    description='daemon and scripts for updating the infozuil',

    url='https://github.com/svsticky/information-column',
    author='Study Association Sticky',
    author_email='info@svsticky.nl',

    packages=['infozuild'],
    entry_points={
        'console_scripts': [
            'zuil-get=infozuild.getscript:main',
            'zuil-send=infozuild.sendscript:main',
            ],
        },
    install_requires=[
        'requests',
    ],
    zip_safe=False
)
