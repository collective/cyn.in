# Calendaring is a simple CMF/Plone calendaring implementation.
# Copyright (C) 2004 Enfold Systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
$Id: test_functional.py 49837 2007-09-21 11:03:20Z regebro $
"""


import os, sys
from os import curdir
from os.path import join, abspath, dirname, split
from StringIO import StringIO
from dateutil.tz import tzutc

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite as DocSuite

# Install our product
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('Calendaring')
ZopeTestCase.installProduct('ATContentTypes')
ZopeTestCase.installProduct('Marshall')

from Products.CMFPlone.tests import PloneTestCase
from Products.Calendaring.tests.utils import installType

class FunctionalTest(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.qi = self.portal.portal_quickinstaller
        self.qi.installProduct('PortalTransforms')
        self.qi.installProduct('Archetypes')
        self.qi.installProduct('Calendaring')
        self.cal = self.portal.portal_calendar

        # Install ATEvent as Event
        installType(self.portal,
                    'ATEvent',
                    'ATContentTypes',
                    'Event',
                    dynamic=True)

        # Install ATFolder as Folder
        installType(self.portal,
                    'ATFolder',
                    'ATContentTypes',
                    'Folder',
                    dynamic=True)

def test_suite():
    suite = unittest.TestSuite()
    functional = [
        (FunctionalTest, 'export.txt'),
        (FunctionalTest, 'marshall.txt'),
        ]
    
    optionflags =  (doctest.ELLIPSIS |
                    doctest.NORMALIZE_WHITESPACE |
                    doctest.REPORT_ONLY_FIRST_FAILURE)    
    for test, f in functional:
        suite.addTest(DocSuite(f, test_class=test,
                               package='Products.Calendaring.tests',
                               globs=globals(),
                               optionflags=optionflags))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
