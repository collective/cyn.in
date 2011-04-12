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
from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPlacelessPortletManager
from plone.app.portlets.interfaces import IColumn

class ISpacesRecent(IViewletManager):
    """A viewlet manager to show the Recent Spaces Viewlet
    """
class IAllSpacesMenuManager(IViewletManager):
    """A viewlet manager to show the All Spaces Menu
    """
class ISearchBoxManager(IViewletManager):
    """A viewlet manager to show the Search Box
    """
class IMyMenu(IViewletManager):
    """A viewlet manager to show the My Menu
    """
class IMyAvatar(IViewletManager):
    """A viewlet manager to show the currently logged in user's Avatar and whatever other details we want to
    """
class ISpaceIcon(IViewletManager):
    """A viewlet manager to show the icon of the Space currently being viewed.
    """
class ISpaceName(IViewletManager):
    """A viewlet manager to show the name and other basic stats of the Space currently being viewed.
    """
class ISpaceStats(IViewletManager):
    """A viewlet manager to show the basic stats of the Space currently being viewed.
    """
class IBreadcrumbsManager(IViewletManager):
    """A viewlet manager to show the breadcrumbs bar
    """
class IItemtitleManager(IViewletManager):
    """A viewlet manager to show the current Item's title
    """
class ITypetitleManager(IViewletManager):
    """A viewlet manager to show the current Item's portal type
    """
class IAddNewMenuManager(IViewletManager):
    """A viewlet manager to show the add new menu
    """
class IItemDateManager(IViewletManager):
    """A viewlet manager to show Item date in a stylized manner
    """
class IItemDescriptionManager(IViewletManager):
    """A viewlet manager to show the current item's description
    """
class IOwnerInfoManager(IViewletManager):
    """A viewlet manager to show the current Item's Owner's info
    """
class IOwnerAvatarManager(IViewletManager):
    """A viewlet manager to show the current Item's Owner's Avatar
    """
class IUbifyColophon(IViewletManager):
    """A viewlet manager to show the Ubify colophon
    """
class ICynapseColophon(IViewletManager):
    """A viewlet manager to show the Cynapse colophon
    """
class IUContentViews(IViewletManager):
    """A viewlet manager to show the View tabs of the actions bar
    """
class IUContentActions(IViewletManager):
    """A viewlet manager to show the Actions bar
    """
class ISiteHome(IViewletManager):
    """A viewlet manager to show all items on site home page
    """
class ISpaceRecentUpdates(IViewletManager):
    """A viewlet manager to show all recently updated items under a space
    """
class ISpaceMyItems(IViewletManager):
    """A viewlet manager to show all items created by current user
    """
class IFullViewMindMap(IViewletManager):
    """A viewlet manager to show all items at particular URL
    """
class ISiteTitle(IViewletManager):
    """A viewlet manager to show title of the site.
    """
class ISiteLogo(IViewletManager):
    """A viewlet manager to show logo of the site.
    """
class ISiteDescription(IViewletManager):
    """A viewlet manager to show site description
    """
class IItemMetaData(IViewletManager):
    """A viewlet manager to show item's meta data
    """
class IWorkFlowHistoryManager(IViewletManager):
    """A viewlet manager to item's workflow history
    """
class IDocumentActionsManager(IViewletManager):
    """A viewlet manager to show document actions 
    """
class ICyninColophon(IViewletManager):
    """A viewlet manager to show colophon for anonymous users
    """
class ICyninDashboard(IViewletManager):
    """A viewlet manager to load viewlet containing portlet manager
    """
class ISpaceMembers(IViewletManager):
    """A viewlet manager to load viewlet containing portlet manager for space members
    """
class ISpaceMembersPage(IViewletManager):
    """A viewlet manager to load viewlet for space members
    """
class IApplicationsTabs(IViewletManager):
    """A viewlet manager to show application tabs for all our applications
    """
class IMyAreaBlock(IViewletManager):
    """A viewlet manager to show a block display of a user's own area
    """
class IItemCounts(IViewletManager):
    """A viewlet manager to display an item's count related information below the description
    """
class IGotoTop(IViewletManager):
    """A viewlet manager to goto links
    """
class IUbifySEOProvider(IViewletManager):
    """A viewlet manager to provide an SEO area at bottom of page
    """
class ITagFilterPanel(IViewletManager):
    """A viewlet manager to provide filter panel
    """
class IApplicationsMenu(IViewletManager):
    """A viewlet manager to display a menu for the applications"""
class INavigationManager(IViewletManager):
    """A viewlet manager to display vertical navigation"""
class IAddDiscussionManager(IViewletManager):
    """A viewlet manager to show a add discussion block
    """    
class ILanguageSelectionManager(IViewletManager):
    """A viewlet manager to allow user to choose UI language
    """
    
# Portlet Manager
class IDashboardColumn(IPortletManager):
    """Common base class for cynin dashboard.
    """
class IHomeContent(IPortletManager,IDashboardColumn):
    """we need our own portlet manager above the content area.
    """