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
# Some portions of this module are Copyright Shuttleworth Foundation.
# The original copyright statement is reproduced below.
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2003 Shuttleworth Foundation
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
$Id: calendar.py,v 1.4 2005/01/25 01:03:49 dreamcatcher Exp $
"""
import warnings

from Products.CMFCalendar.CalendarTool import calendar
from OFS.PropertyManager import PropertyManager

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized

from Products.Archetypes.utils import mapply
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CalendarTool import CalendarTool as BaseTool

class CalendarTool(BaseTool, PropertyManager):
    """ A Calendar Tool implementation
    for import/export of events.
    """
    security = ClassSecurityInfo()

    event_type = 'Event'
    published_states = ('published',)
    _properties = getattr(BaseTool, '_properties', ()) + (
        {'id':'event_type', 'type': 'string', 'mode':'w'},
        {'id':'published_states', 'type': 'lines', 'mode':'w'},)

    manage_options = BaseTool.manage_options + PropertyManager.manage_options

    def __init__(self):
        if hasattr(BaseTool, '__init__'):
            # Plone 2.1 doesn't seem to have a __init__ anymore.
            BaseTool.__init__(self)

    security.declarePrivate('setMapping')
    def setMapping(self, name):
        warnings.warn("portal_calendar.setMapping has been deprecated."
                      "You do not need to call it anymore.",
                      DeprecationWarning, 2)

    security.declarePublic('getDestination')
    def getDestination(self):
        mt = getToolByName(self, 'portal_membership')
        dest = mt.getHomeFolder()
        if dest is None:
            # User does not have a home folder? Try portal and let it fail!
            pt = getToolByName(self, 'portal_url')
            dest = pt.getPortalObject()
        return dest

    security.declarePublic('importCalendar')
    def importCalendar(self, stream, dest=None, kw_map=None, do_action=False):	
        from Products.Calendaring.marshaller import CalendarMarshaller
        mt = getToolByName(self, 'portal_membership')
        if mt.isAnonymousUser():
            raise Unauthorized
        if dest is None:
            dest = self.getDestination()
        marshaller = CalendarMarshaller()

        REQUEST = self.REQUEST
        RESPONSE = REQUEST.RESPONSE
        args = [dest, '']
        items = []
        kwargs = {'file':stream,
                  'context':self,
                  'items': items,
		  'do_action':False,
                  'REQUEST':REQUEST,
                  'RESPONSE':RESPONSE}
        mapply(marshaller.demarshall, *args, **kwargs)	
        return items

    def exportCalendar(self, events=None, REQUEST=None):
        from Products.Calendaring.marshaller import CalendarMarshaller
        marshaller = CalendarMarshaller()
	
        ddata = marshaller.marshall(self, events=events,
                                    REQUEST=REQUEST,
                                    RESPONSE=None)
        content_type, length, data = ddata

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', content_type)
            REQUEST.RESPONSE.setHeader('Content-Length', length)
            REQUEST.RESPONSE.write(data)
        return data

    security.declarePublic('getPublishedStates')
    def getPublishedStates(self):
        return self.getProperty('published_states')

    # catalog_getevents is copied verbatim from CMFCalendar
    # the only thing changed is the possiblility to set a published state
    security.declarePublic('catalog_getevents')
    def catalog_getevents(self, year, month):
        """ given a year and month return a list of days that have events
        """
        def event_time(date):
            return date.Time()
        year = int(year)
        month = int(month)
        last_day = calendar.monthrange(year, month)[1]
        first_date = self.getBeginAndEndTimes(1, month, year)[0]
        last_date = self.getBeginAndEndTimes(last_day, month, year)[1]

        published = self.getPublishedStates()

        query = self.portal_catalog(portal_type=self.calendar_types,
                                    review_state=published,
                                    start={'query': last_date,
                                           'range': 'max'},
                                    end={'query': first_date,
                                         'range': 'min'},
                                    sort_on='start')

        # compile a list of the days that have events
        eventDays = {}
        for daynumber in range(1, 32): # 1 to 31
            eventDays[daynumber] = {'eventslist':[], 'event':0, 'day':daynumber}
        includedevents = []
        for result in query:
            if result.getRID() in includedevents:
                break
            else:
                includedevents.append(result.getRID())
            event = {}
            # we need to deal with events that end next month
            if  result.end.month() != month:
                # doesn't work for events that last ~12 months - fix
                # it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event['end'] = None
            else:
                eventEndDay = result.end.day()
                event['end'] = event_time(result.end)
            # and events that started last month
            if result.start.month() != month:  # same as above re: 12 month thing
                eventStartDay = 1
                event['start'] = None
            else:
                eventStartDay = result.start.day()
                event['start'] = event_time(result.start)
            event['title'] = result.Title or result.id
            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay+1)
                eventDays[eventStartDay]['eventslist'].append(
                    {'end':None,
                     'start':event_time(result.start),
                     'title':result.Title})
                eventDays[eventStartDay]['event'] = 1
                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]['eventslist'].append(
                        {'end':None,
                         'start':None,
                         'title':result.Title})
                    eventDays[eventday]['event'] = 1
                eventDays[eventEndDay]['eventslist'].append(
                    {'end':event_time(result.end),
                     'start':None,
                     'title':result.Title})
                eventDays[eventEndDay]['event'] = 1
            else:
                eventDays[eventStartDay]['eventslist'].append(event)
                eventDays[eventStartDay]['event'] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays

InitializeClass(CalendarTool)
