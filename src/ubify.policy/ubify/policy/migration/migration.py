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
from Products.CMFCore.utils import UniqueObject, getToolByName
import transaction
from StringIO import StringIO
from ubify.coretypes.content import ATDocument
from ubify.coretypes.content import ATFolder
from ubify.coretypes.content import ATTopic
from ubify.coretypes.content import ATImage
from ubify.coretypes.content import ATFile
from ubify.coretypes.content import ATLink
from ubify.coretypes.content import ATEvent
from ubify.coretypes.content import ATNewsItem
from ubify.coretypes.content import LinkDirectory
from ubify.coretypes.content import SpacesFolder

from ubify.spaces.handlers import *
from ubify.policy.migration.onetimeinstall import addDefaultDashboardViews,setup_sitehome_collection_portlets,setup_sitehome_portlets,assignStackerRelatedPortlet
from ubify.policy.migration.onetimeinstall import changeHomePortletsTitles,disable_inlineEditing,remove_navigationportlet,remove_calendarportlet, setchoosertype, configureRatings
from ubify.policy.migration.onetimeinstall import enable_formats_fortextfield,assignCyninNavigation, reorder_contenttyperegistry
from ubify.policy.migration.onetimeinstall import add_custom_site_properties,add_custom_cynin_properties
from ubify.policy.config import contentroot_details
from BTrees.OIBTree import OIBTree
from ubify.cyninv2theme import migrateuserareas

def getInstalledVersion(portal):    
    portal_quickinstaller = getToolByName(portal, 'portal_quickinstaller')
    try:
        objProduct = portal_quickinstaller._getOb('ubify.policy')
        return objProduct.getInstalledVersion()
    except AttributeError:
        return ""

def getFileVersion(portal):
    portal_quickinstaller = getToolByName(portal, 'portal_quickinstaller')
    return portal_quickinstaller.getProductVersion('ubify.policy')

def getCurrentUser(object):
    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl import getSecurityManager
    
    currentOwner = object.getOwner()
    newSecurityManager(None,currentOwner)
    
def getAdminUser(portal):
    from AccessControl.SecurityManagement import noSecurityManager
    from AccessControl.SecurityManagement import newSecurityManager
    adminUser = portal.getParentNode().acl_users.getUserById('admin')
    newSecurityManager(None,adminUser)

def rebuildCatalog(portal):
    ct = getToolByName(portal, 'portal_catalog')
    ct.manage_catalogRebuild()
    
def migrate_to_2_0_4(portal,logger):
    from ubify.coretypes.config import TYPES_TO_MIGRATE
    
    import transaction
    
    new_base = {  
        'LinkBase': LinkDirectory,
        }
    
    def migrateType(self, typename):
        """change the base class of existing instance to be our own one"""    
        ct = getToolByName(self, 'portal_catalog')
        
        objects = [b.getObject() for b in ct(portal_type=typename)]
        
        for o in objects:
            try:
                if o.__class__ != new_base[typename]:
                    o.__class__ = new_base[typename]
                    o._p_changed = 1
                    if typename == 'LinkBase':
                        o.portal_type = 'LinkDirectory'
                    
                    o.reindexObject()
                    #convertObject(o,typename,new_base[typename])
            except AttributeError:
                a = "a" #Empty statement? (dkg)

    def migrateTypes(self, logger, types = TYPES_TO_MIGRATE):
        """call migrateType for all types where we want to have a new base"""    
        for typename in types:
            if new_base.has_key(typename):
                migrateType(self, typename)
                logger.info("migrating %s" % typename )
                
    def convertObject(o,oldtype,newtype):
        if callable(o.id):
            o_id = o.id()
        else:
            o_id = o.id
            
        parent = o.getParentNode()
           
        if newtype.portal_type not in parent.immediatelyAddableTypes:
            return
        if parent.meta_type == oldtype:
            convertObject(parent,oldtype,newtype)            
        
        
        portaltypes = parent.portal_types
        
        portaltypes.constructContent(newtype.portal_type,parent,o_id + '_new',None)
        new_container = parent[o_id + '_new']
        new_container.update(title=o.title)
        
        cb = o.manage_cutObjects(ids=o.objectIds())
        new_container.manage_pasteObjects(cb)
        transaction.savepoint()   
        parent.manage_delObjects(ids=[o_id])
        transaction.savepoint()
        ids=[]
        new_ids=[]
        ids.append(o_id + '_new')
        new_ids.append(o_id)
        parent.manage_renameObjects(ids,new_ids)
        transaction.savepoint()
        
    migrateTypes(portal,logger)

def migrate_to_2_0_4_2(portal,logger):
    cynin_applications_tomigrate = (
        'Gallery',
        'Blog',
        'Wiki',
        'LinkDirectory',
        'FileRepository',
        'Calendar',
        'Folder'
    )
    new_base_folder = {  
        'Folder': ATFolder,
        'SpacesFolder' : SpacesFolder,
        }
    
    def updateWorkflowSecurity(portal,logger):
        pw = getattr(portal,'portal_workflow')    
        count = 0
        if pw <> None:
            count = pw.updateRoleMappings()
            logger.info("Updated workflow role mappings for %s objects" % (count,))
    
    def convertObject(o,oldtype,newtype,ignore=False):
        owner = o.getOwner()
        
        if callable(o.id):
            o_id = o.id()
        else:
            o_id = o.id
            
        parent = o.getParentNode()
        
        if ignore == False:
            if newtype.portal_type not in parent.immediatelyAddableTypes:
                return
            if parent.meta_type == oldtype:
                convertObject(parent,oldtype,newtype)            
        
        portaltypes = parent.portal_types
        
        portaltypes.constructContent(newtype.portal_type,parent,o_id + '_new',None)
        new_container = parent[o_id + '_new']
        new_container.update(title=o.title)
        
        cb = o.manage_cutObjects(ids=o.objectIds())
        new_container.manage_pasteObjects(cb)
        transaction.savepoint()   
        parent.manage_delObjects(ids=[o_id])
        transaction.savepoint()
        ids=[]
        new_ids=[]
        ids.append(o_id + '_new')
        new_ids.append(o_id)
        parent.manage_renameObjects(ids,new_ids)
        transaction.savepoint()
        new_container.changeOwnership(owner)
        
    def migrateApplicationFolders(portal,logger):
        #get all inner applications
        
        ct = getToolByName(portal, 'portal_catalog')
        for type in cynin_applications_tomigrate:
            objects = [b.getObject() for b in ct(portal_type=type)]
            objects.reverse()
            for o in objects:
                parent = o.getParentNode()
                parenttype = parent.portal_type
                try:
                    if parenttype == type and o.__class__ != new_base_folder['Folder']:                                                
                        o.__class__ = new_base_folder['Folder']
                        o.portal_type = 'Folder'
                        o._p_changed = 1
                        
                        o.setConstrainTypesMode(1)
                        o.setImmediatelyAddableTypes(parent.getLocallyAllowedTypes())
                        o.setLocallyAllowedTypes(parent.getLocallyAllowedTypes())
                        o.reindexObject()
                        logger.info("Migrated object of type %s at %s to Folder" % (type,o.absolute_url(),))
                except AttributeError:
                    a = "a" #Empty statement? (dkg)
    
    def migrateUserFoldersForConstrainType(portal,logger):
        ct = getToolByName(portal, 'portal_catalog')
        members = getToolByName(portal,'Members')
        
        if members <> None:
            strPath = members.getPhysicalPath()
            strURL = "/".join(strPath)
            query = {'path': {'query': strURL, 'depth': 1},'Type':'Folder'}
            objects = [b.getObject() for b in ct(query)]
            
            for o in objects:
                from ubify.cyninv2theme import setConstrainsOnMyFolder,setupPlacefulWorkflowOnUser
                #setupPlacefulWorkflowOnUser(o)
                #setConstrainsOnMyFolder(o)
        
    def migrateSpacesForSpaceHomePortletsAssignment(portal,logger):        
        ct = getToolByName(portal, 'portal_catalog')
        ptypes = portal.portal_types
        spacefti = getattr(ptypes,'Space')
        if spacefti <> None:            
            objects = [b.getObject() for b in ct(portal_type= spacefti.id)]            
            
            from ubify.spaces.config import spacemembersportletmanager_name,spacedashboardportletmanager_name
            
            for o in objects:
                assign_space_dashboard(o,None)
                logger.info("Auto assigned portlets to space members manager and applications dashboard manager of space: %s" % (o,)                )
    
    def migrateUsersSpace(portal,logger):
        ct = getToolByName(portal, 'portal_catalog')
        members = getToolByName(portal, 'Members')
        
        if members <> None:
            strPath = members.getPhysicalPath()
            strURL = "/".join(strPath)
            query = {'path': {'query': strURL, 'depth': 1},'Type':'Folder'}
            objects = [b.getObject() for b in ct(query)]
            
            for o in objects:
                if o.__class__ != new_base_folder['SpacesFolder']:                                                
                    o.__class__ = new_base_folder['SpacesFolder']
                    o.portal_type = 'SpacesFolder'
                    o._p_changed = 1
                    
                    if o.getConstrainTypesMode() <> 0:
                        o.setConstrainTypesMode(0)
                    o.reindexObject()
            
            updateWorkflowSecurity(portal,logger)
            
            query = {'path': {'query': strURL, 'depth': 1},'Type':'SpacesFolder'}
            objects = [b.getObject() for b in ct(query)]
            
            for o in objects:
                #import pdb;pdb.set_trace()
                migrateuserareas(o)
                logger.info("Done migration of user's personal space for : %s" % (o))
                
            updateWorkflowSecurity(portal,logger)
    
    def migrateDefaultSmartViewCreationAndHomePortletsAssignment(portal,logger):
        addDefaultDashboardViews(portal,logger)
        setup_sitehome_collection_portlets(portal,logger)
        logger.info("Creation of default smart views and auto assignment of portlets are done.")
        
    migrateApplicationFolders(portal,logger)    
    migrateSpacesForSpaceHomePortletsAssignment(portal,logger)
    migrateDefaultSmartViewCreationAndHomePortletsAssignment(portal,logger)
    migrateUsersSpace(portal,logger)
    
def migrate_to_2_0_5(portal,logger):    
    changeHomePortletsTitles(portal,logger)
    
def migrate_to_2_0_6(portal,logger):
    
    def setupUsersRecycleBin(portal,logger):
        ct = getToolByName(portal, 'portal_catalog')
        members = getToolByName(portal,'Members')
        
        if members <> None:
            strPath = members.getPhysicalPath()
            strURL = "/".join(strPath)
            query = {'path': {'query': strURL, 'depth': 1},'Type':'SpacesFolder'}
            objects = [b.getObject() for b in ct(query)]
            
            for o in objects:
                from ubify.cyninv2theme import setup_users_recyclebin,getCurrentUser,getAdminUser                
                modifiedat = None
                try:
                    modifiedat = o.modified()
                except AttributeError:
                    modifiedat = None
                
                getCurrentUser(o)
                
                from AccessControl import getSecurityManager
                currentuserid = getSecurityManager().getUser().getId()
                if currentuserid is None:
                    getAdminUser(portal)
                    currentuserid = getSecurityManager().getUser().getId()
                
                if currentuserid <> None:
                    setup_users_recyclebin(o)
                    if modifiedat <> None:
                        o.setModificationDate(modifiedat)
                    logger.info("Added Recycle Bin for : %s" % (o.id,))
            logger.info("Rebuilding catalog...")
            ct.manage_catalogRebuild()

    setupUsersRecycleBin(portal,logger)
    
def migrate_to_2_0_7(portal,logger):
    
    def updateSmartViews(portal,logger):
        try:
            from ubify.policy.config import default_sitehome_smartviews
            objviews = getattr(portal,"views")
            for eachview in default_sitehome_smartviews:
                try:
                    sattr = getattr(objviews,eachview["id"])
                    sattr.limitNumber = eachview["limitnumber"]
                    sattr.reindexObject()
                except:
                    logger.info("Unable to set limitnumber for view : %s" % (eachview["id"],))
        except AttributeError:
            logger.info("Unable to update views.")
    
    updateSmartViews(portal,logger)
    
def migrate_to_2_0_7_1(portal,logger):
    
    def updateItemsForlastchangedateparam(portal,logger):
        try:
            ct = getToolByName(portal, 'portal_catalog')
            strPath = portal.getPhysicalPath()
            strURL = "/".join(strPath)
            query = {'path': {'query': strURL, 'depth': -1}}
            objects = [b.getObject() for b in ct(query)]
            
            for b in objects:                
                if b.hasProperty('lastchangedate') == 0:
                    modifiedat = None
                    try:
                        modifiedat = b.modified()
                    except AttributeError:
                        modifiedat = None
                    
                    getCurrentUser(b)
                    
                    from AccessControl import getSecurityManager
                    currentuserid = getSecurityManager().getUser().getId()
                    if currentuserid is None:
                        getAdminUser(portal)
                        currentuserid = getSecurityManager().getUser().getId()
            
                    if currentuserid <> None:                        
                        b.manage_addProperty('lastchangedate',modifiedat,'date')
                        
                        from ubify.coretypes import last_change_action_edit
                        
                        if b.hasProperty('lastchangeaction') == 0:
                            b.manage_addProperty('lastchangeaction',last_change_action_edit,'string')
                        else:
                            b._updateProperty('lastchangeaction',last_change_action_edit)
                        
                        if b.hasProperty('lastchangeperformer') == 0:
                            b.manage_addProperty('lastchangeperformer',currentuserid,'string')
                        else:
                            b._updateProperty('lastchangeperformer',currentuserid)
                            
                        if modifiedat <> None:
                            b.setModificationDate(modifiedat)
                    
                    getAdminUser(portal)
            logger.info("Rebuilding catalog...")
            ct.manage_catalogRebuild()
        except AttributeError:
            pass
    
    assignStackerRelatedPortlet(portal)    
    updateItemsForlastchangedateparam(portal,logger)    
    
def migrate_to_2_1_dev(portal,logger):
    
    def setupUsersStatuslogFolder(portal,logger):
        ct = getToolByName(portal, 'portal_catalog')
        members = getToolByName(portal,'Members')
        
        if members <> None:
            strPath = members.getPhysicalPath()
            strURL = "/".join(strPath)
            query = {'path': {'query': strURL, 'depth': 1},'Type':'SpacesFolder'}
            objects = [b.getObject() for b in ct(query)]
            
            for o in objects:
                from ubify.cyninv2theme import setup_users_statuslogfolder,getCurrentUser,getAdminUser                
                modifiedat = None
                try:
                    modifiedat = o.modified()
                except AttributeError:
                    modifiedat = None
                
                getCurrentUser(o)
                
                from AccessControl import getSecurityManager
                currentuserid = getSecurityManager().getUser().getId()
                if currentuserid is None:
                    getAdminUser(portal)
                    currentuserid = getSecurityManager().getUser().getId()
                
                if currentuserid <> None:
                    setup_users_statuslogfolder(o)
                    if modifiedat <> None:
                        o.setModificationDate(modifiedat)
                    logger.info("Added Status log folder for : %s" % (o.id,))
                    
                getAdminUser(portal)
            logger.info("Rebuilding catalog...")
            ct.manage_catalogRebuild()
            
    def modifyallcommentsview(portal,logger):
        try:
            objViews = getattr(portal,'views')
            if objViews <> None:
                objallcomments = getattr(objViews,'allcomments')
                if objallcomments <> None:
                    critid = getattr(objallcomments,'crit__Type_ATPortalTypeCriterion')
                    if critid <> None:
                        critid.value = ('Message',)
                        objallcomments.reindexObject()
        except AttributeError:
            logger.info("Unable to modify all comments smart view.")
            
    def assignSiteHomePortlets(portal,logger):
        setup_sitehome_portlets(portal,logger)
        logger.info("Auto assignment for site home portlets")
        
    def migrateSpacesForSpaceHomePortletsAssignment(portal,logger):        
        ct = getToolByName(portal, 'portal_catalog')
        ptypes = portal.portal_types
        
        spacefti = getattr(ptypes,'Space')
        if spacefti <> None:            
            objects = [b.getObject() for b in ct(portal_type= spacefti.id)]                        
            from ubify.spaces.config import spacemembersportletmanager_name,spacedashboardportletmanager_name
            
            for o in objects:
                assign_space_dashboard(o,None)
                logger.info("Auto assigned portlets to mindmap manager of space: %s" % (o,)                )
    
    def migrateSpacesForOnlyPublishedState(portal,logger):
        ct = getToolByName(portal,'portal_catalog')
        try:
            spaces = getToolByName(portal,'spaces')
            
            if spaces <> None:
                strPath = spaces.getPhysicalPath()
                strURL = "/".join(strPath)
                query = {'path': {'query': strURL},'Type':'Space','review_state' :('private','project-private')}
                objects = [b.getObject() for b in ct(query)]
                
                for o in objects:
                    o.content_status_modify(workflow_action='publish')
                    logger.info("Modified workflow state for space : %s" % (o,))
        except AttributeError:
            logger.info("Migrate spaces for only published state fails.")
                
    def migrateNestedSpaces(portal,logger):
        
        def checkInnerSpaces(spaces,objSpace,p_catalog,logger):
            strPath = objSpace.getPhysicalPath()
            strURL = "/".join(strPath)
            
            query = {'path':{'query':strURL,'depth':1},'Type':'Space'}
            objSpaces = [b.getObject() for b in p_catalog(query)]
            
            for objS in objSpaces:
                checkInnerSpaces(spaces,objS,p_catalog,logger)
                parentObj = objS.getParentNode()
                if parentObj <> spaces:
                    moveSpace(spaces,objS,parentObj,logger)
        
        def moveSpace(spaces,objSpace,parentSpace,logger):
            #import pdb;pdb.set_trace()
            try:
                from plone.locking.interfaces import ILockable
                lockable = ILockable(objSpace)
                was_locked = False
                if lockable.locked():
                    was_locked = True
                    lockable.unlock()
                
                cb = parentSpace.manage_cutObjects(ids=(objSpace.getId(),))
                spaces.manage_pasteObjects(cb)                           
                
                if was_locked:
                    lockable.lock()
                logger.info("Modified Nested space : %s" % (objSpace,))
            except:                        
                logger.info("Error while moving space : %s" % (objSpace,))
                
        ct = getToolByName(portal,'portal_catalog')        
        try:
            spaces = getToolByName(portal,'spaces')
            
            if spaces <> None:
                strPath = spaces.getPhysicalPath()
                strURL = "/".join(strPath)
                query = {'path': {'query': strURL,'depth': 1},'Type':'Space'}
                objects = [b.getObject() for b in ct(query)]
                
                for o in objects:
                    checkInnerSpaces(spaces,o,ct,logger)
        
        except AttributeError:
            logger.info("Migrate nested spaces fails.")
        
        logger.info("Rebuilding catalog...")
        ct.manage_catalogRebuild()
        
    def migrateUserPublicSpacesContentForOnlyPublishedState(portal,logger):
        ct = getToolByName(portal,'portal_catalog')
        try:
            members = getToolByName(portal,'Members')
            #import pdb;pdb.set_trace()
            if members <> None:
                strPath = members.getPhysicalPath()
                strURL = "/".join(strPath)
                query = {'path': {'query': strURL, 'depth': 1},'portal_type':'SpacesFolder'}
                objects = [b.getObject() for b in ct(query)]
                
                for obj in objects:
                    #retrieve public space
                    alltypes = ('Blog',
                             'Calendar',
                             'FileRepository',
                             'GenericContainer',
                             'Folder',
                             'Gallery',
                             'LinkDirectory',
                             'Topic',
                             'Wiki',
                             'SmartView',
                             'Document',
                             'Event',
                             'File',
                             'Image',
                             'Link',
                             'Blog Entry',
                             )
                    try:
                        publicspace = getattr(obj,'public')
                        if publicspace <> None:
                            #get all objects for this space
                            strpspath = publicspace.getPhysicalPath()
                            strpsURL = "/".join(strpspath)
                            query1 = {'path': {'query': strpsURL},'portal_type':alltypes,'review_state' :('private','project-private')}
                            
                            innerobjects = [b.getObject() for b in ct(query1)]
                            #import pdb;pdb.set_trace()                            
                            for inobj in innerobjects:
                                getCurrentUser(inobj)
                    
                                from AccessControl import getSecurityManager
                                currentuserid = getSecurityManager().getUser().getId()
                                if currentuserid is None:
                                    getAdminUser(portal)
                                    currentuserid = getSecurityManager().getUser().getId()
                                    
                                inobj.content_status_modify(workflow_action='publish')
                                logger.info("Modified workflow state for item : %s" % (inobj,))
                                
                            getAdminUser(portal)
                    except AttributeError:
                        logger.info("unable to find public space for userfolder : %s" % (obj,)                )
        except AttributeError:
            logger.info("Migrate member's public space content for only published state fails.")
            
    def turnOFFNotificationsByDefault(portal,logger):
        from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
        
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
                ntool.manage_changeProperties(**{key: value})
        
        if not ntool.isExtraSubscriptionsEnabled():
            changeProperty('extra_subscriptions_enabled',True)
        
        changeProperty('item_creation_notification_enabled', True)
        changeProperty('on_item_creation_users', [])
        
        changeProperty('item_modification_notification_enabled', True)
        changeProperty('on_item_modification_users', [])
        
        changeProperty('wf_transition_notification_enabled', True)
        changeProperty('on_wf_transition_users',[])
        
        changeProperty('discussion_item_creation_notification_enabled',True)
        changeProperty('on_discussion_item_creation_users',[])
        
        logger.info("Extra subscriptions has been enabled and turned off default notifications to all members.")
    
    def migrateforMembersBTreeFolder(portal,logger):
        try:
            members = getattr(portal,'Members')
            
            if members <> None:
                from BTrees.OOBTree import OOBTree
                from BTrees.OIBTree import OIBTree
                
                keys = members.keys()
                objTree = members._tree
                
                if objTree <> None:
                    objlist = []
                    for eachkey in keys:
                        obj = None
                        try:
                            obj = objTree[eachkey]
                        except KeyError:
                            pass
                        
                        if obj <> None:
                            objlist.append(obj)
                        
                    mti = members._mt_index                    
                    for eachobj in objlist:
                        meta_type = getattr(eachobj,'meta_type',None)
                        if meta_type is not None:
                            id = eachobj.id
                            ids = mti.get(meta_type,None)
                            if ids is None:
                                ids = OIBTree()
                                mti[meta_type] = ids
                            ids[id] = 1
                    
                    for okey,ovalue in mti.items():
                        templist = []
                        for eachkey in ovalue.keys():
                            try:
                                otempobj = objTree[eachkey]
                                if otempobj is None:
                                    templist.append(eachkey)
                                elif otempobj.meta_type <> okey:
                                    templist.append(eachkey)
                            except KeyError:
                                templist.append(eachkey)
                        
                        for tempitem in templist:
                            if ovalue.has_key(tempitem):
                                del ovalue[tempitem]
                        if not ovalue:
                            del mti[okey]
                            
                    logger.info("Done with migrating Members folder for fixing issue.")
        except:
            logger.info("Unable to migrate Members inner index.")
    
    migrateforMembersBTreeFolder(portal,logger)
    setupUsersStatuslogFolder(portal,logger)
    modifyallcommentsview(portal,logger)
    assignSiteHomePortlets(portal,logger)
    migrateSpacesForSpaceHomePortletsAssignment(portal,logger)
    migrateSpacesForOnlyPublishedState(portal,logger)
    
    migrateUserPublicSpacesContentForOnlyPublishedState(portal,logger)
    turnOFFNotificationsByDefault(portal,logger)
    disable_inlineEditing(portal,logger)
    remove_navigationportlet(portal,logger)
    remove_calendarportlet(portal,logger)
    
    from migration21 import migrateto21
    migrateto21(portal,logger)
    

def migrate_to_3_0_dev(portal,logger):
    
    def enableSyndication(portal,obj,logger):
        syn_tool = getToolByName(portal, 'portal_syndication', None)
        if syn_tool is not None:
            if (syn_tool.isSiteSyndicationAllowed() and
                                    not syn_tool.isSyndicationAllowed(obj)):
                syn_tool.enableSyndication(obj)
                logger.info("Enabled syndication for : %s" % (obj.title,))
                
    def enableSyndicationForExistingObjects(portal,logger):
        portal_catalog = getToolByName(portal,"portal_catalog")
        query = {'portal_type':['ContentSpace','MemberSpace','ContentRoot']}
        resbrains = [b.getObject() for b in portal_catalog(query)]
        
        for obj in resbrains:
            enableSyndication(portal,obj,logger)
            
    def modify_allsmartviews(portal,logger):
        from ubify.policy.config import default_sitehome_smartviews
        allcommentblock = [k for k in default_sitehome_smartviews if k['id'] == 'allcomments']
        objviews = None
        try:
            objviews = getattr(portal,"views")
        except AttributeError:
            logger.info("No Advanced view folder found.")
            return
        
        if len(allcommentblock) > 0:
            try:                
                if objviews <> None:                    
                    allcommentsview = getattr(objviews,allcommentblock[0]['id'])
                    if allcommentsview <> None:
                        try:
                            critid = getattr(allcommentsview,'crit__Type_ATPortalTypeCriterion')
                        except AttributeError:
                            critid = sattr.addCriterion(field='Type',criterion_type='ATPortalTypeCriterion')
                        if critid <> None:
                            typecrit = critid
                            typecrit.value = allcommentblock[0]['type']
                            logger.info("Modified all comments view")
                        else:
                            logger.info("Could not create type criteria, critid = %s" % (critid,))
                            
                        allcommentsview.reindexObject()
            except AttributeError:
                pass
            
        for eachview in default_sitehome_smartviews:
            try:
                sattr = getattr(objviews,eachview["id"])
                if sattr <> None:
                    if sattr.id in ("allimages","allblogentries") and sattr.getLayout() != "atct_topic_view":
                        sattr.setLayout("atct_topic_view")
                        logger.info("Modified default view for smart view : %s" % (eachview['id'],))
            except:
                logger.info("No smart view found for id : %s" % (eachview['id'],)                )
    
    def migrateSpacesForSpaceHomePortletsAssignment(portal,logger):        
        ct = getToolByName(portal, 'portal_catalog')
        ptypes = portal.portal_types
        spacefti = getattr(ptypes,'ContentSpace')
        if spacefti <> None:            
            objects = [b.getObject() for b in ct(portal_type= spacefti.id)]            
            
            from ubify.cyninv2theme.browser.cynindashboards import assign_space_dashboard
            
            for o in objects:
                assign_space_dashboard(o,None,True)
                logger.info("Assigned dashboard for space : %s" % (o,)                )
    
    def migratetagsforlowercase(portal,logger):        
        ct = getToolByName(portal,'portal_catalog')
        alltags = ct.uniqueValuesFor('Subject')
        lstmigrationreqdtags = []
        lstmigrationreqdtags = [k for k in alltags if k.lower() != k]
        
        for tag in lstmigrationreqdtags:
            items = ct({'Subject':tag})
            for itm in items:
                o_lastchangedate = None
                o_lastchangeaction = None
                o_lastperformer = None
                o_mdate = None
                o_modifiedby = None
                
                lstlowertags = [k for k in itm.Subject if k.lower() != k]
                
                if len(lstlowertags) > 0:
                    fullitem = itm.getObject()
                    if fullitem <> None:
                        #get all old properties
                        try:
                            o_lastchangedate = fullitem.lastchangedate
                        except AttributeError:
                            o_lastchangedate = None
                            
                        try:
                            o_lastchangeaction = fullitem.lastchangeaction
                        except AttributeError:
                            o_lastchangeaction = None
                            
                        try:
                            o_lastperformer = fullitem.lastchangeperformer
                        except AttributeError:
                            o_lastperformer = None
                            
                        try:
                            o_mdate = fullitem.modified()
                        except AttributeError:
                            o_mdate = None
                            
                        try:
                            o_modifiedby = fullitem.modifiedby
                        except AttributeError:
                            o_modifiedby = None
                            
                        
                        getCurrentUser(fullitem)
                        
                        from AccessControl import getSecurityManager
                        currentuserid = getSecurityManager().getUser().getId()
                        if currentuserid is None:
                            getAdminUser(portal)
                            currentuserid = getSecurityManager().getUser().getId()
                            
                        if currentuserid <> None:
                            old_tags = fullitem.Subject()
                            new_tags = [k.lower() for k in old_tags]
                            fullitem.setSubject(new_tags)
                            
                            try:
                                if o_lastchangedate != None:
                                    fullitem._updateProperty('lastchangedate',o_lastchangedate)                        
                                if o_lastchangeaction != None:
                                    fullitem._updateProperty('lastchangeaction',o_lastchangeaction)
                                if o_lastperformer != None:
                                    fullitem._updateProperty('lastchangeperformer',o_lastperformer)
                                if o_modifiedby != None:
                                    fullitem._updateProperty('modifiedby',o_modifiedby)
                                if o_mdate != None:
                                    fullitem.setModificationDate(o_mdate)
                            except :
                                pass    #catching exception just for not failing this operation due to these steps of migration.
                            
                        getAdminUser(portal)
            
            logger.info("Migration done for tag: %s" % (tag,))

    def removePlacefulWorkflowPolicies(portal,logger):
        placeful_workflow = getToolByName(portal,'portal_placeful_workflow')
        ids = (
                'intranet',
                'old-plone',
                'one-state',
                'simple-publication',
                'ubify_user_spaces_folder_workflow',
                'ubify_user_private_workflow',
                'ubify_user_public_workflow',
                'ubify_publish_spaces_content_workflow',
                'ubify_private_keep_publish',
                'ubify_publish_keep_private',
        )
        if placeful_workflow <> None:
            policies = placeful_workflow.getWorkflowPolicies()
            for pid in ids:
                if pid in placeful_workflow.objectIds():
                    placeful_workflow.manage_delObjects([pid,])
                    logger.info("Removed workflow policy from placeful workflow: %s" % (pid,))
    
    
    def rename_rootObject(portal,logger):
        id = contentroot_details['id']
        oldid = contentroot_details['oldid']
        title = contentroot_details['title']
        oldtitle = contentroot_details['oldtitle']
        
        already_exists = False
        try:            
            obj = getattr(portal,oldid)
            if obj and obj.portal_type == 'ContentRoot':
                already_exists = True
               
            if already_exists:
                try:
                    portal.manage_renameObject(oldid,id)
                except ComponentLookupError,details:
                    pass
                obj = getattr(portal,id)
                if obj.Title().lower() == oldtitle.lower():
                    obj.title = title
                obj.reindexObject()
                logger.info('Renamed object from %s to %s' % (oldid,id,))
        except:
            pass
        
        try:
            if not already_exists:            
                objnew = getattr(portal,id)
                if objnew and objnew.portal_type == 'ContentRoot' and objnew.Title().lower() == oldtitle.lower():                
                    objnew.title = title
                    objnew.reindexObject()
        except:
            pass
    def _cleanupForObject(parent,logger,item=None):
        tree = parent._tree
        mti = parent._mt_index        
        if item:
            fullitem = item.getObject()
            item_id = item.id
            item_meta_type = getattr(fullitem,'meta_type',None)
            if tree.has_key(item_id):
                #fix meta_type if reqd.
                if item_meta_type is not None:
                    ids = mti.get(item_meta_type,None)
                    if ids is None:
                        ids = OIBTree()
                        mti[item_meta_type] = ids
                        ids[item_id] = 1
                    elif not ids.has_key(item_id):
                        ids[item_id] = 1
                    
                    #check in ATFile type
                    fileids = mti.get('ATFile',None)
                    if fileids is not None and fileids.has_key(item_id):
                        del fileids[item_id]
                        if not fileids:
                            del mti['ATFile']
                    
            logger.info("Fixed parent object %s for item %s btree index cleanup" % (parent.id, item.id,))
        else:
            #fix only ATFile type
            fileids = mti.get('ATFile',None)
            removeids = []
            if fileids is not None:
                for id in fileids:
                    #check for existance in tree
                    if not tree.has_key(id):
                        removeids.append(id)
                        
                if len(removeids) > 0:
                    for eachid in removeids:
                        del fileids[eachid]
                
                if not fileids:
                    del mti['ATFile']
            logger.info("Fixed parent object %s for btree index cleanup" % (parent.id,)           )
        
        
    def cleanupSpacesForBTree(portal,logger):
        ct = getToolByName(portal,'portal_catalog')
        query = {'portal_type': ('ContentRoot','ContentSpace','MemberSpace')}
        results = ct(query)        
        for o in results:
            fullobj = o.getObject()
            obj_path = "/".join(fullobj.getPhysicalPath())
            #cleanup tree
            fullobj.manage_cleanup()
            #fix count
            fullobj.manage_fixCount()
            
            #clean up for video,audio types
            #get all video, audio types objects checks whether it has proper entry in mt_index or not
            #also check for id in mt_index ATFile metatype if exists remove
            query1 = {}
            query1 = {'path': {'query': obj_path, 'depth': 1},'portal_type':('Video','Audio')}
            items_results = ct(query1)
            
            if len(items_results) > 0:                
                for item in items_results:
                    _cleanupForObject(fullobj,logger,item)
                    
            _cleanupForObject(fullobj,logger)
            
            #cleanup tree
            fullobj.manage_cleanup()
            #fix count
            fullobj.manage_fixCount()
    
    reorder_contenttyperegistry(portal,logger)
    setchoosertype(portal,logger)
    enableSyndicationForExistingObjects(portal,logger)
    configureRatings(portal,logger)
    enable_formats_fortextfield(portal,logger)
    modify_allsmartviews(portal,logger)    
    setup_sitehome_portlets(portal,logger,True)
    migrateSpacesForSpaceHomePortletsAssignment(portal,logger)
    removePlacefulWorkflowPolicies(portal,logger)
    rename_rootObject(portal,logger)
    assignCyninNavigation(portal,logger)
    cleanupSpacesForBTree(portal,logger)
    migratetagsforlowercase(portal,logger)     #should be last method in this migration step since it requires rebuilding catalog

def re_add_properties(portal,logger):
    add_custom_site_properties(portal,logger)
    add_custom_cynin_properties(portal,logger)    

def migrate_to_3_0_1dev(portal,logger):
    re_add_properties(portal,logger)

def migrate_to_3_0_5dev(portal,logger):
    re_add_properties(portal,logger)

def EmptyMigration(portal,logger):
    pass

migration_sequence = {
    "2.0.4": {
                "next_version_method":"2.0.4.2",
                "current_version_method":migrate_to_2_0_4,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "2.0.4.2": {
                "next_version_method":"2.0.5",
                "current_version_method":migrate_to_2_0_4_2,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":True,
              },
    "2.0.5": {
                "next_version_method":"2.0.6",
                "current_version_method":migrate_to_2_0_5,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":True,
              },
    "2.0.6": {
                "next_version_method":"2.0.7",
                "current_version_method":migrate_to_2_0_6,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":True,
              },
    "2.0.7": {
                "next_version_method":"2.0.7.1",
                "current_version_method":migrate_to_2_0_7_1,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "2.0.7.1": {
                "next_version_method":"2.1dev",
                "current_version_method":migrate_to_2_0_7_1,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "2.0.8":{
                "next_version_method":"2.1dev",
                "current_version_method":None,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "2.1dev":{
                "next_version_method":"3.0dev",
                "current_version_method":migrate_to_2_1_dev,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "2.2dev":{
                "next_version_method":"3.0dev",
                "current_version_method":None,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "3.0":{
                "next_version_method":"3.0.1dev",
                "current_version_method":None,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "3.0dev":{
                "next_version_method":"3.0.1dev",
                "current_version_method":migrate_to_3_0_dev,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "3.0.1":{
                "next_version_method":"3.0.2dev",
                "current_version_method":None,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "3.0.1dev":{
                "next_version_method":"3.0.2dev",
                "current_version_method":migrate_to_3_0_1dev,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":True,
              },
    "3.0.2dev":{
                "next_version_method":"3.0.3dev",
                "current_version_method":EmptyMigration,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":False,
              },
    "3.0.2":{
                "next_version_method":"3.0.3dev",
                "current_version_method":EmptyMigration,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":False,
              },
    "3.0.3dev":{
                "next_version_method":"3.0.4dev",
                "current_version_method":EmptyMigration,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":False,
              },
    "3.0.4dev":{
                "next_version_method":"3.0.4",
                "current_version_method":None,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":False,
              },
    "3.0.4":{
                "next_version_method":"3.0.5dev",
                "current_version_method":None,
                "rerun_current_version":False,
                "requires_prior_catalog_rebuild":False,
              },
    "3.0.5dev":{
                "next_version_method":"3.1",
                "current_version_method":migrate_to_3_0_5dev,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "3.1":{
                "next_version_method":"3.1.1dev",
                "current_version_method":EmptyMigration,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "3.1.1dev":{
                "next_version_method":"3.1.1",
                "current_version_method":EmptyMigration,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "3.1.1":{
                "next_version_method":"3.1.2",
                "current_version_method":EmptyMigration,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "3.1.2":{
                "next_version_method":"3.1.3dev",
                "current_version_method":EmptyMigration,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "3.1.3dev":{
                "next_version_method":"3.1.3",
                "current_version_method":EmptyMigration,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
    "3.1.3":{
                "next_version_method":None,
                "current_version_method":EmptyMigration,
                "rerun_current_version":True,
                "requires_prior_catalog_rebuild":False,
              },
}
def getMigrationStep(current_step_string):
    """Returns migration_step dict from migration dict object or None if not found"""
    try:
        return migration_sequence[current_step_string]
    except KeyError:
        return None
    
def getNextMigrationStep(current_step_string):
    """Returns next_migration_str, next_migration_step dict object or None,None if there's nothing to do."""
    try:
        current_step = getMigrationStep(current_step_string)
        if current_step != None:
            next_migration_str = current_step['next_version_method']
            next_migration_step = migration_sequence[next_migration_str]
            return next_migration_str,next_migration_step
    except KeyError:
        return None,None
    return None,None
    
def startMigration(context,logger):
    """Does the actual migration with all version dependent logic, here"""
    
    portal = context.getSite()
    fileVersion = getFileVersion(portal)
    installedVersion = getInstalledVersion(portal)
    logger.info("Current File Version: %s" % (fileVersion,))
    logger.info("Product current version: %s" % (installedVersion,))
    
    if fileVersion <> '':
        if fileVersion != installedVersion:
            #Get Current Migration step and pre-run it
            currstep = getMigrationStep(installedVersion)
            if currstep != None and currstep['rerun_current_version'] == True:
                logger.info("Pre-running install step for current installed version: %s" % installedVersion)
                currstep['current_version_method'](portal,logger)
                
            stepstr,step = getNextMigrationStep(installedVersion)

            while step:
                logger.info("Starting next migration step: %s" % stepstr)
                
                #If target version is greter than 3 then we use catalog rebuild requirement flag
                if int(stepstr[0]) > 2 and step['requires_prior_catalog_rebuild'] == True:
                    logger.info("Pre - re - building the catalog for version: %s" % stepstr)
                    rebuildCatalog(portal)
                
                if step['current_version_method'] != None and stepstr != fileVersion:
                    step['current_version_method'](portal,logger)
                    stepstr,step = getNextMigrationStep(stepstr)
                elif stepstr == fileVersion:
                    #We've arrived at the final version, let's run the final install step and then break out of the migrate loop
                    if step['current_version_method'] != None:
                        step['current_version_method'](portal,logger)
                    step = None
                    stepstr = None
		elif step['current_version_method'] == None and step['next_version_method'] != None:
		    #Nothing to do for current version, but it is not final version and there is a next version method defined
		    stepstr,step = getNextMigrationStep(stepstr)
        else:
            #Get Current Migration step and pre-run it
            currstep = getMigrationStep(installedVersion)
            if currstep != None:
                currstep['current_version_method'](portal,logger)
        
        logger.info("Doing final catalog rebuild...")
        rebuildCatalog(portal)
        logger.info("Migration Done from %s to %s" % (installedVersion,fileVersion,))
    else:
        logger.info("Could not determine cyn.in file version, skipping migration at this time.")
