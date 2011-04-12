"""Browser tests for CMFNotification event handlers.

$Id: testNotificationViaBrowser.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.CMFNotification.utils import getPreviousVersion
from Products.CMFNotification.exceptions import DisabledFeature
from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
from Products.CMFNotification.permissions import SUBSCRIBE_PERMISSION

from Products.CMFNotification.tests.base import FakeMailHost
from Products.CMFNotification.tests.base import CMFNotificationBrowserTestCase
from Products.CMFNotification.tests.plonetestbrowser import Browser


class TestNotificationViaBrowser(CMFNotificationBrowserTestCase):
    """Make sure that the notification works when we use a browser.

    While ``testNotification.TestNotification`` tests programmatic
    creation, edition, etc. of contents, this test case uses
    ``zope.testbrowser`` to mimic what an user does with his/her
    browser.

    Note that these tests do not check the contents of the e-mails. It
    only check the number of e-mails that have been sent.
    """

    def failUnlessSent(self, n):
        """Make the test fail unless ``n`` mails have been sent."""
        mh = self.portal.MailHost
        self.failUnless(len(mh.getSentList()) == n,
                        "Expected %s mail(s), but "\
                        "sent %s" % (n, len(mh.getSentList())))


    def afterSetUp(self):
        """Called before each tests.

        This method:

        - replaces the mailhost by a fake one which does not send
        mails but keeps them in a list;

        - create dummy users and content.
        """
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        ntool.manage_changeProperties(item_creation_notification_enabled=False)
        self.createTestUsersAndContent()
        ntool.manage_changeProperties(item_creation_notification_enabled=True)

        ## Set up a fake mail host
        if 'MailHost' in portal.objectIds():
            portal._delObject('MailHost')
        portal._setObject('MailHost', FakeMailHost())


    def testOnItemCreation(self):
        """Test notification on item creation."""
        portal = self.portal
        mh = portal.MailHost

        ## Set correct rules so that 3 mails should be sent.
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        self.login('manager')
        changeProperty('item_creation_notification_enabled', True)
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:creation_mail_notification'])

        ## Create a document with the browser
        browser = Browser(self.portal.absolute_url() + '/login_form')
        browser.loginAsManager()
        browser.createItem(portal, 'Document', title='My document')
        self.failUnlessSent(1)
        portal.manage_delObjects(['my-document'])
        mh.clearSentList()


    ## FIXME: test "copy and paste", "cut and paste".


    def testOnItemModification(self):
        """Test notification on item modification."""
        portal = self.portal
        mh = portal.MailHost

        ## Set correct rules so that an e-mail should be sent.
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        self.login('manager')
        changeProperty('item_modification_notification_enabled', True)
        changeProperty('on_item_modification_users', ['* :: *'])
        changeProperty('on_item_modification_mail_template',
                       ['* :: string:modification_mail_notification'])

        ## Edit a document with the browser
        browser = Browser(self.portal.absolute_url() + '/login_form')
        browser.loginAsManager()
        document = portal.folder.document1
        old_title = document.Title()
        document.unmarkCreationFlag()
        browser.editItem(document, title='New title')
        self.failUnlessSent(1)
        mh.clearSentList()


    def testOnWorkflowTransition(self):
        """Test notification on workflow transition."""
        portal = self.portal
        mh = portal.MailHost

        ## Set correct rules so that 3 mails should be sent.
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        self.login('manager')
        changeProperty('wf_transition_notification_enabled', True)
        changeProperty('on_wf_transition_users',
                       ['* :: *'])
        changeProperty('on_wf_transition_mail_template',
                       ['* :: string:workflow_mail_notification'])

        ## Publish item with the browser
        browser = Browser(self.portal.absolute_url() + '/login_form')
        browser.loginAsManager()
        document = portal.folder.document1
        browser.doWorkflowTransitionOn('publish', document)
        self.failUnlessSent(3)
        mh.clearSentList()


    def testOnMemberRegistration(self):
        """Test notification on member registration."""
        portal = self.portal
        mh = portal.MailHost

        ## Set correct rules so that 3 mails should be sent.
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        self.login('manager')
        changeProperty('member_registration_notification_enabled', True)
        changeProperty('on_member_registration_users', ['* :: *'])
        changeProperty('on_member_registration_mail_template',
                       ['* :: string:registration_mail_notification'])

        ## Register new member with the browser
        ## FIXME
        userid = 'a_new_member'
        #self.failUnlessSent(3)
        #mtool = getToolByName(portal, 'portal_membership')
        #mtool.deleteMembers([userid, ])
        mh.clearSentList()


    def testOnMemberModification(self):
        """Test notification on member modification."""
        pass ## FIXME: implement me! (Damien)


    def testOnDiscussionItemCreation(self):
        """Test notification on discussion item creation."""
        portal = self.portal
        mh = portal.MailHost

        ## Set correct rules so that 1 e-mail should be sent.
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        self.login('manager')
        changeProperty('on_discussion_item_creation_notification_enabled',
                       True)
        changeProperty('on_discussion_item_creation_users',
                       ['* :: *'])
        changeProperty('on_discussion_item_creation_mail_template',
                       ['* :: string:discussion_mail_notification'])

        ## Add discussion item with the browser.
        document = portal.folder.document1
        document.allow_discussion = True
        ## FIXME
        #self.failUnlessSent(1)
        #mh.clearSentList()


    def testHandlersDoNotOverlap(self):
        """Test that handlers do not overlap themselves, i.e. that at
        most one handler is called for any event.
        """
        portal = self.portal
        mh = portal.MailHost

        ## Enable everything
        self.login('manager')
        users = ['* :: *']
        member_template = ['* :: string:member_notification']
        discussion_template = ['* :: string:discussion_notification']
        properties = {
           'item_creation_notification_enabled': True,
           'on_item_creation_users': users,
           'on_item_creation_mail_template': ['* :: string:creation_mail_notification'],
           'item_modification_notification_enabled': True,
           'on_item_modification_users': users,
           'on_item_modification_mail_template': ['* :: string:modification_mail_notification'],
           'wf_transition_notification_enabled': True,
           'on_wf_transition_users': users,
           'on_wf_transition_mail_template': ['* :: string:workflow_mail_notification'],
           'member_registration_notification_enabled': True,
           'on_member_registration_users': users,
           'on_member_registration_mail_template':['* :: string:registration_mail_notification'],
           'discussion_item_creation_notification_enabled': True,
           'on_discussion_item_creation_users': users,
           'on_discussion_item_creation_mail_template': ['* :: string:discussion_mail_notification'],
           }
        ntool = getToolByName(portal, NTOOL_ID)
        ntool.manage_changeProperties(properties)

        ## Initialize browser and log in
        browser = Browser(self.portal.absolute_url() + '/login_form')
        browser.loginAsManager()

        ## Create item
        browser.createItem(portal, 'Document', title='My document')
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Modify it
        document = portal['my-document']
        browser.editItem(document, title='New title')
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Publish it
        browser.doWorkflowTransitionOn('publish', document)
        self.failUnlessSent(3)
        mh.clearSentList()

        ## Test member registration
        userid = 'a_new_member'
        ## FIXME: register new member
        #self.failUnlessSent(3)
        mh.clearSentList()

        ## FIXME: Test member modification

        ## Test discussion item creation
        document.allow_discussion = True
        ## FIXME: add discussion item
        #self.failUnlessSent(1)
        mh.clearSentList()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNotificationViaBrowser))
    return suite
