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
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import NotFound
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from DateTime import DateTime

from ubify.viewlets.browser.custommethods import get_displaycountforlist,canreply,getjsondata

from ubify.cyninv2theme import getListingTemplateForContextParent

class ItemDetails(BrowserView):
    """Contains backend code for expanded item
    """
    
    template = ViewPageTemplateFile('itemdetails.pt')
    
    def __call__(self):
        uid = None
        itemindex = 0
        if self.request.form.has_key('uid'):
            uid = self.request.form['uid']
        if self.request.form.has_key('itemindex'):
            itemindex = self.request.form['itemindex']
            
        if uid is not None:
            query = {'UID':uid}
            pdt = getToolByName(self.context,'portal_discussion')
            cat = getToolByName(self.context, 'uid_catalog')
            resbrains = cat.searchResults(query)
            if len(resbrains) == 1:
                item = resbrains[0]
                contobj = item.getObject()
                fullpath = item.getPath()
                splitpath = fullpath.split('/')[:-1]
                prettypath = '/' + '/'.join(splitpath)
                URLsuffix = getListingTemplateForContextParent(item)
                pathlink = self.context.portal_url() + prettypath + '/' + URLsuffix
                pathtitle = prettypath
                
                lasttimestamp = DateTime().timeTime()
                lastcommentid = '0'
                showxmorelink = True
                commentscount = 0
                xmorecomments = 0
                replydict = []
                
                isDiscussable = contobj.isDiscussable()
                canReply = canreply(contobj)
                jsondata = getjsondata(self.context,replydict,self.context.portal_url(),contobj.absolute_url())
                
                if isDiscussable:
                    dobj = pdt.getDiscussionFor(contobj)                
                    alldiscussions = dobj.objectValues()
                    alldiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
                    maxdispcomments = get_displaycountforlist()
                    lastxdiscussions = alldiscussions[:maxdispcomments]
                    
                    commentscount = dobj.replyCount(contobj)
                    if commentscount > maxdispcomments:
                        showxmorelink = True
                        xmorecomments = commentscount - maxdispcomments
                    elif commentscount > 0 and commentscount <= maxdispcomments:
                        showxmorelink = False
                        xmorecomments = 0
                    else:
                        showxmorelink = True
                        commentscount = 0
                        xmorecomments = 0                        
                    
                    if len(alldiscussions) > 0:
                        lasttimestamp = alldiscussions[0].modified().timeTime()
                        lastcommentid = alldiscussions[0].id
                        
                    
                    lastxdiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()))
                    for eachdisc in lastxdiscussions:
                        reply = dobj.getReply(eachdisc.id)
                        if reply <> None:
                            replydict.append({'depth': 0,'object':reply,'showoutput':True})
                    
                    other_data = {'view_type':'listview','canreply': str(canReply)}
                    
                    jsondata = getjsondata(self.context,replydict,self.context.portal_url(),contobj.absolute_url(),other_data)
                    
                return self.template(item_type=contobj.portal_type,item_type_title=contobj.Type(),item=item,pathlink=pathlink,pathtitle=pathtitle,contobj=contobj,showxmorelink = showxmorelink, xmorecomments = xmorecomments,allowdiscussion = isDiscussable,usercanreply = canReply,uid=uid,reply_dict=jsondata,title=contobj.Title(),commentcount=commentscount,lasttimestamp = lasttimestamp,lastcommentid = lastcommentid,itemindex=itemindex,view_type='listview')
            else:
                raise NotFound('Object not found for request','Not found',self.request)
        else:
            raise NotFound('uid is not passed','Not found',self.request)
            
    
    