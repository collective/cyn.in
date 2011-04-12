###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that
#enables teams to seamlessly work together on files, documents and content in
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software
#Foundation, either version 3 of the License, or any later version and observe
#the Additional Terms applicable to this program and must display appropriate
#legal notices. In accordance with Section 7(b) of the GNU General Public
#License version 3, these Appropriate Legal Notices must retain the display of
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in.
#For any queries regarding the licensing, please send your mails to
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
from StringIO import StringIO

from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryUtility, getUtility, getSiteManager

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.portlets import cache

from zope import schema
from zope.formlib import form

from plone.memoize import ram
from plone.memoize.instance import memoize
from plone.memoize.compress import xhtml_compress

from Acquisition import aq_inner, aq_base, aq_parent
from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import INonStructuralFolder, IBrowserDefault
from Products.CMFPlone import utils
from ubify.policy import CyninMessageFactory as _

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from plone.app.portlets.portlets.navigation import QueryBuilder as base
from plone.app.portlets.portlets.navigation import Renderer as baseRenderer
from plone.app.portlets.portlets.navigation import NavtreeStrategy as baseStrategy
from plone.app.portlets.portlets.navigation import INavigationPortlet
from plone.app.portlets.portlets.navigation import getRootPath
from zope.app.publisher.interfaces.browser import IBrowserMenu
from ubify.policy.config import contentroot_details,collection_details

class QueryBuilder(base):
    """Build a navtree query based on the settings in navtree_properties
    and those set on the portlet.
    """
    implements(INavigationQueryBuilder)
    adapts(Interface, INavigationPortlet)

    def __init__(self, context, portlet):
        #import pdb;pdb.set_trace()
        #base.__init__(self,context,portlet)
        self.context = context
        self.portlet = portlet

        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        portal_url = getToolByName(context, 'portal_url')

        # Acquire a custom nav query if available
        customQuery = getattr(context, 'getCustomNavQuery', None)
        #if customQuery is None:
        #    customQuery = {'path':{'query':'/'.join(context.getPhysicalPath()),'depth':1},'portal_type':'Space'}
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query

        rootPath = getNavigationRoot(context, relativeRoot=portlet.root)
        currentPath = '/'.join(context.getPhysicalPath())


        #custom implementation starts here
        currentObject = self.context
        parentList = currentObject.aq_chain
        parentspace = None
        found = 0

        try:
            for type in parentList:
                if type.portal_type == 'Space' and type.meta_type == 'Space':
                    parentspace = type
                    found = 1
                if found == 1:
                    break
        except AttributeError:
                pass

        rootObject = self.context.portal_url.getPortalObject()

        objNavtree = 1
        if parentspace <> None:
            parentList.reverse()
            pos_parentspace = parentList.index(parentspace)
            pos_root = parentList.index(rootObject)
            objNavtree = pos_parentspace - pos_root
            parentList.reverse()

        isMemberFolder = False
        members = rootObject.Members

        if parentspace is None:
            if members in parentList:
                isMemberFolder = True
                parentList.reverse()
                objNavtree = 2
                parentList.reverse()
        #custom implementation ends here.

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.        
        #import pdb;pdb.set_trace()
        if not currentPath.startswith(rootPath):
            if not rootPath.endswith('/Members'):
                query['path'] = {'query' : rootPath, 'depth' : 1}
            else:
                query['path'] = {'query' : rootPath, 'depth' : 0}
            if portlet.root == '/' + members.id and self.context == rootObject and len(self.context.REQUEST.steps) > 0 and self.context.REQUEST.steps[-1] in ('author','personalize_form',):                
                traverse_subpath = self.context.REQUEST.traverse_subpath
                if len(traverse_subpath) > 0:
                    userid = traverse_subpath[0]                    
                else:
                    currentuser = getSecurityManager().getUser()
                    if currentuser <> None:
                        userid = currentuser.getId()
                if userid <> None:
                    currentPath = "/".join(rootObject.getPhysicalPath()) + "/" + members.id + "/" + userid
                    query['path'] = {'query': currentPath, 'navtree': 2}
        elif parentspace <> None:
            query['path'] = {'query': currentPath, 'navtree': objNavtree}
        elif isMemberFolder == True:
            if self.context == members:
                query['path'] = {'query' : currentPath, 'depth' : 0}
            else:
                query['path'] = {'query': currentPath, 'navtree': objNavtree}        
        else:
            query['path'] = {'query' : currentPath, 'navtree' : 1}

        if parentspace <> None:
            pass
        else:
            topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
            if topLevel and topLevel > 0:
                query['path']['navtree_start'] = topLevel + 1

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query['portal_type'] = utils.typesToList(context)

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        # Filter on workflow states, if enabled
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', ())        
        #import pdb;pdb.set_trace()
        self.query = query

    def __call__(self):
        return self.query

class Renderer(baseRenderer):

    _template = ViewPageTemplateFile('navigation.pt')
    recurse = ViewPageTemplateFile('navigation_recurse.pt')
    
    @property
    def available(self):        
        isavailable = baseRenderer.available.fget(self)
        rootid = contentroot_details['id']        
        viewsid = collection_details['id']
        if not isavailable and self.navigation_root() and hasattr(self.navigation_root(),'getId') and self.navigation_root().getId() in ('Members'):
            isavailable = True
        if not isavailable and self.navigation_root() and hasattr(self.navigation_root(),'getId') and self.navigation_root().getId() in (rootid,viewsid):
            tree = self.getNavTree()
            if (len(tree['children']) == 0):
                isavailable = True
        return isavailable
    
    def getAddTypeLink(self):        
        addmenuitems = []
        rootid = contentroot_details['id']        
        viewsid = collection_details['id']
        menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')
        root = self.navigation_root()
        if root and ((hasattr(root,'getId') and root.getId() == rootid) or (hasattr(root,'portal_type') and root.portal_type == 'ContentRoot' )):
            addmenuitems = menu.getMenuItems(root,self.request)
            spaceadd = [ob for ob in addmenuitems if ob.has_key('id') and ob['id'] == 'ContentSpace']
            addmenuitems = spaceadd
        elif root and ((hasattr(root,'getId') and root.getId() == viewsid) or (hasattr(root,'portal_type') and root.portal_type == 'SmartviewFolder' )):
            addmenuitems = menu.getMenuItems(root,self.request)
            viewsadd = [ob for ob in addmenuitems if ob.has_key('id') and ob['id'] in ('Topic',)]
            addmenuitems = viewsadd
        return addmenuitems
    
    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)

        # Special case - if the root is supposed to be pruned, we need to
        # abort here        

        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)
        
        obj = context
        if queryBuilder.portlet.root == "/Members" and self.context == self.context.portal_url.getPortalObject() and len(self.context.REQUEST.steps) > 0 and self.context.REQUEST.steps[-1] in ('author','personalize_form',):            
            userid = None
            traverse_subpath = self.context.REQUEST.traverse_subpath
            if len(traverse_subpath) > 0:
                userid = traverse_subpath[0]
            else:
                currentuser = getSecurityManager().getUser()
                if currentuser <> None:
                    userid = currentuser.getId()
            if userid <> None:
                currentPath = "/".join(self.context.getPhysicalPath()) + "/Members/" + userid
                try:
                    obj = context.restrictedTraverse(currentPath)
                except AttributeError:
                    obj = None
                if obj == None:
                    obj = context        
        return buildFolderTree(context, obj=obj, query=queryBuilder(), strategy=strategy)

class NavtreeStrategy(baseStrategy):
    """The navtree strategy used for the default navigation portlet
    """
    implements(INavtreeStrategy)
    adapts(Interface, INavigationPortlet)
    
    def __init__(self, context, portlet):
        
        SitemapNavtreeStrategy.__init__(self, context, portlet)
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = portlet.bottomLevel or navtree_properties.getProperty('bottomLevel', 0)

        currentFolderOnly = portlet.currentFolderOnly or navtree_properties.getProperty('currentFolderOnlyInNavtree', False)
        topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
        #custom implementation starts here
        currentObject = self.context
        parentList = currentObject.aq_chain
        parentspace = None
        found = 0

        try:
            for type in parentList:
                if type.portal_type == 'Space' and type.meta_type == 'Space':
                    parentspace = type
                    found = 1
                if found == 1:
                    break
        except AttributeError:
                pass

        rootObject = self.context.portal_url.getPortalObject()

        objNavtree = 1

        isMemberFolder = False
        members = rootObject.Members
        if parentspace is None:
            if members in parentList:
                isMemberFolder = True
        
        if parentspace <> None:
            self.rootPath = '/'.join(parentspace.getPhysicalPath())                
        else:
            topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
            self.rootPath = getRootPath(context, currentFolderOnly, topLevel, portlet.root)


        #custom implementation ends here.
        
    def decoratorFactory(self, node):
        newnode = baseStrategy.decoratorFactory(self,node)
        if newnode['currentParent'] and not self.context.restrictedTraverse('@@plone').isStructuralFolder() and hasattr(newnode['item'],'UID'):
            newnodeuid =  newnode['item'].UID
            if hasattr(self.context,'getParentNode'):
                parent = self.context.getParentNode()
                if parent <> None and hasattr(parent,'UID') and parent.UID() == newnodeuid:                    
                    newnode['currentItem'] = True                    
        if newnode['currentItem']:
            if newnode['item'] and hasattr(newnode['item'],'portal_type') and newnode['item'].portal_type == 'MemberSpace':
                newnode['link_remote'] = newnode['getRemoteUrl'] = self.context.portal_url() + "/author/" + newnode['item'].id
        return newnode

from plone.app.portlets.portlets import navigation
from ubify.cyninv2theme.browser.interfaces import ICyninNavigation, INavigationCollectionContent, INavigationSpacesContent, INavigationMembersContent
from Products.CMFCore.interfaces import ISiteRoot

class CyninNavigation(object):
    """Vertical navigation.
    """    
    implements(ICyninNavigation)
    adapts(ISiteRoot)
    
    def __init__(self, site):
        self.site = site
    
    def __call__(self):
        from ubify.policy.config import contentroot_details,collection_details
        rootid = contentroot_details['id']
        viewsid = collection_details['id']
        try:
            objRoot = "/" + rootid
            if getattr(self.site,rootid) == None:
                objRoot = None
        except AttributeError:
            objRoot = None
            
        try:
            objViews = "/" + viewsid
            if getattr(self.site,viewsid) == None:
                objViews = None
        except AttributeError:
            objViews = None
        
        try:
            objMembers = "/Members"
            if getattr(self.site,"Members") == None:
                objMembers = None
        except AttributeError:
            objMembers = None
            
        return {
            'ubify.navigationspacesportletmanager' : (navigation.Assignment(name=u"", root=objRoot, currentFolderOnly=False, includeTop=False, topLevel=0, bottomLevel=0),),
            'ubify.navigationcollectionportletmanager' : (navigation.Assignment(name=u"", root=objViews, currentFolderOnly=False, includeTop=False, topLevel=0, bottomLevel=0),),
            'ubify.navigationmembersportletmanager' : (navigation.Assignment(name=u"", root=objMembers, currentFolderOnly=False, includeTop=False, topLevel=0, bottomLevel=0),),
        }


from plone.portlets.interfaces import IPortletManager
from zope.component.interfaces import ComponentLookupError
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.manager import PortletManager
from zope.interface import alsoProvides
from zope.app.container.interfaces import INameChooser
from ubify.policy.config import contentroot_details

def assign_cynin_navigation(portal):
    cyninnav = ICyninNavigation(portal)
    if cyninnav is None:
        return
    
    portlets = cyninnav()    
    for name in portlets.keys():        
        assignments = portlets.get(name)
        if assignments:
            try:
                portletManager = getUtility(IPortletManager, name=name)
            except ComponentLookupError:
                sm = getSiteManager(portal)
                objportletManager = PortletManager()
                if name == 'ubify.navigationspacesportletmanager':
                    alsoProvides(objportletManager,INavigationSpacesContent)
                elif name == 'ubify.navigationcollectionportletmanager':
                    alsoProvides(objportletManager,INavigationCollectionContent)
                elif name == 'ubify.navigationmembersportletmanager':
                    alsoProvides(objportletManager,INavigationMembersContent)
                    
                sm.registerUtility(component=objportletManager,
                                   provided=IPortletManager,
                                   name = name)        
                portletManager = getUtility(IPortletManager, name=name) 
            
            assignable = getMultiAdapter((portal, portletManager,), ILocalPortletAssignmentManager)
            manager = getMultiAdapter((portal, portletManager), IPortletAssignmentMapping)

            if portletManager is not None:            
                chooser = INameChooser(manager)
                for assignment in assignments:
                    if name == 'ubify.navigationspacesportletmanager':
                        bfound = False
                        for eobj in manager.values():                            
                            if isinstance(eobj,assignment.__class__):
                                bfound = True
                            if bfound and eobj.root == '/' + contentroot_details['oldid']:
                                bfound = False
                                del manager[eobj.id]
                            if bfound:
                                break;
                        if not bfound:
                            manager[chooser.chooseName(None, assignment)] = assignment
                    elif name == 'ubify.navigationcollectionportletmanager':
                        bfound = False
                        for eobj in manager.values():
                            if isinstance(eobj,assignment.__class__):
                                bfound = True                            
                            if bfound:
                                break;
                        
                        if not bfound:
                            manager[chooser.chooseName(None, assignment)] = assignment
                    elif name == 'ubify.navigationmembersportletmanager':                        
                        bfound = False
                        for eobj in manager.values():
                            if isinstance(eobj,assignment.__class__):
                                bfound = True                            
                            if bfound:
                                break;
                        
                        if not bfound:
                            manager[chooser.chooseName(None, assignment)] = assignment    
                        
            assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)