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
from plone.app.portlets.manager import ColumnPortletManagerRenderer as BaseClass
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer as baseCEPMR
from plone.portlets.interfaces import ILocalPortletAssignable
from Products.CMFCore.utils import getToolByName

class ColumnPortletManagerRenderer(BaseClass):
    """A customized renderer for the column portlets
    """
    template = ViewPageTemplateFile('column.pt')
    
    def isinmanagerrole(self):        
        returnval = False
        
        from AccessControl import getSecurityManager
        from zope.component import getMultiAdapter
        
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        if not portal_state.anonymous():
            user = getSecurityManager().getUser()
            bFound = False
            for erole in user.getRoles():
                if erole.lower() == 'manager':
                    bFound = True
                if bFound:
                    break;
            
            if bFound:
                returnval = True
        return returnval
    
    def can_manage_portlets(self):
        context = self._context()
        if not ILocalPortletAssignable.providedBy(context):
            return False
        mtool = getToolByName(context, 'portal_membership')
        return mtool.checkPermission("Portlets: Manage portlets", context) and self.isinmanagerrole()

from zope.interface import Interface
from zope.component import adapts, getMultiAdapter

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.manager import PortletManagerRenderer
from ubify.viewlets.browser.interfaces import IDashboardColumn
from interfaces import ISpaceMembersColumn, IMindmapColumn, IHomeLeftblockColumn

class DashboardColumnPortletRenderer(PortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IDashboardColumn)
    
    template = ViewPageTemplateFile('homecontentdashboard.pt')
    
class SpaceMembersColumnPortletRenderer(PortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView,ISpaceMembersColumn)
    
    template = ViewPageTemplateFile('spacemembersportletdashboard.pt')
    
class MindmapColumnPortletRenderer(PortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IMindmapColumn)
    
    template = ViewPageTemplateFile('mindmapdashboard.pt')
    
class HomeLeftBlockColumnPortletRenderer(PortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IHomeLeftblockColumn)
    
    template = ViewPageTemplateFile('homeleftblockdashboard.pt')
    
class ContextualEditPortletManagerRenderer(baseCEPMR):
    template = ViewPageTemplateFile('edit-manager-contextual.pt')
    
    def is_available(self):        
        returnval = False
        
        from AccessControl import getSecurityManager
        from zope.component import getMultiAdapter
        
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        if not portal_state.anonymous():
            user = getSecurityManager().getUser()
            bFound = False
            for erole in user.getRoles():
                if erole.lower() == 'manager':
                    bFound = True
                if bFound:
                    break;
            
            if bFound:
                returnval = True
        return returnval
    
    
from plone.app.iterate.containers import HomeFolderLocator as BaseHomeFolderLocator
class HomeFolderLocator(BaseHomeFolderLocator):
    
    @property
    def available(self):
        return None
    
    
from Products.ZipFileTransport.browser.zipexport import ExportForm as BaseExportForm
from zope.formlib.form import action
import string

class ExportForm(BaseExportForm):
    """ Render the export form  """
    
    @action('Export')
    def action_export(self, action, data):
        #Discover Object Paths in hidden form fields
        obj_paths = None
        try:
            self.context.REQUEST['form.obj_paths']
            paths = self.context.REQUEST['form.obj_paths']
            obj_paths = []
            for x in paths:
                x = x.encode('utf-8')
                obj_paths += [x]
        except:
            pass
        filename = self.context.REQUEST['form.filename']

        if string.find(filename,'.zip') == -1:
            filename += ".zip"
        
        if self.context.portal_membership.isAnonymousUser() != 0:
            return

        zipfilename = self.zft_util.generateSafeFileName(filename)

        content = self.zft_util.exportContent(context=self.context,obj_paths=obj_paths, filename=filename)

        self.context.REQUEST.RESPONSE.setHeader('content-type', 'application/zip')
        self.context.REQUEST.RESPONSE.setHeader('content-length', len(content))
        self.context.REQUEST.RESPONSE.setHeader('Content-Disposition',' attachment; filename='+zipfilename)

        return content

from plone.app.contentmenu.menu import DisplaySubMenuItem as BaseDisplaySubMenuItem
from plone.memoize.instance import memoize

class DisplaySubMenuItem(BaseDisplaySubMenuItem):
    
    @memoize
    def disabled(self):
        return True

from plone.app.contentmenu.menu import FactoriesSubMenuItem as BaseFactoriesSubMenuItem
class FactoriesSubMenuItem(BaseFactoriesSubMenuItem):
    
    def available(self):        
        return False
    
from plone.app.contentmenu.menu import WorkflowSubMenuItem as BaseWorkflowSubMenuItem
from ubify.policy import CyninMessageFactory as _
class WorkflowSubMenuItem(BaseWorkflowSubMenuItem):
    
    title = _(u'lbl_change_state', default=u'Change State')
    
    @property
    def description(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return _(u'title_change_state_of_item', default=u'Change the state of this item')
        else:
            return u''
    
from plone.app.contentmenu.view import ContentMenuProvider as BaseContentMenuProvider
from zope.component import getUtility,getAdapters
from zope.app.publisher.interfaces.browser import IBrowserMenu
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class ContentMenuProvider(BaseContentMenuProvider):
    
    render = ZopeTwoPageTemplateFile('contentmenu.pt')
    
    def menu(self):        
        items = BaseContentMenuProvider.menu(self)
        removeWFMenu = False
        wfmenuitems = [k for k in items if k.has_key('extra') and k['extra'].has_key('id') and k['extra']['id'] == 'plone-contentmenu-workflow']
        if len(wfmenuitems) > 0:
            wfmenuitem = wfmenuitems[0]
            if wfmenuitem.has_key('submenu'):
                submenus = wfmenuitem['submenu']
                #first check for policy access.
                if submenus <> None:
                    policyresults = [k for k in submenus if k.has_key('extra') and k['extra'].has_key('id') and k['extra']['id'] == 'policy']
                    if len(policyresults) > 0:
                        from ubify.cyninv2theme import checkHasPermission
                        if not checkHasPermission('Manage portal',self.context):
                            submenus.remove(policyresults[0])                                
        
        return items

from plone.app.iterate.relation import CheckinCheckoutReferenceAdapter as baseCheckinCheckoutReferenceAdapter
class CheckinCheckoutReferenceAdapter(baseCheckinCheckoutReferenceAdapter):
    def checkout( self, baseline, wc, refs, storage ):
        from Products.ATRatings.references import RatingsReference        
        for ref in refs:
            if not isinstance(ref,RatingsReference):
                wc.addReference( ref.targetUID, ref.relationship, referenceClass=ref.__class__)

