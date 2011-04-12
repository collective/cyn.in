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
from ubify.coretypes.interfaces import ISpaceDefaultDashboard,IContentSpace, ISiteDefaultDashboard
from ubify.cyninv2theme.portlets import spacemembersportlet
from ubify.cyninv2theme.portlets import wikiportlet,blogportlet,eventsportlet,filesportlet,linksportlet,imagesportlet,commentsportlet
from zope.interface import implements
from zope.component import adapts
from ubify.cyninv2theme.portlets import spacemindmapportlet
from ubify.cyninv2theme.portlets import myitemsportlet, recentupdatesportlet
from ubify.cyninv2theme.portlets import applicationportlet

from plone.portlets.interfaces import IPortletManager
from zope.component.interfaces import ComponentLookupError
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.manager import PortletManager
from zope.interface import alsoProvides
from zope.app.container.interfaces import INameChooser
from ubify.cyninv2theme.browser.interfaces import IMindMapContent,IHomeLeftblockContent
from ubify.viewlets.browser.interfaces import IHomeContent
from Products.Five.browser import BrowserView
from Products.CMFPlone.interfaces import IPloneSiteRoot

from ubify.cyninv2theme.portlets import recentsiteupdatesportlet, topratedportlet, statisticsportlet
from ubify.cyninv2theme.portlets import sitedescriptionportlet, tagsportlet, activityportlet, commentsportlet
from plone.portlet.static import static

from zope.component import adapts, getMultiAdapter, queryUtility, getUtility, getSiteManager

spacedashboardportletmanager_name = 'ubify.homecontentportletsmanager'
spacemindmapmanager_name = 'ubify.mindmapportletmanager'
spacehomeleftblockmanager_name = 'ubify.homeleftblockportletmanager'

site_home_top_banner_static_header = """Site Home Banner"""
site_home_top_banner_static_text="""
<div class="homebannercontainer">
<div class="homebannerimgholder">
    	<img src="banner-business-team.png" alt="cyn.in banner Image" height="250" width="330" /></div>
<div class="homebannertextholder">
<div class="homebannertextwelcome">Welcome to our cyn.in powered</div>
<div class="homebannertexttitle">Collaboration Portal</div>
<div class="homebannertextmessage">The administrator needs to set a cool message here...</div>
</div>
</div>
"""

space_home_top_banner_static_header = """Space Home Banner"""
space_home_top_banner_static_text=""


class SpaceDashboardView(BrowserView):
    """Power the dashboard
    """

class SpaceDefaultDashboard(object):
    """The default default dashboard.
    """
    implements(ISpaceDefaultDashboard)
    adapts(IContentSpace)

    def __init__(self, space):
        self.space = space

    def __call__(self):
        return {
            'ubify.homecontentportletsmanager' : (sitedescriptionportlet.Assignment(),tagsportlet.Assignment(),activityportlet.Assignment(count=20),commentsportlet.Assignment(),),
            'ubify.mindmapportletmanager' : (),
            'ubify.homeleftblockportletmanager' : (recentsiteupdatesportlet.Assignment(),topratedportlet.Assignment(),statisticsportlet.Assignment(),),
        }

class SiteHomeDefaultDashboard(object):
    """The default dashboard for site
    """
    implements(ISiteDefaultDashboard)
    adapts(IPloneSiteRoot)

    def __init__(self,portal):
        self.portal = portal

    def __call__(self):
        return {
            'ubify.homecontentportletsmanager' : (sitedescriptionportlet.Assignment(),tagsportlet.Assignment(),activityportlet.Assignment(count=20),commentsportlet.Assignment(),),
            'ubify.mindmapportletmanager' : (static.Assignment(header=site_home_top_banner_static_header,text=site_home_top_banner_static_text,omit_border=True),),
            'ubify.homeleftblockportletmanager' : (recentsiteupdatesportlet.Assignment(),topratedportlet.Assignment(),statisticsportlet.Assignment(),),
        }

def assign_space_dashboard(space,event,isReinstall=False):
    site = space.portal_url.getPortalObject()
    objDashboard = ISpaceDefaultDashboard(space,None)
    if objDashboard is None:
        return

    portlets = objDashboard()

    for name in portlets.keys():
        assignments = portlets.get(name)
        try:
            portletManager = getUtility(IPortletManager, name=name)
        except ComponentLookupError:
            sm = getSiteManager(site)
            objportletManager = PortletManager()
            if name == spacedashboardportletmanager_name:
                alsoProvides(objportletManager,IHomeContent)
            elif name == spacemindmapmanager_name:
                alsoProvides(objportletManager,IMindMapContent)
            elif name == spacehomeleftblockmanager_name:
                alsoProvides(objportletManager,IHomeLeftblockContent)

            sm.registerUtility(component=objportletManager,
                               provided=IPortletManager,
                               name = name)
            portletManager = getUtility(IPortletManager, name=name)


        assignable = getMultiAdapter((space, portletManager,), ILocalPortletAssignmentManager)
        manager = getMultiAdapter((space, portletManager), IPortletAssignmentMapping)

        if portletManager is not None:
            reorderrecentportlet = False
            recentportletname = ''
            chooser = INameChooser(manager)
            for assignment in assignments:
                if name == spacemindmapmanager_name:
                    bfound = False
                    for eobj in manager.values():
                        if isinstance(eobj,static.Assignment) and eobj.id == space_home_top_banner_static_header.lower().replace(' ','-'):
                            bfound = True
                        if bfound:
                            break
                    if not bfound:
                        manager[chooser.chooseName(None, assignment)] = assignment
                elif name == spacehomeleftblockmanager_name:
                    bfound = False
                    for eobj in manager.values():
                        if isinstance(eobj,assignment.__class__):
                            bfound = True
                        if bfound:
                            #check for recentsiteupdate portlet fix
                            try:
                                if isinstance(eobj,recentsiteupdatesportlet.Assignment) and hasattr(eobj,'data') and hasattr(eobj.data,'resultcount') and isinstance(eobj.data.resultcount,int):
                                    bfound = False
                                    del manager[eobj.id]
                                    reorderrecentportlet = True
                                    recentportletname = eobj.id.encode('ascii','replace')
                            except AttributeError:
                                pass
                        if bfound:
                            break
                    if not bfound:
                        manager[chooser.chooseName(None, assignment)] = assignment
                elif name == spacedashboardportletmanager_name:
                    bfound = False
                    for eobj in manager.values():
                        if isinstance(eobj,assignment.__class__):
                            bfound = True
                        if bfound:
                            break
                    if not bfound:
                        manager[chooser.chooseName(None, assignment)] = assignment
            if reorderrecentportlet and isReinstall:                
                keys = list(manager.keys())
                idx = keys.index(recentportletname)                
                keys.remove(recentportletname)
                keys.insert(0, recentportletname)
                manager.updateOrder(keys)
        if assignable is not None:
            assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

def assign_portal_dashboard(portal,event,isReinstall=False):
    site = portal
    objDashboard = ISiteDefaultDashboard(portal,None)
    if objDashboard is None:
        return

    portlets = objDashboard()

    for name in portlets.keys():
        assignments = portlets.get(name)
        try:
            portletManager = getUtility(IPortletManager, name=name)
        except ComponentLookupError:
            sm = getSiteManager(site)
            objportletManager = PortletManager()
            if name == spacedashboardportletmanager_name:
                alsoProvides(objportletManager,IHomeContent)
            elif name == spacemindmapmanager_name:
                alsoProvides(objportletManager,IMindMapContent)
            elif name == spacehomeleftblockmanager_name:
                alsoProvides(objportletManager,IHomeLeftblockContent)

            sm.registerUtility(component=objportletManager,
                               provided=IPortletManager,
                               name = name)
            portletManager = getUtility(IPortletManager, name=name)


        assignable = getMultiAdapter((portal, portletManager,), ILocalPortletAssignmentManager)
        manager = getMultiAdapter((portal, portletManager), IPortletAssignmentMapping)
        
        if portletManager is not None:
            reorderrecentportlet = False
            recentportletname = ''
            chooser = INameChooser(manager)
            for assignment in assignments:
                if name == spacemindmapmanager_name:
                    bfound = False
                    if isReinstall:
                        removeAssignedPortlets(portal,manager,name)
                    for eobj in manager.values():
                        if isinstance(eobj,static.Assignment) and eobj.id == site_home_top_banner_static_header.lower().replace(' ','-'):
                            bfound = True
                        if bfound:
                            break
                    if not bfound:
                        manager[chooser.chooseName(None, assignment)] = assignment
                elif name == spacehomeleftblockmanager_name:
                    bfound = False                    
                    if isReinstall:
                        removeAssignedPortlets(portal,manager,name)
                    for eobj in manager.values():                        
                        if isinstance(eobj,assignment.__class__):
                            bfound = True
                        if bfound:
                            #check for recentsiteupdate portlet fix
                            try:
                                if isinstance(eobj,recentsiteupdatesportlet.Assignment) and hasattr(eobj,'data') and hasattr(eobj.data,'resultcount') and isinstance(eobj.data.resultcount,int):
                                    bfound = False
                                    del manager[eobj.id]
                                    reorderrecentportlet = True
                                    recentportletname = eobj.id.encode('ascii','replace')
                            except AttributeError:
                                pass
                        if bfound:
                            break
                    if not bfound:
                        manager[chooser.chooseName(None, assignment)] = assignment
                elif name == spacedashboardportletmanager_name:
                    bfound = False
                    if isReinstall:
                        removeAssignedPortlets(portal,manager,name)
                    for eobj in manager.values():
                        if isinstance(eobj,assignment.__class__):
                            bfound = True
                        if bfound:
                            break
                    if not bfound:
                        manager[chooser.chooseName(None, assignment)] = assignment
            if reorderrecentportlet and isReinstall:                
                keys = list(manager.keys())
                idx = keys.index(recentportletname)                
                keys.remove(recentportletname)
                keys.insert(0, recentportletname)
                manager.updateOrder(keys)
        if assignable is not None:
            assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def removeAssignedPortlets(portal,manager,portletmanagername):
    from ubify.cyninv2theme.portlets import sitemindmapportlet
    from ubify.cyninv2theme.portlets import myitemsportlet, recentupdatesportlet
    from ubify.policy.migration.onetimeinstall import get_assignments_for_sitehome_collectionportlets
    from StringIO import StringIO
    out = StringIO()

    if portletmanagername == spacemindmapmanager_name:
        for portlet in manager.values():
            if isinstance(portlet,sitemindmapportlet.Assignment):
                for key in manager.keys():
                    if portlet.id == key:
                        del manager[key]
    elif portletmanagername == spacehomeleftblockmanager_name:
        bFound = False
        for portlet in manager.values():
            if isinstance(portlet,myitemsportlet.Assignment):
                bFound = True
            elif isinstance(portlet,recentupdatesportlet.Assignment):
                bFound = True

            if bFound:
                for key in manager.keys():
                    if portlet.id == key:
                        del manager[key]
    elif portletmanagername == spacedashboardportletmanager_name:
        objviews = getattr(portal,'views')
        oldassignments = get_assignments_for_sitehome_collectionportlets(portal,objviews,out)
        for o_ass in oldassignments:
            bFound = False
            for portlet in manager.values():
                if isinstance(portlet,o_ass.__class__):
                    bFound = True

                if bFound:
                    for key in manager.keys():
                        if portlet.id == key:
                            del manager[key]
