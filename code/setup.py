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

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',

        'Environment :: Console',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],

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
        'python-dateutil',
        'apscheduler',
        'unidecode',
        'sv-fortune',
    ],
    tests_require=[
        'nose2',
        'pylint',
        'hypothesis',
    ],
    test_suite='nose2.collector.collector',
    include_package_data=True,
    zip_safe=False
)
