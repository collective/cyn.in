##################################################################################
#    Copyright (C) 2004-2007 Utah State University, All rights reserved.          
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation; either version 2 of the License, or            
#    (at your option) any later version.                                          
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]

from zope.app.component.interfaces import ISite
from Products.Five.site.localsite import enableLocalSiteHook
from zope.app.component.hooks import setSite
from utilities.interfaces import IZipFileTransportUtility
from utilities.utils import ZipFileTransportUtility
from zope.component import getSiteManager


def importFinalSteps(context):
    site = context.getSite()
    setupUtilities(site)

def setupUtilities(site):
    """ Register a local utility """

    if not ISite.providedBy(site):
        enableLocalSiteHook(site)

    setSite(site)

    sm = getSiteManager()
    if not sm.queryUtility(IZipFileTransportUtility):
        sm.registerUtility(ZipFileTransportUtility('zipfiletransport'),
                        IZipFileTransportUtility)
