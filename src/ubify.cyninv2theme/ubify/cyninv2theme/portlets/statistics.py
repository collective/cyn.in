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
from ubify.policy.config import spacesdefaultaddablenonfolderishtypes
import math
from openFlashChart import template
from openFlashChart_varieties import HBar, hbar_value, Pie, pie_value, x_axis_labels
from AccessControl import getSecurityManager
from ubify.policy import CyninMessageFactory as _

def buildQuery(query,queryparam):
    for key in queryparam.keys():
        query[key] = queryparam[key]    
    return query

def getTotalCountForQuery(context,path=None,queryparam={}):
    ct = getToolByName(context,'portal_catalog')
    count = 0
    query = {}
    if path is not None and path != '':
        query['path'] = {'query':path}
    count = len(ct(**(buildQuery(query,queryparam))))
    return count

def getchartmax(max):
    newmax = max
    found = False
    for i in range(1,11):
        if max > math.pow(10,i-1) and max < math.pow(10,i):
            newmodval = math.pow(10,i-1)
            modvalue = math.fmod(max,newmodval)
            newmax = max + (newmodval - modvalue)
            found = True
        if found:
            break;

    return newmax

def getchartsteps(min,max):
    diff = 0
    steps = 0.5
    found = False

    if min == max :
        diff = min / (5 - 1)
    else:
        diff = (max - min) / (5 - 1)

    if diff != 0:
        for i in range(1,11):
            if diff > math.pow(10,i-1) and diff < math.pow(10,i):

                if max > math.pow(10,i):
                    steps = math.pow(10,i)
                else:
                    steps = math.pow(10,i-1)
                found = True
            if found:
                break;

    return steps

def getTopContributors(context,path=None,depth=None):
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    if path is not None and path != '':
        query['path'] = {'query':path}
    query['portal_type'] = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)
    lstinfo = [{'userid':k,'count':len(ct(**(buildQuery(query,{'modifiers':k}))))} for k in ct.uniqueValuesFor('modifiers')]
    lstinfo.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)

    return lstinfo

def getContributionCount(context,path=None,depth=None,user=None):
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    query['portal_type'] = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)
    count = len(ct(**(buildQuery(query,{'modifiers':user}))))
    return count

def getTopCommenter(context,path=None,depth=None):
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    if path is not None and path != '':
        query['path'] = {'query':path}
    lstinfo = [{'userid':k,'count':len(ct(**(buildQuery(query,{'Creator':k,'portal_type':'Discussion Item'}))))} for k in ct.uniqueValuesFor('Creator')]
    lstinfo.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)
    return lstinfo

def getCommentCount(context,path=None,depth=None,user=None):
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    count = len(ct(**(buildQuery(query,{'Creator':user,'portal_type':'Discussion Item'}))))
    return count

def getRecentlyActiveMembers(context,path=None,depth=None):
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    if path is not None and path != '':
        query['path'] = {'query':path}
    query['portal_type'] = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)
    query['sort_order'] = 'reverse'
    query['sort_on'] = 'lastchangedate'
    lstinfo = [{'userid':k,'lastchangedate':ct(**(buildQuery(query,{'lastchangeperformer':k})))[0].lastchangedate} for k in ct.uniqueValuesFor('lastchangeperformer') if len(ct(**(buildQuery(query,{'lastchangeperformer':k})))) > 0]
    lstinfo.sort(lambda x,y: cmp(x['lastchangedate'],y['lastchangedate']),reverse=True)
    return lstinfo

def getMostUsedTags(context,path=None,depth=None):
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    if path is not None and path != '':
        query['path'] = {'query':path}
    query['portal_type'] = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)
    lstinfo = [{'tagname':k,'count':len(ct(**(buildQuery(query,{'Subject':k}))))} for k in ct.uniqueValuesFor('Subject')]
    lstinfo.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)
    return lstinfo

def getMostUsedTagsForUser(context,user=None,path=None):
    if user is None:
        currentuserid = getSecurityManager().getUser().getId()
        if currentuserid <> None:
            user = currentuserid
    
    ct = getToolByName(context,'portal_catalog')
    lstinfo = []
    query = {}
    if path is not None and path != '':
        query['path'] = {'query':path}
    query['portal_type'] = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)
    query['modifiers'] = user
    
    lstinfo = [{'tagname':k,'count':len(ct(**(buildQuery(query,{'Subject':k}))))} for k in ct.uniqueValuesFor('Subject')]
    lstinfo = [k for k in lstinfo if k['count'] > 0]
    lstinfo.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)
    return lstinfo

def getTotalCountForIndexType(context,path,indextype):
    """Returns total of unique index type. For eg. when 'Subject' is passed, this method returns total tags count."""
    ct = getToolByName(context,'portal_catalog')
    count = 0
    count = len(ct.uniqueValuesFor(indextype))
    return count

def getTotalUsersCount(context):
    userscount = 0
    usersdata = []    
    if context.portal_type in ('ContentSpace'):
        usersdata = getUsersCountForSpace(context,('Users','Editors','Contributors','Readers',))        
    else:
        search_view = context.restrictedTraverse('@@pas_search')
        userscount = len(search_view.searchUsersByRequest(context.REQUEST, sort_by='fullname'))
        usersdata.append({'id':'Users','dispid':context.translate(_(u'lbl_stats_users',u'Users')),'count':userscount})
    return usersdata

def getContentItemsCount(context,path=None):
    lstinfo = []

    totalwikipages = getTotalCountForQuery(context,path,{'portal_type':'Document'})
    lstinfo.append({'id':'Wiki Pages','dispid':context.translate(_(u'lbl_stats_wiki_pages',u'Wiki Pages')),'count':totalwikipages})

    totalblogentries = getTotalCountForQuery(context,path,{'portal_type':'Blog Entry'})
    lstinfo.append({'id':'Blog Entries','dispid':context.translate(_(u'lbl_stats_blog_entries',u'Blog Entries')),'count':totalblogentries})

    totalfiles = getTotalCountForQuery(context,path,{'portal_type':'File'})
    lstinfo.append({'id':'Files','dispid':context.translate(_(u'lbl_stats_files',u'Files')),'count':totalfiles})

    totalimages = getTotalCountForQuery(context,path,{'portal_type':'Image'})
    lstinfo.append({'id':'Images','dispid':context.translate(_(u'lbl_stats_status_images',u'Images')),'count':totalimages})

    totallinks = getTotalCountForQuery(context,path,{'portal_type':'Link'})
    lstinfo.append({'id':'WebLinks','dispid':context.translate(_(u'lbl_stats_status_weblinks',u'WebLinks')),'count':totallinks})

    totalstatusmessages = getTotalCountForQuery(context,path,{'portal_type':'StatuslogItem'})
    lstinfo.append({'id':'Status Messages','dispid':context.translate(_(u'lbl_stats_status_msgs',u'Status Messages')),'count':totalstatusmessages})

    totalvideos = getTotalCountForQuery(context,path,{'portal_type':'Video'})
    lstinfo.append({'id':'Videos','dispid':context.translate(_(u'lbl_stats_videos',u'Videos')),'count':totalvideos})

    totalevents = getTotalCountForQuery(context,path,{'portal_type':'Event'})
    lstinfo.append({'id':'Events','dispid':context.translate(_(u'lbl_stats_events',u'Events')),'count':totalevents})
    
    totaldiscussions = getTotalCountForQuery(context,path,{'portal_type':'Discussion'})
    lstinfo.append({'id':'Discussions','dispid':context.translate(_(u'lbl_stats_discussions',u'Discussions')),'count':totaldiscussions})
    
    totalaudios = getTotalCountForQuery(context,path,{'portal_type':'Audio'})
    lstinfo.append({'id':'Audios','dispid':context.translate(_(u'lbl_stats_audios',u'Audios')),'count':totalaudios}) 

    return lstinfo

def getTotalItemCount(context):
    return  getTotalCountForQuery(context,path='/'.join(context.getPhysicalPath()),queryparam={'portal_type':spacesdefaultaddablenonfolderishtypes})

def getSiteStatistics(context,path=None,ignoreviews=True,ignoretags=True):
    lstinfo = []
    
    lstinfo.extend(getTotalUsersCount(context))
    
    totalspaces = getTotalCountForQuery(context,path,{'portal_type':'ContentSpace'})
    lstinfo.append({'id':'Spaces','dispid':context.translate(_(u'lbl_stats_spaces',u'Spaces')),'count':totalspaces})

    if not ignoreviews:
        totalviews = getTotalCountForQuery(context,path,{'portal_type':'Topic'}) + getTotalCountForQuery(context,path,{'portal_type':'SmartView'})
        lstinfo.append({'id':'Collections','dispid':context.translate(_(u'lbl_stats_collections',u'Collections')),'count':totalviews})

    if not ignoretags:
        totaltags = getTotalCountForIndexType(context,path,'Subject')
        lstinfo.append({'id':'Tags','dispid':context.translate(_(u'lbl_stats_tags',u'Tags')),'count':totaltags})

    totalitems = getTotalCountForQuery(context,path,{'portal_type':spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)})
    lstinfo.append({'id':'Items','dispid':context.translate(_(u'lbl_stats_items',u'Items')),'count':totalitems})

    totalcomments = getTotalCountForQuery(context,path,{'portal_type':'Discussion Item'})
    lstinfo.append({'id':'Comments','dispid':context.translate(_(u'lbl_stats_comments',u'Comments')),'count':totalcomments})

    return lstinfo

def getjsondata(context,records=10,type=None):
    site_encoding = context.plone_utils.getSiteEncoding()
    strpath = "/".join(context.getPhysicalPath())
    portal = context.portal_url.getPortalObject()
    
    try:
        from ubify.policy.config import contentroot_details
        rootid = contentroot_details['id']                
        objRoot = getattr(portal,rootid)
        if context == objRoot:
            strpath = "/".join(portal.getPhysicalPath())            
        else:
            strpath = "/".join(context.getPhysicalPath())            
    except AttributeError:
        strpath = "/".join(context.getPhysicalPath())
        
    if type is None:
        raise "No chart type was passed"
    elif type.lower() == "topcontributors":
        chart = template('')
        plot = HBar()
        results = getTopContributors(context,strpath)[:records]
        results.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)
        objvalues = [k['count'] for k in results if k['count'] > 0]

        users = [j['userid'] for j in results if j['count'] > 0]
        users.reverse()

        xlabels = x_axis_labels()
        xlabels.set_colour("#666666")
        chartsteps = 1.0
        if len(objvalues) > 0:
            chartsteps = getchartsteps(objvalues[-1],objvalues[0])
        chart.set_x_axis(offset = False, labels = xlabels,steps = chartsteps,colour="#cccccc",grid_colour="#f1f1f1")
        chart.set_y_axis(offset=True,labels = users,colour="#666666",grid_colour="#f1f1f1")

        for val in objvalues:
            #plot.append_values(hbar_value((0, val), tooltip = '#right# contributions', colour = '#4092D8'))
            plot.append_values(
                               hbar_value((0, val), 
                               tooltip = '#right# %s' % (context.translate(_(u'lbl_stats_tooltip_contributions',u'contributions'))),
                               colour = '#4092D8')
            )
        chart.add_element(plot)
        chart.set_tooltip(stroke=1,colour="#1f1f1f",bg_colour="#292929",title_style="font-size:12px;color:#ffffff;font-weight:bold",body_style="font-size:12px;color:#ffffff",behaviour="hover")

        chart.set_bg_colour("#FFFFFF")
        return chart.encode()

    elif type.lower() == "topcommenters":
        chart = template('')
        plot = HBar()
        results = getTopCommenter(context,strpath)[:records]
        results.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)
        objvalues = [k['count'] for k in results if k['count'] > 0]

        users = [j['userid'] for j in results if j['count'] > 0]
        users.reverse()

        xlabels = x_axis_labels()
        xlabels.set_colour("#666666")
        chartsteps = 1.0
        if len(objvalues) > 0:
            chartsteps = getchartsteps(objvalues[-1],objvalues[0])
        chart.set_x_axis(offset = False, labels = xlabels,steps = chartsteps,colour="#cccccc",grid_colour="#f1f1f1")
        chart.set_y_axis(offset=True,labels = users,colour="#666666",grid_colour="#f1f1f1")
        
        for val in objvalues:
            #plot.append_values(hbar_value((0, val), tooltip = '#right# comments', colour = '#57AC0B'))
            #if len(val) == 1:
            #   tooltip_comment = '#right# %s' % (context.translate(_(u'lbl_stats_tooltip_comment',u'comment'))),
            #if len(val) > 1:
            #   tooltip_comment = '#right# %s' % (context.translate(_(u'lbl_stats_tooltip_comments',u'comments'))),
            plot.append_values(
                               hbar_value((0, val), 
                                          #tooltip = '#right# %s' % (tooltip_comment),                                             
                                          tooltip = '#right# %s' % (context.translate(_(u'lbl_stats_tooltip_comments',u'comments'))),
                                          colour = '#57AC0B')
            )
        chart.add_element(plot)
        chart.set_tooltip(stroke=1,colour="#1f1f1f",bg_colour="#292929",title_style="font-size:12px;color:#ffffff;font-weight:bold",body_style="font-size:12px;color:#ffffff",behaviour="hover")

        chart.set_bg_colour("#FFFFFF")
        return chart.encode()

    elif type.lower() == "contentstats":
        #For pie chart
        results = [k for k in getContentItemsCount(context,strpath) if k['count'] > 0]
        results.sort(lambda x,y: cmp(x['count'],y['count']),reverse=True)

        chart = template('')
        plot = Pie(start_angle = 35, animate = True, values = [pie_value(val = k['count'],label = (k['id'],None, None)) for k in results],colours = ['#4092D8', '#57AC0B', '#CC0000', '#862DFF', '#FF6600',  '#00FFF6','#FF37D2', '#5251ff', '#F0EA80', '#abff00',], label_colour = '#666666')
#        plot.set_tooltip('#label#: #val# of #total#<br>#percent# of 100%')
#        plot = Pie(
#		start_angle = 35, 
#		animate = True, 
#		values = [pie_value(val = k['count'],
#		label = (k['id'],None, None)) for k in results],
#		colours = ['#4092D8', '#57AC0B', '#CC0000', '#862DFF', '#FF6600', '#00FFF6','#FF37D2', '#5251ff', '#F0EA80', '#abff00',], 
#		label_colour = '#666666'
#	)
        msg = '#label#: #val# %s #total#<br>#percent# %s' % (context.translate(_(u'lbl_stats_val_of_total',u'of')),
                                                             context.translate(_(u'lbl_stats_val_of_100',u'of 100%'))
                                                            )
        plot.set_tooltip(msg)
        plot.set_gradient_fill(True)
        plot.set_no_labels(False)

        chart.add_element(plot)
        chart.set_tooltip(stroke=1,colour="#1f1f1f",bg_colour="#292929",title_style="font-size:12px;color:#ffffff;font-weight:bold",body_style="font-size:12px;color:#ffffff",behaviour="hover")
        chart.set_bg_colour("#FFFFFF")
        return chart.encode()

    else:
        raise "Unknown chart type was passed"

def getRecentContributionForUser(context,user=None,types_to_include=None,records=10):
    portal = context.portal_url.getPortalObject()
    ct = getToolByName(context,'portal_catalog')

    if user is None:
        currentuserid = getSecurityManager().getUser().getId()
        if currentuserid <> None:
            user = currentuserid

    if types_to_include is None:
        types_to_include = spacesdefaultaddablenonfolderishtypes

    moreurl = ''
    try:
        from ubify.policy.config import contentroot_details
        rootid = contentroot_details['id']
        objRoot = getattr(portal,rootid)
        strpath = "/".join(portal.getPhysicalPath())
        moreurl = objRoot.absolute_url()
    except AttributeError:
        strpath = "/".join(context.getPhysicalPath())
        moreurl = context.absolute_url()
    query = {}
    objpath = {'query':strpath}
    if types_to_include == 'Discussion Item':
        query = buildQuery(query,{'path':objpath,'portal_type':types_to_include,'Creator':user,'sort_on':'lastchangedate','sort_order':'reverse'})
    elif types_to_include == 'StatuslogItem':
        query = buildQuery(query,{'path':objpath,'portal_type':types_to_include,'Creator':user,'sort_on':'created','sort_order':'reverse'})
    else:
        query = buildQuery(query,{'path':objpath,'portal_type':types_to_include,'modifiers':user,'sort_on':'lastchangedate','sort_order':'reverse'})

    objresults = ct(**(query))
    morerecordscount = len(objresults) - records

    moreurl_part = "?modifiers:list=%s&sort_on=%s&sort_order=reverse" % (user,'lastchangedate')

    if types_to_include == 'StatuslogItem':
        moreurl_part = "?Creator=%s&sort_on=%s&sort_order=reverse" % (user,'created')
    
    if types_to_include == 'Discussion Item':
        moreurl = portal.absolute_url() + "/search?portal_type=Discussion Item&Creator=%s&sort_on=Date&sort_order=reverse" % (user,)
    else:
        moreurl = moreurl + "%s" + moreurl_part    
    
    return objresults[:records], morerecordscount, moreurl

def getTopRatedContent(context,path=None,depth=None,records=10):
    portal = context.portal_url.getPortalObject()
    ct = getToolByName(context,'portal_catalog')
    rtool = getToolByName(context,'portal_ratings')
    
    if rtool is None:
        return []
    
    types_to_include = rtool.allowed_rating_types
    if path is not None and path != '':
        strpath = path
    else:
        try:
            from ubify.policy.config import contentroot_details
            rootid = contentroot_details['id']                
            objRoot = getattr(portal,rootid)
            if context == objRoot:
                strpath = "/".join(portal.getPhysicalPath())
            else:
                strpath = "/".join(context.getPhysicalPath())
        except AttributeError:
            strpath = "/".join(context.getPhysicalPath())        
        
    query = {}
    objpath = {'query':strpath}    
    query = buildQuery(query,{'path':objpath,'portal_type':types_to_include})
    
    objresults = ct(**(query))
    
    ratedContent =  rtool.getTopRatingsAll(objresults)
    
    hasmorerateditems = False
    
    return ratedContent[:records], len(ratedContent) > records
    

def getTopRatedContentForUser(context,user=None):
    portal = context.portal_url.getPortalObject()
    ct = getToolByName(context,'portal_catalog')
    
    if user is None:
        currentuserid = getSecurityManager().getUser().getId()
        if currentuserid <> None:
            user = currentuserid
    
    rtool = getToolByName(context,'portal_ratings')
    
    if rtool is None:
        return [],''
    
    types_to_include = rtool.allowed_rating_types
        
    moreurl = ''
    try:
        from ubify.policy.config import contentroot_details
        rootid = contentroot_details['id']                
        objRoot = getattr(portal,rootid)        
        strpath = "/".join(portal.getPhysicalPath())
        moreurl = objRoot.absolute_url()
    except AttributeError:
        strpath = "/".join(context.getPhysicalPath())        
        moreurl = context.absolute_url()
    query = {}
    objpath = {'query':strpath}    
    query = buildQuery(query,{'path':objpath,'portal_type':types_to_include,'modifiers':user})
    
    objresults = ct(**(query))    
    
    moreurl_part = "?modifiers:list=%s&sort_on=%s&sort_order=reverse" % (user,'rating')
    moreurl = moreurl + "%s" + moreurl_part    
    
    return objresults, moreurl

def checkIfGroupGetUsers(listobjects,context):
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
    
def getUsersCountForSpace(context,roles_to_search):
    results = []
    
    listReaders = context.users_with_local_role('Reader')
    listReaders = checkIfGroupGetUsers(listReaders,context)
    
    listContributors = context.users_with_local_role('Contributor')
    listContributors = checkIfGroupGetUsers(listContributors,context)
    
    listReviewers = context.users_with_local_role('Reviewer')
    listReviewers = checkIfGroupGetUsers(listReviewers,context)

    listEditors = context.users_with_local_role('Editor')
    listEditors = checkIfGroupGetUsers(listEditors,context)

    
    for role_to_search in roles_to_search:
        objresults = []
        if role_to_search == 'Readers':
            for user in listReaders:
                if user not in listContributors and user not in listReviewers and user not in listEditors:
                    objresults.append(user)
        elif role_to_search == 'Contributors':
            for user in listContributors:
                if user not in listReviewers and user not in listEditors:
                    objresults.append(user)
        elif role_to_search == 'Reviewers':
            for user in listReviewers:
                if user not in listEditors:
                    objresults.append(user)
        elif role_to_search == 'Editors':
            objresults = listEditors
        else:   #Special case when all members will be listed priority given to managers
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
    
        results.append({'id':role_to_search,'dispid':context.translate(_(role_to_search,role_to_search)),'count':len(objresults)})
    
    return results
    
    
    