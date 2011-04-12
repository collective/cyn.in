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
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from urllib import quote_plus


class MyMenu(ViewletBase):
    render = ViewPageTemplateFile('mymenu.pt')
    mymenuvisible = True

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

        sm = getSecurityManager()

        self.cportal_url = portal_state.portal_url()

        self.user_actions = context_state.actions().get('user', None)
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.anonymous = portal_state.anonymous()
        #import pdb;pdb.set_trace()
        if not self.anonymous:

            member = portal_state.member()
            userid = member.getId()

            if sm.checkPermission('Portlets: Manage own portlets', self.context):
                self.homelink_url = self.cportal_url + '/dashboard'
            else:
                self.homelink_url = self.cportal_url + '/author/' + quote_plus(userid)

            member_info = tools.membership().getMemberInfo(member.getId())
            self.fullname = member_info.get('fullname', '')
            self.user_name = userid

            #setting Logged in user portrait
            portal_membership = getToolByName(self.context,'portal_membership')
            portrait = portal_membership.getPersonalPortrait(userid,1)
            self.portraiturl = portrait.absolute_url()

            self.display_sitesetuplink = False
