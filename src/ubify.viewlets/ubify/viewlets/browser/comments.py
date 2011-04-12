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
from plone.app.layout.viewlets.comments import CommentsViewlet as BaseClass
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from DateTime import DateTime

class CommentsViewlet(BaseClass):
    render = ViewPageTemplateFile('comments.pt')

    def member_avatarurl(self, creator):
        """
        Returns the image of the URL of the item's avatar
        """
        return  self.context.portal_membership.getPersonalPortrait(creator).absolute_url()

    def update(self):
        BaseClass.update(self)
        self.lastcommentid = '0'
        self.lasttimestamp = self.getlastchangedate()
        
        if self.request.has_key('comcynapsecyninnewcommentsubmit'):
            #A new comment was submitted
            if self.request.has_key('comcynapsecyninNewCommentSubject') and self.request.has_key('comcynapsecyninNewCommentBody') and self.request.has_key('comcynapsecynincontextUID'):
                cont_uid = self.request['comcynapsecynincontextUID'];
                query = {'UID':cont_uid}
                pdt = self.portal_discussion
                cat = getToolByName(self.context, 'uid_catalog')
                resbrains = cat.searchResults(query)
                if len(resbrains) == 1:
                    contobj = resbrains[0].getObject()
                    if contobj.isDiscussable() and self.canreply(contobj) > 0:
                        dobj = pdt.getDiscussionFor(contobj)
                        id = dobj.createReply(title="", text=self.request['comcynapsecyninNewCommentBody'], Creator=self.current_user())
                        reply = dobj.getReply(id)
                        if reply <> None:
                            from ubify.cyninv2theme import triggerAddOnDiscussionItem
                            triggerAddOnDiscussionItem(reply)
            else:
                return

    def canreply(self,obj):
        return getSecurityManager().checkPermission('Reply to item', aq_inner(obj)) > 0
    def current_user(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getAuthenticatedMember().getId()
    def getlastchangedate(self):        
        lastchangedate = DateTime().timeTime()
        
        pdt = self.portal_discussion
        if self.context.isDiscussable():
            dobj = pdt.getDiscussionFor(self.context)
            comments = dobj.objectValues()
            comments.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
            if len(comments) > 0:
                recentcomment = comments[0]
                if recentcomment <> None:
                    commentmodifiedat = recentcomment.modified()
                    lastchangedate = commentmodifiedat.timeTime()
                    self.lastcommentid = recentcomment.id
                
        return lastchangedate
        