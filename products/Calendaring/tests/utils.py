# Calendaring is a simple CMF/Plone calendaring implementation.
# Copyright (C) 2004 Enfold Systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
$Id: utils.py,v 1.2 2004/09/17 13:58:26 dreamcatcher Exp $
"""

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.ArchetypeTool import FactoryTypeInformation
from Products.Archetypes.ArchetypeTool import fixActionsForType, getType
# XXX I have no idea what this is supposed to do, but it doesn't exist anymore.
# And it doesn't seem to be needed. //regebro
#from Products.Archetypes.Extensions.utils import _getFtiAndDataFor
from Products.CMFDynamicViewFTI import DynamicViewTypeInformation

# Mostly copied from ArchetypeTool.manage_installType
def installType(self, typeName, package, 
                portal_type=None, global_allow=False,
                dynamic=False):

    typesTool = getToolByName(self, 'portal_types')

    typeDesc = getType(typeName, package)
    klass = typeDesc['klass']
    typeinfo_name = "%s: %s (%s)" % (package, klass.__name__,
                                     klass.meta_type)

    if not portal_type:
        portal_type = typeDesc['portal_type']

    try:
        typesTool._delObject(portal_type)
    except:
        pass

    ft = FactoryTypeInformation
    if dynamic:
        ft = DynamicViewTypeInformation

    typesTool.manage_addTypeInformation(
        ft.meta_type,
        id=portal_type,
        typeinfo_name=typeinfo_name)

# XXX I have no idea what this is supposed to do, but it doesn't exist anymore.
# And it doesn't seem to be needed. //regebro
#    t, fti = _getFtiAndDataFor(typesTool, klass.portal_type, 
#                               klass.__name__, package)
#    if t and fti:
#        t.manage_changeProperties(**fti)

