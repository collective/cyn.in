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
from ubify.cyninv2theme import setCurrentStatusMessageForUser

class MyAreaBlockViewlet(ViewletBase):
    render = ViewPageTemplateFile('myareablock.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

        sm = getSecurityManager()

        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.has_status_message = False

        self.anonymous = portal_state.anonymous()
        if not self.anonymous:
            self.user_name = portal_state.member().getId()
            if self.request.has_key('com.cynapse.cynin.statusmessagesubmit') and self.request.has_key('com.cynapse.cynin.statusmessageinput'):
                #User pressed submit button on set status
                setCurrentStatusMessageForUser(portal_state.portal(),self.user_name,self.request['com.cynapse.cynin.statusmessageinput'])
            self.status_messages = self.context.portal_catalog.searchResults(Creator = portal_state.member().getId(),portal_type=('StatuslogItem',),sort_on = 'created',sort_order='reverse',sort_limit=1)

            if sm.checkPermission('Portlets: Manage own portlets', self.context):
                self.homelink_url = '/dashboard'
            else:
                self.homelink_url = '/author/' + quote_plus(portal_state.member().getId())

            member_info = tools.membership().getMemberInfo(portal_state.member().getId())
            self.fullname = member_info.get('fullname', '')

            #setting Logged in user portrait
            portal_membership = getToolByName(self.context,'portal_membership')
            portrait = portal_membership.getPersonalPortrait(portal_state.member().getId(),1)
            self.portraiturl = portrait.absolute_url()
            
            self.messageuid = ''
            
            
            status_messages = self.context.portal_catalog.searchResults(Creator = self.user_name,portal_type=('StatuslogItem',),sort_on = 'created',sort_order='reverse',sort_limit=1);
            if len(status_messages) > 0:
                self.has_status_message = True
                self.recent_message = status_messages[0].Title
                self.messageuid = status_messages[0].UID
                full_message = status_messages[0].getObject()
                pdt = getToolByName(self.context, 'portal_discussion', None)
                if full_message.isDiscussable():
                    self.discuss_url = full_message.absolute_url()
                    self.status_comment_count = pdt.getDiscussionFor(full_message).replyCount(full_message)
            else:
                self.discuss_url = ''
                self.status_comment_count = 0
                self.recent_message = ""
