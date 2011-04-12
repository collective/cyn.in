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
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _

from zope.component import getUtility
from zope.app.publisher.interfaces.browser import IBrowserMenu

class IApplicationPortlet(IPortletDataProvider):
    """A portlet which renders mindmap for cyn.in site.
    """

class Assignment(base.Assignment):
    implements(IApplicationPortlet)    

    title = u"manage space."
    
def _render_cachekey(fun, self):
    raise ram.DontCache()
    if self.anonymous:
        raise ram.DontCache()
    return render_cachekey(fun, self)

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('applicationportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        menu = getUtility(IBrowserMenu, name='plone_contentmenu_factory')
        self.addnewitems = menu.getMenuItems(self.context, self.request)
        
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.canview = False
        if not self.anonymous:
            member = portal_state.member()
            if member.checkPermission('Add portal content',self.context):
                self.canview = True
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.canview

class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
