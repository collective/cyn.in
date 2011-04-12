from StringIO import StringIO
from Products.CMFCore.utils import getToolByName, manage_addTool
from Products.Archetypes.Extensions.utils import install_subskin
from Products.ATRatings.config import * 

import sys, os, string

#def uninstall(self):
#    out=StringIO()
#    return out.getvalue()

def setupCatalog(portal, out):
    catalog = getToolByName(portal, 'portal_catalog')
    
    print >> out, 'fix catalog'
    if not 'UID' in catalog.schema():
        catalog.addColumn('UID')
        print >> out, 'UID added to catalog schema'
        print >> out, 'NEED RECATALOG PORTAL_CATALOG!!!!'
    else:
        print >> out, 'UID already existed in the catalog schema, finished fixing catalog.'

def clearRatings(portal, out):
    """
    """

    ratings_tool = getToolByName(portal, 'portal_ratings')
    ref_catalog = getToolByName(portal, 'reference_catalog')

    bRefs = ratings_tool.getBRefs()

    if bRefs:
        print >> out, 'Clearing references for ratings.'
        for bRef in bRefs:
            bRef.deleteReference(ratings_tool, 'HasRatings')
            print >> out, 'Deleted references for %s.' % bRef.getId()


def install(self):
    out=StringIO()

    install_subskin(self, out, GLOBALS)

    print >> out, "skin installed"

    if not hasattr(self,'portal_ratings'):
        m = self.manage_addProduct['ATRatings']
        manage_addTool(m, 'Ratings Tool')
        print >> out, 'tool installed'

    setupCatalog(self, out)
    return out.getvalue()

def uninstall(self):
    out=StringIO()

    if CLEAR_REFS_ON_UNINSTALL:
        clearRatings(self, out)

    return out.getvalue()
