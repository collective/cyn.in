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
$Id: marshaller.py 51519 2007-10-14 12:20:50Z rocky $
"""

import re
import transaction

from urllib import quote
from types import ListType, TupleType
from datetime import datetime, date
from dateutil.tz import gettz, tzutc
from rfc822 import parseaddr, dump_address_pair
from icalendar import Calendar as iCalendar, Event as VEvent
from icalendar.prop import vCalAddress, vDate
from icalendar.prop import vDatetime, vText, vDDDTypes
from icalendar.parser import Parameters
import zope.event

from StringIO import StringIO
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCalendar.Event import Event as CMFEvent
from Products.Archetypes.Marshall import Marshaller

from Products.Calendaring.config import log
from Products.Calendaring.common import dt2DT, utc_strftime
from Products.Calendaring.zopeevents import DemarshalledVEventEvent

from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent

ICAL_FIXUP = re.compile(r'\\"')
UID_ATTR = '_event_uid'

def generateUID(event):
    uid = getattr(aq_base(event), UID_ATTR, None)
    if uid is not None:
        return uid
    id = event.getId()
    if id:
        return id
    h_event = abs(hash(repr(event)))
    h_id = abs(hash(id))
    return "%s-%s-RID" % (h_event, h_id)

def _cleanId(id):
    quoted = quote(id.encode('utf-8'))
    return quoted.replace('-', '--').replace('%', '-')

def _generateId(uid, title, context=None):
    pt = getToolByName(context, 'plone_utils', None)
    if uid:
        if pt is not None:
            return pt.normalizeString(uid)
        else:
            return _cleanId(uid)
    if pt is not None:
        return pt.normalizeString(title)
    return _cleanId(id)

def generateId(event, context=None):    
    uid = event.decoded('uid', None)
    title = event.decoded('summary', None)
    return _generateId(uid, title, context)

def person2text(value):
    name = value.params.get('cn', '')
    email = value.decode().lower()
    if not 'mailto:' in email:
        email = ''
    else:
        email = filter(None, email.split('mailto:'))
        email = email and email[0] or ''
    if email:
        return dump_address_pair((name, email))
    return name

def prop2Text(prop):
    """Convert a vText instance to a string.

    Fixup iCal, which thinks double quotes need to be escaped.

    >>> a = vText('\"The brown fox jumps over the lazy dog\" -- said Sidnei')
    >>> prop2Text(a)
    u'"The brown fox jumps over the lazy dog" -- said Sidnei'

    """
    return ICAL_FIXUP.sub('"', prop)

def prop2DateTime(prop):
    """Convert a vDDDTypes instance with TZID in params to a DateTime in UTC.

    Should be 10am BRT, converted to 10am local (GMT-2).

    >>> import os
    >>> os.environ['TZ'] = 'Brazil/East'

    >>> a = vDDDTypes(datetime(2005, 11, 10, 10, 0, 0))
    >>> a.params = Parameters({'tzid': 'Brazil/East'})
    >>> prop2DateTime(a)
    DateTime('2005/11/10 10:00:00 GMT-2')

    Should be 10am BRT, converted to 10am local (GMT-3).

    >>> a = vDDDTypes(datetime(2005, 07, 10, 10, 0, 0))
    >>> a.params = Parameters({'tzid': 'Brazil/East'})
    >>> prop2DateTime(a)
    DateTime('2005/07/10 10:00:00 GMT-3')

    Should be 10am UTC, converted to 8am local.

    >>> a = vDDDTypes(datetime(2005, 11, 10, 10, 0, 0, tzinfo=tzutc()))
    >>> prop2DateTime(a)
    DateTime('2005/11/10 08:00:00 GMT-2')

    Should be 10am local time, converted to 10am local.
    >>> a = vDDDTypes(datetime(2005, 11, 10, 10, 0, 0))
    >>> prop2DateTime(a)
    DateTime('2005/11/10 10:00:00 GMT-2')
    """
    dt = prop.dt
    tzid = None
    if isinstance(dt, datetime):
        params = getattr(prop, 'params', {})
        tzid = params.get('tzid', None)
    return dt2DT(dt, tzid, local=True)

def convert(value, encoding='utf-8'):
    def _convert(value, encoding=encoding):
        for t, c in converters.items():
            if isinstance(value, t):
                value = c(value)
                break
        #if hasattr(value, 'decode'):
            #value = value.decode()
        if isinstance(value, unicode):
            value = value.encode(encoding)
        return value
    if type(value) not in (ListType, TupleType):
        return _convert(value)
    return map(_convert, value)


status_mapping = {'TENTATIVE':('submit', 'reject', 'retract', 'show'),
                  'CONFIRMED':('publish',),
                  'CANCELLED':('hide',),
                  }
re_status_mapping = {'published':'CONFIRMED',
                     'pending':'TENTATIVE',
                     'visible':'TENTATIVE',
                     'private':'CANCELLED'}

converters = {datetime : dt2DT,
              date : dt2DT,
              vText: prop2Text,
              vDDDTypes: prop2DateTime,
              vCalAddress: person2text}

kw_mappings = []
default_mapping = {'dtstart':'startDate',
                   'dtend':'endDate',
                   'summary':'title',
                   'description':'description',
                   'location':'location',
                   'attendee':'attendees',
                   'categories':'subject',
                   'url':'eventUrl'}

# The following is to support CMF Event.
kw_mappings.append((CMFEvent, {'dtstart':'start_date',
                               'dtend':'end_date',
                               'summary':'title',
                               'description':'description'}))


cmf_update = {'start_date': 'setStartDate',
              'end_date': 'setEndDate',
              'title': 'setTitle',
              'description': 'setDescription',
              'url': 'setEventURL'}

def cmf_event_update(self, **kw):
    for key, name in cmf_update.items():
        value = kw.get(key)
        if value:
            method = getattr(self, name)
            method(value)
    self.reindexObject()

def cmf_set_event_url(self, event_url):
    self.event_url = event_url

CMFEvent.update = cmf_event_update
CMFEvent.setEventURL = cmf_set_event_url

def set_event_info_from_vevent(instance, ev, kw_map, do_action=True):
    # Make sure a subtransaction happens. We might end up renaming the
    # event, and we don't really know if it was existing or new.
    transaction.savepoint(optimistic=True)
    info = {}
    for k, v in kw_map.items():
        value = ev.get(k, None)
        if value is None:
            # Ugh, special case for dtend
            if k in ('dtend',):
                # dtstart and duration *must* exist.
                dtstart = ev.get('dtstart')
                params = getattr(dtstart, 'params', {})
                duration = ev.get('duration')
                if duration is None:
                    dtend = dtstart.dt
                else:
                    dtend = dtstart.dt + duration.dt
                value = vDDDTypes(dtend)
                value.params = Parameters(dict(params))
            else:
                continue
        value = convert(value)
        info[v] = value

    instance.update(**info)
    uid = ev.decoded('uid', None)
    if uid is None:
        uid = generateUID(instance)
    setattr(instance, UID_ATTR, uid)

    if do_action:
        # XXX NAAAAASTY Code. We need to create a special
        # workflow for Event. This assumes the default Plone workflow.	
        wf = getToolByName(instance, 'portal_workflow')
        state = wf.getInfoFor(instance, 'review_state')
        status = ev.get('status', 'CONFIRMED')
        if not re_status_mapping.get(state, 'CONFIRMED') == status:
            set_event_state_from_status(instance, status, wf)

    instance.reindexObject()

def set_event_state_from_status(instance, status, wf=None):    
    if wf is None:
        wf = getToolByName(instance, 'portal_workflow')
    actions = status_mapping.get(status, 'publish')
    for action in actions:
        try:
            wf.doActionFor(instance, action)
        except WorkflowException:
            # Try to revert to visible
            for a in ('retract', 'show'):
                try:
                    wf.doActionFor(instance, 'retract')
                except WorkflowException:
                    pass
            try:
                wf.doActionFor(instance, action)
            except WorkflowException:
                pass
            else:
                break
        else:
            break    
    state = wf.getInfoFor(instance, 'review_state')
    assert re_status_mapping.get(state, 'CONFIRMED') == status

def marshall_event_to_vevent(instance):
    wf = getToolByName(instance, 'portal_workflow')
    dtstamp = utc_strftime(datetime.utcnow(), "%Y%m%dT%H%M%SZ")
    uid_hash = abs(hash(instance))
    state = wf.getInfoFor(instance, 'review_state')
    status = re_status_mapping.get(state, 'TENTATIVE')
    event = VEvent()
    event.add('uid', generateUID(instance))
    event.add('summary', instance.Title(), encode=False)
    event.add('description', instance.Description(), encode=False)
    if hasattr(aq_base(instance), 'getLocation'):
        location = instance.getLocation()
        if location:
            event.add('location', location, encode=False)
    if hasattr(aq_base(instance), 'Subject'):
        subject = instance.Subject()
        if subject:
            for category in subject:
                event.add('categories', category, encode=False)
    if hasattr(aq_base(instance), 'event_url'):
        url = instance.event_url
        if callable(url):
            # Ugh, it's callable in ATContentTypes.
            url = url()
        if url:
            event.add('url', url)
            event['url'].params['value'] = 'URI'
    if hasattr(aq_base(instance), 'getAttendees'):
        for att in instance.getAttendees():
            name, email = parseaddr(att)
            if not name:
                name = att
                email = ''
            if email:
                email = 'mailto:%s' % email
            else:
                email = 'invalid:nomail'
            address = vCalAddress(email)
            address.params['cn'] = name
            event.add('attendee', address, encode=False)
    if (hasattr(aq_base(instance), 'duration') and
        instance.duration == date.resolution):
        # All day event.
        dtstart = vDate.from_ical(
            utc_strftime(instance.start_date, '%Y%m%d'))
        event.add('dtstart', dtstart)
        dtend = vDate.from_ical(
            utc_strftime(instance.end_date, '%Y%m%d'))
        event.add('dtend', dtend)
    else:
        # Normal event
        dtstart = vDatetime.from_ical(
            utc_strftime(instance.start_date, '%Y%m%dT%H%M%SZ'))
        event.add('dtstart', dtstart)
        dtend = vDatetime.from_ical(
            utc_strftime(instance.end_date, '%Y%m%dT%H%M%SZ'))
        event.add('dtend', dtend)
    dtstamp = vDatetime.from_ical(dtstamp)
    event.add('dtstamp', dtstamp)
    #event.add('status', status)
    return event

def wrap_into_vcalendar(*vevents, **kw):
    calendar = iCalendar()
    calendar.add('prodid',  "-//Plone/NONSGML Calendaring//EN")
    calendar.add('version', '2.0')
    title = kw.get('title')
    if title:
        title = unicode(title, 'utf-8')
        calendar.add('x-wr-calname', title)
    for vevent in vevents:
        calendar.add_component(vevent)
    return calendar.as_string()

class EventMarshaller(Marshaller):

    def marshall(self, instance, **kw):
        vevent = marshall_event_to_vevent(instance)
        vcal = wrap_into_vcalendar(vevent)
        return ('text/calendar', len(vcal), vcal)

    def demarshall(self, instance, data, **kw):
        file = kw.get('file', None)
        if file is not None:
            if not data:
                data = file.read()
        calendars = iCalendar.from_string(data, multiple=True)
        do_action = kw.get('do_action', True)
        kw_map = default_mapping
        for klass, mapping in kw_mappings:
            if isinstance(instance, klass):
                kw_map = mapping
        for calendar in calendars:
            for ev in calendar.walk('VEVENT'):
                # We only care about the first one here.
                set_event_info_from_vevent(instance, ev, kw_map,
                                           do_action=do_action)
                break

class CalendarMarshaller(Marshaller):

    def marshall(self, instance, **kw):
        events = kw.get('events', None)
        if events is None:
            event_types = getattr(instance, 'event_types', ('ATEvent', 'Event'))
            events = instance.contentValues(
                filter={'portal_type':event_types})
        events.sort()
        vevents = [marshall_event_to_vevent(event) for event in events]
        if not vevents:
            # There were no events.  iCalendar spec (RFC 2445) requires
            # VCALENDAR to have at least one subcomponent.  Let's create
            # a fake event.
            # NB Mozilla Calendar produces a 0-length file when publishing
            # empty calendars.  Sadly it does not then accept them
            # (http://bugzilla.mozilla.org/show_bug.cgi?id=229266).
            dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            event = VEvent()
            vevents.append(event)
            event.add('uid', "placeholder-%s" % dtstamp)
            event.add('summary', 'Empty calendar')
            dtstart = vDatetime.from_ical(dtstamp[:-1])
            event.add('dtstart', dtstart)
            dtstamp = vDatetime.from_ical(dtstamp)
            event.add('dtstamp', dtstamp)	
        vcal = wrap_into_vcalendar(*vevents, **{'title': instance.context.Title()})
        return ('text/calendar', len(vcal), vcal)

    def demarshall(self, instance, data, **kw):
        file = kw.get('file', None)
        if file is not None:
            if not data:
                data = file.read()
        calendars = iCalendar.from_string(data, multiple=True)
        do_action = kw.get('do_action', True)
        items = kw.get('items', [])

        title = None
        for calendar in calendars:
            if title is None:
                for cal in calendar.walk('VCALENDAR'):
                    title = cal.get('x-wr-calname', None) # Apple's iCal Title
                    if title is not None:
                        title = convert(title)
                        break
            for ev in calendar.walk('VEVENT'):
                # We figure out the mapping after the first one has been
                # created, or at least one exists.
                id = generateId(ev, context=instance)
                event = instance._getOb(id, default=None)
                created = False
                
                if event is None:
                    instance.invokeFactory('Event', id)
                    event = instance._getOb(id)
                    created = True
                items.append((id, event))
                # Detect kw_map to use. Can be different for different
                # kinds of events in the same calendar. That's a fairly
                # cornerish case though.
                kw_map = None
                for klass, mapping in kw_mappings:
                    if isinstance(event, klass):
                        kw_map = mapping
                if kw_map is None:
                    kw_map = default_mapping		
                set_event_info_from_vevent(event, ev, kw_map, do_action=do_action)
                
                if created:
                    notify(ObjectInitializedEvent(event))                
