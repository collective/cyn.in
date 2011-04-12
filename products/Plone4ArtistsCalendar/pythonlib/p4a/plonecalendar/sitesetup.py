from p4a.calendar import interfaces
from p4a.plonecalendar import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils
from p4a.subtyper.sitesetup import setup_portal as subtyper_setup
from Products.CMFCore import utils as cmfutils 

import logging
logger = logging.getLogger('p4a.plonecalendar.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False


def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)
    indexing.ensure_object_provides(portal)

    qi = cmfutils.getToolByName(portal, 'portal_quickinstaller')
    qi.installProducts(['Marshall', 'Calendaring'])
    
    subtyper_setup(portal)

def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

      >>> from p4a.calendar import interfaces
      >>> from p4a.common.testing import MockSite

      >>> site = MockSite()
      >>> site.queryUtility(interfaces.ICalendarSupport) is None
      True

      >>> setup_site(site)
      >>> site.getUtility(interfaces.ICalendarSupport)
      <CalendarSupport ...>

    """
    sm = site.getSiteManager()
    if not sm.queryUtility(interfaces.ICalendarSupport):
        #registerUtility api changed between Zope 2.9 and 2.10
        if HAS_FLSM:
            sm.registerUtility(content.CalendarSupport('calendar_support'),
                               interfaces.ICalendarSupport)
        else:
            sm.registerUtility(interfaces.ICalendarSupport,
                               content.CalendarSupport('calendar_support'))            

def _cleanup_utilities(site):
    raise NotImplementedError('Current ISiteManager support does not '
                              'include ability to clean up')

def unsetup_portal(portal):
    count = utils.remove_marker_ifaces(portal, interfaces.ICalendarEnhanced)
    logger.warn('Removed ICalendarEnhanced interface from %i objects for '
                'cleanup' % count)
