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
import transaction
from StringIO import StringIO
from onetimeinstall import getOrCreateType
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from ubify.policy.config import contentroot_details
from ubify.policy.config import spacesdefaultaddablenonfolderishtypes
from zope.component.interfaces import ComponentLookupError

def getCurrentUserid(portal):
    currentuserid = getSecurityManager().getUser().getId()
    return currentuserid

def impersonateWithObjectOwner(object):    
    currentOwner = object.getOwner()
    newSecurityManager(None,currentOwner)
    
def impersonateAdminUser(portal):
    adminUser = portal.getParentNode().acl_users.getUserById('admin')
    newSecurityManager(None,adminUser)
    
def impersonateSiteadmin(portal):
    siteadminUser = portal.acl_users.getUserById('siteadmin')
    newSecurityManager(None,siteadminUser)
    
def impersonateOwner(portal,object):
    #get owner of an object
    impersonateWithObjectOwner(object)
    if getSecurityManager().getUser().getId() is None:
        impersonateSiteadmin(portal)
        if getSecurityManager().getUser().getId() is None:
            impersonateAdminUser(portal)
            
def getRootObject(portal):
    id = contentroot_details['id']
    objRoot = None
    
    objRoot = getOrCreateType(portal,portal,id,"ContentRoot")
    return objRoot

def manage_copyProperties(old_object,new_object,logger):
    lstCopyableProperties = ['modifiedby','modifiers','lastchangedate','lastchangeaction','lastchangeperformer']
    logger.info("Copying properties started")
    logger.info("Properties for old object: %s" % (old_object.propertyItems(),))
    
    for prop in lstCopyableProperties:
        if old_object.hasProperty(prop):
            prop_value = old_object.getProperty(prop)
            prop_type = old_object.getPropertyType(prop)
            if new_object.hasProperty(prop):
                new_object._updateProperty(prop,prop_value)
            else:
                new_object.manage_addProperty(prop,prop_value,prop_type)
                
    new_object.reindexObject()
    logger.info("Properties for new object: %s" % (new_object.propertyItems(),))
    
    logger.info("Done with Copying properties")
    
def manage_createdDateTime(old_object,new_object,logger):    
    if old_object.created() <> None:
        new_object.setCreationDate(old_object.created())
        new_object.reindexObject()
        logger.info("old creation date for space %s is %s" % (old_object.Title(), old_object.created(),))
        logger.info("new creation date for space %s is %s" % (new_object.Title(), new_object.created(),))
        
def manage_modifiedDateTime(old_object,new_object,logger): 
    if old_object.modified() <> None:
        new_object.setModificationDate(old_object.modified())
        new_object.reindexObject()
        logger.info("old modification date for space %s is %s" % (old_object.Title(), old_object.modified(),))
        logger.info("new modification date for space %s is %s" % (new_object.Title(), new_object.modified(),))

def manage_workflows(portal,old_space,new_space,logger):    
    placeful_workflow = getToolByName(portal, 'portal_placeful_workflow')
    try:
        old_config = placeful_workflow.getWorkflowPolicyConfig(old_space)
        new_config = placeful_workflow.getWorkflowPolicyConfig(new_space)
    except:
        pass
    
    old_policyin = None
    old_policybelow = None
    if old_config <> None :
        old_policyin = old_config.getPolicyIn()
        old_policybelow = old_config.getPolicyBelow()
    
    bFlag = False
    
    if new_config <> None:
        if old_policyin <> None:
            if new_config.getPolicyIn() <> None and new_config.getPolicyIn() <> old_policyin:
                new_config.setPolicyIn(policy=old_policyin.getId())
                bFlag = True
                logger.info("Setting at policy for space %s to %s" % (new_space.Title(),old_policyin.getId()))
        
        if old_policybelow <> None:
            if new_config.getPolicyBelow() <> None and new_config.getPolicyBelow() <> old_policybelow:                
                new_config.setPolicyBelow(policy=old_policybelow.getId())
                bFlag = True
                logger.info("Setting below policy for space %s to %s" % (new_space.Title(),old_policybelow.getId()))
        
    if bFlag:
        new_space.reindexObject()
        transaction.savepoint()
    
def replicate_spaceToNewLocation(portal,target,old_space,logger):
    o = old_space
    
    #impersonate owner of the space
    logger.info("impersonating owner of space: %s" % (o.Title(),))
    impersonateOwner(portal,o)
    logger.info("impersonated user: %s" % (getCurrentUserid(portal),))
    #create space at target location with same title and description with owner impersonation
    
    old_spaceid = o.getId()
    old_spacetitle = o.title
    old_spacedescription = o.description
    
    try:
        o_newspace = getOrCreateType(portal,target,old_spaceid,"ContentSpace")
    except TypeError, v:
        pass
    
    o_newspace.title = old_spacetitle
    o_newspace.setDescription(old_spacedescription)
    
    manage_createdDateTime(o,o_newspace,logger)
    o_newspace.reindexObject()
    
    #set local permissions on newly created object same as old object
    #assign inheritance property first.
    try:
        o_newspace.__ac_local_roles_block__ = o.__ac_local_roles_block__
    except AttributeError:
        pass
    #assign local roles
    o_newspace.__ac_local_roles__ = o.__ac_local_roles__
    
    transaction.savepoint()
    impersonateAdminUser(portal)
    return o_newspace
    
def has_innerspace(portal,sourcespace):
    
    ct = getToolByName(portal,'portal_catalog')
    if sourcespace <> None:
        strPath = sourcespace.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL,'depth': 1},'portal_type':'Space'}
        
        if len(ct(query)) > 0:
            return True
        else:
            return False


def move_all_items_totarget(portal,sourcespace,targetspace,logger):
    
    ct = getToolByName(portal,'portal_catalog')
    logger.info("Moving items from %s to %s" % (sourcespace,targetspace,))
    
    if sourcespace <> None:
        #impersonate owner of the space
        #print >> out, "impersonating owner of space: %s" % (sourcespace.Title(),)
        #impersonateOwner(portal,sourcespace)
        
        strPath = sourcespace.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL},'portal_type':spacesdefaultaddablenonfolderishtypes}
        objects = [b.getObject() for b in ct(query)]
        
        logger.info("Moving %s items from space : %s" % (len(objects), sourcespace,))
        
        for o in objects:
            
            if callable(o.id):
                o_id = o.id()
            else:
                o_id = o.id
            try:
                
                from plone.locking.interfaces import ILockable
                lockable = ILockable(o)
                was_locked = False
                if lockable.locked():
                    was_locked = True
                    lockable.unlock()
                  
                parentobject = o.getParentNode()
                cb = parentobject.manage_cutObjects(ids=[o_id])
                targetspace.manage_pasteObjects(cb)
                
                if was_locked:
                    lockable.lock()
                    
                transaction.savepoint()
            except ComponentLookupError:
                pass
            
        #impersonateAdminUser(portal)
        
        query1 = query = {'path': {'query': "/".join(targetspace.getPhysicalPath()),'depth':1},'portal_type':spacesdefaultaddablenonfolderishtypes}
        movedobjects = ct(query1)
        logger.info("Moved %s items to space : %s" % (len(movedobjects), targetspace,))
        

def replicate_innerspaces(portal,sourcespace,targetspace,logger):
    
    ct = getToolByName(portal,'portal_catalog')
    logger.info("Checking for inner spaces at location of space: %s" % (sourcespace.title,))
    
    if sourcespace <> None:
        strPath = sourcespace.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL,'depth': 1},'portal_type':'Space'}
        objects = [b.getObject() for b in ct(query)]
        
        for o in objects:
            
            new_space = replicate_spaceToNewLocation(portal,targetspace,o,logger)
            manage_workflows(portal,o,new_space,logger)
            if has_innerspace(portal,o):
                replicate_innerspaces(portal,o,new_space,logger)
            
            #move all items at this location to new location
            move_all_items_totarget(portal,o,new_space,logger)                
            
            
            impersonateOwner(portal,o)
            #set it at end of execution
            #set properties on newly created object same as old object
            manage_copyProperties(o,new_space,logger)
            manage_modifiedDateTime(o,new_space,logger)
            
            impersonateAdminUser(portal)
    

def spaces_data_migration(portal,logger):
    
    logger.info("Migrating all spaces.")
    ct = getToolByName(portal,'portal_catalog')        
    spaces = None
    try:
        spaces = getToolByName(portal,'spaces')
        if spaces.portal_type != 'SpacesFolder':
            spaces = None
    except AttributeError:
        pass
        
    if spaces <> None:
        strPath = spaces.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL,'depth': 1},'portal_type':'Space'}
        objects = [b.getObject() for b in ct(query)]
        
        for o in objects:
            objRoot = getRootObject(portal)
            new_space = replicate_spaceToNewLocation(portal,objRoot,o,logger)
            manage_workflows(portal,o,new_space,logger)
            if has_innerspace(portal,o):
                replicate_innerspaces(portal,o,new_space,logger)
            
            #move all items at this location to new location
            move_all_items_totarget(portal,o,new_space,logger)
            
            impersonateOwner(portal,o)
            #set it at end of execution
            #set properties on newly created object same as old object
            manage_copyProperties(o,new_space,logger)
            manage_modifiedDateTime(o,new_space,logger)
            
            impersonateAdminUser(portal)

        o = getRootObject(portal)
        strRootPath = ''
        if o:
            strRootPath = "/".join(o.getPhysicalPath())
        oldspacequery = {'path':{'query':strURL},'portal_type':'Space'}
        newspacequery = {'path':{'query':strRootPath},'portal_type':'ContentSpace'}
        
        oldspaceresult = ct(oldspacequery)
        newspaceresult = ct(newspacequery)
        
        logger.info("Old space count: %s" % len(oldspaceresult))
        logger.info("new space count: %s" % len(newspaceresult))
        
        impersonateAdminUser(portal)
        if len(objects) > 0:
            logger.info("Rebuilding catalog...")
            ct.manage_catalogRebuild()
            updateWorkflowSecurity(portal,logger)
    
def remove_spacesobject_fromsite(portal,logger):
    from plone.app.linkintegrity.interfaces import ILinkIntegrityNotificationException
    portal_properties=getToolByName(portal, 'portal_properties')
    is_link_integrity = portal_properties.site_properties.enable_link_integrity_checks
    if is_link_integrity:
        portal_properties.site_properties.manage_changeProperties(enable_link_integrity_checks=False)
    
    spaces = None
    try:
        spaces = getToolByName(portal,'spaces')
        if spaces.portal_type != 'SpacesFolder':
            spaces = None
    except AttributeError:
        pass
    
    spacesid = 'spaces'
    
    try:
        if spaces <> None:
            if callable(spaces.id):
                o_id = spaces.id()
            else:
                o_id = spaces.id
            
            spacesid = o_id
            
            from plone.locking.interfaces import ILockable
            lockable = ILockable(spaces)
            was_locked = False
            if lockable.locked():
                was_locked = True
                lockable.unlock()
            
            portal.manage_delObjects(ids=[o_id])
            logger.info("Deleted spaces object from site.")
            transaction.savepoint()
    except ILinkIntegrityNotificationException:
        pass
        
    recyclebin = getToolByName(portal,'recyclebin')
    
    if recyclebin <> None:
        
        try:
            objspaces = getattr(portal,spacesid)
            if objspaces.portal_type == 'SpacesFolder':
                from plone.locking.interfaces import ILockable
                lockable = ILockable(objspaces)
                was_locked = False
                if lockable.locked():
                    was_locked = True
                    lockable.unlock()
                
                recyclebin.manage_delObjects(ids=[spacesid])
                logger.info("Deleting spaces object from global recyclebin.")
        except AttributeError:
            pass
        
    if is_link_integrity:
        portal_properties.site_properties.manage_changeProperties(enable_link_integrity_checks=True)

def get_members_contentspace(portal,logger):
    objRoot = getRootObject(portal)
    memberspace = None
    if objRoot <> None:
        memberspace = getOrCreateType(portal,objRoot,'memberspaces',"ContentSpace")
        if memberspace.title == '':
            memberspace.title = 'Members Spaces'
        
        memberspace.reindexObject()
    return memberspace

def move_all_member_items_to_newspace(portal,membersspaceatroot,memberfolder,logger):
    #create new space at memberspaces for memberfolder
    
    impersonateOwner(portal,memberfolder)
    
    target_memberspace = getOrCreateType(portal,membersspaceatroot,memberfolder.getId(),"ContentSpace")
    if target_memberspace.title == '':
        target_memberspace.title = memberfolder.Title()
        target_memberspace.reindexObject()
    
    if target_memberspace <> None:
        logger.info("Created member username space: %s " % (target_memberspace.getId()))
    
    #get all items from memberfolder from each space.
    ct = getToolByName(portal,'portal_catalog')    
    strURL = "/".join(memberfolder.getPhysicalPath())
    query = {'path':{'query':strURL},'portal_type':'Space'}
    objMemSpaces = [b.getObject() for b in ct(query)]
    
    for oMS in objMemSpaces:
        move_all_items_totarget(portal,oMS,target_memberspace,logger)
        
    impersonateAdminUser(portal)
    
    
def delete_unwanted_objects_from_memberfolder(portal,memberfolder,logger):
    ct = getToolByName(portal,'portal_catalog')    
    strURL = "/".join(memberfolder.getPhysicalPath())
    query = {'path':{'query':strURL},'portal_type':('Space','RecycleBin')}
    objMemSpaces = [b.getObject() for b in ct(query)]
    
    for o in objMemSpaces:
        
        if callable(o.id):
            o_id = o.id()
        else:
            o_id = o.id        
        try:
                
            from plone.locking.interfaces import ILockable
            lockable = ILockable(o)
            was_locked = False
            if lockable.locked():
                was_locked = True
                lockable.unlock()
              
            parentItem = o.getParentNode()
            parentItem.manage_delObjects(ids=[o_id])   
            
            transaction.savepoint()
        except ComponentLookupError:
            pass
        
        logger.info("Deleted %s object from %s member folder." % (o_id, memberfolder.getId(),))
        transaction.savepoint()

def migrateFolderToMemberSpace(portal,memberfolder,logger):
    
    from ubify.coretypes.content import MemberSpace
    new_base_folder = {          
        'MemberSpace' : MemberSpace,
        }
    ct = getToolByName(portal,'portal_catalog')    
    strURL = "/".join(memberfolder.getPhysicalPath())
    query = {'path':{'query':strURL},'portal_type':('StatuslogItem',)}
    statusmessages = [b.getObject() for b in ct(query)]
    
    logger.info("Count of status messages for %s are : %s" % (memberfolder.Title(),len(statusmessages),))
    if memberfolder <> None:
        from plone.locking.interfaces import ILockable
        lockable = ILockable(memberfolder)
        was_locked = False
        if lockable.locked():
            was_locked = True
            lockable.unlock()
            
        parent_member = memberfolder.getParentNode()
        #rename old user folder and create new memberspace object and move status log items to
        #newly created userfolder and Delete old folder.
        old_id = memberfolder.getId()
        new_id = old_id + '_old'
        try:
            parent_member.manage_renameObject(old_id,new_id)
        except ComponentLookupError:
            pass
        
        impersonateOwner(portal,memberfolder)
        
        new_memberfolder = getOrCreateType(portal,parent_member,old_id,"MemberSpace")
        
        if new_memberfolder <> None and new_memberfolder.title == '':
            new_memberfolder.title = memberfolder.Title()
            new_memberfolder.reindexObject()
            
        impersonateAdminUser(portal)
        
        for message in statusmessages:           
            
            if callable(message.id):
                o_id = message.id()
            else:
                o_id = message.id
            try:
                
                from plone.locking.interfaces import ILockable
                lockable = ILockable(message)
                was_locked = False
                if lockable.locked():
                    was_locked = True
                    lockable.unlock()
                  
                parentItem = message.getParentNode()
            
                cb = parentItem.manage_cutObjects(ids = [o_id])
                new_memberfolder.manage_pasteObjects(cb)
                
                if was_locked:
                    lockable.lock()
                    
                transaction.savepoint()
            except ComponentLookupError:
                pass
            
        
        #delete statuslog folder
        query1 = {'path':{'query':"/".join(memberfolder.getPhysicalPath())},'portal_type':('StatuslogFolder',)}
        logFolders = [b.getObject() for b in ct(query1)]
        
        for lFolder in logFolders:            
            
            if callable(lFolder.id):
                o_id = lFolder.id()
            else:
                o_id = lFolder.id
                
            try:
                
                from plone.locking.interfaces import ILockable
                lockable = ILockable(lFolder)
                was_locked = False
                if lockable.locked():
                    was_locked = True
                    lockable.unlock()
                  
                parentItem = lFolder.getParentNode()
            
                parentItem.manage_delObjects(ids=[o_id])
                
                if was_locked:
                    lockable.lock()
                    
                transaction.savepoint()
            except ComponentLookupError:
                pass
            logger.info("Deleted member status log folder for %s" % (parentItem.Title(),))
        
        
        
        
        try:
                
            from plone.locking.interfaces import ILockable
            lockable = ILockable(memberfolder)
            was_locked = False
            if lockable.locked():
                was_locked = True
                lockable.unlock()
              
            parentItem = memberfolder.getParentNode()
        
            parentItem.manage_delObjects(ids=[memberfolder.getId()])
            
            if was_locked:
                lockable.lock()
                
            transaction.savepoint()
        except ComponentLookupError:
            pass
        
        new_memberfolder.reindexObject()
        
    statusmessages = [b.getObject() for b in ct(query)]
    logger.info("After Migration Count of status messages for %s are : %s" % (memberfolder.Title(),len(statusmessages),))
    
def members_data_migration(portal,logger):
    logger.info("Migrating Member's data")
    
    ct = getToolByName(portal,'portal_catalog')
    members = getToolByName(portal, 'Members')
    
    if members <> None:
        
        strPath = members.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL, 'depth': 1},'portal_type':'SpacesFolder'}
        objects = [b.getObject() for b in ct(query)]
        
        if len(objects) > 0:
            membersspace = get_members_contentspace(portal,logger)
        
        for o in objects:
            move_all_member_items_to_newspace(portal,membersspace,o,logger)
            delete_unwanted_objects_from_memberfolder(portal,o,logger)
            migrateFolderToMemberSpace(portal,o,logger)
            
        if len(objects) > 0:
            logger.info("Rebuilding catalog...")
            ct.manage_catalogRebuild()
            updateWorkflowSecurity(portal,logger)
    
def fixOwnership(portal,o,logger):
    
    o_id = o.getId()
    try:
        portal.plone_utils.changeOwnershipOf(o,o_id)
        logger.info("Fixed ownership of object : %s" % (o_id,))
    except KeyError:
        pass
    
    
def fix_membersareaforownership(portal,logger):
    ct = getToolByName(portal,'portal_catalog')
    members = getToolByName(portal, 'Members')
    
    if members <> None:
        
        strPath = members.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL, 'depth': 1},'portal_type':'MemberSpace'}
        objects = [b.getObject() for b in ct(query)]
        
        for o in objects:
            fixOwnership(portal,o,logger)
        
        if len(objects) > 0:
            logger.info("Rebuilding catalog...")
            ct.manage_catalogRebuild()
            updateWorkflowSecurity(portal,logger)


def print_previous_spaces(portal,logger):
    ct = getToolByName(portal,'portal_catalog')        
    spaces = None
    try:
        spaces = getToolByName(portal,'spaces')
        if spaces.portal_type != 'SpacesFolder':
            spaces = None
    except AttributeError:
        pass
        
    if spaces <> None:
        strPath = spaces.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL},'portal_type':'Space'}
        
        resbrains = ct(query)
        
        logger.info("Count of spaces at old location : %s" % (len(resbrains),))
        
        query1 = {'path': {'query': strURL},'portal_type':spacesdefaultaddablenonfolderishtypes}
        resitems = ct(query1)
        
        logger.info("Count of items at old location : %s" % (len(resitems),))
        
        query1['portal_type'] = 'Blog Entry'
        logger.info("Blog Entry Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Document'
        logger.info("Document Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Event'
        logger.info("Event Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'File'
        logger.info("File Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Image'
        logger.info("Image Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Link'
        logger.info("Link Count: %s" % (len(ct(query1)),))
        
        
        
        


def print_new_spaces(portal,logger):
    ct = getToolByName(portal,'portal_catalog')
    
    objRoot = getRootObject(portal)
    if objRoot <> None:
        strPath = objRoot.getPhysicalPath()
        strURL = "/".join(strPath)
        query = {'path': {'query': strURL},'portal_type':'ContentSpace'}
        
        resbrains = ct(query)
        
        logger.info("Count of spaces at new location : %s" % (len(resbrains),))
        
        query1 = {'path': {'query': strURL},'portal_type':spacesdefaultaddablenonfolderishtypes}
        resitems = ct(query1)
        
        logger.info("Count of items at new location : %s" % (len(resitems),))
        
        query1['portal_type'] = 'Blog Entry'
        logger.info("Blog Entry Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Document'
        logger.info("Document Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Event'
        logger.info("Event Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'File'
        logger.info("File Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Image'
        logger.info("Image Count: %s" % (len(ct(query1)),))
        
        query1['portal_type'] = 'Link'
        logger.info("Link Count: %s" % (len(ct(query1)),))



def updateWorkflowSecurity(portal,logger):
        out = StringIO()
        pw = getattr(portal,'portal_workflow')    
        count = 0
        if pw <> None:
            count = pw.updateRoleMappings()
            logger.info("Updated workflow role mappings for %s objects" % (count,))
        return out.getvalue()
    


def migrateto21(portal,logger):
    #working code commented timebeing
    
    print_previous_spaces(portal,logger)
    spaces_data_migration(portal,logger)
    print_new_spaces(portal,logger)
    print_previous_spaces(portal,logger)
    members_data_migration(portal,logger)
    
    #end working code    
    remove_spacesobject_fromsite(portal,logger)
    
    fix_membersareaforownership(portal,logger)
    