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
from ubify.policy.config import *
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
from Products.CMFCore.Expression import Expression
from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
from Acquisition import aq_inner, aq_parent, aq_base

from Products.CMFPlone.utils import _createObjectByType
from AccessControl import Unauthorized
from ubify.policy.migration.migration import *

from ubify.spaces.config import PLACEFUL_WORKFLOW_POLICY, SPACE_PLACEFUL_WORKFLOW_POLICY, REVIEW_PLACEFUL_WORKFLOW_POLICY


import transaction

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent
from zope.component import createObject
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility,getMultiAdapter,getSiteManager

def getOrCreateType(portal, atobj, newid, newtypeid):
    """
    Gets the object specified by newid if it already exists under
    atobj or creates it there with the id given in newtypeid
    """
    #import pdb;pdb.set_trace()
    try:
        newobj = getattr(atobj,newid) #get it if it already exists
    except AttributeError:  #newobj doesn't already exist
        try:            
            _ = atobj.invokeFactory(id=newid,type_name=newtypeid)            
        except ValueError:
            _createObjectByType(newtypeid, atobj, newid)
        except Unauthorized:
            _createObjectByType(newtypeid, atobj, newid)
        except TypeError, v:            
            pass
        newobj = getattr(atobj,newid)
        notify(ObjectCreatedEvent(newobj))
    return newobj

def getViews(portal):
    viewsid = collection_details['id']
    return getOrCreateType(portal,portal,viewsid,"SmartviewFolder")

def updateWorkflowSecurity(portal,logger):
    out = StringIO()
    pw = getattr(portal,'portal_workflow')    
    count = 0
    if pw <> None:
        count = pw.updateRoleMappings()
        logger.info("Updated workflow role mappings for %s objects" % (count,))
    return out.getvalue()

def get_assignments_for_sitehome_collectionportlets(portal,views,logger):
    assignments = []
    from plone.portlet.collection import collection
    
    for item in default_sitehome_smartviews:
        try:
            objsmartview = getattr(views,item["id"])
            target_coll = "/".join(objsmartview.getPhysicalPath())
            assignments.append(collection.Assignment(header=item["displaytitle"],target_collection=target_coll,limit=item["limit"],show_more=True,show_dates=False))
        except:
            logger.info("Unable to assign collection portlet for smartview : %s" % (item["id"],))
    
    return assignments
        
def setup_sitehome_portlets(portal,logger,reInstall=False):    
    from ubify.cyninv2theme.browser.cynindashboards import assign_portal_dashboard    
    assign_portal_dashboard(portal,None,reInstall)
    logger.info("Assigned site home portlets.")
        
def setup_sitehome_collection_portlets(portal,logger):
    
    from plone.portlets.interfaces import IPortletManager
    from plone.portlets.interfaces import ILocalPortletAssignmentManager
    from plone.portlets.constants import CONTEXT_CATEGORY
    from zope.app.container.interfaces import INameChooser
    from plone.portlets.interfaces import IPortletAssignmentMapping
    from zope.component.interfaces import ComponentLookupError
    
    from plone.portlets.interfaces import IPortletManager
    from plone.portlets.manager import PortletManager
    from zope.interface import alsoProvides
    
    from ubify.viewlets.browser.interfaces import IHomeContent
    
    try:
        objviews = getattr(portal,'views')
        assignments = get_assignments_for_sitehome_collectionportlets(portal,objviews,logger)
        sm = getSiteManager(portal)
        name = 'ubify.homecontentportletsmanager'
        try:
            portletManager = getUtility(IPortletManager, name=name)
        except ComponentLookupError:
            objportletManager = PortletManager()
            alsoProvides(objportletManager,IHomeContent)
                
            sm.registerUtility(component=objportletManager,
                               provided=IPortletManager,
                               name = name)        
            portletManager = getUtility(IPortletManager, name=name)
            
        assignable = getMultiAdapter((portal, portletManager,), ILocalPortletAssignmentManager)
        manager = getMultiAdapter((portal, portletManager), IPortletAssignmentMapping)
        
        if assignments:        
            if portletManager is not None:            
                chooser = INameChooser(manager)            
                for assignment in assignments:
                    if manager.has_key(assignment.id) == 0:
                        manager[chooser.chooseName(None, assignment)] = assignment
                        logger.info("Assigning collection portlet manager for %s" % (assignment.id,)        )
    except AttributeError:
        logger.info("Unable to set up site home collection portlets.")
        
def changeHomePortletsTitles(portal,logger):
    
    from plone.portlets.interfaces import IPortletManager
    from plone.portlets.interfaces import ILocalPortletAssignmentManager
    from plone.portlets.constants import CONTEXT_CATEGORY
    from zope.app.container.interfaces import INameChooser
    from plone.portlets.interfaces import IPortletAssignmentMapping
    from zope.component.interfaces import ComponentLookupError
    
    from plone.portlets.interfaces import IPortletManager
    from plone.portlets.manager import PortletManager
    from zope.interface import alsoProvides
    
    from ubify.viewlets.browser.interfaces import IHomeContent
    
    try:
        objviews = getattr(portal,'views')
        assignments = get_assignments_for_sitehome_collectionportlets(portal,objviews,logger)
        sm = getSiteManager(portal)
        name = 'ubify.homecontentportletsmanager'
        try:
            portletManager = getUtility(IPortletManager, name=name)
        except ComponentLookupError:
            objportletManager = PortletManager()
            alsoProvides(objportletManager,IHomeContent)
                
            sm.registerUtility(component=objportletManager,
                               provided=IPortletManager,
                               name = name)        
            portletManager = getUtility(IPortletManager, name=name)
            
        assignable = getMultiAdapter((portal, portletManager,), ILocalPortletAssignmentManager)
        manager = getMultiAdapter((portal, portletManager), IPortletAssignmentMapping)
        
        mgkeys = manager.keys()
        for k in mgkeys:
            del manager[k]
            
        if assignments:        
            if portletManager is not None:            
                chooser = INameChooser(manager)            
                for assignment in assignments:
                    if manager.has_key(assignment.id) == 0:
                        manager[chooser.chooseName(None, assignment)] = assignment
                        logger.info("Assigning collection portlet manager for %s" % (assignment.id,)  )
    except AttributeError:
        logger.info("Unable to set up site home collection portlets.")
        
def addDefaultDashboardViews(portal,logger):
    out = StringIO()
    objviews = getViews(portal)
    
    for eachview in default_sitehome_smartviews:
        try:
            sattr = getattr(objviews,eachview["id"])
        except:
            sattr = getOrCreateType(portal,objviews,eachview["id"],"Topic")
            sattr.title = eachview["title"]
            sattr.description = eachview["description"]
            sattr.limitNumber = eachview["limitnumber"]
            sattr.itemCount = eachview["itemcount"]
            
            try:
                critid = getattr(sattr,'crit__Type_ATPortalTypeCriterion')
            except AttributeError:
                critid = sattr.addCriterion(field='Type',criterion_type='ATPortalTypeCriterion')
            if critid <> None:
                typecrit = critid
                typecrit.value = eachview["type"]
            else:
                logger.info("Could not create type criteria, critid = %s" % (critid,))
                
            try:
                critid = getattr(sattr,'crit__modified_ATSortCriterion')
            except AttributeError:
                critid = sattr.addCriterion(field='modified',criterion_type='ATSortCriterion')
            if critid <> None:
                sortcrit = critid
                sortcrit.reversed = True
            else:
                logger.info("Could not create sort criteria, critid = %s" % (critid,))
                
            logger.info("Added smart view with id : %s" % (eachview["id"],))
            
            notify(ObjectInitializedEvent(sattr))
            sattr.reindexObject()
    return out.getvalue()

def addDefaultSmartViews(portal,logger):
    out = StringIO()
    try:
        objView = getattr(portal,"views")
        if objView <> None:
            for q in defaultsmartviews:
                obj = getOrCreateType(portal,objView,q["id"],"SmartView")
                obj.title = q["title"]
                obj.description = q["description"]
                obj.query = str(q["query"])
                obj.reindexObject()
                logger.info("Created smartview for %s" % (q["title"],))
    except:
        pass
    return out.getvalue()

def assignStackerRelatedPortlet(portal):
    from ubify.policy.config import list_of_portletmanagers_for_stackerportlet_assignment,cynin_desktop_left_column_text
    static_portlet_text = cynin_desktop_left_column_text
    
    #static_portlet_nav_url = portal.absolute_url() + "/stacker-badge"
    #static_portlet_text = static_portlet_text % (static_portlet_nav_url)
    
    from plone.portlet.static import static
    assignments = (
                    static.Assignment(header='cyn.in Desktop',text=static_portlet_text,omit_border=True),
                  )
    
    for name in list_of_portletmanagers_for_stackerportlet_assignment:
        if assignments:
            try:
                portletManager = getUtility(IPortletManager, name=name)
            except ComponentLookupError:
                sm = getSiteManager(portal)
                objportletManager = PortletManager()                
                    
                sm.registerUtility(component=objportletManager,
                                   provided=IPortletManager,
                                   name = name)        
                portletManager = getUtility(IPortletManager, name=name) 
                
            assignable = getMultiAdapter((portal, portletManager,), ILocalPortletAssignmentManager)
            manager = getMultiAdapter((portal, portletManager), IPortletAssignmentMapping)
            
            if portletManager is not None:            
                chooser = INameChooser(manager)
                for assignment in assignments:
                    strtitle = assignment.title.lower()
                    strtitle = strtitle.replace(' ','-')
                    if manager.has_key(strtitle) == 0:
                        manager[chooser.chooseName(None, assignment)] = assignment
                        
def setupContentRoot(portal):
    out = StringIO()
    id = contentroot_details['id']
    title = contentroot_details['title']
    oldid = contentroot_details['oldid']
    bFlag_setlocalroles = False
    from zope.component.interfaces import ComponentLookupError
    
    already_exists = False
    try:
        obj = getattr(portal,oldid)
        if obj and obj.portal_type == 'ContentRoot':
            already_exists = True
    except:
        pass
    
    if not already_exists:
        try:
            obj = getattr(portal,id)
        except AttributeError:
            bFlag_setlocalroles = True
        try:
            obj = getOrCreateType(portal,portal,id,"ContentRoot")
            
            if obj.title == '':
                obj.title = title
                obj.reindexObject()
                
            if bFlag_setlocalroles:
                setupAuthenticatedUsersAsContributorAtContext(obj)
        except:
            pass
    return out.getvalue()

def setupAuthenticatedUsersAsContributorAtContext(context):   
    
    contributor_access = ('Contributor','Reader')
    context.manage_setLocalRoles('AuthenticatedUsers',list(contributor_access))
    context.reindexObject()

def disableGlobalAdds(portal,logger):
    out = StringIO()
    portal_types = getToolByName(portal, 'portal_types')
    fti = getattr(portal_types, 'News Item')
    fti.global_allow = False
    
    fti = getattr(portal_types, 'SpacesFolder')
    fti.global_allow = False
    fti = getattr(portal_types,'SmartviewFolder')
    fti.global_allow = False
    fti = getattr(portal_types,'RecycleBin')
    fti.global_allow = False
    fti = getattr(portal_types,'StatuslogFolder')
    fti.global_allow = False
    fti = getattr(portal_types,'ContentRoot')
    fti.global_allow = False
    
    logger.info("Disabled News Item")
    logger.info("Disabled SpacesFolder")
    logger.info("Disabled SmartviewFolder")
    logger.info("Disabled RecycleBin")
    logger.info("Disabled Statuslog Folder")
    logger.info("Disabled ContentRoot")
    return out.getvalue()

def disable_inlineEditing(portal,logger):    
    from plone.app.controlpanel.site import SiteControlPanelAdapter
    scpa = SiteControlPanelAdapter(portal)
    if scpa.enable_inline_editing:
        scpa.enable_inline_editing = False
    logger.info("Disabled inline editing")
    
def remove_navigationportlet(portal,logger):
    from plone.portlets.interfaces import IPortletManager
    from zope.component import getMultiAdapter
    from plone.portlets.interfaces import IPortletAssignmentMapping
    
    leftColumn = getUtility(IPortletManager,
                             name=u'plone.leftcolumn',
                             context=portal)
    left = getMultiAdapter((portal, leftColumn),
                            IPortletAssignmentMapping,
                            context=portal)
    if 'navigation' in left:
        del left['navigation']
        logger.info("Removed navigation portlet")
        
def remove_calendarportlet(portal,logger):
    from plone.portlets.interfaces import IPortletManager
    from zope.component import getMultiAdapter
    from plone.portlets.interfaces import IPortletAssignmentMapping
    
    rightColumn = getUtility(IPortletManager,
                             name=u'plone.rightcolumn',
                             context=portal)
    right = getMultiAdapter((portal, rightColumn),
                            IPortletAssignmentMapping,
                            context=portal)
    if 'calendar' in right:
        del right['calendar']
        logger.info("Removed calendar portlet")
    
def setchoosertype(portal,logger):    
    from Products.PluggableAuthService.plugins.ChallengeProtocolChooser import ChallengeProtocolChooser
    aclusers = getToolByName(portal,"acl_users")
    if aclusers is None:
        return
    if aclusers.chooser <> None and isinstance(aclusers.chooser, ChallengeProtocolChooser):
        if aclusers.chooser._map.has_key('RSS') == 0:
            aclusers.chooser._map.insert('RSS','http')
            logger.info("Modified chooser for RSS protocol entry.")
        if aclusers.chooser._map.has_key('CAL') == 0:
            aclusers.chooser._map.insert('CAL','http')
            logger.info("Modified chooser for CAL protocol entry.")
        if aclusers.chooser._map.has_key('FILEDOWNLOAD') == 0:
            aclusers.chooser._map.insert('FILEDOWNLOAD','http')
            
def configureRatings(portal,logger):
    try:
        types_list = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)        
        ratingstool = getToolByName(portal,'portal_ratings')
        if ratingstool != None:
            ratingstool.allowed_rating_types = types_list
            ratingstool.allowed_counting_types = types_list
            if portal.hasProperty('enableRatings') == 0:
                portal.manage_addProperty('enableRatings',True,'boolean')
            if portal.hasProperty('enableCountings') == 0:
                portal.manage_addProperty('enableCountings',True,'boolean')
                
            logger.info("Configured ratings")
        else:
            logger.info("No rating product available to configure.")
    except AttributeError:
        logger.info("No rating product available to configure.")
        
def enable_formats_fortextfield(portal,logger):
    from plone.app.controlpanel.markup import MarkupControlPanelAdapter
    mcpa = MarkupControlPanelAdapter(portal)
    mcpa.set_allowed_types(('text/html',))
    logger.info("Set alternative formats for text field ")
    logger.info(mcpa.get_allowed_types())
    
def assignCyninNavigation(portal,logger):    
    from ubify.cyninv2theme.browser.navigation import assign_cynin_navigation    
    assign_cynin_navigation(portal)
    logger.info("Assigned cyn.in navigation")
    
def reorder_contenttyperegistry(portal,logger):
    ctr = getToolByName(portal, 'content_type_registry')
    
    predicate_ids = list( ctr.predicate_ids )    
        
    for eachpredicate in ('audio_ext','video_ext'):        
        if eachpredicate not in ctr.predicate_ids:
            ctr.addPredicate(eachpredicate, 'extension' )
            if eachpredicate == 'audio_ext':
                ctr.getPredicate(eachpredicate).edit('mp3 wav')
                ctr.assignTypeName(eachpredicate,'Audio')
                ndxaudio = predicate_ids.index('audio')
                ctr.reorderPredicate(eachpredicate,ndxaudio - 1)
                logger.info("added and reordered %s type predicate" % (eachpredicate,))
            elif eachpredicate == 'video_ext':
                ctr.getPredicate(eachpredicate).edit('flv mp4')
                ctr.assignTypeName(eachpredicate,'Video')
                ndxvideo = predicate_ids.index('video')
                ctr.reorderPredicate(eachpredicate,ndxvideo - 1)
                logger.info("added and reordered %s type predicate" % (eachpredicate,))
        else:
            if eachpredicate == 'audio_ext':
                ndxaudio = predicate_ids.index('audio')
                ctr.reorderPredicate(eachpredicate,ndxaudio - 1)
                logger.info("Reordered %s type predicate" % (eachpredicate,))
            elif eachpredicate == 'video_ext':                
                ndxvideo = predicate_ids.index('video')
                ctr.reorderPredicate(eachpredicate,ndxvideo - 1)
                logger.info("Reordered %s type predicate" % (eachpredicate,))
                
def add_custom_site_properties(portal,logger):
    portal_properties = portal.portal_properties
    site_properties = getattr(portal_properties,'site_properties',None)
    if site_properties <> None:
        for prop in custom_site_properties:
            if not site_properties.hasProperty(prop['name']):
                site_properties.manage_addProperty(prop['name'],prop['value'],prop['type'])
                logger.info("Added site property for %s" % (prop['name'],))
            else:
                logger.info("Property exists : %s" % (prop['name'],))
            
def add_custom_cynin_properties(portal,logger):
    portal_properties = portal.portal_properties
    cynin_site_properties = getattr(portal_properties,'cynin_properties',None)
    if cynin_site_properties <> None:
        for prop in custom_cynin_properties:
            if not cynin_site_properties.hasProperty(prop['name']):
                cynin_site_properties.manage_addProperty(prop['name'],prop['value'],prop['type'])
                logger.info("Added site property for %s" % (prop['name'],))
            else:
                logger.info("Property exists : %s" % (prop['name'],))