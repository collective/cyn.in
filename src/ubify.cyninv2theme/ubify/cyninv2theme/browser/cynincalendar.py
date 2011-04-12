###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that 
#enables teams to seamlessly work together on files, documents and content in 
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license 
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software 
#Foundation, either version 3 of the License, or any later version and observe 
#the Additional Terms applicable to this program and must display appropriate 
#legal notices. In accordance with Section 7(b) of the GNU General Public 
#License version 3, these Appropriate Legal Notices must retain the display of 
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with 
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
#For any queries regarding the licensing, please send your mails to 
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
try:
    from Products.Five.browser.pagetemplatefile import \
         ZopeTwoPageTemplateFile as PageTemplateFile
except ImportError:
    from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from Products.CMFCore.utils import getToolByName
from p4a.calendar.browser.month import MonthView as BaseMonthViewClass
from p4a.calendar.browser.events import EventListingView as BaseEventListingView
from p4a.plonecalendar.browser.icalendar import IiCalendarView as BaseIiCalendarView
from p4a.plonecalendar.browser.icalendar import iCalendarView as BaseiCalendarView
from p4a.plonecalendar.eventprovider import ATEventProvider as BaseATEventProvider
import datetime

class MonthView(BaseMonthViewClass):
    
    def next_month_link(self):
        year = self.default_day.year
        month = self.default_day.month
        
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        
        return '%s%s?year=%s&month=%s' % (self.context.absolute_url(),'/app_calendar',
                                        year,
                                        month)

    def prev_month_link(self):
        year = self.default_day.year
        month = self.default_day.month
        
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        
        return '%s%s?year=%s&month=%s' % (self.context.absolute_url(),'/app_calendar',
                                        year,
                                        month)
    
    @property
    def _duplicateevents(self):
        
        import datetime
        from p4a.calendar import interfaces
        events = getattr(self, '_dup_cached_events', None)
        if events is not None:
            return events
        
        if not hasattr(self, 'context'):
            self._dup_cached_events = []
            return self._dup_cached_events

        default = self.default_day
        
        start = datetime.datetime(default.year, default.month, 1, 0, 0)
        
        if default.month < 12:
            end = datetime.datetime(default.year, default.month+1, 1, 23, 59)
            end -= datetime.timedelta(days=1)
        elif default.month == 12:
            end = datetime.datetime(default.year, default.month, 31, 23, 59)
        
        provider = interfaces.IEventProvider(self.context)

        self._dup_cached_events = provider.gather_events(start, end, 
                                                     **self.request.form)
        return self._dup_cached_events
    
    def getTags(self):
        
        from ubify.cyninv2theme import getTagsAndTagsCount
        tags = []
        
        objtemp = self._duplicateevents;
        objevents = [event for event in objtemp]        
        tags = getTagsAndTagsCount(objevents)
        return tags
    
    
class EventListingView(BaseEventListingView):
    
    eventlist = PageTemplateFile('app_cal_events.pt')
    
    def getTags(self):        
        from p4a.calendar import interfaces
        from ubify.cyninv2theme import getTagsAndTagsCount
        tags = []
        provider = interfaces.IEventProvider(self.context)
        now = datetime.datetime.now()
        events = []
        if self.context.REQUEST.URL.endswith('upcomingEvents'):            
            events = list(provider.gather_events(start=now, stop=None, **self.request.form))
        else:
            events = list(provider.gather_events(start=None, stop=now, **self.request.form))
        tags = getTagsAndTagsCount(events)
        return tags
    
class iCalendarView(BaseiCalendarView):
    pass

class IiCalendarView(BaseIiCalendarView):
    pass

class ATEventProvider(BaseATEventProvider):
    
    def gather_events(self, start=None, stop=None, **kw):
        from Products.CMFCore import utils as cmfutils
        from Products.CMFCore.utils import getToolByName
        from p4a.calendar import interfaces
        from p4a.plonecalendar.eventprovider import _make_zcatalog_query
        
        
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        kw = _make_zcatalog_query(start, stop, kw)
        if self.context.portal_type != 'MemberSpace':
            event_brains = catalog(portal_type='Event', path=path, **kw)
        else:
            memberid = self.context.getId()
            portal = self.context.portal_url.getPortalObject()
            if portal <> None:
                path = "/".join(portal.getPhysicalPath())
                
            event_brains = catalog(portal_type='Event', path=path,modifiers = memberid, **kw)
            
        return (interfaces.IEvent(x) for x in event_brains)
    
    def all_events(self):
        from Products.CMFCore import utils as cmfutils
        from Products.CMFCore.utils import getToolByName
        from p4a.calendar import interfaces
        
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        
        if self.context.portal_type != 'MemberSpace':
            event_brains = catalog(portal_type='Event', path={'query':path,'depth':1})
        else:
            memberid = self.context.getId()
            portal = self.context.portal_url.getPortalObject()
            if portal <> None:
                path = "/".join(portal.getPhysicalPath())
                
            event_brains = catalog(portal_type='Event', path={'query':path,'depth':1},modifiers = memberid)
            
        
        return (interfaces.IEvent(x) for x in event_brains)
    
    def event_creation_link(self, start=None, stop=None):
        ##sumo: following code is commented till we fix problem of condition.
        if self.context.portal_membership.checkPermission(
            'Add portal content',self.context):
            return self.context.absolute_url() + '/createObject?type_name=Event'
        
        return ''