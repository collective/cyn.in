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
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import process_types, listTypes
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager

from ubify.recyclebin.config import *

from AccessControl import allow_module
from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo("ubify.recyclebin").declarePublic("movetotrash")
ModuleSecurityInfo("ubify.recyclebin.utils").declarePublic("deleteObjectsByPaths")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    import ubify.recyclebin.content
    from Products.ATContentTypes.permission import permissions

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)

    allTypes = zip(content_types, constructors)

    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        if atype.portal_type not in TYPES_NEW:

            ContentInit(
                kind,
                content_types      = (atype,),
                permission         = permissions[atype.portal_type],
                extra_constructors = (constructor,),
                ).initialize(context)
        else:
            ContentInit(
                kind,
                content_types      = (atype,),
                permission         = DEFAULT_ADD_CONTENT_PERMISSION,
                extra_constructors = (constructor,),
                ).initialize(context)
    

def _get_id(newParent, id):
    # Allow containers to override the generation of
    # object copy id by attempting to call its _get_id
    # method, if it exists.
    import re
    copy_re = re.compile('^copy([0-9]*)_of_(.*)')
    
    match = copy_re.match(id)
    if match:
        n = int(match.group(1) or '1')
        orig_id = match.group(2)
    else:
        n = 0
        orig_id = id
    while 1:
        if newParent._getOb(id, None) is None:
            return id
        id='copy%s_of_%s' % (n and n+1 or '', orig_id)
        n=n+1
    
def addPropertiesOnDelete(portal,object,org_object,actionowner,parentpath):
    #persist username of user who has initiated delete action
    if object.hasProperty('deletedby') == 0:
        object.manage_addProperty('deletedby',actionowner.getId(),'string')
    else:
        object._updateProperty('deletedby',actionowner.getId())
        
    #persist the parent object path as restorepath
    if object.hasProperty('restorepath') == 0:
        object.manage_addProperty('restorepath',parentpath,'string')
    else:
        object._updateProperty('restorepath',parentpath)
    
    #persist original owner of an object
    if object.hasProperty('org_owner') == 0:
        object.manage_addProperty('org_owner',org_object.getOwner().getUserName(),'string')
    else:
        object._updateProperty('org_owner',org_object.getOwner().getUserName())
    
    #persists workflow state
    
    wf_tool = getattr(portal,'portal_workflow')
    
    current_state = wf_tool.getInfoFor(org_object,'review_state')
    
    wf_def = wf_tool.getWorkflowsFor(org_object)
    if len(wf_def) > 0:
        curr_wf = wf_def[0]
        wf_states = curr_wf.states
        current_state_title = wf_states[current_state].title
        if object.hasProperty('wfstate') == 0:
            object.manage_addProperty('wfstate',current_state,'string')
        else:
            object._updateProperty('wfstate',current_state)
            
        if object.hasProperty('wfstatetitle') == 0:
            object.manage_addProperty('wfstatetitle',current_state_title,'string')
        else:
            object._updateProperty('wfstatetitle',current_state_title)

def getPreferredRecycleBin(object,global_recycle_bin=True):
    from ubify.recyclebin.utils import getGlobalRecycleBin,getMemberRecycleBin
    portal = object.portal_url.getPortalObject()
    
    members = portal.Members
    
    parentslist = object.aq_chain
    parentslist.reverse()
    if parentslist.__contains__(members) and object <> members:
        global_recycle_bin = False
        
    parentslist.reverse()
    # check whether /Members is in the path if not then use global recycle bin else get Member specific recycle bin object
    if global_recycle_bin == True:
        return getGlobalRecycleBin(portal)
    else:
        return None

def impersonateUser(portal,username):
    user = portal.acl_users.getUserById(username)
    userid = None
    if user <> None:
        userid = user.getId()
    if userid <> None:        
        newSecurityManager(None,user)
    else:
        app = portal.getParentNode()
        user = app.acl_users.getUserById('admin')
        newSecurityManager(None,user)

def getUserToImpersonate(portal,object):
    members = portal.Members
    
    parentslist = object.aq_chain
    parentslist.reverse()
    
    if parentslist.__contains__(members):
        idx = parentslist.index(members)
        memberfolder = parentslist[idx+1]
        if memberfolder <> None:
            return memberfolder.getOwner().getId()
        else:
            return 'siteadmin'
    else:
        return 'siteadmin'

def onObjectDeletion(object=None):
    
    import transaction
    from zope.event import notify
    from zope.app.container.contained import ObjectMovedEvent
    from zope.app.container.contained import notifyContainerModified
    from OFS.event import ObjectClonedEvent
    import OFS.subscribers
    from zope.lifecycleevent import ObjectCopiedEvent
    
    if object <> None:
        portal = object.portal_url.getPortalObject()       
        
        org_user = getSecurityManager().getUser()
        
        
        
        try:
            objRBin = getPreferredRecycleBin(object)
            
            if objRBin <> None:
                #impersonateUser
                username = getUserToImpersonate(portal,objRBin)
                impersonateUser(portal,username)
                #
                parent = aq_parent(aq_inner(object))        
                
                orig_id = object.getId()
                id = _get_id(objRBin,orig_id)
                
                orig_ob = object
                object = object._getCopy(parent)
                
                object._setId(id)
                
                addPropertiesOnDelete(portal,object,orig_ob,org_user,"/".join(parent.getPhysicalPath()))
                
                notify(ObjectCopiedEvent(object, orig_ob))
                objRBin._setObject(id, object)
                
                ob = objRBin._getOb(id)            
                ob._postCopy(objRBin, op=0)            
                OFS.subscribers.compatibilityCall('manage_afterClone', ob, ob)
                notify(ObjectClonedEvent(ob))
            
        except AttributeError:
            pass
        
        #undo imporsination
        newSecurityManager(None,org_user)

def is_deleted_from_recyclebin(object):
    objRBin = getPreferredRecycleBin(object)
    
    parentslist = aq_parent(aq_inner(object)).aq_chain
    
    if parentslist.__contains__(objRBin):
        return True
    else:
        return False
    
def movetotrash(object):
    
    isdeletedFromRecycleBin = is_deleted_from_recyclebin(object)
    if not isdeletedFromRecycleBin:
        onObjectDeletion(object)