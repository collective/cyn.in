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

class SpaceIconViewlet(ViewletBase):
    render = ViewPageTemplateFile('space_icon.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        cportal_url = portal_state.portal_url()

        current_object = self.context.aq_inner
        self.has_space_icon = False
        self.space_icon = ""
        self.space_url = ""

        parentslist = current_object.aq_chain
        new_object = None
        found = 0
        try:
            for type in parentslist:
                if type.portal_type == 'Space' and type.meta_type == 'Space':
                    new_object = type
                    found = 1
                if found == 1:
                    break
        except AttributeError:
                a = self.space_icon
        if new_object <> None:
            #implement code here for binding space icon
            if new_object.space_icon <> "":
                self.space_icon = cportal_url + "/" + new_object.space_icon
            else:
                self.space_icon = default_space_icon
            self.space_url = new_object.absolute_url()
            self.has_space_icon = True
        else:
            self.site_icon = portal_state.portal_url() + "/logo.jpg"
            self.site_url = portal_state.portal_url()
            self.render = ViewPageTemplateFile('site_logo.pt')
