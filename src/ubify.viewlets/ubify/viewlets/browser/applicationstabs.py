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

class ApplicationsTabsViewlet(ViewletBase):
    render = ViewPageTemplateFile('applicationstabs.pt')

    def update(self):
        self.applications = [
            {
            'title':'',
            'url':'home',
            'icon':'home.png',
            'selected':False,
            'visible':False,
            },
            {
            'title':'All Updates',
            'url':'app_all',
            'icon':'icon-asterisk_yellow.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Wiki',
            'url':'app_wiki',
            'icon':'wiki.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Files',
            'url':'app_files',
            'icon':'file_icon.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Blog',
            'url':'app_blog',
            'icon':'blog.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Images',
            'url':'app_images',
            'icon':'image.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Calendar',
            'url':'app_calendar',
            'icon':'calendar.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Links',
            'url':'app_links',
            'icon':'link_icon.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Videos',
            'url':'app_videos',
            'icon':'video.png',
            'selected':False,
            'visible':True,
            },
            {
            'title':'Status Log',
            'url':'app_statuslog',
            'icon':'status_online.png',
            'selected':False,
            'visible':False,
            },
            {
            'title':'Videos',
            'url':'app_videos',
            'icon':'video.png',
            'selected':False,
            'visible':False,
            },
            ]

        req = self.context.request
        if self.context.portal_type == 'ContentRoot':
            self.applications[0]['visible'] = True
            self.applications[-1]['visible'] = True
        if self.context.portal_type == 'MemberSpace':
            self.applications[-1]['visible'] = True
        last = req.physicalPathFromURL(req.getURL())[-1]
        res = [i for i in self.applications if i['url'] in last]
        if len(res)>0:
            selview = res[0]
            selview['selected'] = True
