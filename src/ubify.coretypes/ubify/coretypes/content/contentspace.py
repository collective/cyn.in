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

from Products.ATContentTypes.content.folder import ATBTreeFolder as BaseClass
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema as DefaultSchema

from Products.ATContentTypes.content.base import registerATCT

from ubify.coretypes.config import PROJECTNAME,applications
from zope.interface import implements
from ubify.coretypes.interfaces import IImportExportCoretype,ISyndication,IApplicationPerspectives,IContentSpace, ITypesRestriction
from Products.CMFCore.utils import getToolByName

schema = DefaultSchema.copy()


class ContentSpace(BaseClass):
    implements(IContentSpace,IImportExportCoretype,ISyndication,IApplicationPerspectives,ITypesRestriction)

    __doc__ = BaseClass.__doc__ + "(customizable version)"

    portal_type = "ContentSpace"
    archetype_name = BaseClass.archetype_name

    if schema['title'] <> None and schema['title'].widget <> None:
        if schema['title'].widget.maxlength:
            schema['title'].widget.maxlength = '60'
    
    schema = schema
    
    # Override initializeArchetype to turn on syndication by default
    def initializeArchetype(self, **kwargs):        
        ret_val = BaseClass.initializeArchetype(self, **kwargs)
        # Enable topic syndication by default
        self.enableSyndication()
        return ret_val
    
    def enableSyndication(self):
        syn_tool = getToolByName(self, 'portal_syndication', None)
        if syn_tool is not None:
            if (syn_tool.isSiteSyndicationAllowed() and
                                    not syn_tool.isSyndicationAllowed(self)):
                syn_tool.enableSyndication(self)
    
    def getEntries(self,num_of_entries):
        """Getter for syndacation support
        """
        syn_tool = getToolByName(self, 'portal_syndication')
        if num_of_entries is None:
            num_of_entries = int(syn_tool.getMaxItems(self))
        
        return self.queryfolderbytype()[0][:num_of_entries]
    
    def synContentValues(self):
        """Getter for syndacation support
        """        
        syn_tool = getToolByName(self, 'portal_syndication')
        num_of_entries = int(syn_tool.getMaxItems(self))
        brains = self.getEntries(num_of_entries)
        objs = [brain.getObject() for brain in brains]
        return [obj for obj in objs if obj is not None]
        
    def listApplications(self):
        apps = []
        apps.extend(applications)
        gen_items = [k['id'] for k in apps[1:3]]
        type_items = [k['id'] for k in apps[4:]]
        apps.remove(apps[11])
        showall = True
        if self.hasProperty('availableappviews'):
            available_appviews = self.getProperty('availableappviews')
            
            if len(available_appviews) > 0:
                showall = False
                for eachapp in apps:
                    if eachapp['id'] in available_appviews:
                        eachapp['visible'] = True
                    else:
                        eachapp['visible'] = False
                    if eachapp['id'] == 'genericseparator':
                        eachapp['visible'] = len([k for k in available_appviews if k in gen_items]) > 0
                    elif eachapp['id'] == 'appviewseparator':
                        eachapp['visible'] = len([k for k in available_appviews if k in type_items]) > 0
        if showall:
            for eachapp in apps:
                eachapp['visible'] = True
        returnapps = [k for k in apps if k['visible'] == True]        
        return returnapps
    
    def disallowedtypes(self):
        ptypes_tool = getToolByName(self,'portal_types')
        fti = getattr(ptypes_tool,self.portal_type)
        allowedtypes = []
        if fti <> None:
            allowedtypes = fti.allowed_content_types
        
        dis_types = [obj for obj in allowedtypes if obj not in self.getImmediatelyAddableTypes()]
        
        return dis_types

registerATCT(ContentSpace, PROJECTNAME)