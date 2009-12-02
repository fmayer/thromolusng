#!/usr/bin/env python
# -*- coding: us-ascii -*-

# asynchia - asynchronous networking library
# Copyright (C) 2009 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    # If we got setuptools, use it so we get the nice develop cmd.
    from setuptools import setup
except:
    # Doesn't matter if we don't have it though.
    from distutils.core import setup


VERSION = '0.1a1'


setup(
    name='thromolusng',
    version=VERSION,
    description='Clone of the Amiga game Thromolus.',
    author='Florian Mayer',
    author_email='flormayer@aim.com',
    url='http://github.com/segfaulthunter/thromolusng',
    keywords='game board',
    license='GPL',
    zip_safe=True,
    packages=['thromolusng', 'thromolusng.data', 'thromolusng.interface'],
)
