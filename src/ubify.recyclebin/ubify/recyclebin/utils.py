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
from ZODB.POSException import ConflictError
from AccessControl.requestmethod import postonly
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from Products.CMFPlone.utils import transaction_note
from AccessControl import ClassSecurityInfo, Unauthorized
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import Unauthorized
from Products.CMFPlone.utils import _createObjectByType
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.component import createObject
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent

from ubify.recyclebin import movetotrash

security = ClassSecurityInfo()

# This is public because we don't know what permissions the user
# has on the objects to be deleted.  The restrictedTraverse and
# manage_delObjects calls should handle permission checks for us.
security.declarePublic('deleteObjectsByPaths')
def deleteObjectsByPaths(context,paths, handle_errors=True, REQUEST=None):    
    failure = {}
    success = []
    # use the portal for traversal in case we have relative paths
    portal = getToolByName(context, 'portal_url').getPortalObject()
    traverse = portal.restrictedTraverse
    for path in paths:
        # Skip and note any errors
        if handle_errors:
            sp = transaction.savepoint(optimistic=True)
        try:
            obj = traverse(path)
            obj_parent = aq_parent(aq_inner(obj))
            movetotrash(obj)            
            obj_parent.manage_delObjects([obj.getId()])
            success.append('%s (%s)' % (obj.title_or_id(), path))
        except AttributeError, details:            
            results = []
            if details.__str__().__contains__('_getReferenceAnnotations'):
                
                def getOb(obj,results):
                    
                    for eobj in obj.objectItems():
                        if hasattr(eobj[1],'objectItems'):
                            getOb(eobj[1],results)
                        results.append(eobj[1])
                    return results
                
                getOb(obj,results)
                results.append(obj)
                
                for o in results:                    
                    paths.append("/".join(o.getPhysicalPath()))
                
            if handle_errors:
                sp.rollback()
        except ConflictError:
            raise
        except LinkIntegrityNotificationException:
            raise
        except Exception, e:
            if handle_errors:
                sp.rollback()
                failure[path]= e
            else:
                raise
    transaction_note('Deleted %s' % (', '.join(success)))
    return success, failure
deleteObjectsByPaths = postonly(deleteObjectsByPaths)

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

def getGlobalRecycleBin(portal):
    from ubify.recyclebin.config import global_recyclebin_id,global_recyclebin_title,GLOBAL_RECYCLEBIN_POLICY
    isnew = False
    try:
        objRecyclebin = getattr(portal,global_recyclebin_id)
    except AttributeError:
        isnew = True
        
    objRecyclebin = getOrCreateType(portal,portal,global_recyclebin_id,"RecycleBin")
    if isnew:
        notify(ObjectInitializedEvent(objRecyclebin))
    if objRecyclebin.title == '':
        objRecyclebin.title = global_recyclebin_title
        objRecyclebin.reindexObject()
        
        from ubify.cyninv2theme import set_placeful_workflow_policy
        set_placeful_workflow_policy(objRecyclebin,GLOBAL_RECYCLEBIN_POLICY,GLOBAL_RECYCLEBIN_POLICY)
    return objRecyclebin

def getMemberRecycleBin(memberfolder):    
    from ubify.recyclebin.config import member_recyclebin_id,member_recyclebin_title,MEMBER_RECYCLEBIN_POLICY
    objRecyclebin = getOrCreateType(memberfolder,memberfolder,member_recyclebin_id,"RecycleBin")
    if objRecyclebin.title == '':
        objRecyclebin.title = member_recyclebin_title
        objRecyclebin.reindexObject()        
        
        from ubify.cyninv2theme import set_placeful_workflow_policy
        set_placeful_workflow_policy(objRecyclebin,MEMBER_RECYCLEBIN_POLICY,MEMBER_RECYCLEBIN_POLICY)
    return objRecyclebin
