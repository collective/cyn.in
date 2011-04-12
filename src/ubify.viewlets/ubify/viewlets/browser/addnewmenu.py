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
from zope.app.publisher.interfaces.browser import IBrowserMenu

from ubify.policy.config import spacesdefaultaddablenonfolderishtypes
from Acquisition import aq_inner, aq_base, aq_parent
from ubify.cyninv2theme import checkHasPermission, getRootID, getLocationListForAddContent, canAddContent, getBestMatchedLocationForAddingContent, getDisallowedTypes

class AddNewMenuViewlet(ViewletBase):
    render = ViewPageTemplateFile('addnew_menu.pt')

    def getAddMenuItems(self,portal,id):
        objlist = []
        try:
            objMenu = getattr(portal,id)
            menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')
            newmenu = menu.getMenuItems(objMenu,self.request)

            for ob in newmenu:
                if ob['extra']['id'] <> '_settings' and ob['extra']['id'] <> 'settings':
                    if id == 'views' and ob.has_key('id'):
                        if ob.has_key('absolute_url') == False:
                            ob['absolute_url'] = ob['action']
                        if ob.has_key('Title') == False:
                            ob['Title'] = ob['title']
                        if ob.has_key('portal_type') == False:
                            ob['portal_type'] = ob['id']
                        objlist.append(ob)

        except AttributeError:
            pass

        return objlist

    def update(self):
        self.addnewitems = []
        self.viewmenu = []
        self.currentcontextmenu = []        
        self.currentcontexttitle = ''
        
        self.contextualurl = ''
        self.contextuid = ''
        self.contextdisallowedtypes = []
        
        portal_state = getMultiAdapter((self.context, self.request),name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')
        typetool= getToolByName(self.context, 'portal_types')
        object_typename = self.context.portal_type
        portal = portal_state.portal()
        
        self.spaceslist = getLocationListForAddContent(portal)        
        
        self.viewmenu = self.getAddMenuItems(portal,'views')
        self.anonymous = portal_state.anonymous()
        if not self.anonymous:
            for eachtype in spacesdefaultaddablenonfolderishtypes:
                object_typeobj = typetool[eachtype]
                if object_typeobj <> None:
                    self.addnewitems.append({'id': object_typeobj.id, 'title': object_typeobj.Title(),'description':object_typeobj.Description(),'icon': object_typeobj.content_icon})
            
            self.addnewcontainers = []
            object_typeobj = typetool['ContentSpace']
            self.addnewcontainers.append({'id': object_typeobj.id, 'title': object_typeobj.Title(),'description':object_typeobj.Description(),'icon': object_typeobj.content_icon})
            
            self.addnewitems.sort(lambda x,y: cmp(x['title'].lower(),y['title'].lower()))

            
            menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')
            
            if object_typename in ('RecycleBin',):
                self.currentcontextmenu = []
            elif object_typename in ('Plone Site',):
                #get root object and check for it
                objRoot = getattr(portal,getRootID())
                if checkHasPermission('Add portal content', aq_inner(objRoot)):
                    self.currentcontextmenu = menu.getMenuItems(objRoot,self.request)
                    self.contextualurl = aq_inner(objRoot).absolute_url()
                    self.currentcontexttitle = objRoot.Title()
                    self.contextuid = objRoot.UID()
                    self.contextdisallowedtypes = objRoot.disallowedtypes()
            else:
                if object_typename in ('ContentRoot','ContentSpace') and self.context.isPrincipiaFolderish and checkHasPermission('Add portal content',aq_inner(self.context)):                
                    self.currentcontextmenu = menu.getMenuItems(self.context, self.request)
                    self.contextualurl = aq_inner(self.context).absolute_url()
                    
                    if object_typename in ('ContentRoot','ContentSpace'):
                        self.currentcontexttitle = context_state.object_title()
                        self.contextuid = aq_inner(self.context).UID()
                        self.contextdisallowedtypes = (aq_inner(self.context)).disallowedtypes()
                else:
                    currentobject = aq_inner(self.context)
                    parentList = currentobject.aq_chain
                    parentspace = None
                    found = 0
            
                    try:
                        for type in parentList:
                            if type.portal_type in ('ContentRoot','ContentSpace'):
                                parentspace = type
                                if checkHasPermission('Add portal content',aq_inner(parentspace)):
                                    found = 1
                            if found == 1:
                                break
                    except AttributeError:
                        parentspace = None
                        pass
                    
                    if parentspace <> None:
                        self.currentcontextmenu = menu.getMenuItems(aq_inner(parentspace),self.request)
                        self.currentcontexttitle = parentspace.Title()
                        self.contextualurl = parentspace.absolute_url()
                        self.contextuid = parentspace.UID()
                        self.contextdisallowedtypes = parentspace.disallowedtypes()
            
            #strip out 'settings' item(s)
            self.currentcontextmenu = [ob for ob in self.currentcontextmenu if ob['extra']['id'] <> 'settings' and  ob['extra']['id'] <> '_settings']
            if self.contextuid == '':
                #best match element is brain                
                bestmatchedspace = getBestMatchedLocationForAddingContent(portal)
                if bestmatchedspace:
                    self.currentcontexttitle = bestmatchedspace.Title
                    self.contextuid = bestmatchedspace.UID
                    self.contextualurl = bestmatchedspace.getURL()
                    self.contextdisallowedtypes = bestmatchedspace.disallowedtypes

    def icon(self, action):
        icon = action.get('icon', None)
        if icon is None:
            icon = self.getIconFor('content_actions', action['id'])
        return icon
