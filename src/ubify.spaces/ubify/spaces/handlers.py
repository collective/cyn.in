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
#from zope.interface import implements
#from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
#from ubify.spaces.utils import get_factory_permission
from ubify.spaces.config import PLACEFUL_WORKFLOW_POLICY
from ubify.spaces.config import SPACE_PLACEFUL_WORKFLOW_POLICY
from ubify.spaces.config import spacehome_portlets_assignment
from ubify.spaces.config import spacemembersportletmanager_name,spacedashboardportletmanager_name,spacemindmapmanager_name
from ubify.spaces.config import spacehomeleftblockmanager_name

from ubify.spaces.spacedashboard import SpaceDefaultDashboard
from interfaces import ISpaceDefaultDashboard
from zope.component import getMultiAdapter, getUtility, getSiteManager,queryUtility
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY
from zope.app.container.interfaces import INameChooser
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.component.interfaces import ComponentLookupError

from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager
from zope.interface import alsoProvides
from ubify.cyninv2theme.browser.interfaces import ISpaceMembersContent,IMindMapContent,IHomeLeftblockContent
from ubify.viewlets.browser.interfaces import IHomeContent
from ubify.cyninv2theme.portlets import spacemindmapportlet, myitemsportlet, recentupdatesportlet


def add_local_space_workflow(space, event):
    """Apply the local workflow for spaces when a space is added.
    """
    placeful_workflow = getToolByName(space, 'portal_placeful_workflow')
    try:
        config = placeful_workflow.getWorkflowPolicyConfig(space)
    except:
        space.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(space)
    
    if config is None:
        space.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(space)
        
    config.setPolicyIn(policy=SPACE_PLACEFUL_WORKFLOW_POLICY)
    config.setPolicyBelow(policy=PLACEFUL_WORKFLOW_POLICY)
    
    space.__ac_local_roles_block__ = True ##DKG: Disallow inheritance of sharing (DKG)
    
    #add owner to all roles
    
    #space manager access:
    manager_access = ('Contributor','Editor','Reader',)
    space.manage_setLocalRoles(space.getOwner().getUserName(), list(manager_access))
    
    #allow logged in users to have reader access only in case if parent is spacefolder object at /spaces
    try:
        portal = space.portal_url.getPortalObject()
        objspaceparent = space.getParentNode()
        
        objspaces = getattr(portal,'spaces')
        
        if objspaceparent == objspaces:
            viewer_access = ('Reader',)
            space.manage_setLocalRoles('AuthenticatedUsers',list(viewer_access))
    except AttributeError:
        pass
    
    add_defined_applications(space,event)
    space.reindexObject()
    
def add_defined_applications(space,event):
    from ubify.policy.config import space_defined_applications
    from ubify.policy.setuphandlers import getOrCreateType
    
    try:
        portal = space.portal_url.getPortalObject()
        objspaceparent = space.getParentNode()
        
        objspaces = getattr(portal,'spaces')
        
        objcatalog = getattr(portal,'portal_catalog')
        strPath = space.getPhysicalPath()
        strURL = "/".join(strPath)
        
        if objspaceparent == objspaces and space <> None:
            #create applications
            if len(space.objectIds()) <= 1:
                for item in space_defined_applications:
                    id = item["id"]
                    title = item["title"]
                    type = item["type"]
                    
                    query = {'path':{'query':strURL,'depth':1},'portal_type':type}
                    objItems = objcatalog(query)
                    
                    if len(objItems) <= 0:                    
                        try:
                            newobj = getattr(space,id)
                        except AttributeError:
                            newobj = getOrCreateType(portal,space,id,type)
                        
                        if newobj.title == '':
                            newobj.title = title
                        newobj.reindexObject()
    except:
        pass
    


def manage_edit(space,event):    
    space.reindexObject()
    
def assign_space_dashboard(space,event):
    #import pdb;pdb.set_trace()
    site = space.portal_url.getPortalObject()
    objDashboard = ISpaceDefaultDashboard(space,None)
    if objDashboard is None:
        return
    
    spaceid = space.id
    portlets = objDashboard()
    
    for name in (spacemembersportletmanager_name,spacedashboardportletmanager_name,spacemindmapmanager_name,spacehomeleftblockmanager_name):
        assignments = portlets.get(name)        
        if assignments:
            try:
                portletManager = getUtility(IPortletManager, name=name)
            except ComponentLookupError:
                sm = getSiteManager(site)
                objportletManager = PortletManager()
                if name == spacedashboardportletmanager_name:
                    alsoProvides(objportletManager,IHomeContent)
                elif name == spacemembersportletmanager_name:
                    alsoProvides(objportletManager,ISpaceMembersContent)
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
                chooser = INameChooser(manager)
                for assignment in assignments:
                    if name == spacemindmapmanager_name:
                        bfound = False
                        for eobj in manager.values():
                            if isinstance(eobj,spacemindmapportlet.Assignment):
                                bfound = True
                            if bfound:
                                break;
                        if not bfound:
                            manager[chooser.chooseName(None, assignment)] = assignment
                    elif name == spacehomeleftblockmanager_name:
                        bfound = False
                        for eobj in manager.values():
                            if isinstance(eobj,assignment.__class__):
                                bfound = True
                            elif isinstance(eobj,assignment.__class__):
                                bfound = True
                            
                            if bfound:
                                break;
                        
                        if not bfound:
                            manager[chooser.chooseName(None, assignment)] = assignment
                    elif name == spacemembersportletmanager_name:
                        bfound = False
                        for eobj in manager.values():
                            if isinstance(eobj,assignment.__class__):
                                bfound = True
                            elif isinstance(eobj,assignment.__class__):
                                bfound = True
                            
                            if bfound:
                                break;
                        
                        if not bfound:
                            manager[chooser.chooseName(None, assignment)] = assignment
                    else:
                        strtitle = assignment.title.lower()
                        strtitle = strtitle.replace(' ','-')
                        if manager.has_key(strtitle) == 0:
                            manager[chooser.chooseName(None, assignment)] = assignment
                        
            assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

    
#def enable_addable_types(space, event):
#    """Give the given role the add permission on all the selected types.
#    """
#    portal_types = getToolByName(space, 'portal_types')
#    role = 'TeamMember'
#    #import pdb;pdb.set_trace()
#    for fti in portal_types.listTypeInfo():
#        type_id = fti.getId()
#
#        permission = get_factory_permission(space, fti)
#        if permission is not None:
#            roles = [r['name'] for r in space.rolesOfPermission(permission) if r['selected']]
#            acquire = bool(space.permission_settings(permission)[0]['acquire'])
#            if type_id in space.addable_types and role not in roles:
#                roles.append(role)
#            elif type_id not in space.addable_types and role in roles:
#                roles.remove(role)
#            space.manage_permission(permission, roles, acquire)