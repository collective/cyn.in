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
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.app.publisher.interfaces.browser import IBrowserMenu
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from ubify.cyninv2theme import getRootURL

# Sample code for a basic viewlet (In order to use it, you'll have to):
# - Un-comment the following useable piece of code (viewlet python class).
# - Rename the vielwet template file ('browser/viewlet.pt') and edit the
#   following python code accordingly.
# - Edit the class and template to make them suit your needs.
# - Make sure your viewlet is correctly registered in 'browser/configure.zcml'.
# - If you need it to appear in a specific order inside its viewlet manager,
#   edit 'profiles/default/viewlets.xml' accordingly.
# - Restart Zope.
# - If you edited any file in 'profiles/default/', reinstall your package.
# - Once you're happy with your viewlet implementation, remove any related
#   (unwanted) inline documentation  ;-p

#class MyViewlet(ViewletBase):
#    render = ViewPageTemplateFile('viewlet.pt')
#
#    def update(self):
#        self.computed_value = 'any output'


class AllSpacesViewlet(ViewletBase):

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
                            ob['Title'] = "Add " + ob['title']
                        if ob.has_key('portal_type') == False:
                            ob['portal_type'] = ob['id']
                        objlist.append(ob)

        except AttributeError:
            pass

        return objlist

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),name=u'plone_portal_state')

        catalog = getToolByName(self.context, "portal_catalog")
        p_url = getToolByName(self.context,"portal_url")

        #strPath = "/" + self.context.portal_url.getPortalObject().virtual_url_path() + "/spaces"
        strPath = "/".join(p_url.getPortalObject().getPhysicalPath()) + getRootURL()
        query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['ContentSpace'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
        objects = [b.getObject() for b in catalog(query)]
        self.spacesbrains = objects

        strPath = "/".join(p_url.getPortalObject().getPhysicalPath()) + "/views"
        query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['SmartView','Topic'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
        objects = [b.getObject() for b in catalog(query)]
        self.viewbrains = objects

        self.display_managemenu = False
        sm = getSecurityManager()
        if sm.checkPermission('Manage portal', self.context):
            self.display_managemenu = True

    render = ViewPageTemplateFile('allspacesviewlet.pt')
    recurse = ViewPageTemplateFile('recursespace.pt')
    recurseview = ViewPageTemplateFile('recurseview.pt')

    def getChildren(self,item):
        catalog = getToolByName(self.context, "portal_catalog")
        #import pdb;pdb.set_trace()
        try:
            strPath = "/".join(item.getPhysicalPath())
            query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['ContentSpace'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
            self.options = [b.getObject() for b in catalog(query)]
            #import pdb;pdb.set_trace()
            outp = self.recurse(self.options).strip()
            return outp
        except AttributeError:
            return ""

    def getChildrenViews(self,item):
        catalog = getToolByName(self.context, "portal_catalog")

        try:
            strPath = "/".join(item.getPhysicalPath())
            query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['SmartView','Topic'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
            self.options = [b.getObject() for b in catalog(query)]
            outp = self.recurseview(self.options).strip()
            return outp
        except AttributeError:
            return ""

    def getCssClass(self,classnormal,classmanage):
        if self.display_managemenu == True:
            return classmanage
        else:
            return classnormal
