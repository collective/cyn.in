from zope import component
from zope import interface
from zope import schema
from p4a.calendar import interfaces

class Support(object):
    """A view that returns certain information regarding p4acal status.
    """

    interface.implements(interfaces.IBasicCalendarSupport)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def support_enabled(self):
        """Check to make sure an ICalendarSupport utility is available and
        if so, query it to determine if support is enabled.
        """
        
        support = component.queryUtility(interfaces.ICalendarSupport)
        if support is None:
            return False

        return support.support_enabled
