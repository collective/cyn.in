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

from ubify.coretypes.content import ATDocument
from ubify.coretypes.content import ATFolder
from ubify.coretypes.content import ATBTreeFolder
from ubify.coretypes.content import ATTopic
from ubify.coretypes.content import ATImage
from ubify.coretypes.content import ATFile
from ubify.coretypes.content import ATLink
from ubify.coretypes.content import ATFavorite
from ubify.coretypes.content import ATEvent
from ubify.coretypes.content import ATNewsItem
from ubify.coretypes.content import LinkDirectory

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
                #o.__class__ = new_base[typename]
                #o._p_changed = 1
                convertObject(o,typename,new_base[typename])
        except AttributeError:
            a = "a" #Empty statement? (dkg)

def migrateTypes(self, out, types = TYPES_TO_MIGRATE):
    """call migrateType for all types where we want to have a new base"""    
    for typename in types:
        if new_base.has_key(typename):
            migrateType(self, typename)
            print >> out, "migrating %s" % typename 
            
def convertObject(o,oldtype,newtype,ignore = False):
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
    }
def migrateApplicationFolders(portal,out):
    #get all inner applications
    ###import pdb;pdb.set_trace()
    ct = getToolByName(portal, 'portal_catalog')
    for type in cynin_applications_tomigrate:
        objects = [b.getObject() for b in ct(portal_type=type)]
        objects.reverse()
        for o in objects:
            parent = o.getParentNode()
            parenttype = parent.portal_type
            try:
                if parenttype == type and o.__class__ != new_base_folder['Folder']:                    
                    convertObject(o,type,new_base_folder['Folder'],ignore = True)
            except AttributeError:
                a = "a" #Empty statement? (dkg)