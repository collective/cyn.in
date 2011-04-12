from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.Five import BrowserView

from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.interfaces import INavigationTree
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder, SitemapQueryBuilder

# Nasty hack to circumvent 'plone' modulealias
import sys
import plone
del sys.modules['Products.CMFPlone.browser.plone']

from plone.app.layout.navigation.interfaces import INavtreeStrategy

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

import zope.deferredimport
zope.deferredimport.deprecated(
    "It has been moved to plone.app.layout.navigation.defaultpage. "
    "This alias will be removed in Plone 4.0",
    DefaultPage = 'plone.app.layout.navigation.defaultpage:DefaultPage',
    )


def get_url(item):
    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()

def get_id(item):
    getId = getattr(item, 'getId')
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()

def get_view_url(context):
    props = getToolByName(context, 'portal_properties')
    stp = props.site_properties
    view_action_types = stp.getProperty('typesUseViewActionInListings', ())

    item_url = get_url(context)
    name = get_id(context)

    if context.portal_type in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url
import config

class PhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)
        
        try:
            name, item_url = get_view_url(context)
        except AttributeError:
            print context
            raise


        if hasattr(context,"UID"):
            if callable(context.UID):
                theuid = context.UID()
            else:
                theuid = context.UID
        else:
            theuid = ''

        if container is None:
            return [{'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context),
                     'applications':None,
                     'UID': theuid,
                     'portal_type': context.portal_type
                    }]

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = view.breadcrumbs()

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())


        # don't show default pages in breadcrumbs or pages above the navigation root
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):            
            if not base:
                base = []

            tempapps = []
            tempobj = {}
            tempobj['absolute_url'] = item_url
            tempobj['Title'] = utils.pretty_title_or_id(context,context)
            tempobj['UID'] = theuid
            tempobj['portal_type'] = context.portal_type
            tempobj['applications'] = []
            
            
            try:
                if hasattr(context,'listApplications'):
                    tempobj['applications'] = context.listApplications()
            except AttributeError:
                pass            
            
            base.append(tempobj)            
        return base

class ApplicationPerspectives(BrowserView):
    def applications(self):
        apps = config.applications
        if self.context.portal_type == 'ContentRoot':
            apps[1]['visible'] = True
            apps[-1]['visible'] = True
        elif self.context.portal_type == 'MemberSpace':
            apps[1]['visible'] = False
            apps[-1]['visible'] = True
        else:
            apps[1]['visible'] = False
            apps[-1]['visible'] = False
        return apps
