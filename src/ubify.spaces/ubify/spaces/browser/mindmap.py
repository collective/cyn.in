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
from Products.Five import BrowserView
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _

from ubify.spaces.interfaces import IMindMappable
from ubify.spaces.config import mindmapshowabletypes
from Products.CMFCore.utils import getToolByName
import logging
from ubify.policy.config import spacesdefaultaddablenonfolderishtypes

class SpaceFreeMindMap(BrowserView):
    """Contains backend code the xml template in mindmap.pt
    """

    template = ViewPageTemplateFile('mindmap.xml')
    recurse = ViewPageTemplateFile('mindmap_recurse.xml')

        
    def __call__(self):        
        self.logger = logging.getLogger()
        
        self.isfullview = False
        self.showleafitems = False
        
        if 'fullviewmapdata' in self.request.steps:
            self.isfullview = True
        self.typetool= getToolByName(self.context, 'portal_types')
        if self.isfullview:
            portal = self.context.portal_url.getPortalObject()
            mnode = portal
            return self.template(mainnode=portal)
        else:
            if self.context.portal_type == 'ContentRoot':
                portal = self.context.portal_url.getPortalObject()
                mnode = portal
                return self.template(mainnode=portal)
            else:
                return self.template(mainnode=self.context)        
    
    def getTypeIcon(self,obj):
        object_typename = obj.portal_type
        object_typeobj = self.typetool[object_typename]
        fulliconpath = object_typeobj.content_icon
        #self.logger.info('returned typeicon: %s' % (fulliconpath))
        return fulliconpath
    
    def getChildren(self,obj):        
        """Gets the immediate children of the passed object"""
        
        cat = obj._getCatalogTool()
        currpath = '/'.join(obj.getPhysicalPath())
        display_portal_types = mindmapshowabletypes
        #import pdb; pdb.set_trace()
        
        if self.showleafitems:
            display_portal_types = mindmapshowabletypes + spacesdefaultaddablenonfolderishtypes
        else:
            if self.context.portal_type == 'Plone Site' or obj.portal_type in ('ContentRoot','ContentSpace'):
                display_portal_types = mindmapshowabletypes            
            else:
                display_portal_types = mindmapshowabletypes + spacesdefaultaddablenonfolderishtypes
            
        catresults = cat.searchResults({'path': {'query': currpath, 'depth': 1},'portal_type':display_portal_types})
        
        return catresults        

def pathsort(x,y):
    """ Sorts by path of object first and then by string"""
    #DKG: Unused. Was written to sort a mybrains list based on the paths of the objects in it.
    xpath = x.getPath()
    ypath = y.getPath()
    xsplit = xpath.split('/')
    ysplit = ypath.split('/')
    if len(xsplit) > len(ysplit):
        return 1
    elif len(xsplit) < len(ysplit):
        return -1
    else:  #objects are peers in path
        if xpath > ypath:
            return 1
        elif xpath < ypath:
            return -1
        else: #objects are having same path!?!?!
            return 0
