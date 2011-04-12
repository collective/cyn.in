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
from plone.theme.interfaces import IDefaultPloneLayer
from plone.portlets.interfaces import IPortletManager
from zope.interface import Interface

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
    
class ISpaceMembersColumn(IPortletManager):
    """Common base class for cynin dashboard.
    """
class ISpaceMembersContent(IPortletManager,ISpaceMembersColumn):
    """we need our own portlet manager above the content area.
    """
    
class IMindmapColumn(IPortletManager):
    """Common base class for cynin mindmap dashboard
    """
    
class IMindMapContent(IMindmapColumn):
    """portlet manager for adding mindmap portlet
    """
    
class IHomeLeftblockColumn(IPortletManager):
    """Common base class for left block on home page
    """
    
class IHomeLeftblockContent(IHomeLeftblockColumn):
    """portlet manager for adding recent updates blocks
    """
    
class INavigationColumn(IPortletManager):
    """Common base class for navigation manager
    """

class INavigationSpacesContent(INavigationColumn):
    """portlet manager for adding navigation portlet for spaces
    """

class INavigationCollectionContent(INavigationColumn):
    """portlet manager for adding navigation portlet for collection
    """
    
class INavigationMembersContent(INavigationColumn):
    """portlet manager for adding navigation portlet for members
    """
    
class ICyninNavigation(Interface):
    """ cyn.in site need to have vertical navigation 
    """
    
class IUnknownColumn(IPortletManager):
    """Common base class for assigning portlets which we don't want to be available in new version to end users
    """