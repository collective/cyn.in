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
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import process_types, listTypes
from Acquisition import aq_base, aq_inner, aq_parent
from ubify.coretypes.config import *
from AccessControl import ModuleSecurityInfo
from ubify.spaces.config import PLACEFUL_WORKFLOW_POLICY,SPACE_PLACEFUL_WORKFLOW_POLICY
from ubify.policy import CyninMessageFactory as _
from ubify.cyninv2theme import getAdminUser, getCurrentUser

#constants defined for lastchangeaction
last_change_action_add = 'created'
last_change_action_edit = 'modified'
last_change_action_workflowstate_change = 'workflowstatechanged'
last_change_action_comment = 'commented'


last_change_action_mapping = {
                                last_change_action_add : _(u'last_change_created',u'created'),
                                last_change_action_edit : _(u'last_change_edited','edited'),
                                last_change_action_workflowstate_change : _(u'last_change_workflowed','workflowed'),
                                last_change_action_comment : _(u'last_change_discussed','discussed'),
}

def initialize(context):

    import ubify.coretypes.content
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

    ModuleSecurityInfo("ubify.coretypes").declarePublic("get_action_mapped")

def is_portal_factory(context):
    """Find out if the given object is in portal_factory
    """
    portal_factory = getToolByName(context, 'portal_factory', None)
    if portal_factory is not None:
        return portal_factory.isTemporary(context)
    else:
        return False

def get_action_mapped(action):
    if action == last_change_action_add:
        return last_change_action_mapping[last_change_action_add]
    elif action == last_change_action_edit:
        return last_change_action_mapping[last_change_action_edit]
    elif action == last_change_action_workflowstate_change:
        return last_change_action_mapping[last_change_action_workflowstate_change]
    elif action == last_change_action_comment:
        return last_change_action_mapping[last_change_action_comment]

def onObjectModification(object,action,datetime):
    from AccessControl import getSecurityManager
    from DateTime import DateTime
    #event though we are passing datetime factor we are not using passed datetime
    #we will change the definition and other method calls appropriately
    datetime = DateTime()
    currentuserid = getSecurityManager().getUser().getId()
    if currentuserid <> None:
        if object.hasProperty('lastchangedate') == 0:
            object.manage_addProperty('lastchangedate',datetime,'date')
        else:
            object._updateProperty('lastchangedate',datetime)

        if object.hasProperty('lastchangeaction') == 0:
            object.manage_addProperty('lastchangeaction',action,'string')
        else:
            object._updateProperty('lastchangeaction',action)

        if object.hasProperty('lastchangeperformer') == 0:
            object.manage_addProperty('lastchangeperformer',currentuserid,'string')
        else:
            object._updateProperty('lastchangeperformer',currentuserid)

def setProperties(object):
    from AccessControl import getSecurityManager
    sm = getSecurityManager()

    currentuserid = getSecurityManager().getUser().getId()
    if currentuserid <> None:
        if object.hasProperty('modifiedby') == 0:
            object.manage_addProperty('modifiedby',currentuserid,'string')
        else:
            object._updateProperty('modifiedby',currentuserid)

        if object.hasProperty('modifiers') == 0:
            object.manage_addProperty('modifiers',(currentuserid,),'ulines')
        else:
            modifiers = object.getProperty('modifiers')
            lstmodifiers = [mo for mo in modifiers]

            if lstmodifiers.__contains__(currentuserid) == False:
                object._updateProperty('modifiers', modifiers + (currentuserid,))

def onObjectEditedEvent(object,event):
    from AccessControl import getSecurityManager
    sm = getSecurityManager()

    currentuserid = getSecurityManager().getUser().getId()
    if currentuserid <> None:
        setProperties(object)
        onObjectModification(object,last_change_action_edit,object.modified())
        object.reindexObject()

def setNextPreviousEnabledOnFolderishContentTypes(object,event):
    object.setNextPreviousEnabled(True)

def onDiscussionItemAddedEvent(object,event):
    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl import getSecurityManager
    import transaction

    contextuser = getSecurityManager().getUser()

    discussion_item = object
    discussed_item = discussion_item
    while discussed_item.meta_type == discussion_item.meta_type:
        discussed_item = discussed_item.aq_inner.aq_parent.aq_parent


    modifiedat = None
    try:
        modifiedat = discussion_item.created()
    except AttributeError:
        modifiedat = None

    if modifiedat <> None:
        try:
            onObjectModification(discussed_item,last_change_action_comment,modifiedat)
            onObjectModification(discussion_item,last_change_action_add,modifiedat)
            discussed_item.reindexObject()
            discussion_item.reindexObject()
        except:
            currentOwner = discussed_item.getOwner()
            newSecurityManager(None,currentOwner)
            onObjectModification(discussed_item,last_change_action_comment,modifiedat)
            onObjectModification(discussion_item,last_change_action_add,modifiedat)
            discussed_item.reindexObject()
            discussion_item.reindexObject()
            newSecurityManager(None,contextuser)

def impersonateuser(user):
    from AccessControl.SecurityManagement import newSecurityManager
    newSecurityManager(None,user)    
    
def onObjectCreatedEvent(object,event):
    if is_portal_factory(event.object):
        return

    if object.portal_type=='ContentSpace':
        space = object
        manager_access = ('Contributor','Editor','Reader',)
        space.manage_setLocalRoles(space.getOwner().getUserName(), list(manager_access))

        placeful_workflow = getToolByName(space, 'portal_placeful_workflow')
        portalworkflowtool = getToolByName(space,'portal_workflow')
        portal = space.portal_url.getPortalObject()
        
        #impersonating admin user since placefulworkflow method requires Manage portal permission
        from AccessControl import getSecurityManager        
        currentuser = getSecurityManager().getUser()
        
        getAdminUser(portal)
        
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
        portalworkflowtool.updateRoleMappings()
        
        #impersonating back to original user
        impersonateuser(currentuser)
        
        #assign space dashboard
        from ubify.cyninv2theme.browser.cynindashboards import assign_space_dashboard
        assign_space_dashboard(space,event)

    onObjectModification(object,last_change_action_add,object.created())
    setProperties(object)
    object.reindexObject()

def onActionSucceededEvent(object,event):
    setProperties(object)
    onObjectModification(object,last_change_action_workflowstate_change,object.modified())
    object.reindexObject()

def onFlashUploadedEvent(object,event):
    #import pdb;pdb.set_trace()
    title = object.Title()
    object.title = title.replace("_"," ")
    object.reindexObject()
