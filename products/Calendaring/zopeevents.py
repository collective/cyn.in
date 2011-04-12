from zope.interface import implements
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent

class IDemarshalledVEventEvent(IObjectEvent):
    """An event indicating that a VEvent was demarshalled"""

class DemarshalledVEventEvent(ObjectEvent):
    implements(IDemarshalledVEventEvent)
