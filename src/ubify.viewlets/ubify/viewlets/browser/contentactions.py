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
from zope.interface import implements, alsoProvides
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Acquisition import aq_base, aq_inner
from plone.app.layout.globals.interfaces import IViewView

class ContentActionsViewlet(ViewletBase):
    render = ViewPageTemplateFile('contentactions.pt')

    def update(self):
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        self.object_actions = context_state.actions().get('object_actions', [])

        plone_utils = getToolByName(context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.portal_actionicons = getToolByName(context, 'portal_actionicons')

        # The drop-down menus are pulled in via a simple content provider
        # from plone.app.contentmenu. This behaves differently depending on
        # whether the view is marked with IViewView. If our parent view
        # provides that marker, we should do it here as well.
        if IViewView.providedBy(self.__parent__):
            alsoProvides(self, IViewView)

    def icon(self, action):
        icon = action.get('icon', None)
        if icon is None:
            icon = self.getIconFor('content_actions', action['id'])
        return icon
