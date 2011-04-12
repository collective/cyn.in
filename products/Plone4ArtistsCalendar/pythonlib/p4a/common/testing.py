from zope import interface
from zope.component.interfaces import ISiteManager
from zope.app.component.interfaces import ISite

import logging
logger = logging.getLogger('p4a.common.testing')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False

class MockSite:
    """A simple ISite/ISiteManager combo for testing purposes.
    """

    interface.implements(ISite, ISiteManager)

    def __init__(self):
        self.utils = {}

    def getUtility(self, iface):
        return self.utils[iface]

    def queryUtility(self, iface):
        return self.utils.get(iface, None)

    def getSiteManager(self):
        return self

    if not HAS_FLSM:
        def registerUtility(self, iface, obj):
            self.utils[iface] = obj
    else:
        def registerUtility(self, obj, iface):
            self.utils[iface] = obj
