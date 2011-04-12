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

class IRecentSiteUpdatesPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list?'),
                       required=True,
                       default=10)   
    

class Assignment(base.Assignment):
    implements(IRecentSiteUpdatesPortlet)

    def __init__(self, count=10):
        self.count = count        
        self.resultscount = {}

    @property
    def title(self):
        return _(u"Recent Site Updates")

def _render_cachekey(fun, self):    
    if self.anonymous:
        raise ram.DontCache()
    
    context = aq_inner(self.context)
    
    def add(brain):        
        path = brain.getPath().decode('ascii', 'replace')        
        return "%s\n%s\n\n" % (path, brain.modified)
    
    objdata = self._data()
    objalldata = [objdata.extend(self._data(k)) for k in self.typesToShow]
    
    fingerprint = "".join(map(add,objdata)) + "\n" + "\n".join([str(k) for k in self.data.resultscount.values()])
    
    anonymous = getToolByName(context, 'portal_membership').isAnonymousUser()

    return "".join((
        getToolByName(aq_inner(self.context), 'portal_url')(),
        get_language(aq_inner(self.context), self.request),
        str(anonymous),
        self.manager.__name__,
        self.data.__name__,
        fingerprint))

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('recentsiteupdatesportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = spacesdefaultaddablenonfolderishtypes + ('StatuslogItem',)
        self.plone_view = getMultiAdapter((self.context, self.request),name='plone')
        self.title = "Recent Updates"
        self.limit_display = self.data.count
        
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
        context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')
        from urllib import urlencode
        strCurrentPath = "/".join(context_state.context.getPhysicalPath())
        self.location = urlencode({'path':strCurrentPath})
        
        self.portal = portal_state.portal()
        self.showmessages = False
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):        
        return len(self._data())

    def results(self,types=None):        
        return self._data(types)
    
    def resultscount(self,types=None):
        totalcount = 0
        if types is None:
            totalcount = self.data.resultscount['all']
        else:
            totalcount = self.data.resultscount[types]
        return totalcount
    
    
    @memoize
    def _data(self,types=None):        
        if types is None:
            types = self.typesToShow
            ptypes = 'all'
        else:
            ptypes = types
            
        limit = self.data.count
        try:
            from ubify.policy.config import contentroot_details
            rootid = contentroot_details['id']                
            objRoot = getattr(self.portal,rootid)
            if self.context == objRoot:
                strpath = "/".join(self.portal.getPhysicalPath())
                self.showmessages = True
            else:
                strpath = "/".join(self.context.getPhysicalPath())
                if self.context.portal_type in ('MemberSpace'):
                    self.showmessages = True                
        except AttributeError:
            strpath = "/".join(self.context.getPhysicalPath())        
        
        objpath = {'query':strpath}
        objresults = self.catalog(path=objpath,
                            portal_type=types,
                            sort_on='lastchangedate',
                            sort_order='reverse')
        
        self.data.resultscount[ptypes] = (len(objresults) - limit)
        return objresults[:limit]


class AddForm(base.AddForm):
    form_fields = form.Fields(IRecentSiteUpdatesPortlet)
    label = _(u"Add Recent Site Updates Portlet")
    description = _(u"A portlet that renders a list of recent content of all types from within the context of the space and all contained spaces.")

    def create(self, data):
        return Assignment(count=data.get('count', 10))

class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentSiteUpdatesPortlet)
    label = _(u"Edit Recent Site Updates Portlet")
    description = _(u"A portlet that renders a list of recent content of all types from within the context of the space and all contained spaces.")
