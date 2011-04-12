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
import jsonlib
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from ubify.cyninv2theme import setCurrentStatusMessageForUser
from ubify.cyninv2theme import getLocationListForAddContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml
from ubify.policy import CyninMessageFactory as _
from kss.core import force_unicode

EmptymessageError = 'Empty message'
EmptydiscussionError = 'Empty Discussion'
RatingError = 'Rating Error'
EmptycommentError = 'Empty comment text'

def get_displaycountforlist():
    return 5

def canreply(obj):
    return getSecurityManager().checkPermission('Reply to item', aq_inner(obj)) > 0
    
def getjsondata(context,reply_dict,portal_url,item_url,extra_data={}):
        site_encoding = context.plone_utils.getSiteEncoding()        
        mi = getToolByName(context, 'portal_membership')
        util = getToolByName(context,'translation_service')
        output = {}
        items = []
        for eachobj in reply_dict:
            temp = {}
            temp['depth'] = 0
            if eachobj.has_key('prev_id'):
                temp['prev_id'] = eachobj['prev_id']
            else:
                temp['prev_id'] = ''
            reply = eachobj['object']
            if reply <> None:
                temp['id'] = reply.id
                temp['replyurl'] = reply.absolute_url()
                temp['replytoid'] = '-1'
                if reply.inReplyTo() and reply.inReplyTo().portal_type == 'Discussion Item':
                    temp['replytoid'] = reply.inReplyTo().getId()
                temp['depth'] = eachobj['depth']
                temp['mdate'] = util.ulocalized_time(reply.ModificationDate(), 1, context, domain='plonelocales')                
                creator = reply.Creator()
                temp['userid'] = creator
                temp['userinfourl'] = portal_url + '/userinfo?userid=' + creator
                temp['useravatarurl'] = mi.getPersonalPortrait(creator).absolute_url()
                temp['replycooked'] = reply.cooked_text.decode(site_encoding)                
                temp['permalink'] = item_url + '#' + reply.id
                
            items.append(temp)
        
        output['items'] = items        
        for key,val in extra_data.items():
            output[key] = val
        
        return jsonlib.write(output)
    
class CustomMethods(object):
    
    def findpreviouscommentid(self,allreplies,current_reply):
        prev_id = ''        
        indexlist =  [j for j in [allreplies.index(k) for k in allreplies if k['id'] == current_reply.id]]

        if len(indexlist) > 0:
            idx_reply = indexlist[0]
            prev_idx = idx_reply - 1
            #find id of an object with previndex
            prev_list = [k['id'] for k in allreplies if allreplies.index(k) == prev_idx]
            if len(prev_list) > 0:
                prev_id = prev_list[0]
                
        return prev_id
    
    def get_replies(self,pd,object):
        replies = []

        def getRs(obj, replies, counter):
            rs = pd.getDiscussionFor(obj).getReplies()
            if len(rs) > 0:
                rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                for r in rs:
                    replies.append({'depth':counter,'id':r.id, 'object':r})
                    getRs(r, replies, counter=counter + 1)

        try:
            getRs(object, replies, 0)
        except DiscussionNotAllowed:
            # We tried to get discussions for an object that has not only
            # discussions turned off but also no discussion container.
            return []
        return replies
    
    def setstatusmessage(self):        
        portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
        if portal_state.anonymous():
            return
        user_token = portal_state.member().getId()
        if user_token is None:
            return
        
        message = ''        
        if self.request.form.has_key('com.cynapse.cynin.statusmessageinput'):
            message = self.request.form['com.cynapse.cynin.statusmessageinput']
        htmltitle = ''
        if self.request.form.has_key('comcynapsesmessagetitle'):
            htmltitle = self.request.form['comcynapsesmessagetitle']
        message = message.strip(' ')
        
        if message == '' or message.lower() == htmltitle.lower():
            raise EmptymessageError, 'Unable to set message.'
        
        obj = setCurrentStatusMessageForUser(portal_state.portal(),user_token,message,self.context)
        
        return message
    
    def creatediscussion(self):
        strDiscussion = ''
        strTags = ''
        discussiontitle = ''
        tagstitle = ''
        obj = None
        location = self.context
        is_discussiontitle_reqd = False
        strDiscussionTitle = ''
        
        portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
        cat = getToolByName(self.context, 'uid_catalog')
        portal = portal_state.portal()
        if self.request.has_key('com.cynapse.cynin.discussionmessageinput'):
            strDiscussion = self.request['com.cynapse.cynin.discussionmessageinput']
        if self.request.has_key('comcynapsediscussiontag'):
            strTags = self.request['comcynapsediscussiontag']
        if self.request.has_key('comcynapsediscussiontitle'):
            discussiontitle = self.request['comcynapsediscussiontitle']
        if self.request.has_key('comcynapsetagstitle'):
            tagstitle = self.request['comcynapsetagstitle']
        if self.request.has_key('comcynapseadddiscussioncontextuid'):
            locationuid = self.request['comcynapseadddiscussioncontextuid']
        else:
            locationuid = ''
            
        if self.request.has_key('com.cynapse.cynin.discussiontitle'):
            is_discussiontitle_reqd = True
            strDiscussionTitle = self.request['com.cynapse.cynin.discussiontitle']        
        
        query = {'UID':locationuid}
        resbrains = cat.searchResults(query)
        if len(resbrains) == 1:
            location = resbrains[0].getObject()
        
        if strDiscussion == '' or strDiscussion.lower() == discussiontitle.lower():            
            raise EmptydiscussionError, 'Unable to add discussion with blank text.'
        elif is_discussiontitle_reqd and (strDiscussionTitle == ''):
            raise EmptydiscussionError, 'Unable to add discussion with blank title.'
        else:
            from ubify.cyninv2theme import addDiscussion
            strActualTags = ''
            if strTags.lower() != tagstitle.lower():
                strActualTags = strTags
            obj = addDiscussion(portal,strDiscussion,strActualTags,location,strDiscussionTitle)
            if obj <> None:
                here_text = _(u'lbl_here',u'here')
                strlink = "<a href='%s'>%s</a>" % (obj.absolute_url(),self.context.translate(here_text),)
                return strlink
            
    def fetchlocationstoaddcontent(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
        portal = portal_state.portal()
        
        results = getLocationListForAddContent(portal)
        
        output = {}
        items = []
        for eachobj in results:
            temp = {}
            temp['title'] = force_unicode(eachobj['object'].Title,'utf8')
            temp['UID'] = eachobj['object'].UID
            temp['occ'] = ''
            if eachobj['canAdd'] == False or 'Discussion' in eachobj['disallowedtypes']:
                temp['occ'] = 'disabledspaceselection'
            temp['depth'] = eachobj['depth']
            items.append(temp)
        
        output['items'] = items
        output = jsonlib.write(output)
        
    
        return output
    
    def ratecontent(self):        
        ratevalue = None
        uid = None
        if self.request.form.has_key('ratevalue'):
            ratevalue = self.request.form['ratevalue']
        if self.request.form.has_key('itemUID'):
            uid = self.request.form['itemUID']
            
        if ratevalue is None:
            raise RatingError,'No rating value.'
        elif uid is None:
            raise RatingError,'No rating item.'
        else:
            pr = getToolByName(self.context, 'portal_ratings', None)
            cat = getToolByName(self.context, 'uid_catalog')
            pr.addRating(int(ratevalue), uid)
            
            query = {'UID':uid}
            resbrains = cat.searchResults(query)
            if len(resbrains) == 1:
                obj = resbrains[0].getObject()
                obj.reindexObject()
            
            myval = int(pr.getUserRating(uid))
            newval = int(pr.getRatingMean(uid))
            ratecount = pr.getRatingCount(uid)
            value_totalscore = pr.getCyninRating(uid)
            value_scorecountlist = pr.getCyninRatingCount(uid)
            value_pscore = value_scorecountlist['positivescore']
            value_pcount = value_scorecountlist['positive']
            value_nscore = value_scorecountlist['negativescore']
            value_ncount = value_scorecountlist['negative']
            
            if myval == 1:
                newtitle=_(u'hated_it',u"Hate it (-2)")
            elif myval == 2:
                newtitle=_(u'didnt_like_it',u"Dislike it (-1)")
            elif myval == 3:
                newtitle=''
            elif myval == 4:
                newtitle=_(u'liked_it',u"Like it (+1)")
            elif myval == 5:
                newtitle=_(u'loved_it',u"Love it (+2)")
            
            trans_title = self.context.translate(newtitle)
            
            if value_totalscore > 0:
                plus_sign = "+"
            else:
                plus_sign = ""
            totalscore = plus_sign + str(value_totalscore)
            
            output = trans_title + ',' + totalscore + ',' + str(value_pcount) + ',' + str(value_ncount)
            return output
    
    def fetchcomments(self,uid,itemindex,lasttimestamp,commentcount,lastcommentid,viewtype):
        
        query = {'UID':uid}
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog')
        resbrains = cat.searchResults(query)
        replydict = []
        jsondata = getjsondata(self.context,replydict,self.context.portal_url(),'')        
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            isDiscussable = contobj.isDiscussable()
            canReply = canreply(contobj)
            if isDiscussable and canReply:                
                passedcommentcount = 0
                passedcommentcount = int(commentcount)
                flasttimestamp = float(lasttimestamp)
                datefromlasttimestamp = DateTime(flasttimestamp)
                newlastdate = datefromlasttimestamp.timeTime()
                marker_delete_objectid = ''
                removeallcomments = False
                
                disc_container = pdt.getDiscussionFor(contobj)
                newreplycount = disc_container.replyCount(contobj)
                allreplies = self.get_replies(pdt,contobj)
                
                if passedcommentcount <> newreplycount:                    
                    jsondata = getjsondata(self.context,replydict,self.context.portal_url(),contobj.absolute_url())
                    alldiscussions = disc_container.objectValues()
                    newlastcommentid = lastcommentid
                    
                    newlyaddedcomments = [k for k in alldiscussions if k.modified().greaterThan(datefromlasttimestamp) and k.id not in (lastcommentid)]
                    newlyaddedcomments.sort(lambda x,y:cmp(x.modified(),y.modified()))
                    
                    lenofnewcomments = len(newlyaddedcomments)
                    display_count = get_displaycountforlist()
                    
                    lastxdiscussions = []
                    if lenofnewcomments >= display_count:
                        newlyaddedcomments.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
                        lastxdiscussions = newlyaddedcomments[:display_count]
                        lastxdiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()))
                        if viewtype.lower() == 'listview':
                            removeallcomments = True
                    else:
                        lastxdiscussions = newlyaddedcomments                        
                        if lenofnewcomments > 0 and len(alldiscussions) > display_count and viewtype.lower() == 'listview':
                            alldiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
                            marker_discussion = alldiscussions[display_count-1: display_count]
                            if len(marker_discussion) > 0:
                                #delete nodes before this item                                
                                marker_delete_objectid = 'commenttable' + marker_discussion[0].id                                
                    
                    complete_output = ''
                    list_reply_ids = []
                    for eachcomment in lastxdiscussions:                    
                        reply = disc_container.getReply(eachcomment.id)
                        if reply <> None:     
                            parentsInThread = reply.parentsInThread()
                            depthvalue = 0
                            if viewtype.lower() == 'threadedview':
                                lenofparents = len(parentsInThread)
                                depthvalue = lenofparents - 1
                            
                            prev_reply_id = self.findpreviouscommentid(allreplies,reply)
                            
                            newlastdate = reply.modified().timeTime()
                            newlastcommentid = reply.id
                            
                            replydict.append({'depth': depthvalue, 'object': reply,'prev_id':prev_reply_id,'view_type':viewtype})
                            list_reply_ids.append(reply.id)                            
                            
                    other_data = {}
                    other_data['timeoutuid'] = uid
                    other_data['timeoutindex'] = itemindex
                    other_data['timeouttimestamp'] = str(newlastdate)
                    other_data['timeoutlastcommentid'] = newlastcommentid
                    other_data['timeoutcommentcount'] = str(newreplycount)
                    
                    other_data['marker_delete'] = marker_delete_objectid
                    other_data['removeallcomments'] = str(removeallcomments)
                    
                    other_data['shownocomments'] = str(False)
                    other_data['showmorecomments'] = str(False)
                    other_data['view_type'] = viewtype
                    other_data['canreply'] = str(canReply)
                    
                    if newreplycount > display_count:
                        xmorecomments = newreplycount - display_count
                        other_data['xmorecomments'] = str(xmorecomments)
                        other_data['showmorecomments'] = str(True)
                    elif newreplycount > 0 and newreplycount <= display_count:
                        other_data['xmorecomments'] = ''
                    else:
                        other_data['shownocomments'] = str(True)
                    
                    jsondata = getjsondata(self.context,replydict,self.context.portal_url(),contobj.absolute_url(),other_data)
        
        return jsondata
        
    def fetchcommentsforlist(self):        
        uid = self.request['comcynapsecyninfetchUID']
        itemindex = self.request['comcynapsecyninfetchindex']
        lasttimestamp = self.request['comcynapselasttimestamp']
        lastcommentid = self.request['comcynapselastcommentid']
        lastcommentcount = self.request['comcynapsecommentcount']
        viewtype = self.request['comcynapseviewtype']
        
        return self.fetchcomments(uid,itemindex,lasttimestamp,lastcommentcount,lastcommentid,viewtype)
        
    def fetchnewcomments(self):        
        uid = self.request['comcynapsecynincontextUID']
        itemindex = ''
        if self.request.has_key('comcynapsecyninfetchindex'):
            itemindex = self.request['comcynapsecyninfetchindex']
        lasttimestamp = self.request['comcynapselasttimestamp']
        lastcommentid = self.request['comcynapselastcommentid']
        lastcommentcount = self.request['comcynapsecommentcount']
        viewtype = self.request['comcynapseviewtype']
        
        return self.fetchcomments(uid,itemindex,lasttimestamp,lastcommentcount,lastcommentid,viewtype)
        
    def addnewcomment(self):        
        uid = ''
        itemindex = ''
        viewtype = ''
        lasttimestamp = ''
        lastcommentid = ''
        commentscount = ''
        inreplyto = ''
        if self.request.has_key('comcynapsecynincontextUID'):
            uid = self.request['comcynapsecynincontextUID']
        if self.request.has_key('comcynapsecyninitemindex'):
            itemindex = self.request['comcynapsecyninitemindex']
        if self.request.has_key('comcynapseviewtype'):
            viewtype = self.request['comcynapseviewtype']
        if self.request.has_key('comcynapselasttimestamp'):
            lasttimestamp = self.request['comcynapselasttimestamp']
        if self.request.has_key('comcynapselastcommentid'):
            lastcommentid = self.request['comcynapselastcommentid']
        if self.request.has_key('comcynapsecommentcount'):
            commentscount = self.request['comcynapsecommentcount']
        if self.request.has_key('inreplyto'):
            inreplyto = self.request['inreplyto']
        
        query = {'UID':uid}
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog')
        resbrains = cat.searchResults(query)
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()	    
            
            if contobj.isDiscussable() and canreply(contobj):
                mtool = getToolByName(self.context, 'portal_membership')
                username = mtool.getAuthenticatedMember().getId()
                dobj = pdt.getDiscussionFor(contobj)
                if len(self.request['comcynapsecyninNewCommentBody'].strip(' ')) == 0 or self.request['comcynapsecyninNewCommentBody'].lower() == self.request['comcynapsenewcommenttitle'].lower():                    
                    raise EmptycommentError, 'No comment text provided.'
                else:
                    id = dobj.createReply(title="",text=self.request['comcynapsecyninNewCommentBody'], Creator=username)
                    reply = dobj.getReply(id)
                    reply.cooked_text = convertWebIntelligentPlainTextToHtml(reply.text)
                    if inreplyto != '':
                        replyto = dobj.getReply(inreplyto)
                        reply.setReplyTo(replyto)
                    if reply <> None:
                        from ubify.cyninv2theme import triggerAddOnDiscussionItem                        
                        triggerAddOnDiscussionItem(reply)
                        return self.fetchcomments(uid,itemindex,lasttimestamp,commentscount,lastcommentid,viewtype)
                        
    
    def togglecommentsview(self):        
        uid = ''
        itemindex = ''
        viewtype = ''
        if self.request.has_key('uid'):
            uid = self.request['uid']
        if self.request.has_key('viewtype'):
            viewtype = self.request['viewtype']
        
        objcommentslist = []
        replydict = []
        jsondata = getjsondata(self.context,replydict,self.context.portal_url(),'')
        
        pdt = getToolByName(self.context, 'portal_discussion', None)
        query = {'UID':uid}
        cat = getToolByName(self.context, 'uid_catalog')
        resbrains = cat.searchResults(query)
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            
            isDiscussable = contobj.isDiscussable()
            canReply = canreply(contobj)
            
            disc_container = pdt.getDiscussionFor(contobj)
            alldiscussions = disc_container.objectValues()
            allreplies = self.get_replies(pdt,contobj)
            newreplycount = disc_container.replyCount(contobj)
            newlastdate = DateTime().timeTime()
            newlastcommentid = '0'
            
            if viewtype == 'flatview':
                alldiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()))
                objcommentslist.extend(alldiscussions)
            else:
                objcommentslist.extend(allreplies)
            
            for eachcomment in objcommentslist:
                if hasattr(eachcomment,'id'):
                    id = eachcomment.id
                elif eachcomment.has_key('id'):
                    id = eachcomment['id']
                    
                reply = disc_container.getReply(id)
                if reply <> None:                        
                    parentsInThread = reply.parentsInThread()
                    depthvalue = 0
                    if viewtype.lower() == 'threadedview':
                        lenofparents = len(parentsInThread)
                        depthvalue = lenofparents - 1
                    
                    prev_reply_id = self.findpreviouscommentid(allreplies,reply)
                    
                    newlastdate = reply.modified().timeTime()
                    
                    replydict.append({'depth': depthvalue, 'object': reply,'prev_id':prev_reply_id,'view_type':viewtype})
            
            if len(alldiscussions) > 0:
                newlastcommentid = str(alldiscussions[-1].id)
            
            other_data = {}
            other_data['timeoutuid'] = uid
            other_data['timeoutindex'] = itemindex
            other_data['timeouttimestamp'] = str(newlastdate)
            other_data['timeoutlastcommentid'] = newlastcommentid
            other_data['timeoutcommentcount'] = str(newreplycount)
            
            other_data['marker_delete'] = ''
            other_data['removeallcomments'] = str(False)
            
            other_data['shownocomments'] = str(False)
            other_data['showmorecomments'] = str(False)
            other_data['view_type'] = viewtype
            other_data['canreply'] = str(canReply)
            
            jsondata = getjsondata(self.context,replydict,self.context.portal_url(),contobj.absolute_url(),other_data)
        
        return jsondata