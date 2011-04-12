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
from AccessControl import allow_module
from AccessControl import ModuleSecurityInfo
from AccessControl import ClassSecurityInfo
from ubify.coretypes.config import cynin_applications,cynin_applications_type_ignore
from ubify.viewlets.config import plone_site_type_title
from StringIO import StringIO
from ubify.policy.config import MEMBERS_PLACEFUL_WORKFLOW_POLICY, MEMBERS_PLACEFUL_WORKFLOW_POLICY_BELOW ,spacecontentworkflowtypes
from Products.CMFCore.utils import getToolByName
from ubify.policy.config import user_private_space_items,user_public_space_items
from ubify.policy.config import USER_SPACEFOLDER_WORKFLOW_POLICY,USER_PRIVATE_SPACE_POLICY,USER_PUBLIC_SPACE_POLICY,USER_PUBLIC_SPACE_BELOW_POLICY
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml,convertHtmlToWebIntelligentPlainText

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from Products.Archetypes.event import ObjectInitializedEvent
import transaction

from Products.CMFPlone.utils import _createObjectByType
from AccessControl import Unauthorized

from Products.ATContentTypes.interface import IATBTreeFolder
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from zope.component import getMultiAdapter
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import SetOwnPassword
from Products.Archetypes.utils import unique

from ubify.policy import CyninMessageFactory as _
from plone.memoize.instance import memoize
from plone.memoize import forever
from ubify.policy.config import contentroot_details,collection_details
from ubify.policy import CyninMessageFactory as _
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent
from zope.app.component.hooks import getSite


import logging
PasteError = "Paste Error"

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("SetPortrait")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("validatePasteData")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("PasteError")

    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getsortedblogentries")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("setup_users_my_area")

    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("triggerAddOnDiscussionItem")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getAllItemsForContext")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("isBTreeFolder")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getDefaultWikiPageForContext")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("setDefaultWikiPageForContext")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("checkEditPermission")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("checkHasPermission")

    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getListingTemplateForContextParent")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getAppTitleForContext")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("buildOneLevelUpURL")

    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getTagsAndTagsCount")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("escapeSingleQuote")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getTitleForRating")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getWorkflowStateTitle")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("isAddNewScreen")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getNavAccordianSelection")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getFormattedHtmlForTextFile")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getCurrentStatusMessageForUser")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("CyninVersion")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("CyninEdition")    
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getAuthorInfo")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getCyninMessageFactory")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getWebdavServerPort")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getWebdavURL")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getWebIntelligentTextToHTML")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getAvailableAppViews")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("notifyobjectinitialization")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("IsSelfRegistrationEnabled")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("licenseCheck")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getSchemaSectionName")


    
    #ContentRoot related methods
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getRootURL")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getRootAllFeedsURL")
    ModuleSecurityInfo("ubify.cyninv2theme").declarePublic("getRootID")

    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getjsondata")
    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getContributionCount")
    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getCommentCount")
    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getRecentContributionForUser")
    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getTopRatedContentForUser")
    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getMostUsedTagsForUser")
    ModuleSecurityInfo("ubify.cyninv2theme.portlets.statistics").declarePublic("getTotalItemCount")
    
def IsSelfRegistrationEnabled(context):
    app_perms = getSite().rolesOfPermission(permission='Add portal member')
    for appperm in app_perms:
        if appperm['name'] == 'Anonymous' and \
           appperm['selected'] == 'SELECTED':
            return True
    return False


def getAuthorInfo(context, memberId=None):
    """
    Return 'harmless' Memberinfo of any member, such as Full name,
    Location, etc
    """
    pm = context.portal_membership
    if not memberId:
        member = pm.getAuthenticatedMember()
    else:
        member = pm.getMemberById(memberId)

    if member is None:
        return None

    return member

def SetPortrait(membertool,portrait,member_id):
    membertool._setPortrait(portrait, member_id)

def validatePasteData(context,data):
    from OFS.CopySupport import *
    import marshal,zlib,urllib
    from marshal import loads, dumps
    from urllib import quote, unquote
    from zlib import compress, decompress
    from App.Dialogs import MessageDialog

    ob,mdatas = loads(decompress(unquote(data)))

    strErrorMessage = ""
    ilen = len(mdatas)
    if ilen > 1:
        for ival in range(1,ilen):
            try:
                performCheck(context,mdatas[ival - 1])
            except PasteError, msg:
                strErrorMessage = strErrorMessage + msg + " "
    elif ilen == 1:
        try:
            performCheck(context,mdatas[ilen - 1])
        except PasteError, msg:
            strErrorMessage = strErrorMessage + msg + " "

    if strErrorMessage <> "":
        strErrorMessage = _(u"error_cannot_paste",u"Cannot paste Folders between different applications.Disallowed to paste item(s).")
        raise PasteError,strErrorMessage

def performCheck(context,mdata):
    strURL = "/".join(mdata)

    rootObject = context.portal_url.getPortalObject()
    copiedObject = rootObject.restrictedTraverse(strURL)
    if copiedObject.portal_type == 'Folder':
        parentObject = copiedObject.getParentNode()
        try:
            getApplication(copiedObject,context,rootObject)
        except PasteError, msg:
            raise PasteError,msg

def getApplication(source,dest,root):
    sourcelist = source.aq_chain
    destlist = dest.aq_chain

    sFound = False
    dFound = False

    sApplication = None
    dApplication = None

    for type in sourcelist:
        try:
            if type.portal_type in cynin_applications:
                sFound = True
                sApplication = type
                if sFound == True:
                    break;
        except AttributeError:
            sApplication = root

    for type in destlist:
        try:
            if type.portal_type in cynin_applications:
                dFound = True
                dApplication = type
                if dFound == True:
                    break;
        except AttributeError:
            dApplication = root

    dtype = getTitle(root,dApplication)
    stype = getTitle(root,sApplication)

    if sApplication <> None and dApplication <> None and sApplication.portal_type != dApplication.portal_type:
        msg = "You are not allowed to paste '%s' from type '%s' to '%s'." % (source.title,stype,dtype,)
        raise PasteError,msg

def getTitle(portal,application):
    from Products.CMFCore.utils import getToolByName
    typetool= getToolByName(portal, 'portal_types')
    object_typename = application.portal_type
    object_typeobj = typetool[object_typename]

    if object_typeobj.title == '' and portal.portal_type.lower() == 'plone site':
        return plone_site_type_title
    else:
        return object_typeobj.title

def setConstrainsOnMyFolder(context):
    allowed_applications = (
        'Gallery',
        'Blog',
        'Wiki',
        'LinkDirectory',
        'FileRepository',
        'Calendar',
        'Folder',
        'GenericContainer',
        'Topic'
    )

    context.setConstrainTypesMode(1)
    context.setImmediatelyAddableTypes(allowed_applications)
    context.setLocallyAllowedTypes(allowed_applications)
    context.reindexObject()

def setupPlacefulWorkflowOnUser(context):
    out = StringIO()

    if context <> None:
        placeful_workflow = getToolByName(context, 'portal_placeful_workflow')
        try:
            config = placeful_workflow.getWorkflowPolicyConfig(context)
        except:
            context.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
            config = placeful_workflow.getWorkflowPolicyConfig(context)

        if config is None:
            context.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
            config = placeful_workflow.getWorkflowPolicyConfig(context)
            config.setPolicyIn(policy=MEMBERS_PLACEFUL_WORKFLOW_POLICY)
            config.setPolicyBelow(policy=MEMBERS_PLACEFUL_WORKFLOW_POLICY_BELOW)
            print >> out, "Configured placeful workflow on %s" % (context,)
            return out.getvalue()
        else:
            config.setPolicyIn(policy=MEMBERS_PLACEFUL_WORKFLOW_POLICY)
            config.setPolicyBelow(policy=MEMBERS_PLACEFUL_WORKFLOW_POLICY_BELOW)
            print >> out, "Configured placeful workflow on %s" % (context,)
            return out.getvalue()

def getsortedblogentries(context):
    results = []
    path = "/".join(context.getPhysicalPath())
    try:
        query = {'path': {'query':path,'depth':1},'sort_on':'created','sort_order':'descending'}
        pcatalog = context.portal_catalog
        results = pcatalog.searchResults(query)
    except (RuntimeError,TypeError,NameError):
        pass
    return results

def getOrCreateType(portal, atobj, newid, newtypeid,doreindex=False):
    """
    Gets the object specified by newid if it already exists under
    atobj or creates it there with the id given in newtypeid
    """
    try:
        if hasattr(atobj,'objectIds') and newid not in atobj.objectIds():
            raise AttributeError
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
        if doreindex==True:
            newobj.reindexObject()
            notify(ObjectInitializedEvent(newobj))
    logging.getLogger('getOrCreateType:').info("Created object with id: %s" % newobj.id)
    return newobj

def updateWorkflowSecurity(portal):
    out = StringIO()
    pw = getattr(portal,'portal_workflow')
    count = 0
    if pw <> None:
        count = pw.updateRoleMappings()
        print >> out, "Updated workflow role mappings for %s objects" % (count,)
    return out.getvalue()

def set_placeful_workflow_policy(target,policyin,policybelow):
    placeful_workflow = getToolByName(target, 'portal_placeful_workflow')
    try:
        config = placeful_workflow.getWorkflowPolicyConfig(target)
    except AttributeError:
        target.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(target)

    if config is None:
        target.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(target)

    if policyin <> None:
        config.setPolicyIn(policy=policyin)
    if policybelow <> None:
        config.setPolicyBelow(policy=policybelow)

    target.reindexObject()

def setup_users_privatespace(context):
    try:
        privatespace = getattr(context,'private')
    except AttributeError:
        privatespace = getOrCreateType(context,context,'private','Space')
    privatespace.title = "Private"
    privatespace.reindexObject()

    set_placeful_workflow_policy(privatespace,USER_PRIVATE_SPACE_POLICY,USER_PRIVATE_SPACE_POLICY)

    if privatespace <> None:
        #create applications
        for item in user_private_space_items:
            id = item["id"]
            title = item["title"]
            type = item["type"]
            try:
                newobj = getattr(privatespace,id)
            except AttributeError:
                newobj = getOrCreateType(context,privatespace,id,type)

            newobj.title = title
            if newobj.portal_type.lower() == 'gallery' and newobj.getLayout() != "atct_album_view":
                newobj.setLayout("atct_album_view")
            newobj.reindexObject()

def setup_users_publicspace(context):
    try:
        publicspace = getattr(context,'public')
    except AttributeError:
        publicspace = getOrCreateType(context,context,'public','Space')
    publicspace.title = "Public"
    publicspace.reindexObject()

    set_placeful_workflow_policy(publicspace,USER_PUBLIC_SPACE_POLICY,USER_PUBLIC_SPACE_BELOW_POLICY)

    if publicspace <> None:
        #create applications
        for item in user_public_space_items:
            id = item["id"]
            title = item["title"]
            type = item["type"]
            try:
                newobj = getattr(publicspace,id)
            except AttributeError:
                newobj = getOrCreateType(context,publicspace,id,type)

            newobj.title = title
            if newobj.portal_type.lower() == 'gallery' and newobj.getLayout() != "atct_album_view":
                newobj.setLayout("atct_album_view")

            newobj.reindexObject()

def setup_users_recyclebin(context):

    context.setConstrainTypesMode(1)
    context.setImmediatelyAddableTypes(('RecycleBin',))
    context.setLocallyAllowedTypes(('RecycleBin',))
    context.reindexObject()
    from ubify.recyclebin.utils import getMemberRecycleBin
    getMemberRecycleBin(context)

    context.setConstrainTypesMode(0)

def setup_users_statuslogfolder(context):
    context.setConstrainTypesMode(1)
    context.setImmediatelyAddableTypes(('Space','RecycleBin','StatuslogFolder'))
    context.setLocallyAllowedTypes(('Space','RecycleBin','StatuslogFolder'))
    context.reindexObject()
    objStatuslogFolder = getOrCreateType(context,context,'statuslog','StatuslogFolder')
    if objStatuslogFolder.title == '':
        objStatuslogFolder.title = 'Status log'
        objStatuslogFolder.reindexObject()

def setup_users_my_area(context):
    #jsumant:if required then only we will uncomment the following statement and work on it
    #set_placeful_workflow_policy(context,USER_SPACEFOLDER_WORKFLOW_POLICY,None)
    #portal = context.portal_url.getPortalObject()
    #updateWorkflowSecurity(portal)
    pass

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


def migrateuserareas(object):

    portal = object.portal_url.getPortalObject()

    #make owner of the object as user in context for creating inner objects
    getCurrentUser(object)

    from AccessControl import getSecurityManager
    currentuserid = getSecurityManager().getUser().getId()
    if currentuserid is None:
        getAdminUser(portal)
        currentuserid = getSecurityManager().getUser().getId()

    if currentuserid <> None and object <> None:
        ids = object.objectIds()
        try:
            myimporteditems = getattr(object,'myimporteditems')
        except AttributeError:
            myimporteditems = getOrCreateType(object,object,'myimporteditems','GenericContainer')

        myimporteditems.title = "My Imported Items"
        myimporteditems.reindexObject()

        for jid in ids:
            try:
                cb = object.manage_copyObjects(ids = jid)
                myimporteditems.manage_pasteObjects(cb)
                transaction.savepoint()
            except Unauthorized:
                getAdminUser(portal)
                cb = object.manage_copyObjects(ids = jid)
                myimporteditems.manage_pasteObjects(cb)
                transaction.savepoint()
                getCurrentUser(object)

        #cb = object.manage_copyObjects(ids= ids)
        #myimporteditems.manage_pasteObjects(cb)
        #transaction.savepoint()

        object.manage_delObjects(ids=ids)
        transaction.savepoint()

        setup_users_privatespace(object)
        setup_users_publicspace(object)

        publicspace = getattr(object,'public')

        cb1 = object.manage_cutObjects(ids=('myimporteditems',))
        publicspace.manage_pasteObjects(cb1)
        transaction.savepoint()

        set_placeful_workflow_policy(object,USER_SPACEFOLDER_WORKFLOW_POLICY,None)

    #make admin as user in context for creating inner objects
    getAdminUser(portal)

def triggerAddOnDiscussionItem(item):
    from zope.event import notify
    from zope.lifecycleevent import ObjectCreatedEvent
    notify(ObjectCreatedEvent(item))
    notify(ObjectInitializedEvent(item))
    
def notifyobjectinitialization(obj):
    notify(ObjectInitializedEvent(obj))

def getStatusMessagesForUser(portal,username=''):
    from AccessControl import getSecurityManager
    ct = portal.portal_catalog
    if username is '':
        username = getSecurityManager().getUser().getId()
    query = {'Creator':username,'portal_type':'StatuslogItem','sort_on':'created','sort_order':'descending'}

    results = ct.searchResults(query)
    return results

def getCurrentStatusMessageForUser(portal,username=''):
    message = None
    if username is None:
        username = ''
    results = getStatusMessagesForUser(portal,username)
    if len(results) > 0:
        message = results[0]
    return message

def setCurrentStatusMessageForUser(portal,username,message,context):
    userhomefolder = portal.portal_membership.getHomeFolder()


    po = context.portal_url.getPortalObject()
    pm = context.portal_membership
    md = pm.getMemberById(username)
    if md is not None:
        user = md.getUser()

    if userhomefolder <> None:
        message = message.replace("\n","")

        new_id = userhomefolder.generateUniqueId('StatuslogItem')

        objMessage = getOrCreateType(userhomefolder,userhomefolder,new_id,'StatuslogItem')
        if objMessage.title == '':
            objMessage.title = message
            objMessage._renameAfterCreation()

        #We're not doing twitter yet! Too much more stuff to do for this release. :(
        ##if user is not None:
        ##    if 'mutable_properties' in user.listPropertysheets():
        ##            mps = user.getPropertysheet('mutable_properties')
        ##            twitterusername = mps.getProperty('twitterusername')
        ##            twitterpassword = mps.getProperty('twitterpassword')
        ##            crossposttotwitter = mps.getProperty('crossposttotwitter')
        ##            if twitterusername and twitterusername != ''  and twitterpassword and twitterpassword != '' and crossposttotwitter == 'on':
        ##                from twitter import Api as TwitterApi
        ##                api = TwitterApi(username=twitterusername,password=twitterpassword)
        ##                api.SetXTwitterHeaders('cyn.in', 'http://cyn.in', '2.2')
        ##                try:
        ##                    api.PostUpdate(message)
        ##                except:
        ##                    pass
        return objMessage
    else:
        return None

def getAllItemsForContext(context,currentpath=None,typestosearchin=None,depth=-1,sorton='modified',sorder='descending',creator=None,modifiers=None):
    results = []
    path = "/".join(context.getPhysicalPath())
    try:
        query = {}
        if currentpath <> None:
            path = currentpath
        query = {'path': {'query':path},'sort_on':sorton,'sort_order':sorder}
        if depth > 0:
            query['path']['depth'] = depth
        if typestosearchin <> None:
            query['portal_type'] = typestosearchin
        if creator <> None:
            query['Creator'] = creator
        elif modifiers <> None:
            query['modifiers'] = {'operator': 'or', 'query': modifiers}

        pcatalog = context.portal_catalog
        results = pcatalog.searchResults(query)
    except (RuntimeError,TypeError,NameError):
        pass
    return results

def isBTreeFolder(context):
    return context.__provides__(IATBTreeFolder)

def setDefaultWikiPageForContext(context,UID):
    from AccessControl import getSecurityManager
    if context.hasProperty('default_wiki_page') == 0:
        context.manage_addProperty('default_wiki_page',UID,'string')
    else:
        context._updateProperty('default_wiki_page',UID)


def getDefaultWikiPageForContext(context):
    objDefaultPage = None
    try:
        if context.hasProperty('default_wiki_page') <> 0:
            uid = context.default_wiki_page
            cat = getToolByName(context, 'uid_catalog', None)
            resbrains = cat.searchResults(UID=uid)

            if len(resbrains) > 0:
                objDefaultPage = resbrains[0].getObject()
    except AttributeError:
        pass
    return objDefaultPage

def checkEditPermission(contextobj):
    return checkHasPermission('Modify portal content',contextobj)

def checkHasPermission(permission,contextobj):
    return getSecurityManager().checkPermission(permission,aq_inner(contextobj)) > 0

def getListingTemplateForContextParent(context):
    tempid = "app_all"
    ptype = context.portal_type
    if ptype == 'Document':
        tempid = "app_wiki"
    elif ptype == 'File':
        tempid = "app_files"
    elif ptype == 'Image':
        tempid = "app_images"
    elif ptype == 'Link':
        tempid = "app_links"
    elif ptype == 'Blog Entry':
        tempid = "app_blog"
    elif ptype == 'Event':
        tempid = "app_calendar"
    elif ptype == 'StatuslogItem':
        tempid = "app_statuslog"
    elif ptype == 'Video':
        tempid = "app_videos"
    elif ptype == 'Discussion':
        tempid = "app_discussions"
    elif ptype == 'Audio':
        tempid = "app_audios"

    return tempid

def buildOneLevelUpURL(context):
    parent = context.getParentNode()
    parent_url = parent.absolute_url()
    up_url = parent_url

    templateId = getListingTemplateForContextParent(context)
    if context.portal_type in ('ContentSpace','MemberSpace'):
        current_perspective = 'app_all'
        req = context.REQUEST
        last = req.physicalPathFromURL(req.getURL())[-1]
        if last in ('pastEvents','upcomingEvents'):
            current_perspective = req.physicalPathFromURL(req.getURL())[-2]
        elif last.startswith('app_'):
            current_perspective = last

        up_url = parent_url + "/" + current_perspective
        #check for view_actions
        current_ploneview = context.restrictedTraverse('@@plone')
        current_viewactions = current_ploneview.prepareObjectTabs()
        selected_view = None
        selected_current_views = [br for br in current_viewactions if br['selected']==True]
        if len(selected_current_views) > 0:
            selected_view = selected_current_views[0]
            selected_url = selected_view['url']
            selected_view_id = selected_view['id']

            parent_ploneview = parent.restrictedTraverse('@@plone')
            parent_viewactions = parent_ploneview.prepareObjectTabs()
            parent_views = [k for k in parent_viewactions if k['id'] == selected_view_id]

            if len(parent_views) > 0:
                up_url = parent_views[0]['url']

    else:
        up_url = parent_url + "/" + templateId

    return up_url

def getAppTitleForContext(context):
    tempid = _(u"activity_stream",u"Activity Stream")
    ptype = context.portal_type
    if ptype == 'Document':
        tempid = _(u"wiki",u"Wiki")
    elif ptype == 'File':
        tempid = _(u"files",u"Files")
    elif ptype == 'Image':
        tempid = _(u"images",u"Images")
    elif ptype == 'Link':
        tempid = _(u"links",u"Links")
    elif ptype == 'Blog Entry':
        tempid = _(u"blogs",u"Blogs")
    elif ptype == 'Event':
        tempid = _(u"calendar",u"Calendar")
    elif ptype == 'StatuslogItem':
        tempid = _(u"statuslog",u"Status Log")
    elif ptype == 'Video':
        tempid = _(u"videos",u"Videos")
    elif ptype == 'Discussion':
        tempid = _(u"discussions",u"Discussions")
    elif ptype == 'Audio':
        tempid = _(u"audios",u"Audios")
        
    return tempid

def getTitleForRating(num):
    if num == 1:
        newtitle=_(u"hated_it",u'Hated it')
    elif num == 2:
        newtitle=_(u"didnt_like_it",u"Didn't like it")
    elif num == 3:
        newtitle=_(u"average",u"Average")
    elif num == 4:
        newtitle=_(u"liked_it",u'Liked it')
    elif num == 5:
        newtitle=_(u"loved_it",u'Loved it')
    return newtitle

def getWorkflowStateTitle(current_object):
    fullobj = current_object
    if hasattr(fullobj,'getObject'):
        fullobj = current_object.getObject()
    workflow_tool = getToolByName(fullobj, 'portal_workflow')
    item_state = ""
    raw_item_state = ""
    has_state = False
    workflow_def = None
    current_workflow = None    
    try:
        item_state = raw_item_state = workflow_tool.getInfoFor(fullobj,'review_state')
        workflow_def = workflow_tool.getWorkflowsFor(fullobj)
        if len(workflow_def) > 0:
            current_workflow = workflow_def[0]
            wf_states = current_workflow.states

            current_state = wf_states[item_state]
            return current_state.title,current_state.description
        else:
            return "",""
    except WorkflowException:
        workflow_def = workflow_tool.getWorkflowsFor(fullobj)
        if len(workflow_def) > 0:
            current_workflow = workflow_def[0]
            wf_states = current_workflow.states
            item_state = workflow_def.initial_state
            current_state = wf_states[item_state]
            return current_state.title, current_state.description
        else:
            return "",""


def getTagsAndTagsCount(results):

    from Products.Archetypes.atapi import Vocabulary, DisplayList
    from Products.Archetypes.utils import unique
    coll = {}

    for o in results:
        lstSubject = []
        try:
            lstSubject = o.Subject
        except AttributeError:
            from p4a.plonecalendar.eventprovider import BrainEvent
            if isinstance(o,BrainEvent):
                lstSubject = o.context.Subject
            else:
                lstSubject = []
        for eSub in lstSubject:
            if coll.get(eSub,None) is None:
                coll[eSub] = {'name':eSub,'count':1}
            else:
                coll[eSub]['count'] = coll.get(eSub)['count'] + 1

    dl = DisplayList()
    collkeys = coll.keys()
    collkeys.sort(lambda x,y: cmp(x.lower(),y.lower()),reverse=False)

    for obj in collkeys:
        dl.add(coll[obj]['name'],coll[obj]['count'])

    return Vocabulary(dl,None,None)

def escapeSingleQuote(value):
    value = value.replace("'","&#39;")
    return value

def isAddNewScreen(context,request):
    context_state = getMultiAdapter((context, request),name=u'plone_context_state')
    if hasattr(context_state.parent(),'portal_type') and context_state.parent().portal_type == 'TempFolder':
        return True
    else:
        return False

def getNavAccordianSelection(context):

    selectedItem = {}
    currentObject = context
    parentList = currentObject.aq_chain
    bFound = False

    isRootInPath = False
    isMembersInPath = False
    isViewsInPath = False
    isRecycleBinInPath = False

    request = context.REQUEST
    steps = request.steps
    traverse_subpath = []
    if hasattr(request,'traverse_subpath'):
        traverse_subpath = getattr(request,'traverse_subpath')

    rootid = contentroot_details['id']
    viewsid = collection_details['id']

    portal_state = getMultiAdapter((context,context.REQUEST),name='plone_portal_state')
    portal = portal_state.portal()

    try:
        objRoot = getattr(portal,rootid)
    except AttributeError:
        objRoot = None

    try:
        objViews = getattr(portal,viewsid)
    except AttributeError:
        objViews = None

    try:
        objMembers = getattr(portal,"Members")
    except AttributeError:
        objMembers = None

    try:
        objRecycle = getattr(portal,"recyclebin")
    except AttributeError:
        objRecycle = None

    if objRoot in parentList:        
        isRootInPath = True
        if context == objRoot or (not context.restrictedTraverse('@@plone').isStructuralFolder() and hasattr(context,'getParentNode') and context.getParentNode() == objRoot):
            selectedItem['currentlink'] = 'vp_home'
        else:
            #check whether current context is temp while adding content.
            try:
                portal_factory = getToolByName(context, 'portal_factory', None)
                if portal_factory is not None and portal_factory.isTemporary(context):
                    try:
                        idx_factorytool = parentList.index(portal_factory)
                        if idx_factorytool < len(parentList) - 1 and parentList[idx_factorytool + 1] == objRoot:
                            selectedItem['currentlink'] = 'vp_home'
                    except ValueError:
                        pass
            except:
                pass
    elif objViews in parentList:
        isViewsInPath = True
    elif objMembers in parentList:
        isMembersInPath = True
    elif objRecycle in parentList:
        isRecycleBinInPath = True
    else:
        if context == portal and steps[-1] in ('author','personalize_form'):
            isMembersInPath = True
            selectedItem['accordion'] = 'users'
        elif context == portal and steps[-1].startswith('plone_control_panel'):
            selectedItem['accordion'] = 'manage'
            selectedItem['currentlink'] = 'vp_controlpanel'
        elif context == portal and steps[-1].startswith('sitelogo_settings'):
            selectedItem['accordion'] = 'manage'
            selectedItem['currentlink'] = 'vp_sitelogo'
        elif context == portal and steps[-1].startswith('@@mail-controlpanel'):
            selectedItem['accordion'] = 'manage'
            selectedItem['currentlink'] = 'vp_mailcontrolpanel'
        elif context == portal and steps[-1] in ('join_form','prefs_users_overview','prefs_user_details','prefs_user_memberships','@@usergroup-controlpanel'):
            selectedItem['accordion'] = 'manage'
            selectedItem['currentlink'] = 'vp_usermanagement'
        elif context == portal and steps[-1] in ('prefs_groups_overview','prefs_group_members','prefs_group_details','@@manage-group-portlets'):
            selectedItem['accordion'] = 'manage'
            selectedItem['currentlink'] = 'vp_groupmanagement'
        elif context == portal and steps[-1].startswith('@@site-controlpanel'):
            selectedItem['accordion'] = 'manage'
            selectedItem['currentlink'] = 'vp_sitesetting'

    if isRootInPath:
        selectedItem['accordion'] = 'spaces'
    elif isViewsInPath:
        selectedItem['accordion'] = 'collections'
    elif isMembersInPath:
        selectedItem['accordion'] = 'users'
    elif isRecycleBinInPath:
        selectedItem['accordion'] = 'manage'
        selectedItem['currentlink'] = 'vp_recyclebin'

    if isMembersInPath:
        if context == objMembers or steps[-1] in ('member_search_results'):
            selectedItem['currentlink'] = 'vn_psearch'

    return selectedItem

def getFormattedHtmlForTextFile(context):
    try:
        from pygments.lexers import guess_lexer,guess_lexer_for_filename,get_lexer_for_filename
    
        lexer = get_lexer_for_filename(context.getFilename())
        data = context.get_data()
        return getHighlightedText(data,lexer)
    except:
        return None

def getHighlightedText(data,lexer):
    from pygments import highlight
    from pygments.formatters import HtmlFormatter

    formatter = HtmlFormatter()
    result = highlight(data,lexer,formatter)
    styles = '<style>' + HtmlFormatter().get_style_defs('.highlight') + '</style>'
    return styles + result


def CyninVersion(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    ubifyVersion = ""
    objProduct = portal_quickinstaller._getOb('ubify.policy')
    if objProduct <> None:
        return objProduct.getInstalledVersion()

def CyninEdition(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    ubifyEdition = ""
    objProduct = portal_quickinstaller._getOb('ubify.enterprise',None)
    objondemandproduct = portal_quickinstaller._getOb('ubify.ondemand',None)
    if objProduct <> None:
        return _('cynin_enterprise_edition','enterprise edition'),'ee'
    elif objondemandproduct <> None:
        return _('cynin_ondemand_edition','on demand edition'),'od'
    else:
        return _('cynin_community_edition','free open source edition'),'ce'

@forever.memoize
def getRootURL():
    rootid = contentroot_details['id']
    return "/" + rootid

@forever.memoize
def getRootAllFeedsURL():
    rootid = contentroot_details['id']
    return "/" + "/".join([rootid,'syndicationinfo'])

@forever.memoize
def getRootID():
    rootid = contentroot_details['id']
    return rootid

def getCyninMessageFactory():
    return _

def addDiscussion(portal,discussion,tags,context,discussionTitle=''):
    if discussion == '':
        return None
    objDiscussion = None
    new_id = context.generateUniqueId('Discussion')
    try:
        objDiscussion = getOrCreateType(portal,context,new_id,'Discussion')
    except:
        objDiscussion = None
        
    if objDiscussion <> None:
        if objDiscussion.title == '':
            if discussionTitle == '':
                objDiscussion.title = convertHtmlToWebIntelligentPlainText(discussion)[:80]
            else:
                objDiscussion.title = discussionTitle
            objDiscussion.setDescription(discussion)
            objDiscussion._renameAfterCreation()
        
        if tags != '':
            try:            
                values = tags.split(",")
                values = [val.strip().lower() for val in values]
                values = [k.lower() for k in list(unique(values)) if k]
            except AttributeError:
                values = []
            objDiscussion.setSubject(values)
        
        objDiscussion.reindexObject()
        notify(ObjectInitializedEvent(objDiscussion))
        
    return objDiscussion
    

#@forever.memoize
def get_dict_for_default_addabletypes(portal):
    dict_value = {}
    ptypes = getattr(portal,'portal_types')
    for eachobj in ('ContentSpace','ContentRoot',):
        obj = getattr(ptypes,eachobj)
        if obj <> None:
            dict_value[eachobj] = obj.allowed_content_types            
    return dict_value

def getDisallowedTypes(portal,obj):    
    if hasattr(obj,'getObject'):
        obj = obj.getObject()
    
    dis_types = []
    
    default_addable_types_dict = get_dict_for_default_addabletypes(portal)
    if not default_addable_types_dict.has_key(obj.portal_type):
        return dis_types
    
    default_addable_types = default_addable_types_dict[obj.portal_type]
    allowed_addable_types = obj.getImmediatelyAddableTypes()
    
    dis_types = [obj for obj in default_addable_types if obj not in allowed_addable_types]
    return dis_types

def getLocationListForAddContent(portal):
    catalog_tool = getToolByName(portal,'portal_catalog')        
    portalpath = "/".join(portal.getPhysicalPath())
    query = {}
    results = []
    
    objRoot = None
    try:
        objRoot = getattr(portal,getRootID())
    except AttributeError:
        objRoot = None
    
    if objRoot <> None:
        query['path'] = {'query': "/".join(objRoot.getPhysicalPath())}
        query['portal_type'] = ('ContentSpace')
        query['sort_on'] = 'sortable_title'
        
        spaces = catalog_tool(**(query))
        custom_spaces = []
        
        for ks in spaces:
            obj = {}
            fullitem = ks.getObject()
            
            obj['object'] = ks
            obj['path'] = ks.getPath().lstrip(portalpath)
            obj['depth'] = len(ks.getPath().lstrip(portalpath).split("/")) - 2
            obj['canAdd'] = checkHasPermission('Add portal content',fullitem)
            obj['disallowedtypes'] = ks.disallowedtypes
            
            custom_spaces.append(obj)
        
        custom_spaces.sort(lambda x,y: cmp(x['path'],y['path']))            
        
        query['portal_type'] = ('ContentRoot')
        rootresults = catalog_tool(**(query))
        custom_rootresults = []
        for k in rootresults:
            obj = {}
            fullitem = k.getObject()
            
            obj['object'] = k
            obj['path'] = k.getPath().lstrip(portalpath)
            obj['depth'] = 0
            obj['canAdd'] = checkHasPermission('Add portal content',fullitem)
            obj['disallowedtypes'] = k.disallowedtypes
            custom_rootresults.append(obj)
        
        results.extend(custom_rootresults)
        results.extend(custom_spaces)
        
    return results
def getBestMatchedLocationForAddingContent(portal):    
    bestmatchedlocation = None
    spaceslist = getLocationListForAddContent(portal)
    addablelocations = [k for k in spaceslist if k['canAdd'] == True]    
    if len(addablelocations) > 0:
        bestmatchedlocation = addablelocations[0]['object']
    return bestmatchedlocation
    
def canAddContent(portal):
    canAddContent = False    
    spaceslist = getLocationListForAddContent(portal)
    addablelocations = [k for k in spaceslist if k['canAdd'] == True]
    canAddContent = len(addablelocations) > 0 or canAddCollections(portal)
    return canAddContent

def canAddCollections(portal):
    canaddcollection = False
    viewsid = collection_details['id']
    
    try:
        objViews = getattr(portal,viewsid)
        canaddcollection = len(objViews.allowedContentTypes()) > 0
    except AttributeError:
        pass

    return canaddcollection

@forever.memoize
def getWebdavServerPort():
    webdavport = None
    from asyncore import socket_map
    bFound = False
    for k,v in socket_map.items():        
        if hasattr(v, 'port') and hasattr(v,'server_protocol') and v.server_protocol.lower() == 'webdav':
            webdavport = v.port
            bFound = True
        if bFound:
            break;
    return webdavport

@forever.memoize
def getWebdavURL(context):
    portal_url = context.portal_url()
    portal = context.portal_url.getPortalObject()
    ##import pdb;pdb.set_trace()
    siteurl = "/".join(portal.getPhysicalPath())
    webdavport = getWebdavServerPort()
    url = ''
    if webdavport:
        if portal_url.count('/') > 2:
            puparts = portal_url.split('/')
            puparts[2] = puparts[2] + ":" + str(webdavport)
            url = '/'.join([puparts[0],puparts[1],puparts[2]])
        else:
            url = portal_url + ":" + str(webdavport) 
        if context.portal_type == 'Plone Site':
            url = url + siteurl + "/" + getRootID()
        else:
            contextualurl = "/".join(context.getPhysicalPath())   
            url = url + contextualurl    
    return url

def getWebIntelligentTextToHTML(text):
    return convertWebIntelligentPlainTextToHtml(text)
    
def getAvailableAppViews(context):
    availableviews = []
    portal_actions = getToolByName(context,'portal_actions')
    if hasattr(portal_actions,'application_views'):
        app_views = getattr(portal_actions,'application_views')
        if app_views <> None:            
            availableviews = app_views.listActions()
            if context.portal_type in ('ContentSpace'):
                availableviews = [k for k in availableviews if k.id != 'statusmessage']
    return availableviews

@forever.memoize
def isLicensingInstalled():
    portal_quickinstaller = getToolByName(getSite(), 'portal_quickinstaller')
    licProd = portal_quickinstaller.isProductAvailable('cynin.licensing')
    eeProd = portal_quickinstaller.isProductAvailable('ubify.enterprise')
    if licProd == True or eeProd == True:
        return True
    else:
        return False

def licenseCheck(request,context):
    if isLicensingInstalled():
        from cynin.licensing import CheckLicense
        islicensed = CheckLicense(context,request)
        return islicensed
    else:
        return True

def getSchemaSectionName(schema):
    returnvalue = 'default'
    if schema.lower() == "categorization":
        returnvalue = _(u"categorization",u"Categorization")
    elif schema.lower() == "dates":
        returnvalue = _(u"schedule",u"Schedule")
    elif schema.lower() == "ownership":
        returnvalue = _(u"ownership",u"Ownership")
    elif schema.lower() == "settings":
        returnvalue = _(u"additional_settings",u"Additional Settings")
    elif schema.lower() == "default":
        returnvalue = _(u"content",u"Content")
    return returnvalue