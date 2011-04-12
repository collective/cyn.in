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
from Acquisition import aq_inner

class SpaceMembersPageViewlet(ViewletBase):

    render = ViewPageTemplateFile('spacememberspageviewlet.pt')

    def generate_dict_list(self,listObjects,context):
        user_role_map = []

        for user in listObjects:

            roleslist = context.get_local_roles_for_userid(user)
            if len(roleslist) > 0:
                user_role_map.append(dict(useritem = user,roles = roleslist ))
            else:
                roles_groupslist = []
                aclusers = context.portal_membership.acl_users
                objUser = aclusers.getUserById(user)
                listGroups = objUser.getGroups()
                for gr in listGroups:
                    templist = context.get_local_roles_for_userid(gr)
                    for lst in templist:
                        if lst not in roleslist:
                            roles_groupslist.append(lst)
                roles_groupslist.sort()
                user_role_map.append(dict(useritem = user,roles = roles_groupslist ))

        return user_role_map

    def checkIfGroupGetUsers(self,listobjects,context):
        listdummy = []
        pm = context.portal_membership
        aclusers = pm.acl_users

        for obj in listobjects:
            if aclusers.getUserById(obj) is None:
                #user doesn't exists with name search in group
                objGroup = aclusers.getGroupById(obj)
                if objGroup <> None:
                    listtemp = objGroup.listAssignedPrincipals(obj)
                    for tempobj in listtemp:
                        if len(tempobj) > 0 and aclusers.getUserById(tempobj[0]):
                            listdummy.append(tempobj[0])
            else:
                listdummy.append(obj)

        return listdummy

    def update(self):
        self.title = "Members"
        self.results = []
        member_type = "Member"

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')

        try:
            membertype = self.request.membertype
            if membertype.lower() not in ('reader','contributor','editor','reviewer','member'):
                membertype = member_type
        except AttributeError:
            membertype = member_type
            pass

        self.anonymous = portal_state.anonymous()

        self.catalog = plone_tools.catalog()

        if not self.anonymous:
            role_to_search = membertype.lower()

            listReaders = context.users_with_local_role('Reader')
            listReaders = self.checkIfGroupGetUsers(listReaders,context)

            listContributors = context.users_with_local_role('Contributor')
            listContributors = self.checkIfGroupGetUsers(listContributors,context)

            listReviewers = context.users_with_local_role('Reviewer')
            listReviewers = self.checkIfGroupGetUsers(listReviewers,context)

            listEditors = context.users_with_local_role('Editor')
            listEditors = self.checkIfGroupGetUsers(listEditors,context)

            objresults = []
            if role_to_search == 'reader':
                self.title = "Readers"
                for user in listReaders:
                    if user not in listContributors and user not in listReviewers and user not in listEditors:
                        objresults.append(user)
                objresults.sort()
            elif role_to_search == 'contributor':
                self.title = "Contributors"
                for user in listContributors:
                    if user not in listReviewers and user not in listEditors:
                        objresults.append(user)
                objresults.sort()
            elif role_to_search == 'reviewer':
                self.title = "Reviewers"
                for user in listReviewers:
                    if user not in listEditors:
                        objresults.append(user)
                objresults.sort()
            elif role_to_search == 'editor':
                self.title = "Editors"
                objresults = listEditors
                objresults.sort()
            else:
                listmembers = []
                listtemp = []

                for userEditor in listEditors:
                    listtemp.append(userEditor)
                    listtemp.sort()
                for userReviewer in listReviewers:
                    if userReviewer not in listmembers and userReviewer not in listtemp:
                        listmembers.append(userReviewer)
                for userContributor in listContributors:
                    if userContributor not in listmembers and userContributor not in listtemp:
                        listmembers.append(userContributor)
                for userReader in listReaders:
                    if userReader not in listmembers and userReader not in listtemp:
                        listmembers.append(userReader)

                listmembers.sort()
                listtemp.extend(listmembers)
                objresults.extend(listtemp)

            self.results = self.generate_dict_list(objresults,context)

    def batch_results(self,b_size):
        from Products.CMFPlone import Batch
        b_start = self.context.REQUEST.get('b_start', 0)
        batch = Batch(self.results, b_size, int(b_start), orphan=0)
        return batch

    def concatroles(self,roleslist):

        strVal = ""
        for obrole in roleslist:
            strVal = strVal + obrole + ', '
        strVal = str(strVal)
        strVal = strVal.rstrip(', ')
        return strVal
