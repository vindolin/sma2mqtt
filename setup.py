# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='sma2mqtt',
    version='0.0.7',
    author='Thomas Schüßler',
    scripts=['scripts/sma2mqtt'],
    description='Command line tool that listens to the multicast Speedwire of a SMA Energy Meter/Home Manger 2.0 and writes the values to a MQTT server.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.0',
    ],
    keywords=['sma', 'mqtt'],
    url='https://github.com/vindolin/sma2mqtt',
    license='MIT',
    packages=['sma2mqtt'],
    install_requires=[
        'paho-mqtt==1.6.1',
    ],
)
