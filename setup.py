#!/usr/bin/env python
from setuptools import setup


VERSION = "0.1.0"

setup (# Distribution meta-data
       name = "rpi-mjpeg",
       version = VERSION,
       author = "Luke Wahlmeier",
       author_email = "lwahlmeier@gmail.com",
       url = "https://github.com/lwahlmeier/rpi-mjpeg",
       download_url = "https://github.com/lwahlmeier/rpi-mjpeg/tarball/%s"%(VERSION),
       #test_suite = "tests",
       license = "unlicense",
       description = "A mjpeg server for rasberrypi",
       install_requires = ['threadly>=0.7.2', 'litesockets>=0.7.1', 'picamera>=1.13'],
       scripts =  ['mjpegServer'],
       keywords = ["networking"],
       classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: Public Domain'
        ],

      )
