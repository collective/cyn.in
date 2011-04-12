from zope.interface import implements
from zope.component import adapts
from p4a.calendar.interfaces import ICalendarEnhanced

from Products.CMFDynamicViewFTI.interfaces import IDynamicallyViewable

class CalendarDynamicViews(object):
    
    implements(IDynamicallyViewable)
    adapts(ICalendarEnhanced)
    

    def __init__(self, context):
        self.context = context # Actually ignored...
        
    def getAvailableViewMethods(self):
        """Get a list of registered view method names
        """
        return [x[0] for x in self.getAvailableLayouts()]

    def getDefaultViewMethod(self):
        """Get the default view method name
        """
        return "month.html"

    def getAvailableLayouts(self):
        """Get the layouts registered for this object.
        """        
        return (("month.html", "Month view"),
                ("events.html", "Event list"),
                ("past_events.html", "Event archive"),
                )
