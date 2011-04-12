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
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

# These are traditional products (in the Products namespace). They'd normally
# be loaded automatically, but in tests we have to load them explicitly. This
# should happen at module level to make sure they are available early enough.

ztc.installProduct('SimpleAttachment')
ztc.installProduct('RichDocument')

@onsetup
def setup_ubify_policy():
    """Set up the additional products required for the Optilux site policy.
    
        The @onsetup decorator causes the execution of this body to be deferred
        until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the optilux.policy package.
    
    fiveconfigure.debug_mode = True
    import ubify.policy
    zcml.load_config('configure.zcml', ubify.policy)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('ubify.policy')
    ztc.installPackage('ubify.theme')

# The order here is important: We first call the (deferred) function
# which installs the products we need for the Optilux package. Then,
# we let PloneTestCase set up this product on installation.

setup_ubify_policy()
ptc.setupPloneSite(products=['ubify.policy'])

class UbifyPolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """