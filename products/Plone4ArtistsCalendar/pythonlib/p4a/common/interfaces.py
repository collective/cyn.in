from zope import interface

class IFeatureStatusChangedEvent(interface.Interface):
    """Fired when a featuer has been activated or deactivated."""

    object = interface.Attribute('Object')
    enhancedinterface = interface.Attribute('Enhanced Interface')

class IFeatureActivatedEvent(IFeatureStatusChangedEvent): pass
class IFeatureDeactivatedEvent(IFeatureStatusChangedEvent): pass

class FeatureStatusChangedEvent(object):
    interface.implements(IFeatureStatusChangedEvent)

    def __init__(self, enhancedinterface, object):
        self.enhancedinterface = enhancedinterface
        self.object = object

class FeatureActivatedEvent(FeatureStatusChangedEvent):
    interface.implements(IFeatureActivatedEvent)

class FeatureDeactivatedEvent(FeatureStatusChangedEvent):
    interface.implements(IFeatureDeactivatedEvent)
