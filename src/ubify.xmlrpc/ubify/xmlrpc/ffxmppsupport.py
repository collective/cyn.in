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
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from interfaces import IStackerAPI
from Products.CMFCore.utils import getToolByName
from ubify.viewlets.config import plone_site_type_title
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml

class StackerView(BrowserView):
    """Contains the Stacker browser view"""
    implements(IStackerAPI)

    #!!WARNING: DO NOT include Discussion Item in stackercontenttypes, below.
    #Catalog search queries for UID return the discussion items
    #on the UID that is passed, so we filter out those by
    #using portal_type in stackercontenttypes in all of the catalog queries.
    stackercontenttypes = ('Document',
                            'Event',
                            'File',
                            'Image',
                            'Link',
                            'Blog Entry',
                            'StatuslogItem',
                            'Video',
                            'Discussion',
                            'Audio',
                        )
    #Need to use this variable in Search query for searching term in discussion item too.
    #But instead of returning Discussion Item, we will return Discussed Item.
    stackersearchcontenttypes = stackercontenttypes + ('Discussion Item',)

    def sayhello(self):
        """Says Hello"""
        return "Hello"

    def echo(self,echostr):
        """Returns the passed string"""
        return echostr

    def getSiteTitle(self):
        """Return the site title"""
        site = self.context.portal_url.getPortalObject()
        return site.Title()

    def setItem(self,obj,commentcount):
        item = None
        if obj <> None:
            item = {
                    'id':obj.id,
                    'itemuid':obj.UID(),
                    'title':obj.Title(),
                    'description':obj.Description(),
                    'portal_type':obj.portal_type,
                    'created':obj.created(),
                    'modified':obj.modified(),
                    'creator':obj.Creator(),
                    'allowedcomments':obj.isDiscussable(),
                    'commentcount': commentcount,
                    'absoluteurl':obj.absolute_url(),
                    'cancomment':self.can_reply(obj),
                    'lastchangedate':obj.lastchangedate,
                    'lastchangeaction':obj.lastchangeaction,
                    'lastchangeperformer':obj.lastchangeperformer,
                    'canedit':self.can_edit(obj),
                }
        return item

    def setSearchResultItem(self,brainobj):
        item = None
        if brainobj:
            item = {
                    'id':brainobj.id,
                    'itemuid': brainobj.UID,
                    'title':brainobj.Title,
                    'portal_type': brainobj.portal_type,
                    'modified':brainobj.modified,
                    'creator': brainobj.Creator,
                    'absoluteurl':brainobj.getURL(),
                    'relevance':brainobj.data_record_normalized_score_,
            }
            if brainobj.portal_type in ('Discussion Item',):
                item['title'] = brainobj.getObject().text
        return item

    def getUpdateCount(self):
        """Returns number of recent items available for recent user"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')
        resbrains = portal_catalog.searchResults(query)
        return len(resbrains)


    def getRecentUpdates(self,maxitemcount=5,pagenumber=1):
        """Return the recent updates, up to a maximum of maxitemcount items will be returned in a list"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')
        indFrom = (maxitemcount * pagenumber) - maxitemcount
        indTo = maxitemcount * pagenumber
        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)
        if len (resbrains) < indTo: #If there are not enough items on this page
            remainder = len(resbrains) % maxitemcount #Determine remainder of items using modulo
            indTo = indFrom + remainder
            if len (resbrains) < indTo: #The call is asking for more pages than can be generated!
                raise ValueError, "You asked for a Page Number that does not exist!"

        resbrains = resbrains[indFrom:indTo] #Slice the list for the requested Page

        outlist = []
        for b in resbrains:
            obj = b.getObject()
            #import pdb; pdb.set_trace()
            if obj.isDiscussable():
                dc = pdt.getDiscussionFor(obj)
                commentcount = dc.replyCount(obj)
            else:
                commentcount = -1
            item = self.setItem(obj,commentcount)
            outlist.append(item)
        return {'itemcount':fullcount,'itemlist':outlist}

    def refreshUpdateItem(self,uid):
        """Resends a single item of the same structure as the one in getRecentUpdates with the most updated info"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog', None)
        resbrains = cat.searchResults(UID=uid)
        if len(resbrains) == 1:
            obj = resbrains[0].getObject()
            if obj.isDiscussable():
                dc = pdt.getDiscussionFor(obj)
                commentcount = dc.replyCount(obj)
            else:
                commentcount = -1
            item = self.setItem(obj,commentcount)
            return item
        else:
            raise ValueError, "Incorrect UID, no item with such a UID found."

    def getTypeInfo(self,typename):
        """Returns the type title and icon url for given typename"""
        typetool= getToolByName(self.context, 'portal_types')
        object_typeobj = typetool[typename]
        typeiconname = object_typeobj.content_icon
        if object_typeobj is not None:
            #import pdb; pdb.set_trace()
            if object_typeobj.title == '' and typename.lower() == 'plone site':
                typetitle = plone_site_type_title
            elif object_typeobj.title == '' and typename.lower() == 'discussion item':
                typetitle = 'Comment'
            else:
                typetitle = object_typeobj.title
            return {'typename':typename,'typetitle':typetitle,'typeiconurl':self.context.portal_url.getPortalObject().absolute_url() + '/' + typeiconname}

    def getUserInfo(self,userid=''):
        """Return the user name details, and avatar url for given userid"""
        if userid == '':
            userid = self.current_user()
        po = self.context.portal_url.getPortalObject()
        pm = self.context.portal_membership
        acl = self.context.acl_users
        md = pm.getMemberById(userid)
        if md is not None:
            user = md.getUser()
            if user is not None:
                if 'mutable_properties' in user.listPropertysheets():
                    mps = user.getPropertysheet('mutable_properties')
                    fullname = mps.getProperty('fullname')
                    email = mps.getProperty('email')
                    home_page = mps.getProperty('home_page')
                    location = mps.getProperty('location')
                    description = mps.getProperty('description')
                else:
                    mps = ''
                    fullname = ''
                    email = ''
                    home_page = ''
                    location = ''
                    description = ''
                portrait = pm.getPersonalPortrait(userid).absolute_url()
                return {'username':userid,'fullname':fullname,'email':email,'home_page':home_page,'location':location,'description':description,'portrait_url':portrait}
            else:
                raise ValueError("User %s Does not Exist!" % userid)
        else:
            raise ValueError("User %s Does not Exist!" % userid)

    def getWikiBody(self,uid):
        """Return the wiki body text, pre-cooked and processed"""
        cat = self.context.portal_catalog
        res = cat.searchResults({'portal_type':'Document','UID':uid})
        if len(res)> 0:
            if len(res) > 1:
                raise ValueError, 'More than 1 item found with the given UID. Since this should not happen normally, do check what is going on?'
            else:
                wikipage = res[0].getObject()
                return self.recook(wikipage.CookedBody())
        else:
            raise ValueError, 'Wiki Page not found - Incorrect UID?'

    def recook(self,html):
        """Fixes things like image links, etc. for best results in external clients. Currently unimplemented!!"""
        return html

    def getEventInfo(self,uid):
        """Return the information available for a Calendar Event"""
        cat = self.context.portal_catalog
        res = cat.searchResults({'portal_type':'Event','UID':uid})
        if len(res)> 0:
            if len(res) > 1:
                raise ValueError, 'More than 1 item found with the given UID. Since this should not happen normally, do check what is going on?'
            else:
                event = res[0].getObject()
                retdict = {'start':event.start(),'end':event.end(),
                           'location':event.getLocation(),'contactName':event.contactName,
                           'contactEmail':event.contactEmail,'contactPhone':event.contactPhone,
                           'attendees':event.getAttendees(),'bodyhtml':self.recook(event.getText())}
                return retdict
        else:
            raise ValueError, 'Event not found - Incorrect UID?'

    def getFileInfo(self,uid):
        """Return the info available for a file"""
        cat = self.context.portal_catalog
        res = cat.searchResults({'portal_type':('File','Image'),'UID':uid})
        if len(res)> 0:
            if len(res) > 1:
                raise ValueError, 'More than 1 item found with the given UID. Since this should not happen normally, do check what is going on?'
            else:
                file = res[0].getObject()
                mtr = self.context.mimetypes_registry
                mimearray = mtr.lookup(file.getContentType())
                if len(mimearray):
                    fileformat = mimearray[0].name()
                else:
                    fileformat = file.getContentType()
                retdict = {'filename':file.getFilename(),'fileformat':fileformat,'filesize':file.getObjSize()}
                return retdict
        else:
            raise ValueError, 'File not found - Incorrect UID?'

    def getLinkInfo(self,uid):
        """Return the info available for a link"""
        cat = self.context.portal_catalog
        res = cat.searchResults({'portal_type':'Link','UID':uid})
        if len(res)> 0:
            if len(res) > 1:
                raise ValueError, 'More than 1 item found with the given UID. Since this should not happen normally, do check what is going on?'
            else:
                link = res[0].getObject()
                retdict = {'remoteurl':link.remote_url()}
                return retdict
        else:
            raise ValueError, 'Link not found - Incorrect UID?'

    def getBlogEntry(self,uid):
        """Return the info available for a Blog Entry"""
        cat = self.context.portal_catalog
        res = cat.searchResults({'portal_type':'Blog Entry','UID':uid})
        if len(res)> 0:
            if len(res) > 1:
                raise ValueError, 'More than 1 item found with the given UID. Since this should not happen normally, do check what is going on?'
            else:
                blogpost = res[0].getObject()
                retdict = {'htmlbody':self.recook(blogpost.CookedBody())}
                return retdict
        else:
            raise ValueError, 'Blog entry not found - Incorrect UID?'

    def getComments(self,uid):
        """Return all the comments for the given object's UID"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog', None)
        resbrains = cat.searchResults(UID=uid)
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            if contobj.isDiscussable():
                replies = []
                def getRs(obj, replies, counter):
                    rs = pdt.getDiscussionFor(obj).getReplies()
                    if len(rs) > 0:
                        rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                        for reply in rs:
                            replies.append({
                                            'depth':counter,
                                            'title':reply.Title(),
                                            'commenter': reply.Creator(),
                                            'commenttext':reply.text,
                                            'modified':reply.modified(),
                                            'id':reply.getId()
                                            })
                            getRs(reply, replies, counter=counter + 1)
                getRs(contobj, replies, 0)
                return replies
            else:
                raise ValueError, 'The object at given UID does not allow comments.'
        else:
            raise ValueError, 'Item with given UID not found!'

    def getCommentsRecursive(self,uid):
        """Return all the comments for the given object's UID. The returned comments are arranged recursively in a children object"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog', None)
        resbrains = cat.searchResults(UID=uid)
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            if contobj.isDiscussable():
                replies = []
                def getRs(obj, replies, counter):
                    rs = pdt.getDiscussionFor(obj).getReplies()
                    if len(rs) > 0:
                        rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                        for reply in rs:
                            comment =   {
                                            'd':counter,
                                            't':reply.Title(),
                                            'u': reply.Creator(),
                                            'c':reply.text,
                                            'm':reply.modified(),
                                            'i':reply.getId(),
                                            'r':[]
                                        }
                            getRs(reply, comment['r'], counter=counter + 1)
                            replies.append(comment)
                getRs(contobj, replies, 0)
                return replies
            else:
                raise ValueError, 'The object at given UID does not allow comments.'
        else:
            raise ValueError, 'Item with given UID not found!'

    def addNewComment(self,uid,comment_title,comment_body,reply_commentid=''):
        """Adds a comment on the provided UID with given title, text and commenter user.
        If reply_commentid is supplied and is a valid id in the object at uid, it is set to be
        a nested reply to that comment.
        Returns UID of the freshly added comment."""

        pdt = getToolByName(self.context, 'portal_discussion', None)
        cat = getToolByName(self.context, 'uid_catalog')
        query = {'UID':uid}
        resbrains = cat.searchResults(query)
        if len(resbrains) == 1:
            contobj = resbrains[0].getObject()
            if contobj.isDiscussable() and self.can_reply(contobj) > 0:
                ditem = None
                dobj = pdt.getDiscussionFor(contobj)
                if reply_commentid != '': #This is a nested comment.
                    try:
                        ditem = dobj.getReply(reply_commentid)
                    except AttributeError:
                        raise ValueError, "The given comment ID does not exist. Please check the comment id of the comment that you are wanting to add this new comment to."
                id = dobj.createReply(title=comment_title, text=comment_body, Creator=self.current_user())
                reply = dobj.getReply(id)
                reply.cooked_text = convertWebIntelligentPlainTextToHtml(reply.text)
                if reply <> None:
                    from ubify.cyninv2theme import triggerAddOnDiscussionItem
                    triggerAddOnDiscussionItem(reply)

                if ditem is not None: #This is supposed to be a nested comment to ditem
                    reply.setReplyTo(ditem)
                return id
            else:
                raise ValueError, 'The object at given UID either does not allow comments OR you do not have permission to comment on this object.'
        else:
            #import pdb; pdb.set_trace()
            raise ValueError, 'More than 1 item found with the given UID. Since this should not happen normally, do check what the heck is going on?'

    def can_reply(self,obj):
        return getSecurityManager().checkPermission('Reply to item', aq_inner(obj)) > 0

    def can_edit(self,obj):
        return getSecurityManager().checkPermission('Modify portal content',aq_inner(obj)) > 0

    def current_user(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getAuthenticatedMember().getId()

    def search(self,searchableText='',maxitemcount=5,pagenumber=1):
        """Returns result for search text entered for recent user"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'SearchableText': searchableText,'portal_type':self.stackersearchcontenttypes}
        portal_catalog = getattr(self.context,'portal_catalog')
        indFrom = (maxitemcount * pagenumber) - maxitemcount
        indTo = maxitemcount * pagenumber
        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)
        if len (resbrains) < indTo: #If there are not enough items on this page
            remainder = len(resbrains) % maxitemcount #Determine remainder of items using modulo
            indTo = indFrom + remainder
            if len (resbrains) < indTo: #The call is asking for more pages than can be generated!
                raise ValueError, "You asked for a Page Number that does not exist!"

        resbrains = resbrains[indFrom:indTo] #Slice the list for the requested Page

        outlist = []
        for b in resbrains:
            item = self.setSearchResultItem(b)
            outlist.append(item)
        return {'itemcount':fullcount,'itemlist':outlist,'term':searchableText}

    def searchIds(self,searchableText='',maxitemcount=5,pagenumber=1):
        """Returns search results with id, lastchangedate and relevance for search text entered."""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'SearchableText': searchableText,'portal_type':self.stackersearchcontenttypes}
        portal_catalog = getattr(self.context,'portal_catalog')
        indFrom = (maxitemcount * pagenumber) - maxitemcount
        indTo = maxitemcount * pagenumber
        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)
        if len (resbrains) < indTo: #If there are not enough items on this page
            remainder = len(resbrains) % maxitemcount #Determine remainder of items using modulo
            indTo = indFrom + remainder
            if len (resbrains) < indTo: #The call is asking for more pages than can be generated!
                raise ValueError, "You asked for a Page Number that does not exist!"

        resbrains = resbrains[indFrom:indTo] #Slice the list for the requested Page

        outlist = []
        for brain in resbrains:
            item = {'i':brain.UID,'d':brain.lastchangedate,'r':brain.data_record_normalized_score_}
            outlist.append(item)
        return {'c':fullcount,'l':outlist,'t':searchableText}

    def getStatusMessages(self,username='',count=1,pagenumber=1):
        """Returns current status message for passed username. For empty username method returns status message for current user"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        from ubify.cyninv2theme import getStatusMessagesForUser
        if username is '':
            username = self.current_user()
        resbrains = getStatusMessagesForUser(self.context,username)

        fullcount = len(resbrains)

        indFrom = (count * pagenumber) - count
        indTo = count * pagenumber

        if fullcount < indTo: #If there are not enough items on this page
            remainder = fullcount % count #Determine remainder of items using modulo
            indTo = indFrom + remainder
            if fullcount < indTo: #The call is asking for more pages than can be generated!
                raise ValueError, "You asked for a Page Number that does not exist!"

        resbrains = resbrains[indFrom:indTo]

        outlist = []
        for b in resbrains:
            obj = b.getObject()
            if obj.isDiscussable():
                dc = pdt.getDiscussionFor(obj)
                commentcount = dc.replyCount(obj)
            else:
                commentcount = -1
            item = self.setItem(obj,commentcount)
            outlist.append(item)
        return {'itemcount':fullcount,'itemlist':outlist}

    def setStatusMessage(self,message):
        """Set status log message for current user"""
        if message <> None and message <> '':
            username = self.current_user()
            from ubify.cyninv2theme import setCurrentStatusMessageForUser
            setCurrentStatusMessageForUser(self.context,username,message,self.context)
            return self.getStatusMessage()

    def getStatusMessage(self,username=''):
        """Returns current status message of passed user."""
        outlist = self.getStatusMessages(username,1,1)
        if outlist['itemcount'] > 0:
            return outlist['itemlist'][0]['title']
        else:
            return ""

    def getLastChangeDate(self):
        """Returns the max lastchangedate for the logged in user."""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        query = {'portal_type':self.stackercontenttypes, 'sort_on':'lastchangedate','sort_order':'descending','sort_limit':1}
        portal_catalog = getattr(self.context,'portal_catalog')
        resbrains = portal_catalog.searchResults(query)
        return resbrains[0]['lastchangedate']

    def getRecentItemIds(self,maxitemcount=5,pagenumber=1):
        """Return the recent UIDs, up to a maximum of maxitemcount items will be returned in a list"""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')
        indFrom = (maxitemcount * pagenumber) - maxitemcount
        indTo = maxitemcount * pagenumber
        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)
        if len (resbrains) < indTo: #If there are not enough items on this page
            remainder = len(resbrains) % maxitemcount #Determine remainder of items using modulo
            indTo = indFrom + remainder
            if len (resbrains) < indTo: #The call is asking for more pages than can be generated!
                raise ValueError, "You asked for a Page Number that does not exist!"

        resbrains = resbrains[indFrom:indTo] #Slice the list for the requested Page

        outlist = []
        for brain in resbrains:
            item = {'i':brain.UID,'d':brain.lastchangedate}
            outlist.append(item)
        return {'c':fullcount,'l':outlist}

    def getItemsByIds(self,arrUIDs):
        """Return the Update items as per the UIDs requested."""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'portal_type':self.stackercontenttypes, 'UID':arrUIDs}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)

        outlist = []
        for b in resbrains:
            obj = b.getObject()
            #import pdb; pdb.set_trace()
            if obj.isDiscussable():
                dc = pdt.getDiscussionFor(obj)
                commentcount = dc.replyCount(obj)
            else:
                commentcount = -1
            item = self.setItem(obj,commentcount)
            outlist.append(item)
        return outlist

    def getSearchItemsByIds(self,arrUIDs):
        """Return the search items as per the UIDs requested."""
        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'portal_type':self.stackercontenttypes, 'UID':arrUIDs}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)

        outlist = []
        for b in resbrains:
            item = self.setSearchResultItem(b)
            outlist.append(item)
        return outlist

    def getUsersByIds(self,arrUserIds):
        """Return the user info objects for the users specified"""
        outlist = []
        for user in arrUserIds:
            try:
                outlist.append(self.getUserInfo(user))
            except ValueError:
                print "User not found %s" % user
        return outlist

    def getTypesByNames(self,arrTypeNames):
        """Return the type info objects for the type names specified"""
        outlist = []
        for type in arrTypeNames:
            try:
                outlist.append(self.getTypeInfo(type))
            except KeyError:
                print "Type not found %s" % type
        return outlist

    def getItemsSinceDate(self,fromDate):
        """Returns items count and items changed after passed date.Date should be in milliseconds."""
        import datetime

        newDate = datetime.datetime.fromtimestamp(fromDate)

        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes,'lastchangedate':{'query':(newDate),'range':'min'}, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)

        outlist = []
        for b in resbrains:
            obj = b.getObject()
            if obj.isDiscussable():
                dc = pdt.getDiscussionFor(obj)
                commentcount = dc.replyCount(obj)
            else:
                commentcount = -1
            item = self.setItem(obj,commentcount)
            outlist.append(item)

        return {'itemcount':fullcount,'itemlist':outlist}

    def getItemsCountSinceDate(self,fromDate):
        """Returns lastchangedate if any and count of items changed after passed date.Date should be in milliseconds."""
        import datetime

        newDate = datetime.datetime.fromtimestamp(fromDate)

        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes,'lastchangedate':{'query':(newDate),'range':'min'}, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)
        if fullcount > 0:
            lstchangedate = resbrains[0]['lastchangedate']
        else:
            lstchangedate = None
        return {'lastchangedate':lstchangedate,'itemcount':fullcount}

    def getItemsCountForDateRange(self,fromDate,toDate):
        """Returns count for items for passed date params.Date should be in milliseconds."""
        import datetime

        startDate = datetime.datetime.fromtimestamp(fromDate)
        endDate = datetime.datetime.fromtimestamp(toDate)

        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes,'lastchangedate':{'query':(startDate,endDate),'range':'min:max'}, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)

        return fullcount

    def getItemIDsForDateRange(self,fromDate,toDate):
        """Returns id and lastchangedate for items for passed date params.Date should be in milliseconds."""
        import datetime

        startDate = datetime.datetime.fromtimestamp(fromDate)
        endDate = datetime.datetime.fromtimestamp(toDate)

        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes,'lastchangedate':{'query':(startDate,endDate),'range':'min:max'}, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)

        outlist = []

        for b in resbrains:
            customitem = {}
            customitem['itemid'] = b.UID
            customitem['item_lastchangedate'] = b.lastchangedate
            outlist.append(customitem)

        return outlist

    def getItemsForDateRange(self,fromDate,toDate):
        """Returns items changed between passed dates.Date should be in milliseconds."""
        import datetime

        startDate = datetime.datetime.fromtimestamp(fromDate)
        endDate = datetime.datetime.fromtimestamp(toDate)

        pdt = getToolByName(self.context, 'portal_discussion', None)
        path =  '/'.join(self.context.getPhysicalPath())
        query = {'path':{'query':path},'portal_type':self.stackercontenttypes,'lastchangedate':{'query':(startDate,endDate),'range':'min:max'}, 'sort_on':'lastchangedate','sort_order':'descending'}
        portal_catalog = getattr(self.context,'portal_catalog')

        resbrains = portal_catalog.searchResults(query)
        fullcount = len(resbrains)

        outlist = []

        for b in resbrains:
            obj = b.getObject()
            if obj.isDiscussable():
                dc = pdt.getDiscussionFor(obj)
                commentcount = dc.replyCount(obj)
            else:
                commentcount = -1
            item = self.setItem(obj,commentcount)
            outlist.append(item)

        return outlist

    def getVersionString(self):
        """Returns version string of cyn.in server"""
        portalquickinstaller = getToolByName(self.context,"portal_quickinstaller")
        strversion = ""
        try:
            objProduct = portalquickinstaller._getOb('ubify.policy')
            if objProduct <> None:
                strversion = objProduct.getInstalledVersion()
        except AttributeError:
            pass

        return strversion

    def getSpaces(self,parentUID=None):
        """Returns objects of type Space below passed parent UID."""
        from ubify.cyninv2theme import getRootURL
        cat = getToolByName(self.context, 'uid_catalog', None)
        portal_catalog = getToolByName(self.context,'portal_catalog',None)
        p_url = getToolByName(self.context,"portal_url")
        
        strPath = "/".join(p_url.getPortalObject().getPhysicalPath()) + getRootURL()

        if parentUID is not None:
            resbrains = cat.searchResults(UID=parentUID)
            if len(resbrains) == 1:
                strPath = "/".join(resbrains[0].getObject().getPhysicalPath())
            resbrains = []

        query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['ContentSpace'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
        resbrains = portal_catalog(query)

        outlist = []
        def getChildren(item,catalog,lstchildren):
            try:
                strPath = "/".join(item.getPhysicalPath())
                query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['ContentSpace'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
                results = catalog(query)

                if len(results) > 0:
                    for o in results:
                        itemresult = {
                                        'spaceid':o.UID,
                                        'c': []
                                     }
                        getChildren(o.getObject(),catalog,itemresult['c'])
                        lstchildren.append(itemresult)
            except AttributeError:
                return ""

        for obj in resbrains:
            itemresult = {
                            'spaceid':obj.UID,
                            'c': []
                         }
            getChildren(obj.getObject(),portal_catalog,itemresult['c'])

            outlist.append(itemresult)
        return outlist

    def getObjectIds(self,uid):
        """Returns immediate children objects of passed UID."""
        outlist = []
        cat = getToolByName(self.context, 'uid_catalog', None)
        pcat = getToolByName(self.context, 'portal_catalog', None)
        resbrains = cat.searchResults(UID=uid)
        results = []
        if len(resbrains) == 1:
            obj = resbrains[0].getObject()

            if obj.portal_type == 'Topic':
                results = obj.queryCatalog()
            elif obj.portal_type == 'SmartView':
                from ubify.smartview import getQValue

                query = getQValue(obj)
                results = pcat(query)
            else:
                strPath = "/".join(obj.getPhysicalPath())
                query = {'path': {'query': strPath,'depth':1}, 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
                results = pcat(query)

            if len(results) > 0:
                for eobj in results:
                    item = {
                        'uid': eobj.UID
                    }
                    outlist.append(item)

        return outlist

    def getUsers(self):
        """Returns list of user ids for cyn.in site."""
        acl_users = getToolByName(self.context,"acl_users",None)
        outlist = []
        if acl_users != None:
            outlist = acl_users.source_users.getUserNames()

        return outlist

    def getViews(self,parentuid=None):
        """Returns objects of type SmartView below passed parent uid if any"""
        cat = getToolByName(self.context, 'uid_catalog', None)
        portal_catalog = getToolByName(self.context,'portal_catalog',None)
        p_url = getToolByName(self.context,"portal_url")
        strPath = "/".join(p_url.getPortalObject().getPhysicalPath()) + "/views"

        if parentuid is not None:
            resbrains = cat.searchResults(UID=parentuid)
            if len(resbrains) == 1:
                strPath = "/".join(resbrains[0].getObject().getPhysicalPath())
            resbrains = []

        query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['SmartView','Topic'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
        resbrains = portal_catalog(query)

        outlist = []
        def getChildren(item,catalog,lstchildren):
            try:
                strPath = "/".join(item.getPhysicalPath())
                query = {'path': {'query': strPath,'depth':1}, 'portal_type': ['SmartView','Topic'], 'sort_on': 'getObjPositionInParent', 'sort_order': 'asc'}
                results = catalog(query)

                if len(results) > 0:
                    for o in results:
                        itemresult = {
                                        'viewid':o.UID,
                                        'c': []
                                     }
                        getChildren(o.getObject(),catalog,itemresult['c'])
                        lstchildren.append(itemresult)
            except AttributeError:
                return ""

        for obj in resbrains:
            itemresult = {
                            'viewid':obj.UID,
                            'c': []
                         }
            getChildren(obj.getObject(),portal_catalog,itemresult['c'])

            outlist.append(itemresult)
        return outlist
    def setOwnPassword(self,newpassword):
        """Sets the current user's password"""
        mt = self.context.portal_membership
        mt.setPassword(newpassword)
        return True