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

from ubify.policy import CyninMessageFactory as _
from ubify.cyninv2theme import getAvailableAppViews

class ApplicationsMenuViewlet(ViewletBase):
    render = ViewPageTemplateFile('ApplicationsMenuViewlet.pt')

    def update(self):
        menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')

        portal_state = getMultiAdapter((self.context, self.request),name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')

        typetool= getToolByName(self.context, 'portal_types')

        object_typename = self.context.portal_type
        fti = getattr(typetool,'Plone Site')
        self.showsitehomemenu = False

        view = self.context.restrictedTraverse('@@plone')
        tabs = view.prepareObjectTabs()
        for eachtab in tabs:
            if eachtab['id'].lower() == 'edit' and eachtab['selected']:
                self.addnewitems = []
        
        available_appviews = []
        show_all_menu = False
        
        if self.context.hasProperty('availableappviews'):
            available_appviews = self.context.getProperty('availableappviews')
            
        if len(available_appviews) == 0:
            show_all_menu = True
            
        self.applications = []
        self.activitystream_item = {}
        self.dashboard_item = {}
        self.applicationviews = getAvailableAppViews(self.context)        
        
        for eachappview in self.applicationviews:
            if eachappview.id == 'activitystream':
                self.activitystream_item = {
                        'title':_(eachappview.title),
                        'id':eachappview.id,
                        'url':eachappview.url_expr.replace("string:",''),
                        'icon':eachappview.icon_expr.replace("string:",''),
                        'selected':False,
                        'visible':show_all_menu or eachappview.id in available_appviews,
                    }
            elif eachappview.id == 'dashboard':
                self.dashboard_item = {
                        'title':_(eachappview.title),
                        'id':eachappview.id,
                        'url':eachappview.url_expr.replace("string:",''),
                        'icon':eachappview.icon_expr.replace("string:",''),
                        'selected':False,
                        'visible':show_all_menu or eachappview.id in available_appviews,
                    }
            else:
                self.applications.append(
                    {
                        'title':_(eachappview.title),
                        'id':eachappview.id,
                        'url':eachappview.url_expr.replace("string:",''),
                        'icon':eachappview.icon_expr.replace("string:",''),
                        'selected':False,
                        'visible':show_all_menu or eachappview.id in available_appviews,
                    }
                )
        
        ##Decide what items to show in the Application menus, here::
        req = self.request
        last = req.physicalPathFromURL(req.getURL())[-1]
        res = [i for i in self.applications if i['url'] in last and i['url'] != '']
        self.lastpart = last
        self.dashboard_selected = False
        self.activitystream_selected = False
        
        if len(res)>0:
            selview = res[0]
            selview['selected'] = True
            self.selectedItem = selview            
        elif last in ('pastEvents','upcomingEvents'):
            calendar_applications = [k for k in self.applications if k['id'].lower() == u'calendar']
            if len(calendar_applications) > 0:
                selview = calendar_applications[0]
                selview['selected'] = True
                self.selectedItem = selview
            else:
                self.selectedItem = None
        elif last in ('placeful_workflow_configuration'):
            selview = {'title':'Workflow Policy','url':'placeful_workflow_configuration','icon':'icon-arrow_switch.png','selected':False,'visible':False,}
            self.selectedItem = selview
        elif last in ('home','dashboard'):
            self.dashboard_selected = True            
        elif last in ('app_all'):
            self.activitystream_selected = True            
        else:
            self.selectedItem = None

        
        
        self.ploneview = self.context.restrictedTraverse('@@plone');
        self.view_actions = self.ploneview.prepareObjectTabs();
        selected_views = [br for br in self.view_actions if br['selected']==True]
        if len(selected_views) > 0:
            self.manage_selectedItem = selected_views[0]
        else:
            self.manage_selectedItem = None

        if self.context.portal_type in ('ContentRoot','ContentSpace','MemberSpace'):
            if self.context.portal_type in ('ContentRoot','MemberSpace',):
                ## Turn on Status Log view
                statuslogs = [k for k in self.applications if k['id'].lower() == 'statusmessage']                
                if len(statuslogs) > 0:
                    selview = statuslogs[0]
                    selview['visible'] = show_all_menu or selview['id'] in available_appviews
            plonecontentmenu = getUtility(IBrowserMenu,name='plone_contentmenu')
            menuitems = plonecontentmenu.getMenuItems(self.context,self.request)

            workflowMenuItem = [mi for mi in menuitems if mi.has_key('extra') and mi['extra'].has_key('state') and mi['extra'].has_key('stateTitle')]
            self.workflowmenuitems = None
            if len(workflowMenuItem) > 0:
                self.workflowmenuitems = workflowMenuItem[0]
                
        self.show_appview_nonselected = len([k for k in self.applications if k['visible']]) > 0

    def icon(self, action):
        icon = action.get('icon', None)
        if icon is None:
            icon = self.getIconFor('content_actions', action['id'])
        return icon
