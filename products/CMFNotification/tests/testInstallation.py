"""Tests for CMFNotification installation ad uninstallation.

$Id: testInstallation.py 65679 2008-05-25 23:45:26Z dbaty $
"""

from zope.component import getUtility
from zope.component import getMultiAdapter
from AccessControl.PermissionRole import rolesForPermissionOn

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFCore.utils import getToolByName

from Products.CMFNotification.config import LAYER_NAME
from Products.CMFNotification.config import PORTLET_NAME
from Products.CMFNotification.NotificationTool import ID as TOOL_ID
from Products.CMFNotification.permissions import SUBSCRIBE_PERMISSION

from Products.CMFNotification.tests.plonetestbrowser import Browser
from Products.CMFNotification.tests.base import CMFNotificationTestCase


class TestInstallation(CMFNotificationTestCase):
    """Make sure that the product is properly installed."""

    def afterSetUp(self):
        pass


    def testToolIsThere(self):
        portal = self.portal
        tool = getToolByName(self.portal, TOOL_ID)
        self.failUnless(tool is not None)


    def testSkinLayerIsThere(self):
        stool = getToolByName(self.portal, 'portal_skins')
        for skin, layers in stool._getSelections().items():
            layers = layers.split(',')
            self.failUnless(LAYER_NAME in layers)
        self.failUnless(LAYER_NAME in stool.objectIds())


    def testPortletCanBeAdded(self):
        base_url = self.portal.absolute_url()
        for name in ('plone.leftcolumn', 'plone.rightcolumn'):
            manager = getUtility(IPortletManager,
                                 name=name,
                                 context=self.portal)
            titles = [p.title for p in manager.getAddablePortletTypes()]
            self.failUnless(PORTLET_NAME in titles)

        manager = getUtility(IPortletManager,
                             name='plone.rightcolumn',
                             context=self.portal)
        right_portlets = getMultiAdapter((self.portal, manager),
                                         IPortletAssignmentMapping,
                                         context=self.portal)
        right_portlets = right_portlets.keys()
        self.failUnless(PORTLET_NAME in right_portlets)


    def testPermissionHasBeenSet(self):
        roles = set(rolesForPermissionOn(SUBSCRIBE_PERMISSION, self.portal))
        self.failUnlessEqual(roles, set(('Manager', 'Member')))


    def testConfigletHasBeenAdded(self):
        cptool = getToolByName(self.portal, 'portal_controlpanel')
        configlets = [c.getId() for c in cptool.listActions()]
        self.failUnless('cmfnotification_configuration' in configlets)



class TestUnInstallation(CMFNotificationTestCase):
    """Test that the product has been properly uninstalled."""

    def afterSetUp(self):
        """Uninstall the product before running each test."""
        qtool = getToolByName(self.portal, 'portal_quickinstaller')
        self.setRoles(['Manager'])
        qtool.uninstallProducts(['CMFNotification'])


    def testToolIsNotThere(self):
        tool = getToolByName(self.portal, TOOL_ID, None)
        self.failUnless(tool is None)


    def testSkinLayerIsNotThere(self):
        stool = getToolByName(self.portal, 'portal_skins')
        for skin, layers in stool._getSelections().items():
            layers = layers.split(',')
            self.failUnless (LAYER_NAME not in layers)
        self.failUnless(LAYER_NAME not in stool.objectIds())


    def testPortletDoNoExist(self):
        base_url = self.portal.absolute_url()
        for name in ('plone.leftcolumn', 'plone.rightcolumn'):
            manager = getUtility(IPortletManager,
                                 name=name,
                                 context=self.portal)
            titles = [p.title for p in manager.getAddablePortletTypes()]
            self.failUnless(PORTLET_NAME not in titles)

        manager = getUtility(IPortletManager,
                             name='plone.rightcolumn',
                             context=self.portal)
        right_portlets = getMultiAdapter((self.portal, manager),
                                         IPortletAssignmentMapping,
                                         context=self.portal)
        right_portlets = right_portlets.keys()
        self.failUnless(PORTLET_NAME not in right_portlets)


    def testConfigletDoNotExist(self):
        cptool = getToolByName(self.portal, 'portal_controlpanel')
        configlets = [c.getId() for c in cptool.listActions()]
        self.failUnless('cmfnotification_configuration' not in configlets)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestUnInstallation))
    return suite
