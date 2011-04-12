"""Miscellaneous tests for CMFNotification.

$Id: testMisc.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from AccessControl import Unauthorized
from zope.component import getUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer

from Products.CMFNotification.utils import getPreviousVersion
from Products.CMFNotification.utils import getPreviousWorkflowState
from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
from Products.CMFNotification.permissions import SUBSCRIBE_PERMISSION
from Products.CMFNotification.tests.base import CMFNotificationTestCase
from Products.CMFNotification.browser import portlet as CMFNotificationPortlet


class TestMisc(CMFNotificationTestCase):
    """Test various utility methods."""

    def afterSetUp(self):
        """Create dummy content."""
        self.createTestUsersAndContent()


    def testGetPath(self):
        """Test ``NotificationTool._getPath()``."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)

        getPath = ntool._getPath
        for obj, path in (
            (portal, '/'),
            (portal.folder, '/folder/'),
            (portal.folder.document1, '/folder/document1'),
            (portal.folder.subfolder, '/folder/subfolder/'),
            (portal.folder.subfolder.document2, '/folder/subfolder/document2'),
            ):
            self.failUnlessEqual(getPath(obj), path)


    def testGetParents(self):
        """Test ``NotificationTool._getParents()``."""
        ntool = getToolByName(self.portal, NTOOL_ID)

        getParents = ntool._getParents
        for path, parents in (
            ('/', []),
            ('/folder/', ('/', )),
            ('/folder/document1', ('/folder/', '/')),
            ('/folder/subfolder/', ('/folder/', '/')),
            ('/folder/subfolder/document2',
             ('/folder/subfolder/', '/folder/', '/')),
            ):
            self.failUnlessEqual(getParents(path), parents)


    def testIsSubscriptionToParentAllowed(self):
        """Test ``NotificationTool.isSubscriptionToParentAllowed()``.
        """
        portal = self.portal
        wtool = getToolByName(portal, 'portal_workflow')
        ntool = getToolByName(portal, NTOOL_ID)

        def isAllowed(obj):
            plone_view = self.folder.restrictedTraverse('@@plone')
            manager = getUtility(IPortletManager,
                                 name='plone.rightcolumn',
                                 context=obj)
            ## Remove previously cached view.
            if hasattr(obj.REQUEST, '__annotations__'):
                del obj.REQUEST.__annotations__
            renderer = getMultiAdapter((obj, obj.REQUEST,
                                        plone_view, manager,
                                        CMFNotificationPortlet.Assignment()),
                                       IPortletRenderer)
            return renderer.isSubscriptionToParentAllowed

        ntool.manage_changeProperties(extra_subscriptions_enabled=True)
        ntool.manage_changeProperties(extra_subscriptions_recursive=True)
        self.failUnless(not isAllowed(portal.folder))
        self.failUnless(not isAllowed(portal.folder.document1))

        portal.folder.setDefaultPage('document1')

        portal.manage_permission(SUBSCRIBE_PERMISSION, ())
        self.failUnless(not isAllowed(portal.folder.document1))

        portal.manage_permission(SUBSCRIBE_PERMISSION, ('Manager', ))
        self.failUnless(isAllowed(portal.folder.document1))

        ntool.manage_changeProperties(extra_subscriptions_recursive=False)
        self.failUnless(not isAllowed(portal.folder.document1))


    def testGetPreviousVersion(self):
        """Test ``utils._getPreviousVersion()``."""
        ntool = getToolByName(self.portal, 'portal_notification')
        document = self.portal.folder.document1
        ## At this point, the versioning mechanism does not yet hold
        ## any reference to 'document'. Even this first version is not
        ## registered, because we have only called 'invokeFactory()'
        ## to create dummy items...
        previous = getPreviousVersion(document)
        self.failUnlessEqual(previous, None)

        ## ... We have to register it manually to mimic what normally
        ## happens through the web.
        rtool = getToolByName(self.portal, 'portal_repository')
        rtool.save(document, comment='initial version')

        title = document.Title()
        document.setTitle('New title')
        document.update_version_on_edit() ## Mimic TTW edition
        previous = getPreviousVersion(document)
        self.failUnlessEqual(document.Title(), 'New title')
        self.failUnlessEqual(previous.Title(), title)


    def testGetPreviousWorkflowState(self):
        """Test ``utils.getPreviousWorkflowState()``."""
        wtool = getToolByName(self.portal, 'portal_workflow')
        document = self.portal.folder.document1
        self.failUnlessEqual(getPreviousWorkflowState(document), None)
        state = wtool.getInfoFor(document, 'review_state')
        wtool.doActionFor(document, 'publish')
        self.failUnlessEqual(getPreviousWorkflowState(document), state)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMisc))
    return suite
