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
import traceback
from StringIO import StringIO

from zope import component
import AccessControl
import Acquisition
import Globals
from AccessControl import Permissions
from Products.CMFPlone import CatalogTool as base

import logging
logger = logging.getLogger('ubify.policy')

from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_base
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from ubify.coretypes.interfaces import ITypesRestriction
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

def disallowedtypes(obj,portal, **kw):
    if ITypesRestriction.providedBy(obj):
        return obj.disallowedtypes()
    else:
        return []
    
registerIndexableAttribute('disallowedtypes', disallowedtypes)
    
class CatalogTool(base.CatalogTool):

    security = AccessControl.ClassSecurityInfo()
    
    def reindexComments(self):
        pass
    
    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        
        def indexObject(obj, path):	    
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject)):
                try:
                    obj.indexObject()
                    pdtool = obj.portal_discussion
                    if pdtool.isDiscussionAllowedFor(obj):                        
                        tb = pdtool.getDiscussionFor(obj)
                        for ob in tb.getReplies():
                                ob.indexObject()
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
        self.manage_catalogClear()
        
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(portal, search_sub=True, apply_func=indexObject)

CatalogTool.__doc__ = base.CatalogTool.__doc__
Globals.InitializeClass(CatalogTool)
