# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='sma2mqtt',
    version='0.1',
    author='Thomas Schüßler',
    description='Command line tool that connects to the multipass stream and writes... TODO',
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
    entry_points={
        'console_scripts': ['sma2mqtt=sma2mqtt.main:main'],
    },
)
