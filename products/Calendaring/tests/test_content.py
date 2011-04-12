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
$Id: test_content.py,v 1.8 2005/01/25 01:03:48 dreamcatcher Exp $
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

import datetime
from DateTime import DateTime
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.tests.base.utils import has_path
from Products.Archetypes.utils import mapply
from Products.Calendaring.tools import calendar
from Products.Calendaring.Extensions.Install import install_tools
from Products.Calendaring.tests.utils import installType
from Products.Calendaring.common import toTime
from Products.Calendaring.marshaller import CalendarMarshaller

def fromFile(obj, stream):
    REQUEST = obj.REQUEST
    RESPONSE = REQUEST.RESPONSE
    marshaller = CalendarMarshaller()
    args = [obj, '']
    items = []
    kwargs = {'file':stream,
              'context':obj,
              'items': items,
              'REQUEST':REQUEST,
              'RESPONSE':RESPONSE}
    mapply(marshaller.demarshall, *args, **kwargs)
    return items

class TestImportCalendar(PloneTestCase.PloneTestCase):

    def _setupCalendar(self):
        self.qi = self.portal.portal_quickinstaller
        # Replace tool manually, to test normal events
        install_tools(self.portal, 'Calendaring',
                      [calendar.CalendarTool.meta_type], StringIO())
        self.cal = self.portal.portal_calendar

        # Install CMF Event as Event.
        pt = self.portal.portal_types
        if 'Event' in pt.objectIds():
            pt.manage_delObjects(ids=['Event'])
        pt.manage_addTypeInformation(
            id='Event',
            add_meta_type='Factory-based Type Information',
            typeinfo_name='CMFCalendar: Event (CMF Event)')
        pt._getOb('Event').manage_changeProperties(
            product='CMFCalendar',
            factory='addEvent',
            title='Event')

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self._setupCalendar()
        self.ct = self.portal.portal_catalog
        self.mt = self.portal.portal_membership
        self.wt = self.portal.portal_workflow
        self.mt.createMemberarea()

    def testImport1(self):
        self.file = open(join(_prefix, 'data', 'example.ics'), 'r')
        self.cal.importCalendar(self.file, do_action=True)
        self.file.close()
        result = self.cal.catalog_getevents(year=2002, month=10)
        events = result[28]['eventslist']
        self.assertEquals(len(events), 1)
        # US/Pacific = GMT-8
        self.assertEquals(events[0]['start'], '19:00:00')
        self.assertEquals(events[0]['end'], '20:00:00')
        self.assertEquals(events[0]['title'], 'Coffee with Jason')
        result = self.cal.catalog_getevents(year=2002, month=11)
        events = result[27]['eventslist']
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0]['start'], '18:00:00')
        self.assertEquals(events[0]['end'], '19:00:00')
        self.assertEquals(events[0]['title'], 'Code Review')
        result = self.cal.catalog_getevents(year=2002, month=12)
        events = result[17]['eventslist']
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0]['start'], '02:00:00')
        self.assertEquals(events[0]['end'], '03:00:00')
        self.assertEquals(events[0]['title'], 'Dinner with T')
        gef = self.cal.getEventsForThisDay
        self.assertEquals(len(gef(DateTime(2002, 10, 28))), 1)
        self.assertEquals(len(gef(DateTime(2002, 11, 27))), 1)
        self.assertEquals(len(gef(DateTime(2002, 12, 17))), 1)
        # Test timezone naive allday event:
        result = self.cal.catalog_getevents(year=2002, month=12)
        events = result[15]['eventslist']
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0]['start'], '00:00:00')
        # Yes, it returns None for all day events
        self.assertEquals(events[0]['end'], None)
        self.assertEquals(events[0]['title'], 'Timezone naive event')

    def testImport2(self):
        self.file = open(join(_prefix, 'data', 'tasks.ics'), 'r')
        self.items = self.cal.importCalendar(self.file, do_action=True)
        self.file.close()
        result = self.cal.catalog_getevents(year=2004, month=4)
        events = result[26]['eventslist']
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0]['start'], '15:30:00')
        self.assertEquals(events[0]['end'], '22:30:00')
        self.assertEquals(events[0]['title'], 'Formal Languages Exam')
        item = self.items[0][1]

        # toTime gives UTC time, date is in GMT-3
        self.assertEquals(toTime(item.start_date), '12:00:00')
        self.assertEquals(toTime(item.end_date), '18:00:00')
        self.assertEquals(item.Title(), 'Send Invoice')
        self.assertEquals(self.wt.getInfoFor(item, 'review_state'), 'private')
        gef = self.cal.getEventsForThisDay
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 1)

    def testImport3(self):
        self.file = open(join(_prefix, 'data', 'frisco.ics'), 'r')
        self.items = self.cal.importCalendar(self.file, do_action=True)
        self.file.close()
        result = self.cal.catalog_getevents(year=2004, month=12)
        events = result[6]['eventslist']
        self.assertEquals(len(events), 1)

        # US/Eastern = GMT-6
        self.assertEquals(events[0]['start'], '23:30:00')
        self.assertEquals(events[0]['end'], None)
        self.assertEquals(events[0]['title'], 'Brazilian jazz at Berkeley')

        events = result[7]['eventslist']
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0]['start'], None)
        self.assertEquals(events[0]['end'], '00:30:00')
        self.assertEquals(events[0]['title'], 'Brazilian jazz at Berkeley')

        item = self.items[0][1]
        self.assertEquals(toTime(item.start_date), '01:30:00')
        self.assertEquals(toTime(item.end_date), '02:30:00')
        self.assertEquals(item.Title(), 'Brazilian jazz at Berkeley')
        self.assertEquals(self.wt.getInfoFor(item, 'review_state'), 'published')
        gef = self.cal.getEventsForThisDay
        self.assertEquals(len(gef(DateTime(2004, 12, 6))), 1)
        self.assertEquals(len(gef(DateTime(2004, 12, 7))), 0)

    def testImport4(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'no_dtend.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        item = self.items[0][1]
        self.failUnlessEqual(item.start_date, item.end_date)

class TestContentTypes(TestImportCalendar):

    def _setupCalendar(self):
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

    def _checkTasks(self, cal, result, items):
        events = result[26]['eventslist']
        self.assertEquals(len(events), 1, events)
        self.assertEquals(events[0]['start'], '15:30:00')
        self.assertEquals(events[0]['end'], '22:30:00')
        self.assertEquals(events[0]['title'], 'Formal Languages Exam')

        item = items[0][1]

        # toTime returns UTC time.
        self.assertEquals(toTime(item.start_date), '12:00:00')
        self.assertEquals(toTime(item.end_date), '18:00:00')
        self.assertEquals(item.Title(), 'Send Invoice')
        self.assertEquals(self.wt.getInfoFor(item, 'review_state'), 'private')

        gef = self.cal.getEventsForThisDay
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 1)
        self.wt.doActionFor(item, 'show')
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 1)
        self.wt.doActionFor(item, 'submit')
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 1)
        self.wt.doActionFor(item, 'publish')
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 2)
        self.wt.doActionFor(item, 'retract')
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 1)
        self.wt.doActionFor(item, 'hide')
        self.assertEquals(len(gef(DateTime(2004, 4, 26))), 1)

        item = items[1][1]

        # toTime returns UTC time.
        self.assertEquals(toTime(item.start_date), '18:30:00')
        self.assertEquals(toTime(item.end_date), '01:30:00')
        self.assertEquals(item.Title(), 'Formal Languages Exam')
        self.assertEquals(self.wt.getInfoFor(item, 'review_state'), 'published')


    def testCalendar(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.portal.invokeFactory('Folder', id='test_calendar2')
        cal2 = self.portal.test_calendar2
        self.file = open(join(_prefix, 'data', 'tasks.ics'), 'r')
        self.items = fromFile(cal, self.file)

        self.assertEquals(len(cal.objectIds()), 2)
        self.assertEquals(len(cal2.objectIds()), 0)

        result = self.cal.catalog_getevents(year=2004, month=4)
        self._checkTasks(cal, result, self.items)

        self.file.seek(0)
        fromFile(cal2, self.file)
        self.file.close()

        self.assertEquals(len(cal2.objectIds()), 2)

    def testKOrganizer(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'korganizer.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        item = self.items[0][1]
        value = '"Sidnei da Silva" <sidnei@awkly.org>'
        attendees = item.getAttendees()
        self.failUnless(value in attendees, (value, attendees))
        self.assertEquals(len(item.getAttendees()), 3, item.attendees)
        self.assertEquals(item.getLocation(), 'Plone.org')

        item = self.items[1][1]
        self.assertEquals(len(item.getAttendees()), 0)
        self.assertEquals(item.getLocation(), 'University')

        item = self.items[2][1]
        self.assertEquals(len(item.getAttendees()), 0)
        self.assertEquals(item.getLocation(), "Mom's House")

        item = self.items[3][1]
        attendees = item.getAttendees()
        value = '"Sidnei da Silva" <sidnei@awkly.org>'
        self.failUnless(value in attendees, (value, attendees))
        value = 'Kitchen Assembler'
        self.failUnless(value in attendees, (value, attendees))
        self.assertEquals(len(item.getAttendees()), 2)
        self.assertEquals(item.getLocation(), 'My Apartment')
        self.assertEquals(item.Title(), 'Assemble Kitchen')
        self.assertEquals(item.Description(),
                          ('Help and supervise the kitchen '
                           'assembling guy. All day :('))

        item = self.items[4][1]
        attendees = item.getAttendees()
        value = '"Sidnei da Silva" <sidnei@awkly.org>'
        self.failUnless(value in attendees, (value, attendees))
        value = '"Paul Everitt" <paul@zope-europe.org>'
        self.failUnless(value in attendees, (value, attendees))
        self.assertEquals(len(item.getAttendees()), 2)
        self.assertEquals(item.getLocation(), 'Europe')
        self.assertEquals(item.Title(), 'Send Invoice')
        self.assertEquals(item.Description(),
                          'Bill for 10h sysadm + 20h development\n')

    def testOutlook1(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'outlook1.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        item = self.items[0][1]
        self.failIf(item.getAttendees())
        self.assertEquals(item.getLocation(), 'Anywhere')
        self.assertEquals(item.Title(), 'Send event to runyaga')
        self.assertEquals(toTime(item.start_date), '08:00:00')
        self.assertEquals(toTime(item.end_date), '08:30:00')

    def testOutlook2(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'outlook2.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        item = self.items[0][1]
        self.failIf(item.getAttendees())
        self.assertEquals(item.Title(), 'My Subject')
        self.assertEquals(item.getLocation(), 'My Location')
        self.assertEquals(item.Description(), 'This is a note.\n')
        self.assertEquals(toTime(item.start_date), '00:00:00')
        self.assertEquals(toTime(item.end_date), '00:00:00')
        self.assertEquals(item.start_date,
                          datetime.datetime(2004, 4, 27, tzinfo=tzutc()))
        self.assertEquals(item.end_date,
                          datetime.datetime(2004, 4, 28, tzinfo=tzutc()))
        self.assertEquals(tuple(item.Subject()), ('Webrent2',))

    def testOutlook3(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'outlook3.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        item = self.items[0][1]
        attendees = item.getAttendees()
        self.failUnless(attendees)
        values = (
            '"Sidnei da Silva" <sidnei@enfoldsystems.com>',
            '"George Alan Runyan" <alan@enfoldsystems.com>',
            '"Toby Roberts" <toby@enfoldsystems.com>',
            '"Andy McKay" <andy@enfoldsystems.com>')
        for value in values:
            self.failUnless(value in attendees, (value, attendees))

        self.assertEquals(item.Title(), 'Test Event: Weekly Meeting')
        self.assertEquals(item.getLocation(), 'Enfold Systems')
        self.assertEquals(item.Description().strip(), '')
        self.assertEquals(toTime(item.start_date), '15:30:00')
        self.assertEquals(toTime(item.end_date), '16:00:00')
        self.assertEquals(item.start_date,
                          datetime.datetime(2005, 10, 21, 15, 30, tzinfo=tzutc()))
        self.assertEquals(item.end_date,
                          datetime.datetime(2005, 10, 21, 16, 0, tzinfo=tzutc()))
        self.assertEquals(tuple(item.Subject()), ())

    def testSunbird(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'sunbird.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        item = self.items[0][1]
        self.failIf(item.getAttendees())
        self.failIf(item.getLocation())
        self.assertEquals(item.Title(), 'IIS Caching')
        # toTime gives UTC, dates are interpreted as local.
        self.assertEquals(toTime(item.start_date), '19:00:00')
        self.assertEquals(toTime(item.end_date), '19:00:00')

    def testiCal(self):
        self.portal.invokeFactory('Folder', id='test_calendar')
        cal = self.portal.test_calendar
        self.file = open(join(_prefix, 'data', 'ical.ics'), 'r')
        self.items = fromFile(cal, self.file)
        self.file.close()

        values = (
            'Tev rehearsal', 'Gig with Tev',
            'BJS Jam Sessions', 'Reason class',
            'Soulive', 'Dirty Dozen Brass Band',
            'Thaddeus Hogarth', 'Anthony Braxton Sextet',
            'BJS Meeting', 'Tev rehearsal', 'Tev',
            'Boston Jazz Now: A Look at the Current Trends on the Boston Scene'
            )
        for value, item in zip(values, self.items):
            self.assertEquals(item[1].Title(), value)

        self.assertEquals(
            self.items[-3][1].Description(),
            '\n'.join((
            "94 1/2 Gore St. #3",
            "T to Lechmere. Get off at Gov't ctr and take shuttle",
            "Walk down Cambridge ", # Note the extra space.
            "R on Sciarratta",
            "L on Gore",
            "top buzzer")))

        # iCal seems to think that double quotes need escaping. That
        # is wrong according to the spec, so we manually fix it up in
        # the marshaller.
        self.assertEquals(
            self.items[-6][1].Description(),
            ('"Take a healthy dose of Sly and The Family Stone, '
             'add a liberal pinch of Stevie Wonder, put on your '
             'dancing shoes and boogie to the music of Thaddeus '
             'Hogarth" - Bruce Gelerman, NPR.'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(
        'Products.Calendaring.common',
        optionflags=doctest.ELLIPSIS | doctest.REPORT_UDIFF))
    suite.addTest(doctest.DocTestSuite(
        'Products.Calendaring.marshaller',
        optionflags=doctest.ELLIPSIS | doctest.REPORT_UDIFF))
    suite.addTest(unittest.makeSuite(TestContentTypes))
    suite.addTest(unittest.makeSuite(TestImportCalendar))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
