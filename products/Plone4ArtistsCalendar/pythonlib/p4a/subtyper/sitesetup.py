from p4a.common import site

from Products.CMFCore import utils as cmfutils
from Products.CMFCore import DirectoryView

import logging
logger = logging.getLogger('p4a.subtyper.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False


def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)

def setup_site(site):
    # In 2.5, install the subtyper profile:
    mt = cmfutils.getToolByName(site, 'portal_migration')
    plone_version = mt.getInstanceVersion()
    if plone_version[0:3] == '2.5':
        # Setup only needed for Plone 3.0
        skin_tool = cmfutils.getToolByName(site, 'portal_skins')
        path = None
        for path in DirectoryView.manage_listAvailableDirectories():
            if path.endswith('p4a_subtyper'):
                break
        assert(path is None, "Subtyper skin directory not found")
        if 'p4a_subtyper' not in skin_tool.objectIds():
            DirectoryView.createDirectoryView(skin_tool, path)

        for skin_name, paths in skin_tool.getSkinPaths():
            if not 'p4a_subtyper' in paths:
                paths = paths.split(',')
                index = paths.index('plone_templates')
                paths.insert(index, 'p4a_subtyper')
                paths = ','.join(paths)
                skin_tool._getSelections()[skin_name] = paths


def unsetup_portal(portal):
    pass
