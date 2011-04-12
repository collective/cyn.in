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
from StringIO import StringIO
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.app.controlpanel.markup import MarkupControlPanelAdapter
from config import *
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
from Products.CMFCore.Expression import Expression
from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
from Acquisition import aq_inner, aq_parent, aq_base

from Products.CMFPlone.utils import _createObjectByType
from AccessControl import Unauthorized
from ubify.policy.migration.migration import *
from ubify.policy.migration.onetimeinstall import *

from ubify.spaces.config import PLACEFUL_WORKFLOW_POLICY, SPACE_PLACEFUL_WORKFLOW_POLICY, REVIEW_PLACEFUL_WORKFLOW_POLICY

from ubify.policy import CyninMessageFactory as _

import transaction

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.component import createObject
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

from ubify.recyclebin.config import GLOBAL_RECYCLEBIN_POLICY



    
def renameScrawl(portal_types):
    blog_fti = getattr(portal_types, 'Blog Entry')
    blog_fti.title = _(u'Blog Post')
    blog_fti.description = _(u"Formatted temporal content",u"Formatted temporal content")
    blog_fti.content_icon = 'blog.png'
    blog_fti.global_allow = True

def removeNewsItemViewFromBlogEntry(portal_types):
    blogentry = getattr(portal_types,'Blog Entry')    
    view = 'blogentry_view'    
    blogentry._updateProperty('view_methods', (view,))

def configureContentTypes(portal,logger):
    portal_types = getToolByName(portal, 'portal_types')
    renameScrawl(portal_types)
    logger.info("Renamed Scrawl")
    removeNewsItemViewFromBlogEntry(portal_types)
    logger.info("Removed News Item View from Blog Entry")

def setup_folders(portal,logger):
    try:
        portal.manage_delObjects('news')
        logger.info("Deleted %s folder" % 'news')
    except AttributeError:
        logger.info("No %s folder detected. Hmm... strange. Continuing..." % 'news')

    try:
        portal.manage_delObjects('events')
        logger.info("Deleted Events folder")
    except AttributeError:
        logger.info("No %s folder detected. Hmm... strange. Continuing..." % 'events')

    try:  #delete front-page
        portal.manage_delObjects('front-page')
        logger.info("Deleted Default front page")
    except AttributeError:
        logger.info("No %s item detected. Hmm... strange. Continuing..." % 'front-page')
    
    portalmembership = getToolByName(portal, 'portal_membership')
    portalmembership.setMemberAreaType('MemberSpace')
    if portalmembership.getMemberareaCreationFlag() == 0:
        _ = portalmembership.setMemberareaCreationFlag()  #Set Member Area Creation On, and discard return value
    
    try:
        portal_actions = getToolByName(portal,'portal_actions')
        user_actions = getattr(portal_actions,'user')
        my_stuff = getattr(user_actions,'mystuff')
        if my_stuff <> None:
            my_stuff._updateProperty('title',user_my_folder_name)
            my_stuff.visible = False
            logger.info("Renamed My Folder to %s" % (user_my_folder_name,))
    except:
        logger.info("unable to rename My Folder")
    


def setVersionedTypes(portal,logger):
    portal_repository = getToolByName(portal, 'portal_repository')
    versionable_types = list(portal_repository.
    getVersionableContentTypes())
    for type_id in versionable_content_types:
        if type_id not in versionable_types:
            versionable_types.append(type_id)
            # Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id,policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)
    logger.info("Set up versionable types.")
    
    #setting up portal_type for portal_diff tool
    portal_diff = getToolByName(portal,'portal_diff')
    
    d = {'any':'Compound Diff for AT types'}
    for type_id in versionable_content_types:
        if portal_diff.getDiffForPortalType(type_id) == {}:
            portal_diff.setDiffForPortalType(type_id,d)
            
    logger.info("Configuration for portal diff tool is done.")

def getOrCreateType(portal, atobj, newid, newtypeid):
    """
    Gets the object specified by newid if it already exists under
    atobj or creates it there with the id given in newtypeid
    """
    try:
        newobj = getattr(atobj,newid) #get it if it already exists
    except AttributeError:  #newobj doesn't already exist
        try:            
            _ = atobj.invokeFactory(id=newid,type_name=newtypeid)            
        except ValueError:
            _createObjectByType(newtypeid, atobj, newid)
        except Unauthorized:
            _createObjectByType(newtypeid, atobj, newid)
        newobj = getattr(atobj,newid)
        notify(ObjectCreatedEvent(newobj))
    return newobj

def enable_wikitype(portal,logger):
    mcpa = MarkupControlPanelAdapter(portal)
    mcpa.set_wiki_enabled_types(('Page',))	
    logger.info("Set default wiki behavior for following content types")
    logger.info(mcpa.get_wiki_enabled_types())

def configureSiteTitle(portal,logger):
    if portal.title.lower() == "site" or portal.title.lower()== "plone site":
        portal.title = "cyn.in site"
        portal.description = "Instant Collaboration"
        logger.info("Configured Site Title and Description.")
    else:
        logger.info("Site title has already been changed, so NOT changing site title or description.")

def addGroups(context,logger):
    portalgroups = getToolByName(context.getSite(), "portal_groups")
    if portalgroups is not None:
        
        currgroups = portalgroups.listGroups()
        for groupname in newgroups:
            if [g for g in currgroups if g.id == groupname] == []:
                portalgroups.addGroup(groupname,(),() )
                if groupname == siteadmingroup:
                    sag = portalgroups.getGroupById(siteadmingroup)
                    sagroles = sag.getRoles()
                    if "Manager" not in sagroles:
                        sagroles.append("Manager")
                        portalgroups.editGroup(siteadmingroup,sagroles, groups=())
                        sagdebug = portalgroups.getGroupById(siteadmingroup)
                        logger.info("SiteAdmin Roles: %s" % sagdebug.getRoles())
                logger.info("Created new group: %s" % groupname)
        
        #Create internal group
        if "internal" not in currgroups: #check if internal group exists
            portalgroups.addGroup("internal",(),() ) #add if it doesn't exist
        sag = portalgroups.getGroupById("internal") #get the group object
        for groupname in newgroups: 
            if "%suser" % groupname not in sag.getGroups():  #if any of our new groups is not already there in internal's groups
                portalgroups.addPrincipalToGroup("%suser" % groupname,sag.id)  #add it

    else:
        logger.info("Could not get group administration tool, something is DRASTICALLY wrong, giving up trying to add groups.")

def setSpacesWorkflowPolicy(sattr,logger,inpolicy=SPACE_PLACEFUL_WORKFLOW_POLICY,belowpolicy=PLACEFUL_WORKFLOW_POLICY):
    placeful_workflow = getToolByName(sattr, 'portal_placeful_workflow')
    try:
        config = placeful_workflow.getWorkflowPolicyConfig(sattr)
    except AttributeError:
        sattr.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(sattr)

    if config is None:
        sattr.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(sattr)
        config.setPolicyIn(policy=inpolicy)
        config.setPolicyBelow(policy=belowpolicy)
        logger.info("set Space: %s workflow policy to %s", (sattr.title, inpolicy))
        logger.info("Set Space: %s BELOW workflow policy to %s" % (sattr.title, belowpolicy))

    if config.getPolicyIn() == None:
        config.setPolicyIn(policy=inpolicy)
        logger.info("Set Space: %s workflow policy to %s" % (sattr.title, inpolicy))
    elif config.getPolicyIn() <> None: ### XXX: Not checking current workflow policy to enable hard coded workflow (DKG)
        config.setPolicyIn(policy=inpolicy)
        logger.info("Set Space: %s workflow policy to %s" % (sattr.title, inpolicy))

    if config.getPolicyBelow() == None:
        config.setPolicyBelow(policy=belowpolicy)
        logger.info("Set Space: %s BELOW workflow policy to %s" % (sattr.title, belowpolicy))
    elif config.getPolicyBelow() <> None : ###and config.getPolicyBelow().workflow_policy != PLACEFUL_WORKFLOW_POLICY  ##XXX: Force setting the below workflow even if it is set so that all spaces follow the default content workflow, at least on site policy install (DKG)
        config.setPolicyBelow(policy=belowpolicy)
        logger.info("Set Space: %s BELOW workflow policy to %s" % (sattr.title, belowpolicy))


def setSpaceUsers(portal, space,groupname):
    """ Sets the users of the space as per our strategy
    Steps:
    1. Get existing user role settings for the space
    2. If the space is new, there will be no userrole settings for the space, so we can proceed to add
    3. If there are already existing settings, then we have to only add the userrole settings that are there, and not remove any
    
    """
    #Step 1: Get existing roles
    #XXX: Ignored for now, will patch up to check current users later. (DKG)
    acl = getattr(portal,'acl_users')
    
    local_roles = acl._getLocalRolesForDisplay(space)
    #local roles list format: name, roles, rtype, rid in local_roles
    
    ##Step 3: Set roles as per schema:
    #1. user 1,2,3 will be only viewers
    #2. user 4,5,6 will be space members
    #3. user 7,8,9 will be space managers
    #4. user 10 will have no access on the space
    
    #space viewer access:
    viewer_access = ('Reader',)
    
    #space member access:
    member_access = ('Contributor',)
    
    #space manager access:
    manager_access = ('Contributor','Editor')
    
    userlist = []
    for i in range(1,11):
        userlist.append("%s%s" % (groupname.lower(),i))
        
    space.manage_setLocalRoles(userlist[0], list(viewer_access))    
    space.manage_setLocalRoles(userlist[1], list(viewer_access))    
    space.manage_setLocalRoles(userlist[2], list(viewer_access))    
    space.manage_setLocalRoles(userlist[3], list(member_access))    
    space.manage_setLocalRoles(userlist[4], list(member_access))    
    space.manage_setLocalRoles(userlist[5], list(member_access))    
    space.manage_setLocalRoles(userlist[6], list(manager_access))    
    space.manage_setLocalRoles(userlist[7], list(manager_access))    
    space.manage_setLocalRoles(userlist[8], list(manager_access))    
    #context.manage_setLocalRoles(userlist[9], list(new_roles))    <-- 10th user has no access
    

def addUsers(context,logger):
    membership = getToolByName(context.getSite(), 'portal_membership')
    portalgroups = getToolByName(context.getSite(), "portal_groups")
    membership.addMember(siteadmin, siteadminpass, ('Member','Authenticated',), ())
    portalgroups.addPrincipalToGroup(siteadmin,siteadmingroup)
    
    logger.info("Created SiteAdmin=> Login: %s, Password: %s" % (siteadmin, siteadminpass))
    #Add test users, comment below lines for production
    if createtestusers:
        for ngname in newgroups:
            for i in range(1,11):                
                username = '%s%s' % (ngname.lower(),i)
                membership.addMember(username, testuserpass, ("Authenticated","Member",), ())
                portalgroups.addPrincipalToGroup(username,ngname)
                logger.info("Created Test User=> Login: %s, Password: %s, Group: %s" % (username,testuserpass,ngname))

def setupSiteTabs(context,logger):
    portal = context.getSite()
    
    # Disable an option that generates tabs for all items created at the root level.
    portal_properties=getToolByName(portal, 'portal_properties')
    
    portal_properties.site_properties.manage_changeProperties(disable_folder_sections=True)
    logger.info("Disabling an option that generates tabs for all items created at the root level.")
    logger.info(portal_properties.site_properties.disable_folder_sections)

    logger.info("Done with setupSiteTabs")

def configureCMFNotification(portal,logger):
    
    ntool = getToolByName(portal, NTOOL_ID)
    changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
    
    if not ntool.isExtraSubscriptionsEnabled():
        changeProperty('extra_subscriptions_enabled',True)
    #enable notification on Item creation
    
    changeProperty('item_creation_notification_enabled', True)
    changeProperty('on_item_creation_mail_template',['* :: string:creation_mail_notification'])
    logger.info("On Item Creation Notification has been enabled.")
    
    #enable notification on Item modification
    changeProperty('item_modification_notification_enabled', True)
    changeProperty('on_item_modification_mail_template',['* :: string:modification_mail_notification'])
    logger.info("On Item Modification Notification has been enabled.")
    
    #enable notification on Work Flow Transition
    changeProperty('wf_transition_notification_enabled', True)
    changeProperty('on_wf_transition_mail_template',['* :: string:workflow_mail_notification'])
    logger.info("On Workflow transition Notification has been enabled.")
    
    #enable notification on Discussion Item Creation
    changeProperty('discussion_item_creation_notification_enabled',True)
    changeProperty('on_discussion_item_creation_mail_template',['* :: string:discussion_mail_notification'])
    logger.info("On Discussion Item Creation Notification has been enabled.")
    

def configureMailHost(portal,logger):
    try:
        mailHost = getattr(portal,'MailHost')
    
        if mailhostconfiguration["configure"]:
            logger.info("Starting Mail Configuration changes")
            if mailHost.smtp_host == '':
                mailHost.smtp_host = mailhostconfiguration["smtphost"]
                logger.info(mailHost.smtp_host)
            if mailHost.smtp_port == None:
                mailHost.smtp_port = mailhostconfiguration["smtpport"]
                logger.info(mailHost.smtp_port)
            if portal.email_from_name == '':
                portal.email_from_name = mailhostconfiguration["fromemailname"]
                logger.info(portal.email_from_name)
            if portal.email_from_address == '':
                portal.email_from_address = mailhostconfiguration["fromemailaddress"]
                logger.info(portal.email_from_address)
            logger.info("Done with Mail Configuration")
    except AttributeError:
        pass        

def configureMaildropHost(portal,logger):
    try:
        mailHost = getattr(portal,'MaildropHost')
    except AttributeError:
        from Products.MaildropHost import MaildropHost
        mailHost = MaildropHost('MaildropHost','MailDropHost')
        portal._setObject('MaildropHost',mailHost)
        mailHost = getattr(portal,'MaildropHost')
    
    if mailhostconfiguration["configure"]:
        logger.info("Starting Maildrop Host Configuration changes")
        if mailHost.smtp_host == '':
            mailHost.smtp_host = mailhostconfiguration["smtphost"]
            logger.info(mailHost.smtp_host)
        if mailHost.smtp_port == None:
            mailHost.smtp_port = mailhostconfiguration["smtpport"]
            logger.info(mailHost.smtp_port)
            

def disableMailHost(portal,logger):
    smtphost = ""
    try:
        mailHost = getattr(portal,'MailHost')       
        
        if mailHost <> None:
            smtphost = mailHost.smtp_host
            mailHost.smtp_host = ""
            logger.info("Disabling configured smtp host before reinstalling : %s" % (smtphost,))
    except AttributeError:
        smtphost = ""
    
    return smtphost

def disableMaildropHost(portal,logger):
    smtphost = ""
    try:
        mailHost = getattr(portal,'MaildropHost')
        if mailHost <> None:
            smtphost = mailHost.smtp_host
            mailHost.smtp_host = ""
            logger.info("Disabling configured smtp host before reinstalling : %s" % (smtphost,))
    except AttributeError:
        smtphost = ""    
    return smtphost

def enableMailHost(portal,logger,smtphost):
    try:
        mailHost = getattr(portal,'MailHost')
        
        if mailHost <> None and smtphost != "":
            mailHost.smtp_host = smtphost
            logger.info("Enabling configured smtp host after reinstallation: %s" % (smtphost,))
    except AttributeError:
        pass
    
def enableMaildropHost(portal,logger,smtphost):
    try:
        mailHost = getattr(portal,'MaildropHost')
        
        if mailHost <> None and smtphost != "":
            mailHost.smtp_host = smtphost
            logger.info("Enabling configured smtp host after reinstallation: %s" % (smtphost,))
    except AttributeError:
        pass

def addRolesToListOfAllowedRolesToAddKeywords(portal,logger):
    portal_properties=getToolByName(portal, 'portal_properties')
    site_prop = portal_properties.site_properties
    for r in ALLOWEDROLESTOADDKEYWORDS:
        if r not in site_prop.allowRolesToAddKeywords:
            site_prop._updateProperty('allowRolesToAddKeywords', site_prop.allowRolesToAddKeywords + (r,))
            logger.info("Added role %s to allow list of roles for adding keywords" % (r,))

def modifyKupuResourceTypes(portal,logger):
    
    kupu_library_tool = getattr(portal,'kupu_library_tool')
    type_map = kupu_library_tool.__of__(portal)
    
    collection_portal_types = type_map.getPortalTypesForResourceType("collection")
    new_portal_types = ('Plone Site','Large Plone Folder','SpacesFolder','StatuslogFolder','SmartviewFolder','ContentRoot','ContentSpace','MemberSpace',) + spacesdefaultaddabletypes
    type_info = [
        dict(resource_type='collection',
            portal_types=new_portal_types),
    ]
    type_map.updateResourceTypes(type_info)
    
    logger.info("Modified collection resourcetype of kupu with these portal types: %s" % (new_portal_types,))
    
    linkable = list(kupu_library_tool.getPortalTypesForResourceType('linkable'))

    # Remove old products linkable types.
    lstremovelinkable = ['Ploneboard','CollageAlias','PloneboardForum','CollageColumn','PloneboardComment','ImageAttachment','FileAttachment','PloneboardConversation','Collage','CollageRow',]
    lstremovelinkable = [li for li in lstremovelinkable if li in linkable] ## Filter down to only the types that actually *need* to be removed
    for rmvlinkable in lstremovelinkable:
        linkable.remove(rmvlinkable)

    for objtype in kupu_linkable_types:
        if objtype not in linkable:
            linkable.append(objtype)
    
    kupu_library_tool.updateResourceTypes(({'resource_type' : 'linkable',
                                   'old_type'      : 'linkable',
                                   'portal_types'  :  linkable},
                                  ))
    logger.info("Modified linkable resourcetype of kupu with these portal types: %s " % (kupu_linkable_types,))
    

def configureKupuToolbar(portal,logger):
    
    kltool = getattr(portal,'kupu_library_tool')
    filteroptions = kltool.getFilterOptions()
    for filteroption in filteroptions:
        if filteroption["id"] in kuputoolbaroptions:    
            filteroption["visible"] = True
    
    kltool.set_toolbar_filters(filteroptions,kltool._global_toolbar_filter)
    
    logger.info("Configured kupu toolbar for these options available %s" % (kuputoolbaroptions,))
    
    if kltool.linkbyuid == False:
        kltool.linkbyuid = True
        logger.info("Configured kupu insert image option to link by uid"    )
    

def removeAnonymousAccessOnMembers(portal,logger):
    try:       
       members = getattr(portal,"Members")
       found = 0
       perms = members.rolesOfPermission('View')
       for perm in perms:
            if perm['name'] == 'Anonymous' and perm['selected'] == 'SELECTED':
                found = 1
            if found == 1:
                break;
                
       if found == 1:
            members.content_status_modify(workflow_action='retract')
            members.content_status_modify(workflow_action='publish')
            logger.info("Modified members access security")
    except:
        pass
    

def migration_steps(portal,logger):
    portal_catalog = getattr(portal,'portal_catalog')

    objects_visible_state = [newObj.getObject() for newObj in portal_catalog(review_state='visible')]    
    for iobj in objects_visible_state:
        iobj.content_status_modify(workflow_action='publish')
        logger.info("Modified state from visible to publish for %s" % (iobj,))
         
    pcontrolpanel = getattr(portal,'portal_controlpanel')
    if pcontrolpanel <> None:
        for action in pcontrolpanel.listActions():
            if action.id.lower() == 'portalskin':
                action.visible = False
            if action.id.lower() == 'zmi':
                action.visible = False

def getViews(portal):
    viewsid = collection_details['id']
    viewstitle = collection_details['title']
    objviews = getOrCreateType(portal,portal,viewsid,"SmartviewFolder")
    
    if objviews <> None and (objviews.title == '' or objviews.title == viewsid):
            objviews.title = viewstitle
            objviews.reindexObject()
    return objviews

def addDefaultViewsForPloneSite(portal,logger):
    portal_types = portal.portal_types
    plonesite = getattr(portal_types,'Plone Site')
    found = False
    for vm in plonesite.view_methods:
        if vm == 'home':
            found = True
        if found:
            break;
    
    if found == False:
        plonesite._updateProperty('view_methods',('home',))
    if found == True:
        plonesite._updateProperty('view_methods',('home',))
    if plonesite.default_view != 'home':
        plonesite._updateProperty('default_view','home')
    if plonesite.getLayout() != 'home':
        plonesite.setLayout('home')
        logger.info("Configured %s as default page for site." % ('home',))
    

def renameDefaultEntries(portal,logger):
    items=[]
    for s in defaulttitles:
        obj = None
        try:
            obj = getattr(portal,s["id"])
        except AttributeError:
            pass
        if obj <> None and obj.portal_type == s["type"] and obj.title == "":
            obj.title = s["title"]
            obj.description = s["description"]
            obj.reindexObject()
            logger.info("Renamed object : %s" % (obj,))

def addDefaultCategories(portal,logger):
    
    pm = portal.portal_metadata
    objdcmi = pm.DCMI
    if objdcmi <> None:
        objdcmi.updateElementPolicy("Subject","<default>",0,0,"",0,default_categories)
        logger.info("Updated default subjects as %s" % (default_categories,))

def configureKupuStyles(portal,logger):
    kupu_library_tool = getattr(portal,'kupu_library_tool')    
    kupu_library_tool.configure_kupu(table_classnames=kupu_table_styles,parastyles=kupu_paragraph_styles,allowOriginalImageSize=True)
    logger.info("Paragraph styles are configured with new styles : %s" % (kupu_paragraph_styles,))

def update_placeful_workflow_policies(portal,name,logger):
    placeful_workflow = getToolByName(portal,'portal_placeful_workflow',None)
    workflowtypes = spacecontentworkflowtypes
    if placeful_workflow is None:
        logger.info("Cannot install placeful workflow policy - CMFPlacefulWorkflow not available")
    elif name in placeful_workflow.objectIds():
        found = False
        policy = placeful_workflow.getWorkflowPolicyById(name)
        if name == 'ubify_user_spaces_folder_workflow':
            workflowtypes = workflowtypes + ('SpacesFolder','RecycleBin',)
            found = True
        if name == 'ubify_user_private_workflow':
            workflowtypes = workflowtypes + ('SpacesFolder','RecycleBin','StatuslogItem',)
            found = True
        if name == 'ubify_recyclebin_workflow':
            workflowtypes = workflowtypes + ('SpacesFolder','RecycleBin','StatuslogItem','ContentSpace','ContentRoot','MemberSpace')
            found = True
        if found == True:
            policy.setChainForPortalTypes((workflowtypes), name)            
            logger.info("Updated workflow policy %s" % name)
    else:
        logger.info("Workflow policy %s already installed" % name)
        

def add_placeful_workflow_policy_for_name(portal,name,title,logger):
    placeful_workflow = getToolByName(portal, 'portal_placeful_workflow', None)
    workflowtypes = spacecontentworkflowtypes
    if placeful_workflow is None:
        logger.info("Cannot install placeful workflow policy - CMFPlacefulWorkflow not available")
    elif name not in placeful_workflow.objectIds():
        placeful_workflow.manage_addWorkflowPolicy(name, 
                                                   duplicate_id='portal_workflow')
        policy = placeful_workflow.getWorkflowPolicyById(name)
        policy.setTitle(title)
        policy.setDefaultChain((name,))
        if name in ('ubify_user_spaces_folder_workflow','ubify_user_private_workflow','ubify_recyclebin_workflow'):
            workflowtypes = workflowtypes + ('SpacesFolder','RecycleBin',)
        if name in ('ubify_user_private_workflow','ubify_recyclebin_workflow'):
            workflowtypes = workflowtypes + ('StatuslogItem',)
        if name in ('ubify_recyclebin_workflow'):
            workflowtypes = workflowtypes + ('ContentSpace','ContentRoot','MemberSpace',)
        policy.setChainForPortalTypes((workflowtypes), name)        
        logger.info("Installed workflow policy %s" % name)
    elif name in placeful_workflow.objectIds():
        update_placeful_workflow_policies(portal,name,logger)
    else:
        logger.info("Workflow policy %s already installed" % name)
        


def add_placeful_workflow_policy(portal,logger):
    """Add the placeful workflow policy used by Spaces.
    """
    placeful_workflow = getToolByName(portal, 'portal_placeful_workflow', None)
    
    add_placeful_workflow_policy_for_name(portal,GLOBAL_RECYCLEBIN_POLICY,'Global Recyclebin Workflow',logger)
    

def setRecycleBin(portal,logger):
    from ubify.recyclebin.utils import getGlobalRecycleBin
    getGlobalRecycleBin(portal)
    logger.info("Created Global Recycle Bin for cyn.in site.")

def addRecyleBinToUsePortalFactory(portal,logger):
    factory = getToolByName(portal, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    for t in ('RecycleBin',):
        if t not in types:
            types.append(t)
            
    factory.manage_setPortalFactoryTypes(listOfTypeIds=types)
    logger.info("Added RecycleBin to the list of types for which portal_factory should be used for object creation.")

def allowembedtag(portal,logger):
    from plone.app.controlpanel.filter import FilterControlPanelAdapter
    objAdapter = FilterControlPanelAdapter(portal)
    nastytags = objAdapter.nasty_tags    

    for t in ['object','embed',]:
        try:
            if nastytags.index(t) >= 0:
                nastytags.remove(t)
        except ValueError:
            pass    # do nothing if tag doesn't exist.
            
    objAdapter.nasty_tags = nastytags
    
    strippedtags = objAdapter.stripped_tags
    
    for t in ['object',]:
        try:
            if strippedtags.index(t) >= 0:
                strippedtags.remove(t)
        except ValueError:
            pass    # do nothing if tag doesn't exist.
            
    objAdapter.stripped_tags = strippedtags
    
    customtags = objAdapter.custom_tags
    
    for t in ['object','embed',]:
        try:
            if customtags.index(t) < 0:
                customtags.append(t)
        except ValueError:
            customtags.append(t)
            
    objAdapter.custom_tags = customtags
    

def replaceCatalog(portal):
    import Acquisition
    from ubify.policy import tool
    
    catalog = getToolByName(portal, 'portal_catalog')
    if not isinstance(Acquisition.aq_base(catalog), tool.CatalogTool):
        catalog.__class__ = tool.CatalogTool
        
def setupContentRoot(portal,logger):
    from migration.onetimeinstall import setupContentRoot
    return setupContentRoot(portal)

def setAbortVersioningOfLargeFiles(portal,logger):
    try:        
        portal_modifier = getattr(portal,'portal_modifier')
        abortversioningobj = getattr(portal_modifier,'AbortVersioningOfLargeFilesAndImages')
        if abortversioningobj <> None:
            abortversioningobj.edit(enabled='True',condition="python: portal_type in ('Image','File','Video','Audio')")
            logger.info("Modified AbortVersioningOfLargeFilesAndImages Condition")
    except AttributeError:
        pass
    
    

def importVarious(context):
    """Miscellanous steps import handle
    """
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('ubify.policy_various.txt') is None:
        return

    portal = context.getSite()
    
    from Products.GenericSetup.context import Logger,SetupEnviron
    obj = SetupEnviron()
    logger = obj.getLogger("ubify.policy")
    
    replaceCatalog(portal)
    old_smtphost = disableMailHost(portal,logger)#<-- Do this first so that reinstallation will not fire any notifications if any
    oldmdh_smtphost = disableMaildropHost(portal,logger)
    
    configureSiteTitle(portal,logger)
    configureContentTypes(portal,logger)
    setup_folders(portal,logger)
    setVersionedTypes(portal,logger)
    setAbortVersioningOfLargeFiles(portal,logger)
    
    enable_wikitype(portal,logger)
    setupSiteTabs(context,logger)
    addGroups(context,logger)        
    addUsers(context,logger)
    
    #creating new content root item at site root
    setupContentRoot(portal,logger)
    
    configureCMFNotification(portal,logger)
    addRolesToListOfAllowedRolesToAddKeywords(portal,logger)
    modifyKupuResourceTypes(portal,logger)
    configureKupuToolbar(portal,logger)
    allowembedtag(portal,logger)
    configureKupuStyles(portal,logger)
    
    add_placeful_workflow_policy(portal,logger)    
    removeAnonymousAccessOnMembers(portal,logger)
    getViews(portal)
    
    addRecyleBinToUsePortalFactory(portal,logger)
    setRecycleBin(portal,logger)
    
    addDefaultViewsForPloneSite(portal,logger)
    renameDefaultEntries(portal,logger)
    
    migration_steps(portal,logger)
    
    startMigration(context,logger)       #<-- Migration step need to be last step before enabling MailHost    
    updateWorkflowSecurity(portal,logger)
    
    configureMailHost(portal,logger)
    configureMaildropHost(portal,logger)
    enableMaildropHost(portal,logger,oldmdh_smtphost)    
    enableMailHost(portal,logger,old_smtphost) #<-- Do this last so that mail smtp host configured before reinstallation will be maintained.
    
