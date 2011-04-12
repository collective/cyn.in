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
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import get_language

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _
from ubify.policy.config import spacesdefaultaddablenonfolderishtypes

from Products.CMFCore.utils import getToolByName

class ITagsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of tags to display'),
                       description=_(u'How many tags to list?'),
                       required=True,
                       default=20)   
    

class Assignment(base.Assignment):
    implements(ITagsPortlet)

    def __init__(self, count=20):
        self.count = count                

    @property
    def title(self):
        return _(u"Tags Portlet")

def _render_cachekey(fun, self):    
    if self.anonymous:
        raise ram.DontCache()
    
    context = aq_inner(self.context)
    
    def add(object):
        tname = object['tagname'].decode('ascii','ignore')
        return "%s\n%s\n\n" % (tname,object['count'])
    
    path = "/".join(self.context.getPhysicalPath()).decode('ascii', 'ignore')
    if self.is_site_home:
        path = "/".join(self.portal.getPhysicalPath()).decode('ascii', 'ignore')
    fingerprint = "".join(map(add,self._data())) + "\n" + path + "\n\n"
    
    anonymous = getToolByName(context, 'portal_membership').isAnonymousUser()

    return "".join((
        getToolByName(aq_inner(self.context), 'portal_url')(),
        get_language(aq_inner(self.context), self.request),
        str(anonymous),
        self.manager.__name__,
        self.data.__name__,
        fingerprint))

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('tagsportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.plone_view = getMultiAdapter((self.context, self.request),name='plone')
        
        self.limit_display = self.data.count
        
        member = portal_state.member()
        self.userid = member.getId()
        
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')
        from urllib import urlencode
        strCurrentPath = "/".join(context_state.context.getPhysicalPath())
        self.location = urlencode({'path':strCurrentPath})
        self.portal = portal_state.portal()
        self.is_site_home = False
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())
    
    def records(self):
        return self.data.count
    
    @property
    def available(self):
        return len(self._data())

    def mostusedtags(self):
        limit = self.data.count
        results = self._data()
        results = [k for k in results if k['count'] > 0]
        results.sort(lambda x,y: cmp(x['tagname'].lower(),y['tagname'].lower()),reverse=False)
        return results
    
    @memoize
    def _data(self):        
        limit = self.data.count
        
        from statistics import getMostUsedTags
        strpath = "/".join(self.context.getPhysicalPath())
        try:
            from ubify.policy.config import contentroot_details
            rootid = contentroot_details['id']                
            objRoot = getattr(self.portal,rootid)
            if self.context == objRoot:
                strpath = "/".join(self.portal.getPhysicalPath())
                self.is_site_home = True
            else:
                strpath = "/".join(self.context.getPhysicalPath())
                self.is_site_home = False
        except AttributeError:
            strpath = "/".join(self.context.getPhysicalPath())
        
        try:
            results = getMostUsedTags(self.context,strpath)
        except AttributeError:
            results = []
        
        results = [k for k in results if k['count'] > 0]
        return results[:limit]
    
class AddForm(base.AddForm):
    form_fields = form.Fields(ITagsPortlet)
    label = _(u"Add Tags Portlet")
    description = _(u"A portlet that renders a tag cloud of tags used within the context of the space and all contained spaces.")

    def create(self, data):
        return Assignment(count=data.get('count', 20))

class EditForm(base.EditForm):
    form_fields = form.Fields(ITagsPortlet)
    label = _(u"Edit Tags Portlet")
    description = _(u"A portlet that renders a tag cloud of tags used within the context of the space and all contained spaces.")
