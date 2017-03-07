import os
from setuptools import setup

basedir = os.path.abspath(os.path.dirname(__file__))

setup(
    name='app',
    packages=['app'],
    include_package_data=True,
    install_requires=[
        'flask', 'gevent', 'gevent-websocket'
    ],
)