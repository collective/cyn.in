from zope import interface
from p4a.calendar import interfaces
from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor

class AbstractCalendarDescriptor(object):
    interface.implements(IPortalTypedFolderishDescriptor)

    title = u'Calendar'
    description = u'A folder that holds event objects'
    type_interface = interfaces.ICalendarEnhanced

class FolderCalendarDescriptor(AbstractCalendarDescriptor):
    for_portal_type = 'Folder'

class TopicCalendarDescriptor(AbstractCalendarDescriptor):
    for_portal_type = 'Topic'

class CalendarCalendarDescriptor(AbstractCalendarDescriptor):
    for_portal_type = 'Calendar'
