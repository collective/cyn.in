from zope import interface
from zope import component

from Products.ZCatalog import CatalogBrains
from p4a.calendar import interfaces
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.ATContentTypes.content import topic
from Products.CMFCore.utils import getToolByName
from utils import dt2DT, DT2dt

def _make_zcatalog_query(start, stop, kw):
    """Takes a IEventProvider query and makes it a ZCaralog query"""
    if kw.has_key('title'):
        # The catalog calls this property "Title" with a 
        # capital T.
        kw['Title'] = kw['title']
        del kw['title']
    if stop is not None:
        kw['start']={'query': dt2DT(stop), 'range': 'max'} 
    if start is not None:
        kw['end']={'query': dt2DT(start), 'range': 'min'} 
    return kw

    
class ATEventProvider(object):
    interface.implements(interfaces.IEventProvider)
    component.adapts(atapi.BaseObject)

    def __init__(self, context):
        self.context = context
        
    def gather_events(self, start=None, stop=None, **kw):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        kw = _make_zcatalog_query(start, stop, kw)
        event_brains = catalog(portal_type='Event', path=path, **kw)
        return (interfaces.IEvent(x) for x in event_brains)
    
    def all_events(self):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        event_brains = catalog(portal_type='Event', path=path)
        return (interfaces.IEvent(x) for x in event_brains)
    
    def event_creation_link(self, start=None, stop=None):
        if self.context.portal_membership.checkPermission(
            'Add portal content',self.context):
            return self.context.absolute_url() + '/createObject?type_name=Event'
        return ''

class TopicEventProvider(object):
    interface.implements(interfaces.IEventProvider)
    component.adapts(topic.ATTopic)

    def __init__(self, context):
        self.context = context
        
    def acceptable_event(self, x, start, stop):
        start = dt2DT(start)
        stop = dt2DT(stop)
        
        return x.portal_type == 'Event' and x.start >= start and x.end <= stop
    
    def gather_events(self, start=None, stop=None, **kw):
        kw = _make_zcatalog_query(start, stop, kw)

        # This sad hack allows us to overwrite whatever restriction
        # the topic makes to the date.  Providing the 'start' and
        # 'date' arguments to the 'queryCatalog' method would
        # otherwise just overwrite our own date criteria.
        # See http://plone4artists.org/products/plone4artistscalendar/issues/35
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        def my_catalog(request, **kwargs):
            kwargs.update(kw)
            return catalog(request, **kwargs)
        self.context.portal_catalog = my_catalog
        self.context.portal_catalog.searchResults = my_catalog
        value = (interfaces.IEvent(x) for x in self.context.queryCatalog())
        del self.context.portal_catalog
        return value

    def all_events(self):
        #query = self.context.buildQuery()
        event_brains = self.context.queryCatalog() 
        return (interfaces.IEvent(x) for x in event_brains)

    def event_creation_link(self, start=None, stop=None):
        return ""


class BrainEvent(object):
    interface.implements(interfaces.IEvent)
    component.adapts(CatalogBrains.AbstractCatalogBrain)

    def __init__(self, context):
        self.context = context
        self.event = None
        catalog = getToolByName(self.context, 'portal_catalog')
        putils = getToolByName(self.context, 'plone_utils')
        self.encoding = putils.getSiteEncoding()
        
    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def _getEvent(self):
        if self.event is None:
            self.event = self.context.getObject()
        return self.event
    
    @property
    def title(self):
        return unicode(self.context.Title,
                       self.encoding)

    @property
    def description(self):
        return unicode(self.context.Description,
                       self.encoding)
    
    @property
    def start(self):
        return DT2dt(self.context.start)

    @property
    def end(self):
        return DT2dt(self.context.end)
    
    @property
    def location(self):
        return self.context.location

    @property
    def local_url(self):
        return self.context.getURL()

    @property
    def type(self):
        type = self._getEvent().eventType
        # This is a list of unicode strings, typically.
        # We want just one string, so we take the first one.
        if type:
            return cmfutils.cookString(type[0])
        return ''
    
    @property
    def timezone(self):
        return self.context.start.timezone()
