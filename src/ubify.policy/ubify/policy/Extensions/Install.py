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
import transaction
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from ubify.policy.config import PRODUCT_DEPENDENCIES,UNINSTALL_PRODUCTS

PRODUCT_DEPENDENCIES = PRODUCT_DEPENDENCIES

EXTENSION_PROFILES = ('ubify.policy:default',
)

def install(self,
 reinstall=False):
    """Install a set of products (which themselves may either use Install.py
    or GenericSetup extension profiles for their configuration) and then
    install a set of extension profiles.
    
    One of the extension profiles we install is that of this product. This
    works because an Install.py installation script (such as this one) takes
    precedence over extension profiles for the same product in 
    portal_quickinstaller. 
    
    We do this because it is not possible to install other products during
    the execution of an extension profile (i.e. we cannot do this during
    the importVarious step for this profile).
    """
    out = StringIO()
    from Products.GenericSetup.context import Logger,SetupEnviron
    import logging
    obj = SetupEnviron()
    logger = obj.getLogger("ubify.policy")
    outch = logging.StreamHandler(out)
    logger.addHandler(outch)
    
    #import pdb; pdb.set_trace()
    
    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')    
    
    if reinstall:        
        for product in PRODUCT_DEPENDENCIES:
            if not portal_quickinstaller.isProductInstalled(product):
                portal_quickinstaller.installProduct(product)
                transaction.savepoint()
        for product in PRODUCT_DEPENDENCIES:
            if portal_quickinstaller.isProductInstalled(product):
                portal_quickinstaller.reinstallProducts([product])
                transaction.savepoint()
            elif not portal_quickinstaller.isProductInstalled(product):
                portal_quickinstaller.installProduct(product)
                transaction.savepoint()
    else:
        for product in PRODUCT_DEPENDENCIES:
            if not portal_quickinstaller.isProductInstalled(product):
               logger.info("Installing missing product: %s" % product)
               portal_quickinstaller.installProduct(product)
               transaction.savepoint()
        
    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id, purge_old=False)
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()        
    
    #call one time installation here if reinstall is false
    portal = self
    
    
    if reinstall:
        
        for product in UNINSTALL_PRODUCTS:
            if portal_quickinstaller.isProductInstalled(product):
                try:                
                    from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct
                    
                    prod=getattr(portal_quickinstaller,product)
                    prod.uninstall(cascade=InstalledProduct.default_cascade, reinstall=False)
                    logger.info("Uninstalled product successfully : %s" % (product,))
                except AttributeError:
                    pass
                transaction.savepoint()
        
        from ubify.policy.migration.onetimeinstall import disableGlobalAdds,reorder_contenttyperegistry
        reorder_contenttyperegistry(portal,logger)
        disableGlobalAdds(portal,logger)
    else:        
        from ubify.policy.migration.onetimeinstall import assignStackerRelatedPortlet,setup_sitehome_portlets
        from ubify.policy.migration.onetimeinstall import disableGlobalAdds,disable_inlineEditing
        from ubify.policy.setuphandlers import addDefaultCategories
        from ubify.policy.migration.onetimeinstall import remove_navigationportlet,remove_calendarportlet
        from ubify.policy.migration.onetimeinstall import setchoosertype,configureRatings,add_custom_site_properties,add_custom_cynin_properties
        from ubify.policy.migration.onetimeinstall import enable_formats_fortextfield,assignCyninNavigation,reorder_contenttyperegistry
        
        add_custom_site_properties(portal,logger)
        add_custom_cynin_properties(portal,logger)
        reorder_contenttyperegistry(portal,logger)
        setchoosertype(portal,logger)                        
        addDefaultCategories(portal,logger)
        assignStackerRelatedPortlet(portal)
        disableGlobalAdds(portal,logger)
        setup_sitehome_portlets(portal,logger)
        disable_inlineEditing(portal,logger)
        remove_navigationportlet(portal,logger)
        remove_calendarportlet(portal,logger)
        configureRatings(portal,logger)
        enable_formats_fortextfield(portal,logger)
        assignCyninNavigation(portal,logger)
        
    from ubify.policy.migration.onetimeinstall import updateWorkflowSecurity
    updateWorkflowSecurity(portal,logger)
    return out.getvalue()
