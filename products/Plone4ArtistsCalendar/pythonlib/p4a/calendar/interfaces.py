from zope import interface
from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('p4a.calendar')  

class IPossibleCalendar(interface.Interface):
    """A marker interface for representing what *could* be a calendar.
    """

class ICalendarEnhanced(interface.Interface):
    """A marker interface to indicate an item that has calendar 
    functionality.
    """

class ICalendarConfig(interface.Interface):
    """Configuration information for a calendar.
    """
    
    calendar_activated = schema.Bool(
        title=_(u'calendar_activated_label',
                default=u'Calendar settings'),
        description=_(u'calendar_activated_desc',
                      default=u'Calendar activated for this folder')
        )

class IEventProvider(interface.Interface):
    """Provides events.
    """
    
    def gather_events(start=None, stop=None, **kw):
        """Return all appropriate events for the given time interval.  The
        *start* and *stop* arguments are expected to be python datetime
        objects or None.
        **kw is used as filtering arguments.
        """

    def all_events():
        """Return all events. Used for exports and such.
        """
        
    def event_creation_link(start=None, stop=None):
        """Returns a url to a page that can create an event.
        
        Optional start and stop times to pre-fill start and end of event.
        """
        

class IEvent(interface.Interface):
    """An event.
    """
    
    title = schema.TextLine(title=u'Title',
                            required=True,
                            readonly=True)
    description = schema.Text(title=u'Description',
                              required=False,
                              readonly=True)
    start = schema.Datetime(title=u'Start Time',
                            required=True,
                            readonly=True)
    end = schema.Datetime(title=u'End Time',
                          required=False,
                          readonly=True)
    location = schema.TextLine(title=u'Location',
                               required=False,
                               readonly=True)
    local_url = schema.TextLine(title=u'URL',
                                required=True,
                                readonly=True)
    type = schema.TextLine(title=u'Type',
                           required=True,
                           readonly=False)
    timezone = schema.TextLine(title=u'Timezone',
                               required=True,
                               readonly=True)

class IBasicCalendarSupport(interface.Interface):
    """Provides certain information about calendar support.
    """

    support_enabled = schema.Bool(title=u'Calendar Support Enabled?',
                                  required=True,
                                  readonly=True)

class ICalendarSupport(IBasicCalendarSupport):
    """Provides full information about calendar support.
    """
