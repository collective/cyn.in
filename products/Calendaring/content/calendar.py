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
$Id: calendar.py,v 1.8 2005/01/11 00:26:34 dreamcatcher Exp $
"""
from types import MethodType, FunctionType
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zExceptions import MethodNotAllowed, NotFound, Unauthorized

from Products.Archetypes.public import *
from Products.Archetypes.utils import mapply
from Products.Calendaring.config import *
from Products.Calendaring.marshaller import CalendarMarshaller
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent, View

calendar_marshaller = CalendarMarshaller()
try:
    from Products.Marshall import ControlledMarshaller
    calendar_marshaller = ControlledMarshaller(calendar_marshaller)
except ImportError:
    pass

class Calendar(BaseFolder):

    meta_type = portal_type = archetype_name = 'Calendar'
    filter_content_types = 1
    event_types = ('ATEvent', 'Event')
    allowed_content_types = event_types + ('Calendar', )
    _at_rename_after_creation = True
    schema = (BaseFolderSchema +
              Schema((), marshall=calendar_marshaller))

    security = ClassSecurityInfo()

    __dav_marshall__ = True
    __dav_collection__ = False
    __dav_resource__ = True
    isAnObjectManager = False

    # XXX Breaks PUT handling on NullResource.
    # A fix has been checked in into Zope 2.7+
    # def __len__(self):
    #     return len(self._objects)

    security.declarePrivate('iterSelf')
    def iterSelf(self):
        return iter(self.objectValues())

    security.declareProtected(ModifyPortalContent, 'addEvent')
    def addEvent(self, event):
        ev = self.getEvent(event, None)
        if ev is not None:
            ev.update(event)
            return
        event = aq_base(event)
        self._setObject(event.getId(), event)

    security.declareProtected(View, 'getEvent')
    def getEvent(self, event, default=None):
        for ev in self.iterSelf():
            if ev == event:
                return ev
        return default

    security.declareProtected(ModifyPortalContent, 'removeEvent')
    def removeEvent(self, event):
        for ev in self.iterSelf():
            if ev == event:
                self.manage_delObjects(ids=[ev.getId()])

    security.declareProtected(ModifyPortalContent, 'update')
    def update(self, calendar=None, **kwargs):
        # XXX Clashes with BaseObject.update
        # so we handle carefully
        if calendar is not None:
            for event in calendar.iterSelf():
                self.addEvent(event)
        elif kwargs:
            return BaseFolder.update(self, **kwargs)
        return None

    security.declareProtected(ModifyPortalContent, 'clear')
    def clear(self):
        ids = self.objectIds()
        self.manage_delObjects(ids=ids)

    security.declareProtected(ModifyPortalContent, 'fromFile')
    def fromFile(self, stream):
        """ Import events from a file into this calendar
        """
        REQUEST = self.REQUEST
        RESPONSE = REQUEST.RESPONSE
        marshaller = self.Schema().getLayerImpl('marshall')
        args = [self, '']
        items = []
        kwargs = {'file':stream,
                  'context':self,
                  'items': items,
                  'REQUEST':REQUEST,
                  'RESPONSE':RESPONSE}
        mapply(marshaller.demarshall, *args, **kwargs)
        return items

    security.declareProtected(View, 'asCalendar')
    def asCalendar(self, REQUEST=None):
        """ Export the contents of this Calendar as an iCalendar file """
        marshaller = self.Schema().getLayerImpl('marshall')
        events = self.contentValues(filter={'portal_type':self.event_types})
        ddata = marshaller.marshall(self, events=events,
                                    REQUEST=REQUEST,
                                    RESPONSE=None)
        content_type, length, data = ddata

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', content_type)
            REQUEST.RESPONSE.setHeader('Content-Length', length)
            REQUEST.RESPONSE.write(data)
        return data

    PUT = BaseContent.PUT.im_func
    manage_afterPUT = BaseContent.manage_afterPUT.im_func
    manage_FTPget = BaseContent.manage_FTPget.im_func

    def HEAD(self, REQUEST, RESPONSE):
        """Retrieve resource information without a response body.
        """
        self.dav__init(REQUEST, RESPONSE)
        # Note that we are willing to acquire the default document
        # here because what we really care about is whether doing
        # a GET on this collection / would yield a 200 response.
        view = None
        putils = getToolByName(self, 'plone_utils')
        obj, pages = putils.browserDefault(self)
        if pages is not None and pages:
            view = getattr(self, pages[0])
            if isinstance(view, (MethodType, FunctionType)):
                # Ignore methods
                view = None
        if view is None:
            # Try to find a action (view)
            try:
                from Products.CMFCore.utils import _getViewFor
                view = _getViewFor(self)
            except (ImportError, Unauthorized, 'Unauthorized', 'Not Found'):
                pass
        if view is not None:
            if hasattr(view, 'HEAD'):
                return view.HEAD(REQUEST, RESPONSE)
            raise MethodNotAllowed, (
                'Method not supported for this resource.'
                )
        raise NotFound, 'The requested resource does not exist.'

registerType(Calendar, PROJECTNAME)
InitializeClass(Calendar)
