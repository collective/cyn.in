from zope import interface
from p4a.calendar import interfaces
from OFS.SimpleItem import SimpleItem

class CalendarSupport(SimpleItem):
    """
    """

    interface.implements(interfaces.ICalendarSupport)

    @property
    def support_enabled(self):
        return True
