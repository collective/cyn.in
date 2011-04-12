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

def default_addable_types(context):
    """Return all globally allowed types where the factory permission
    is given to the Owner role.
    """

    portal_types = getToolByName(context, 'portal_types')
    
    dispatcher = getattr(context, 'manage_addProduct', None)
    types = set()

    for fti in portal_types.listTypeInfo():
        if getattr(fti, 'globalAllow', lambda: False)() == True:            
            role_permission = _get_role_permission_for_fti(context, fti)
            if role_permission is not None:
                if 'Owner' in role_permission.__of__(context):
                    types.add(fti.getId())
    
    return types

        
def get_factory_permission(context, fti):
    """Return the factory perimssion of the given type information object.
    """
    role_permission = _get_role_permission_for_fti(context, fti)
    if role_permission is None:
        return None
    return role_permission.__name__

def _get_role_permission_for_fti(context, fti):
    """Helper method to get hold of a RolePermission for a given FTI.
    """
    factory = getattr(fti, 'factory', None)
    product = getattr(fti, 'product', None)
    dispatcher = getattr(context, 'manage_addProduct', None)

    if factory is None or product is None or dispatcher is None:
        return None

    try:
        product_instance = dispatcher[product]
    except AttributeError:
        return None

    factory_method = getattr(product_instance, factory, None)
    if factory_method is None:
        return None

    factory_instance = getattr(factory_method, 'im_self', None)
    if factory_instance is None:
        return None

    factory_class = factory_instance.__class__
    role_permission = getattr(factory_class, factory+'__roles__', None)
    if role_permission is None:
        return None

    return role_permission