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
from Products.Archetypes.atapi import *

from Products.ATContentTypes.content.folder \
     import ATFolder as BaseClass
from Products.ATContentTypes.content.folder \
     import ATFolderSchema as DefaultSchema

from Products.ATContentTypes.content.base import registerATCT

from ubify.coretypes.config import PROJECTNAME


schema = DefaultSchema.copy()


class ATFolder(BaseClass):

    __doc__ = BaseClass.__doc__ + "(customizable version)"
    
    portal_type = BaseClass.portal_type
    archetype_name = BaseClass.archetype_name

    schema = schema
    
    def manage_afterAdd(self, item, container):        
        if container.portal_type <> 'TempFolder' and item.portal_type == 'Folder':
            #import pdb;pdb.set_trace()
            parentObj = item.getParentNode()
            item.setConstrainTypesMode(1)
            item.setImmediatelyAddableTypes(parentObj.getLocallyAllowedTypes())
            item.setLocallyAllowedTypes(parentObj.getLocallyAllowedTypes())


registerATCT(ATFolder, PROJECTNAME)

