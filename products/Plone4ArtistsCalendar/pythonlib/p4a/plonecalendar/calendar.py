from zope import component
from zope import interface
from zope.app.annotation import interfaces as annointerfaces
from p4a.calendar import interfaces

class FolderCalendarConfig(object):
    """An ICalendarConfig adapter for ATCT folder content.
    """
    
    interface.implements(interfaces.ICalendarConfig)
    component.adapts(interfaces.IPossibleCalendar)

    def __init__(self, context):
        self.context = context

    def __get_calendar_activated(self):
        return interfaces.ICalendarEnhanced.providedBy(self.context) and \
               annointerfaces.IAttributeAnnotatable.providedBy(self.context)
    def __set_calendar_activated(self, activated):
        ifaces = interface.directlyProvidedBy(self.context)
        if activated:
            if not interfaces.ICalendarEnhanced.providedBy(self.context):
                ifaces += interfaces.ICalendarEnhanced
            if not annointerfaces.IAttributeAnnotatable.providedBy(self.context):
                ifaces += annointerfaces.IAttributeAnnotatable
            if getattr(self.context, 'layout', None) is not None:
                self.context.layout = 'month.html'
        else:
            if interfaces.ICalendarEnhanced in ifaces:
                ifaces -= interfaces.ICalendarEnhanced
            if getattr(self.context, 'layout', None) is not None:
                delattr(self.context, 'layout')
        interface.directlyProvides(self.context, ifaces)

    calendar_activated = property(__get_calendar_activated,
                                  __set_calendar_activated)
