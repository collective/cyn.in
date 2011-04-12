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
from ubify.viewlets.config import plone_site_type_title

class ItemtitleViewlet(ViewletBase):
    render = ViewPageTemplateFile('itemtitle.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        typetool= getToolByName(self.context, 'portal_types')
        portal_title = portal_state.portal_title()
        object_title = context_state.object_title()
        object_typename = self.context.portal_type
        object_typeobj = typetool[object_typename]
        self.typeiconname = object_typeobj.content_icon
        if object_typeobj.title == '' and self.context.portal_type.lower() == 'plone site':
            self.typetitle = plone_site_type_title
        else:
            self.typetitle = object_typeobj.title
        self.app_name = object_title
        if self.context.portal_type.lower() == 'plone site':
            self.tdescription = 'cyn.in site|A cyn.in site allows instant collaboration among peers and provides a central social computer and network.'
        else:
            self.tdescription = self.typetitle + '|' + object_typeobj.description
        self.isaddscreen = False
        if hasattr(context_state.parent(),'portal_type') and context_state.parent().portal_type == 'TempFolder':
            self.isaddscreen = True
