from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase
from Products.WebServerAuth.utils import firstIdOfClass
from Products.WebServerAuth.plugin import MultiPlugin, implementedInterfaces
from Products.WebServerAuth.tests.base import WebServerAuthTestCase


PloneTestCase.installProduct('WebServerAuth')
PloneTestCase.setupPloneSite(products=['WebServerAuth'])


class InstallTestCase(WebServerAuthTestCase):
    def installedMultipluginId(self):
        """Return the installed multiplugin or, if none is installed, None."""
        return firstIdOfClass(self._acl_users(), MultiPlugin)


class TestInstall(InstallTestCase):
    def testPluginIsInstalled(self):
        """Make sure the PAS plugin got into acl_users and activated."""
        pluginId = self.installedMultipluginId()
        self.failUnless(pluginId, msg="Installation didn't put a WebServerAuth multiplugin instance into acl_users.")
        for interface in implementedInterfaces:
            self.failUnless(pluginId in self._acl_users()['plugins'].listPluginIds(interface), msg="Plugin wasn't activated on the %s interface." % interface.__name__)


class TestUninstall(InstallTestCase):
    def afterSetUp(self):
        InstallTestCase.afterSetUp(self)
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(products=['WebServerAuth'])
    
    def testPluginIsNotInstalled(self):
        """Make sure the PAS plugin is no longer in acl_users."""
        self.failIf(self.installedMultipluginId(), msg="Uninstallation didn't remove the WebServerAuth multiplugin instance from acl_users.")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstall))
    suite.addTest(makeSuite(TestUninstall))
    return suite
