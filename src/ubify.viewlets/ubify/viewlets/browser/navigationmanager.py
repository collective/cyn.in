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


from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility,getAdapters
from AccessControl import getSecurityManager
from ubify.policy.config import contentroot_details,collection_details
from zope.app.publisher.interfaces.browser import IBrowserMenu

class NavigationViewlet(ViewletBase):
    render = ViewPageTemplateFile('navigationmanager.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')

        typetool= getToolByName(self.context, 'portal_types')
        portal = portal_state.portal()
        
        self.display_managemenu = False
        sm = getSecurityManager()
        if sm.checkPermission('Manage portal', self.context):
            self.display_managemenu = True
            
        self.showCollections = self.get_collection_visibility(portal)
        self.showSpaces = self.get_spaces_visibility(portal)
            
    def get_collection_visibility(self,portal):
        is_visible = False
        viewsid = collection_details['id']
        objViews = getattr(portal,viewsid,None)
        if objViews <> None:
            menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')
            addmenuitems = menu.getMenuItems(objViews,self.request)
            viewsadd = [ob for ob in addmenuitems if ob.has_key('id') and ob['id'] in ('Topic',)]
            
            if len(viewsadd) > 0:
                is_visible = True
            else:
                ct = getattr(portal,'portal_catalog')
                if ct <> None:
                    query = {}
                    query['portal_type'] = ('Topic','SmartView')
                    query['path'] = {'query': "/".join(objViews.getPhysicalPath()),'depth':1}
                    
                    results = ct(**(query))
                    
                    if len(results) > 0:
                        is_visible = True            
        return is_visible
    
    def get_spaces_visibility(self,portal):
        is_visible = False
        rootid = contentroot_details['id']
        objRoot = getattr(portal,rootid,None)
        if objRoot <> None:
            menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')
            addmenuitems = menu.getMenuItems(objRoot,self.request)
            spacesadd = [ob for ob in addmenuitems if ob.has_key('id') and ob['id'] in ('ContentSpace',)]
            
            if len(spacesadd) > 0:
                is_visible = True                
            else:
                ct = getattr(portal,'portal_catalog')
                if ct <> None:
                    query = {}
                    query['portal_type'] = ('ContentSpace')
                    query['path'] = {'query': "/".join(objRoot.getPhysicalPath()),'depth':1}
                    
                    results = ct(**(query))
                    
                    if len(results) > 0:
                        is_visible = True            
        return is_visible