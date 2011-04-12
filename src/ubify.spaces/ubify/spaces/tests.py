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
import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_borg_project():
    """Set up the additional products required for the borg.project tests.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the borg.project package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import borg.project
    zcml.load_config('configure.zcml', borg.project)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Notice the extra package=True argument passed to 
    # installProduct() - this tells it that these packages are *not* in the
    # Products namespace.
    
    ztc.installPackage('borg.localrole')
    ztc.installPackage('borg.project')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Centrepoint package. Then, we let 
# PloneTestCase set up this product on installation.

setup_borg_project()
ptc.setupPloneSite(products=['borg.project'])

def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'README.txt', package='borg.project',
            test_class=ptc.FunctionalTestCase,
            optionflags=(doctest.ELLIPSIS | 
                         doctest.NORMALIZE_WHITESPACE)),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
