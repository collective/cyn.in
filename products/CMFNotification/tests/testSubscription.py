"""Tests for CMFNotification subscription.

$Id: testSubscription.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.CMFNotification.exceptions import DisabledFeature
from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
from Products.CMFNotification.permissions import SUBSCRIBE_PERMISSION

from Products.CMFNotification.tests.base import CMFNotificationTestCase


class TestSubscription(CMFNotificationTestCase):
    """Make sure that the subscription works."""

    def afterSetUp(self):
        """Called before each tests.

        This method:

        - create users and content;

        - enable extra subscriptions.
        """
        self.createTestUsersAndContent()

        ## Enable extra subscriptions, since this is what we want to
        ## test...
        self.login('manager')
        ntool = getToolByName(self.portal, NTOOL_ID)
        ntool.manage_changeProperties(extra_subscriptions_enabled=True)

        ## Finally, log out.
        self.logout()


    def testDisabledSubscriptions(self):
        """Test if subscription is possible if it is disabled."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        document = portal.folder.document1

        self.login('manager')
        ntool.manage_changeProperties(extra_subscriptions_enabled=False)
        self.assertRaises(DisabledFeature, ntool.subscribeTo, document)

        ntool.manage_changeProperties(extra_subscriptions_enabled=True)
        ntool.subscribeTo(document) ## should not raise DisabledFeature


    def testUnauthorizedSubscriptions(self):
        """Test if subscription is possible if the user has not the
        right permission.
        """
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        document = portal.folder.document1

        self.login('manager')
        portal.manage_permission(SUBSCRIBE_PERMISSION, ('Manager', ))

        self.login('member1')
        self.assertRaises(Unauthorized, ntool.subscribeTo, document)

        portal.manage_permission(SUBSCRIBE_PERMISSION,
                                 ('Manager', 'Member'))
        ntool.subscribeTo(document) ## should not raise DisabledFeature


    def testAuthenticatedUsersSubscription(self):
        """Test subscription of authenticated users."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        document = portal.folder.document1

        ## Nodody is subscribed
        path = ntool._getPath(document)
        self.failUnlessEqual(ntool.getExtraSubscribersOf(path).keys(), [])

        ## Subscribe 'member1'
        self.login('member1')
        ntool.subscribeTo(document)
        self.failUnless(ntool.isSubscribedTo(document))

        ## Subscribe 'manager'
        self.login('manager')
        ntool.subscribeTo(document)
        self.failUnless(ntool.isSubscribedTo(document))

        ## Unsubscribe 'manager'
        ntool.unSubscribeFrom(document)
        self.failUnless(not ntool.isSubscribedTo(document))

        ## 'member1' is still subscribed
        self.login('member1')
        self.failUnless(ntool.isSubscribedTo(document))

        ## Unsubscribe 'member1'
        ntool.unSubscribeFrom(document)
        self.failUnless(not ntool.isSubscribedTo(document))

        ## Nobody is subscribed
        self.failUnlessEqual(ntool.getExtraSubscribersOf(path).keys(), [])


    def testUnSubscriptionFromObjectAbove(self):
        """Test unsubscription from the object above."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        folder = portal.folder
        document = folder.document1

        ## Subscribe to 'folder' and 'document'
        self.login('manager')
        ntool.subscribeTo(folder)
        ntool.subscribeTo(document)

        ## Unsubscribe from object above 'document' (unsubscribe from
        ## 'document' itself, actually)
        ntool.unSubscribeFromObjectAbove(document)
        self.failUnless(not ntool.isSubscribedTo(document,
                                                 as_if_not_recursive=True))
        self.failUnless(ntool.isSubscribedTo(document))
        self.failUnless(ntool.isSubscribedTo(folder))

        ## Unsubscribe from object above 'document' (unsubscribe from
        ## 'folder', actually
        ntool.unSubscribeFromObjectAbove(document)
        self.failUnless(not ntool.isSubscribedTo(document))
        self.failUnless(not ntool.isSubscribedTo(folder))

        ## Test special case where the user is subscribed to the
        ## portal root.
        ntool.subscribeTo(portal)
        self.failUnless(ntool.isSubscribedTo(portal))
        ntool.unSubscribeFromObjectAbove(folder)
        self.failUnless(not ntool.isSubscribedTo(folder))
        self.failUnless(not ntool.isSubscribedTo(portal))


    def testRecursiveSubscription(self):
        """Test recursive subscriptions."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        folder = portal.folder
        document = folder.document1

        ## Disable recursion
        ntool.manage_changeProperties(extra_subscriptions_recursive=False)
        self.login('member1')
        ntool.subscribeTo(folder)
        self.failUnless(not ntool.isSubscribedTo(document))

        ## Enable recursion
        ntool.manage_changeProperties(extra_subscriptions_recursive=True)
        self.failUnless(ntool.isSubscribedTo(document))

        ## Test 'as_if_not_recursive' parameter
        self.failUnless(not ntool.isSubscribedTo(document,
                                                 as_if_not_recursive=True))


    def testAnonymousUsersSubscription(self):
        """Test subscription of anonymous users."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        document = portal.folder.document1

        ## By default, anonymous cannot subscribe to an item
        self.logout()
        self.assertRaises(Unauthorized, ntool.subscribeTo, document)
        self.assertRaises(Unauthorized, ntool.unSubscribeFrom, document)
        self.assertRaises(Unauthorized,
                          ntool.unSubscribeFromObjectAbove, document)

        ## And if we enable anonymous subscription, it raises an
        ## error (because it is not implemented).
        portal.manage_permission(SUBSCRIBE_PERMISSION, ('Anonymous', ))
        self.logout()
        email = 'jdoe@exemple.com'
        self.assertRaises(NotImplementedError,
                          ntool.subscribeTo, document, email)
        self.assertRaises(NotImplementedError,
                          ntool.unSubscribeFrom, document, email)
        self.assertRaises(NotImplementedError,
                          ntool.unSubscribeFromObjectAbove, document, email)


    def testBrowserView(self):
        """Test subscription browser view, which is used through the
        portlet.
        """
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        folder = portal.folder
        document = folder.document1

        ## Subscribe to 'folder' and 'document'
        self.login('manager')
        document.restrictedTraverse('subscribe')()
        self.failUnless(ntool.isSubscribedTo(document))
        folder.restrictedTraverse('subscribe')()
        self.failUnless(ntool.isSubscribedTo(folder))

        ## Unsubscribe from 'document'
        document.restrictedTraverse('unsubscribe')()
        self.failUnless(not ntool.isSubscribedTo(document,
                                                 as_if_not_recursive=True))
        document.restrictedTraverse('unsubscribeFromAbove')()
        self.failUnless(not ntool.isSubscribedTo(folder))
        self.failUnless(not ntool.isSubscribedTo(document))


    def testSubscriptionToUnexpectedObject(self):
        """Test that an user is only allowed to subscribe to the
        portal object Archetypes-based objects.
        """
        ntool = getToolByName(self.portal, NTOOL_ID)
        self.login('manager')
        isAllowed = ntool.currentUserHasSubscribePermissionOn
        self.failUnless(isAllowed(self.portal))
        self.failUnless(isAllowed(self.portal.folder))
        self.failUnless(isAllowed(self.portal.folder.document1))
        self.failUnless(not isAllowed(ntool))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubscription))
    return suite
