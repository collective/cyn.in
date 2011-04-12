from zope.component import getMultiAdapter
from plone.app.kss.plonekssview import PloneKSSView
from ubify.cyninv2theme import setCurrentStatusMessageForUser
from kss.core import kssaction
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from kss.core import force_unicode
from ubify.policy import CyninMessageFactory as _
from DateTime import DateTime

from ubify.cyninv2theme import getAppTitleForContext
from ubify.cyninv2theme import getListingTemplateForContextParent
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml



class KSSMethods(PloneKSSView):

    


    @kssaction
    def getOpenedView(self,url,htmlid):
        newpath = self.request.physicalPathFromURL(url)
        obj = self.context.restrictedTraverse(newpath)

        #Set return body in rData variable depending upon portal_type
        rData = ""
        if obj.portal_type == 'Document':
            rData= "<div class='inlininnerdiv'>" +  obj.CookedBody() + "</div>"
        elif obj.portal_type == 'Blog Entry':
            rData = "<div class='inlininnerdiv'>" +  obj.CookedBody() + "</div>"
        elif obj.portal_type == 'Link':
            rData = "<div class='inlineopenedlink'><a target='_blank' href='" + obj.remote_url() + "'>" + obj.remote_url() + "</a></div>"
        elif obj.portal_type == 'Image':
            rData = "<div class='inlineopenedimage'><a href='" + obj.absolute_url() + "/image_view_fullscreen' class='cluetip'>" + obj.tag(scale='preview') + "</a></div>"
        elif obj.portal_type =='File':
            mtr = self.context.mimetypes_registry
            mimearray = mtr.lookup(obj.getContentType())
            if len(mimearray) > 0:
                fileformat = mimearray[0].name()
            else:
                fileformat = obj.getContentType()
            rData = """
                <div id="filetitleviewwidget"><span><a href="%s"><img src="%s" />%s</a><span class="discreet">&mdash; %s, %s</span></div>
            """ % (obj.absolute_url(),obj.getIcon(),obj.getFilename(),fileformat,obj.getObjSize())
        elif obj.portal_type =='Video':
            mtr = self.context.mimetypes_registry
            mimearray = mtr.lookup(obj.getContentType())

            swf_url = self.context.portal_url() + "/flowplayer-3.0.1.swf"
            if len(mimearray) > 0:
                fileformat = mimearray[0].name()
            else:
                fileformat = obj.getContentType()
            flashobj = """
                <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="640" height="480" allowFullScreen="true">
                    <param name="movie" value="%s" />
                    <param name="flashvars"  value="config={'clip':'%s'}" />
                    <param name="wmode" value="transparent" />
                    <embed type="application/x-shockwave-flash" width="640" height="480" allowFullScreen="true" src="%s" flashvars="config={'clip':'%s'}" wmode="transparent"/>
                </object>
            """ % (swf_url,obj.absolute_url(),swf_url,obj.absolute_url())
            rData = """
                <div id="videotitleviewwidget"><div align="center">%s</div><span><a href="%s"><img src="%s" />%s</a><span class="discreet">&mdash; %s, %s</span></div>
            """ % (flashobj,obj.absolute_url(),obj.getIcon(),obj.getFilename(),fileformat,obj.getObjSize())
        elif obj.portal_type =='Event':
            rData = """
    <table class="ubereventtable" width="100%%"><tr><td width="100%%">
    <table align="center" id="eventbothdatescontainer" width="100%%"><tr><td>
    <table class="recentitem" cellpadding="10" cellspacing="0" width="100%%">
        <tr>
            <td valign="top" align="right">
                <table cellpadding="0" cellspacing="0">
                    <tr valign="middle">
                        <td class="itemonlydatecontainer">
                            <table cellpadding="0" cellspacing="0"><tr valign="middle" class="itemdate_daterow"><td class="itemday" >%s</td><td><table cellpadding="0" cellspacing="0" class="itemdatemonthyearcontainer"><tr><td class="itemmonth" >%s</td></tr><tr><td class="itemyear"  align="right">%s</td></tr></table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td width="100%%" align="center" class="itemdatetime" >%s</td>
        </tr>
    </table>
    </td></tr></table>
    </td>
    <td id="eventtoseperator" align="center"> to </td>
    <td>
    <table class="recentitem" cellpadding="10" cellspacing="0" width="100%%">
        <tr>
            <td valign="top">
                <table cellpadding="0" cellspacing="0">
                    <tr valign="middle">
                        <td class="itemonlydatecontainer">
                            <table cellpadding="0" cellspacing="0"><tr valign="middle" class="itemdate_daterow"><td class="itemday" >%s</td><td><table cellpadding="0" cellspacing="0" class="itemdatemonthyearcontainer"><tr><td class="itemmonth" >%s</td></tr><tr><td class="itemyear" align="right">%s</td></tr></table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td width="100%%" align="center" class="itemdatetime" >%s</td>
        </tr>
    </table>
    </td></tr></table>
    </td></tr>
    <tr><td colspan="3">%s</td><tr>
    </table>
        </td><td valign="top"><table class="eventdetailscontainer"><tr><td>
        <table class="eventdetailsmain"
               summary="Event details" cellpadding="0" cellspacing="0">

            <tbody>
                <tr>
                    <th >Where</th>
                    <td class="location">%s</td>
                </tr>
                <tr >
                    <th >Contact Name</th>
                    <td class="fn">%s</td>
                </tr>
                <tr >
                    <th >Contact Email</th>
                    <td class="email">
                        <a id="parent-fieldname-contactEmail"
                          >%s</a>
                    </td>
                </tr>
                <tr >
                    <th >Contact Phone</th>
                    <td class="tel">%s</td>
                </tr>
                <tr >
                    <th nowrap="nowrap">Attendees</th>
                    <td class="attendees">%s</td>
                </tr>
                <tr>
                    <th >Add event to calendar</th>
                    <td>
                        <a href="%s"
                           title="Add this item to your vCal calendar"
                           >
                            <img src="%s"  />
                            <span >vCal</span></a><br />
                        <a href="%s"
                           title="Add this item to your iCal calendar"
                           >
                            <img src="%s"  />
                            <span >iCal</span></a>
                    </td>
                </tr>
            </tbody>
        </table>
        </td></table></td></tr></table>
            """ % (self.context.formatday(obj.start().day()), obj.start().Month(), obj.start().year(), obj.start().AMPMMinutes(), self.context.formatday(obj.end().day()), obj.end().Month(), obj.end().year(), obj.end().AMPMMinutes(), obj.getText(), obj.location, obj.contactName, obj.contactEmail,obj.contactPhone,obj.getAttendees(),obj.absolute_url() + '/vcs_view', obj.absolute_url() + '/icon_export_vcal.png', obj.absolute_url() + '/ics_view', obj.absolute_url() + '/icon_export_ical.png')
            rData = "<div class='inlininnerdiv'>" +  rData  + "</div>"
        else:
            rData = "Unimplemented."
        ###############################################################Selectors
        divid = "comcynapsecyninlistingopenid"
        openid = "comcynapsecyninlistingopen"
        closeid = "comcynapsecyninlistingclose"
        openidbottom = "comcynapsecyninlistingopenbottom"
        closeidbottom = "comcynapsecyninlistingclosebottom"
        tableid = "recentitemtable"
        holderbottomid = "kssactionholderbottom"

        ###############################################################Commands
        ksscore = self.getCommandSet('core')
        replacediv = ksscore.getHtmlIdSelector(divid + htmlid)
        rData = force_unicode(rData,'utf')
        ksscore.replaceInnerHTML(replacediv,rData)
        openlink = ksscore.getHtmlIdSelector(openid + htmlid)
        ksscore.setStyle(openlink,'display','none')
        closelink = ksscore.getHtmlIdSelector(closeid + htmlid)
        ksscore.setStyle(closelink,'display','inline')
        openlinkbottom = ksscore.getHtmlIdSelector(openidbottom + htmlid)
        ksscore.setStyle(openlinkbottom,'display','none')
        closelinkbottom = ksscore.getHtmlIdSelector(closeidbottom + htmlid)
        ksscore.setStyle(closelinkbottom,'display','inline')
        recenttable = ksscore.getHtmlIdSelector(tableid + htmlid)
        ksscore.toggleClass(recenttable,'openedrecentitem')
        bottomholder = ksscore.getHtmlIdSelector(holderbottomid+ htmlid)
	jq = self.getCommandSet('jquery')
	ksscore.setStyle(bottomholder,'display','block')
	jq.serverEffect(replacediv,"slideDown", "slow")
    
    @kssaction
    def replyToComment(self,viewtype,lasttimestamp,commentcount,lastcommentid):
        query = {'UID':self.request['cont_uid']}
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog')
        resbrains = cat.searchResults(query)
	ksscore = self.getCommandSet('core')
        zopecore = self.getCommandSet('zope')
        jq = self.getCommandSet('jquery')
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            if contobj.isDiscussable() and self.canreply(contobj):
                mtool = getToolByName(self.context, 'portal_membership')
                username = mtool.getAuthenticatedMember().getId()
                dobj = pdt.getDiscussionFor(contobj)
                if len(self.request['commentbody'].strip(' ')) == 0 or self.request['commentbody'].lower() == self.request['comcynapsenewcommenttitle'].lower():
                    comcynapsecommenterrorlabel = ksscore.getHtmlIdSelector('comcynapsecommenterror'+ self.request['inreplyto'])
		    ksscore.setStyle(comcynapsecommenterrorlabel,'display','block')		    
                else:
                    id = dobj.createReply(title="", text=self.request['commentbody'], Creator=username)
                    reply = dobj.getReply(id)
                    reply.cooked_text = convertWebIntelligentPlainTextToHtml(reply.text)
                    replyto = dobj.getReply(self.request['inreplyto'])
                    reply.setReplyTo(replyto)
                    if reply <> None:
                        from ubify.cyninv2theme import triggerAddOnDiscussionItem
                        triggerAddOnDiscussionItem(reply)

                        #################Determine full reply to discussion to get placement peer of current comment
                        view_type = self.request['cviewtype']
                        replies = []
                        def getRs(obj, replies, counter):
                            rs = pdt.getDiscussionFor(obj).getReplies()
                            if len(rs) > 0:
                                rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                                for r in rs:
                                    replies.append({'depth':counter, 'object':r})
                                    getRs(r, replies, counter=counter + 1)

                        getRs(replyto, replies, 0)

                        if len(replies) > 1: ##There are more than 1 comments already children of the comment we just replied to, so the current comment can't have been the first reply
                            prevrep = replies[0]['object']
                        else:
                            prevrep = replyto

                        for rep in replies:
                            if rep['object'].id == reply.id:
                                belowreply = prevrep
                            else:
                                prevrep = rep['object']

                        mi = mtool.getMemberInfo();
                        commenttemplate = ViewPageTemplateFile('ksstemplates/commentrow.pt')
                        commenttemplate = commenttemplate.__of__(self.context)
                        depthvalue = 0
                        if view_type == 'threadedview':
                            depthvalue = int(self.request['depth']) + 1
                            
                        replydict = [{'depth': depthvalue, 'object': reply,'view_type':view_type},]
                        output = commenttemplate.render(indent=int(self.request['depth'])+2,fullname = mi['fullname'], avatarurl=self.context.portal_membership.getPersonalPortrait(username).absolute_url(),creator=username,showreply=self.canreply(self.context),showdelete=getSecurityManager().checkPermission('Manage portal',aq_inner(self.context)),commenttime=self.context.toLocalizedTime(reply.created,True),replyid=reply.id,replytitle=reply.Title(),replybody=reply.CookedBody(),replyurl=reply.absolute_url(),reply_dict=replydict)
                        
                        if view_type == 'threadedview':
                            commentscontainer = ksscore.getHtmlIdSelector('commenttable' + prevrep.id)
                            ksscore.insertHTMLAfter(commentscontainer,output)
                        else:
                            commentsoutercontainer = ksscore.getHtmlIdSelector('comcynapsecyninitemcommentscontainer')
                            ksscore.insertHTMLAsLastChild(commentsoutercontainer,output)
                        
                        taAddNewComment = ksscore.getCssSelector('textarea.commentbodyta')
                        ksscore.setAttribute(taAddNewComment,"value","")
                        itemcountcommentcount = ksscore.getHtmlIdSelector('itemcountcommentcount')
                        countofcomments = dobj.replyCount(self.context)
                        discussionlabel = ksscore.getHtmlIdSelector('discussionlabel')
                        ksscore.replaceInnerHTML(discussionlabel,str(countofcomments))
                        ksscore.replaceInnerHTML(itemcountcommentcount,str(countofcomments))
                        newcomment = ksscore.getHtmlIdSelector('commenttable' + reply.id)
                        frmreply = ksscore.getHtmlIdSelector('replyform' + self.request['inreplyto'])			
			ksscore.setStyle(frmreply,'display','none')
			comcynapsecommenterrorlabel = ksscore.getHtmlIdSelector('comcynapsecommenterror'+ self.request['inreplyto'])
			ksscore.setStyle(comcynapsecommenterrorlabel,'display','none')
                        self.fetchnewcomments(lasttimestamp,commentcount,lastcommentid,viewtype)

    def canreply(self,obj):
        return getSecurityManager().checkPermission('Reply to item', aq_inner(obj)) > 0
    @kssaction
    def refreshMyAreaBlock(self,messageuid,count):
        portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
        
        if portal_state.anonymous():
            return
        user_token = portal_state.member().getId()
        if user_token is None:
            return
        
        status_messages = self.context.portal_catalog.searchResults(Creator = user_token,portal_type=('StatuslogItem',),sort_on = 'created',sort_order='reverse',sort_limit=1);
        
        if len(status_messages) > 0:
            pdt = getToolByName(self.context, 'portal_discussion', None)
            newuid = status_messages[0].UID
            full_message = status_messages[0].getObject()
            newcount = 0
            message = status_messages[0].Title
            
            if full_message.isDiscussable():
                newcount = pdt.getDiscussionFor(full_message).replyCount(full_message)
            
            if newuid != messageuid or int(count) != newcount:                
                zopecommands = self.getCommandSet('zope')
                ksscore = self.getCommandSet('core')
                
                message = force_unicode(message,'utf')
                commenttext = ''
                
                if newcount < 1 or newcount > 1:
                    commenttext = _(u'text_comments',u"comments")
                elif newcount == 1:
                    commenttext = _(u'text_1_comment',u"comment")
                
                commenttext = self.context.translate(commenttext)
                commenttext = force_unicode(commenttext,'utf')
                
                selector = ksscore.getHtmlIdSelector('currentmessagediv')
                ksscore.replaceInnerHTML(selector,message)
                
                countselector = ksscore.getHtmlIdSelector('comcynapsecyninstatuscomments')
                ksscore.replaceInnerHTML(countselector,'<a href="%s">%s %s</a>' % (full_message.absolute_url(),newcount,commenttext,))
                
                kssattrselector = ksscore.getHtmlIdSelector('comcynapsecyninmyareablock')
                ksscore.setKssAttribute(kssattrselector,'messageid',str(newuid))
                ksscore.setKssAttribute(kssattrselector,'count',str(newcount))
    
    def get_replies(self,pd,object):
        replies = []

        context = aq_inner(self.context)
        container = aq_parent(context)
        
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
    
    def current_user(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getAuthenticatedMember().getId()
    
    @kssaction
    def fetchnewcomments(self,lasttimestamp,commentcount,lastcommentid,viewtype):        
        passedcommentcount = 0
        passedcommentcount = int(commentcount)
        
        flasttimestamp = float(lasttimestamp)
        datefromlasttimestamp = DateTime(flasttimestamp)
        
        newlastdate = datefromlasttimestamp.timeTime()
        
        zopecommands = self.getCommandSet('zope')
        ksscore = self.getCommandSet('core')
        jq = self.getCommandSet('jquery')
        
        pdt = getToolByName(self.context, 'portal_discussion', None)        
        
        if pdt <> None:
            allreplies = self.get_replies(pdt,self.context)
            
            disc_container = pdt.getDiscussionFor(self.context)
            replies = disc_container.getReplies()
            newreplycount = disc_container.replyCount(self.context)
            commentshiddencontainer = ksscore.getHtmlIdSelector('comcynapsehiddencomments')
            commentscontainer = ksscore.getHtmlIdSelector('comcynapsecyninitemcommentscontainer')
            addnewlasttimestamp = ksscore.getHtmlIdSelector('comcynapselasttimestamp')
            addnewlastcommentid = ksscore.getHtmlIdSelector('comcynapselastcommentid')
            addnewcommentcount = ksscore.getHtmlIdSelector('comcynapsecommentcount')
            
            if passedcommentcount <> newreplycount:
                #if comment count mismatch then only modify the stuff
                alldiscussions = disc_container.objectValues()                
                newlyaddedcomments = [k for k in alldiscussions if k.modified().greaterThan(datefromlasttimestamp) and k.id not in (lastcommentid)]
                newlyaddedcomments.sort(lambda x,y:cmp(x.modified(),y.modified()))
                for eachcomment in newlyaddedcomments:                    
                    reply = disc_container.getReply(eachcomment.id)
                    if reply <> None:                        
                        parentsInThread = reply.parentsInThread()
                        depthvalue = 0
                        if viewtype.lower() == 'threadedview':
                            lenofparents = len(parentsInThread)
                            depthvalue = lenofparents - 1
                        
                        prev_reply_id = self.findpreviouscommentid(allreplies,reply)
                        
                        newlastdate = reply.modified().timeTime()
                        commenttemplate = ViewPageTemplateFile('ksstemplates/commentrow.pt')
                        commenttemplate = commenttemplate.__of__(self.context)
                        replydict = [{'depth': depthvalue, 'object': reply,'prev_id':prev_reply_id,'view_type':viewtype},]
                        output = commenttemplate.render(reply_dict=replydict)
                        
                        #delete the node if already exists
                        old_comment = ksscore.getHtmlIdSelector('commenttable' + reply.id)
                        ksscore.deleteNode(old_comment)
                        
                        
                        #if there is no prev id found for new comment then insert it as last item to commentscontainer
                        #else insert it after prev id comments table.
                        if viewtype == 'flatview':
                            ksscore.insertHTMLAsLastChild(commentscontainer,output)
                        else:
                            if prev_reply_id == '':
                                ksscore.insertHTMLAsLastChild(commentscontainer,output)
                            else:
                                prevcommentcontainer = ksscore.getHtmlIdSelector('commenttable' + prev_reply_id)
                                ksscore.insertHTMLAfter(prevcommentcontainer,output)
                        
                        newcomment = ksscore.getHtmlIdSelector('commenttable' + reply.id)
                
                if len(newlyaddedcomments) > 0:
                    strlastcommentid = str(newlyaddedcomments[-1].id)
                    ksscore.setKssAttribute(commentshiddencontainer,'lastcommentid',strlastcommentid)
                    ksscore.setAttribute(addnewlastcommentid,'value',strlastcommentid)
		    jq.serverCall(commentscontainer,'truncatetextonitemexpand')
		    
            newlasttimestamp = str(newlastdate)
            strcommentcount = str(newreplycount)
            ksscore.setKssAttribute(commentshiddencontainer,'lasttimestamp',newlasttimestamp)
            ksscore.setKssAttribute(commentshiddencontainer,'commentcount',strcommentcount)
            ksscore.setAttribute(addnewlasttimestamp,'value',newlasttimestamp)
            ksscore.setAttribute(addnewcommentcount,'value',strcommentcount)
            
            
            itemcountcommentcount = ksscore.getHtmlIdSelector('itemcountcommentcount')            
            discussionlabel = ksscore.getHtmlIdSelector('discussionlabel')
            ksscore.replaceInnerHTML(discussionlabel,strcommentcount)
            ksscore.replaceInnerHTML(itemcountcommentcount,strcommentcount)
            
    @kssaction
    def toggleCommentsView(self,viewtype):
        zopecommands = self.getCommandSet('zope')
        ksscore = self.getCommandSet('core')
        jq = self.getCommandSet('jquery')
        commentshiddencontainer = ksscore.getHtmlIdSelector('comcynapsehiddencomments')
        commentscontainer = ksscore.getHtmlIdSelector('comcynapsecyninitemcommentscontainer')
        addnewlasttimestamp = ksscore.getHtmlIdSelector('comcynapselasttimestamp')
        addnewlastcommentid = ksscore.getHtmlIdSelector('comcynapselastcommentid')
        addnewcommentcount = ksscore.getHtmlIdSelector('comcynapsecommentcount')
            
        objcommentslist = []
        pdt = getToolByName(self.context, 'portal_discussion', None)
        if pdt <> None:
            disc_container = pdt.getDiscussionFor(self.context)
            alldiscussions = disc_container.objectValues()
            allreplies = self.get_replies(pdt,self.context)
            newreplycount = disc_container.replyCount(self.context)
            newlastdate = DateTime().timeTime()
            
            if viewtype == 'flatview':
                alldiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()))
                objcommentslist.extend(alldiscussions)
            else:
                objcommentslist.extend(allreplies)
            
            ksscore.replaceInnerHTML(commentscontainer,'')
            complete_output = ''
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
                    commenttemplate = ViewPageTemplateFile('ksstemplates/commentrow.pt')
                    commenttemplate = commenttemplate.__of__(self.context)
                    replydict = [{'depth': depthvalue, 'object': reply,'prev_id':prev_reply_id,'view_type':viewtype,'showoutput':True},]
                    output = commenttemplate.render(reply_dict=replydict)
                    
                    #if there is no prev id found for new comment then insert it as last item to commentscontainer
                    #else insert it after prev id comments table.
                    if viewtype == 'flatview':                        
                        complete_output += output
                    else:
                        complete_output += output                        
            
            if complete_output <> '' and len(objcommentslist) > 0:
                ksscore.replaceInnerHTML(commentscontainer,complete_output)
                jq.serverCall(commentscontainer,'truncatetextonitemexpand')
            if len(alldiscussions) > 0:
                strlastcommentid = str(alldiscussions[-1].id)
                ksscore.setKssAttribute(commentshiddencontainer,'lastcommentid',strlastcommentid)
                ksscore.setAttribute(addnewlastcommentid,'value',strlastcommentid)
        
        
            newlasttimestamp = str(newlastdate)
            strcommentcount = str(newreplycount)
            ksscore.setKssAttribute(commentshiddencontainer,'lasttimestamp',newlasttimestamp)            
            ksscore.setKssAttribute(commentshiddencontainer,'commentcount',strcommentcount)            
            
            ksscore.setAttribute(addnewlasttimestamp,'value',newlasttimestamp)
            ksscore.setAttribute(addnewcommentcount,'value',strcommentcount)
            
            itemcountcommentcount = ksscore.getHtmlIdSelector('itemcountcommentcount')            
            discussionlabel = ksscore.getHtmlIdSelector('discussionlabel')
            ksscore.replaceInnerHTML(discussionlabel,strcommentcount)
            ksscore.replaceInnerHTML(itemcountcommentcount,strcommentcount)            
            
        ksscore.setKssAttribute(commentshiddencontainer,'viewtype',viewtype)
        addnewcommentviewtype = ksscore.getHtmlIdSelector('comcynapseviewtype')
        ksscore.setAttribute(addnewcommentviewtype,'value',viewtype)
        ksscore.setStyle(commentscontainer,'display','block')
        
    @kssaction
    def getDiscussionView(self,uid,itemindex,state,openeditemindex):
        ksscore = self.getCommandSet('core')
        zopecore = self.getCommandSet('zope')
        jq = self.getCommandSet('jquery')
        
        clickednode = ksscore.getHtmlIdSelector('listitemdiscusslinktop' + itemindex)
        listcommentcontainer = ksscore.getHtmlIdSelector('listitemdiscussrow' + itemindex)
        listtimeoutuid = ksscore.getHtmlIdSelector('comcynapsecyninfetchUID')
        listtimeoutindex = ksscore.getHtmlIdSelector('comcynapsecyninfetchindex')
        listtimeouttimestamp = ksscore.getHtmlIdSelector('comcynapselasttimestamp')
        listtimeoutlastcommentid = ksscore.getHtmlIdSelector('comcynapselastcommentid')
        listtimeoutcommentcount = ksscore.getHtmlIdSelector('comcynapsecommentcount')
        listitemdetailright = ksscore.getHtmlIdSelector('listitemdetail' + itemindex)
        
        if openeditemindex != itemindex:            
            openednode = ksscore.getHtmlIdSelector('listitemdiscusslinktop' + openeditemindex)
            listopenedcommentcontainer = ksscore.getHtmlIdSelector('listitemdiscussrow' + openeditemindex)
            ksscore.setKssAttribute(openednode,'state','closed')
            ksscore.replaceInnerHTML(listopenedcommentcontainer,'')
            
        if state.lower() != 'closed':
            ksscore.setKssAttribute(clickednode,'state','closed')
            ksscore.replaceInnerHTML(listcommentcontainer,'')
            return
        
        query = {'UID':uid}
        pdt = getToolByName(self.context,'portal_discussion')
        cat = getToolByName(self.context, 'uid_catalog')
        resbrains = cat.searchResults(query)
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            isDiscussable = contobj.isDiscussable()
            canReply = self.canreply(contobj)
            if isDiscussable and canReply:
                dobj = pdt.getDiscussionFor(contobj)                
                alldiscussions = dobj.objectValues()
                alldiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
		maxdispcomments = self.get_displaycountforlist()
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
                lasttimestamp = DateTime().timeTime()
                lastcommentid = '0'
                if len(alldiscussions) > 0:
                    lasttimestamp = alldiscussions[0].modified().timeTime()
                    lastcommentid = alldiscussions[0].id
                    
                commenttemplate = ViewPageTemplateFile('ksstemplates/listcomment.pt')
                commenttemplate = commenttemplate.__of__(self.context)
                
                
                replydict = []
                lastxdiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()))
                for eachdisc in lastxdiscussions:
                    reply = dobj.getReply(eachdisc.id)
                    if reply <> None:
                        replydict.append({'depth': 0,'object':reply,'view_type':'listview','showoutput':True})
                
                output = commenttemplate.render(contobj=contobj, showxmorelink = showxmorelink, xmorecomments = xmorecomments, itemindex=itemindex,uid=uid,reply_dict=replydict,title=contobj.Title(),commentcount=commentscount,lasttimestamp = lasttimestamp,lastcommentid = lastcommentid,allowdiscussion = isDiscussable,usercanreply = canReply)
                
                detailtemplate = ViewPageTemplateFile('ksstemplates/listitemdetails.pt')
                detailtemplate = detailtemplate.__of__(self.context)
                
                
                item = resbrains[0]
                fullpath = item.getPath()
                splitpath = fullpath.split('/')[:-1]
                prettypath = '/' + '/'.join(splitpath)
                URLsuffix = getListingTemplateForContextParent(item)
                pathlink = self.context.portal_url() + prettypath + '/' + URLsuffix
                pathtitle = prettypath
                
                detail = detailtemplate.render(item_type=contobj.portal_type,portal_url=self.context.portal_url(),item_type_title=contobj.Type(),item=item,pathlink=pathlink,pathtitle=pathtitle,contobj=contobj)
                ksscore.replaceInnerHTML(listitemdetailright,force_unicode(detail,'utf'))
                ksscore.replaceInnerHTML(listcommentcontainer,output)
                
                ksscore.setKssAttribute(clickednode,'state','opened')
                
                ksscore.setAttribute(listtimeoutuid,'value',uid)
                ksscore.setAttribute(listtimeoutindex,'value',itemindex)
                ksscore.setAttribute(listtimeouttimestamp,'value',str(lasttimestamp))
                ksscore.setAttribute(listtimeoutlastcommentid,'value',lastcommentid)
                ksscore.setAttribute(listtimeoutcommentcount,'value',str(commentscount))
		jq.serverCall(clickednode,'truncatetextonitemexpand')
		jq.serverCall(clickednode,'marklistedtags')
		jq.serverCall(listcommentcontainer,'activateinputlabel')

    def get_displaycountforlist(self):
        return 5
    
    def fetchcomments(self,uid,itemindex,lasttimestamp,commentcount,lastcommentid,viewtype):
        query = {'UID':uid}
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog')
        resbrains = cat.searchResults(query)
        if len(resbrains) == 1:
            zopecommands = self.getCommandSet('zope')
            ksscore = self.getCommandSet('core')
            jq = self.getCommandSet('jquery')
            
            listcommentcontainer = ksscore.getHtmlIdSelector('comcynapselistcommentscontainer' + itemindex)
	    listcountspan = ksscore.getHtmlIdSelector('commentcountspan' + itemindex)
	    nocommentsyet = ksscore.getCssSelector('.nocommentsyet')
            listtimeoutuid = ksscore.getHtmlIdSelector('comcynapsecyninfetchUID')
            listtimeoutindex = ksscore.getHtmlIdSelector('comcynapsecyninfetchindex')
            listtimeouttimestamp = ksscore.getHtmlIdSelector('comcynapselasttimestamp')
            listtimeoutlastcommentid = ksscore.getHtmlIdSelector('comcynapselastcommentid')
            listtimeoutcommentcount = ksscore.getHtmlIdSelector('comcynapsecommentcount')
	    
            
            listcommentscount = ksscore.getHtmlIdSelector('listdiscussioncount' + itemindex)            
            
            contobj = resbrains[0].getObject()
            isDiscussable = contobj.isDiscussable()
            canReply = self.canreply(contobj)
            if isDiscussable and canReply:                
                passedcommentcount = 0
                passedcommentcount = int(commentcount)
                flasttimestamp = float(lasttimestamp)
                datefromlasttimestamp = DateTime(flasttimestamp)
                newlastdate = datefromlasttimestamp.timeTime()
                
                disc_container = pdt.getDiscussionFor(contobj)
                newreplycount = disc_container.replyCount(contobj)
                allreplies = self.get_replies(pdt,contobj)
                
                if passedcommentcount <> newreplycount:
                    alldiscussions = disc_container.objectValues()
                    newlastcommentid = lastcommentid
                    
                    newlyaddedcomments = [k for k in alldiscussions if k.modified().greaterThan(datefromlasttimestamp) and k.id not in (lastcommentid)]
                    newlyaddedcomments.sort(lambda x,y:cmp(x.modified(),y.modified()))
                    
                    lenofnewcomments = len(newlyaddedcomments)
                    display_count = self.get_displaycountforlist()
                    
                    lastxdiscussions = []
                    if lenofnewcomments >= display_count:
                        newlyaddedcomments.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
                        lastxdiscussions = newlyaddedcomments[:display_count]
                        lastxdiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()))
                        ksscore.clearChildNodes(listcommentcontainer)
                    else:
                        lastxdiscussions = newlyaddedcomments
                        if lenofnewcomments > 0 and len(alldiscussions) > display_count:
                            alldiscussions.sort(lambda x,y:cmp(x.modified(),y.modified()),reverse=True)
                            marker_discussion = alldiscussions[display_count-1: display_count]
                            if len(marker_discussion) > 0:
                                #delete nodes before this item
                                marker_node = ksscore.getHtmlIdSelector('commenttable' + marker_discussion[0].id)
                                ksscore.deleteNodeBefore(marker_node)
                    
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
                            commenttemplate = ViewPageTemplateFile('ksstemplates/commentrow.pt')
                            commenttemplate = commenttemplate.__of__(self.context)
                            
                            replydict = [{'depth': depthvalue, 'object': reply,'prev_id':prev_reply_id,'view_type':viewtype, 'showoutput':False},]
                            output = commenttemplate.render(reply_dict=replydict,allowdiscussion = isDiscussable,usercanreply = canReply)
                            list_reply_ids.append(reply.id)
                            complete_output += output
                            
                    if complete_output <> '' and len(lastxdiscussions) > 0:
                        ksscore.insertHTMLAsLastChild(listcommentcontainer,complete_output)
                        for erid in list_reply_ids:
                            newcomment = ksscore.getHtmlIdSelector('commenttable' + erid)
                            jq.serverEffect(newcomment,"fadeIn", "slow")			    
                        
                    ksscore.setAttribute(listtimeoutuid,'value',uid)
                    ksscore.setAttribute(listtimeoutindex,'value',itemindex)
                    ksscore.setAttribute(listtimeouttimestamp,'value',str(newlastdate))
                    ksscore.setAttribute(listtimeoutlastcommentid,'value',newlastcommentid)
                    ksscore.setAttribute(listtimeoutcommentcount,'value',str(newreplycount))
		    ksscore.setAttribute(listtimeoutuid,'value',uid)
		    
		    if newreplycount > display_count:
			xmorecomments = newreplycount - display_count
			ksscore.replaceInnerHTML(listcommentscount,str(xmorecomments))
			jq.serverEffect(nocommentsyet,"fadeOut", "fast")
			jq.serverEffect(listcountspan,"fadeIn", "slow")
		    elif newreplycount > 0 and newreplycount <= display_count:
			jq.serverEffect(nocommentsyet,"fadeOut", "fast")
		    
		    jq.serverCall(listcommentcontainer,'truncatetextonitemexpand')
