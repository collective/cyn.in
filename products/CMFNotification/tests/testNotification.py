"""Tests CMFNotification event handlers.

$Id: testNotification.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from zope import event
import transaction
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.event import ObjectInitializedEvent

from Products.CMFNotification.exceptions import DisabledFeature
from Products.CMFNotification.NotificationTool import ID as NTOOL_ID
from Products.CMFNotification.permissions import SUBSCRIBE_PERMISSION

from Products.CMFNotification.tests.base import FakeMailHost
from Products.CMFNotification.tests.base import CMFNotificationTestCase

## FIXME: would be nice to check log warnings, too.


class TestNotification(CMFNotificationTestCase):
    """Make sure that the notification works, which would be just
    great, since this is the very purpose of this product.

    The current tests are a bit verbose and very similar. They could
    be generated dynamically, but I think debugging would be much
    harder.

    Note that these tests do not check the contents of the e-mails. It
    only checks the number of e-mails that have been sent.
    """

    def failUnlessSent(self, n):
        """Make the test fail unless 'n' mails have been sent."""
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
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        mh = portal.MailHost
        self.login('manager')

        ## Set correct rules so that 3 mails should be sent.
        changeProperty('item_creation_notification_enabled', True)
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:creation_mail_notification'])

        portal.invokeFactory('Document', 'document')
        ## See 'events/events.txt' for futher details about this
        ## manually fired event.
        event.notify(ObjectInitializedEvent(portal['document']))
        self.failUnlessSent(1)
        portal.manage_delObjects(['document'])
        mh.clearSentList()

        ## Set workflow initial state to 'publish', thus showing the
        ## new item to every users.
        wtool.simple_publication_workflow.initial_state = 'published'
        portal.invokeFactory('Document', 'document')
        event.notify(ObjectInitializedEvent(portal['document']))
        self.failUnlessSent(3)
        portal.manage_delObjects(['document'])
        mh.clearSentList()

        ## Disable notification
        changeProperty('item_creation_notification_enabled', False)
        portal.invokeFactory('Document', 'document')
        event.notify(ObjectInitializedEvent(portal['document']))
        self.failUnlessSent(0)
        portal.manage_delObjects(['document'])
        mh.clearSentList()

        ## Enable notification but set the notified users list to []
        changeProperty('item_creation_notification_enabled', True)
        ntool.manage_changeProperties(on_item_creation_users='* :: python: []')
        portal.invokeFactory('Document', 'document')
        event.notify(ObjectInitializedEvent(portal['document']))
        self.failUnlessSent(0)
        portal.manage_delObjects(['document'])
        mh.clearSentList()

        ## Set the notified users list to "everybody" but ask for a
        ## missing mail template
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:does_not_exist'])
        portal.invokeFactory('Document', 'document')
        event.notify(ObjectInitializedEvent(portal['document']))
        self.failUnlessSent(0)
        portal.manage_delObjects(['document'])
        mh.clearSentList()


    def testOnItemCopiedAndPasted(self):
        """Test notification when an item is copied and then
        pasted.

        This test is actually a copy of ``testOnItemCreation()``,
        since CMFNotification shoudl have the same behaviour in both
        events.
        """
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        mh = portal.MailHost
        self.login('manager')

        def copyAndPaste():
            cb = portal.folder.manage_copyObjects(['document1'])
            portal.manage_pasteObjects(cb)

        ## Set correct rules so that 3 mails should be sent.
        changeProperty('item_creation_notification_enabled', True)
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:creation_mail_notification'])
        copyAndPaste()
        self.failUnlessSent(1)
        portal.manage_delObjects(['document1'])
        mh.clearSentList()

        ## Set workflow initial state to 'publish', thus showing the
        ## new item to every users.
        wtool.simple_publication_workflow.initial_state = 'published'
        copyAndPaste()
        self.failUnlessSent(3)
        portal.manage_delObjects(['document1'])
        mh.clearSentList()

        ## Disable notification
        changeProperty('item_creation_notification_enabled', False)
        copyAndPaste()
        self.failUnlessSent(0)
        portal.manage_delObjects(['document1'])
        mh.clearSentList()

        ## Enable notification but set the notified users list to []
        changeProperty('item_creation_notification_enabled', True)
        ntool.manage_changeProperties(on_item_creation_users='* :: python: []')
        copyAndPaste()
        self.failUnlessSent(0)
        portal.manage_delObjects(['document1'])
        mh.clearSentList()

        ## Set the notified users list to "everybody" but ask for a
        ## missing mail template
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:does_not_exist'])
        copyAndPaste()
        self.failUnlessSent(0)
        portal.manage_delObjects(['document1'])
        mh.clearSentList()


    def testOnItemCutAndPasted(self):
        """Test notification when an item is cut and then pasted."""
        ## Since there is currently no special rule for cut and paste,
        ## we should not send anything.
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        mh = portal.MailHost
        self.login('manager')

        ## Enable some rules just to make sure that none of them
        ## match.
        changeProperty('item_creation_notification_enabled', True)
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:creation_mail_notification'])
        changeProperty('item_modification_notification_enabled', True)
        changeProperty('on_item_modification_users', ['* :: *'])
        changeProperty('on_item_modification_mail_template',
                       ['* :: string:modification_mail_notification'])
        changeProperty('item_wf_transition_notification_enabled', True)
        changeProperty('on_wf_transition_modification_users', ['* :: *'])
        changeProperty('on_wf_transition_modification_mail_template',
                       ['* :: string:workflow_mail_notification'])

        transaction.savepoint() ## We need this to cut/paste objects.
        cb = portal.folder.manage_cutObjects(['document1'])
        portal.manage_pasteObjects(cb)
        self.failUnlessSent(0)


    def testOnItemRenamed(self):
        """Test notification when an item is renamed."""
        ## Since there is currently no special rule for this event, we
        ## should not send anything.
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        mh = portal.MailHost
        self.login('manager')

        ## Enable some rules just to make sure that none of them
        ## match.
        changeProperty('item_creation_notification_enabled', True)
        changeProperty('on_item_creation_users', ['* :: *'])
        changeProperty('on_item_creation_mail_template',
                       ['* :: string:creation_mail_notification'])
        changeProperty('item_modification_notification_enabled', True)
        changeProperty('on_item_modification_users', ['* :: *'])
        changeProperty('on_item_modification_mail_template',
                       ['* :: string:modification_mail_notification'])
        changeProperty('item_wf_transition_notification_enabled', True)
        changeProperty('on_wf_transition_modification_users', ['* :: *'])
        changeProperty('on_wf_transition_modification_mail_template',
                       ['* :: string:workflow_mail_notification'])

        transaction.savepoint() ## We need this to cut/paste objects.
        portal.folder.manage_renameObjects(('document1', ),
                                           ('renamed-document', ))
        self.failUnlessSent(0)


    def testOnItemModification(self):
        """Test notification on item modification."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        document = portal.folder.document1
        document.unmarkCreationFlag()
        mh = portal.MailHost
        self.login('manager')

        ## Set correct rules so that an e-mail should be sent.
        changeProperty('item_modification_notification_enabled', True)
        changeProperty('on_item_modification_users', ['* :: *'])
        changeProperty('on_item_modification_mail_template',
                       ['* :: string:modification_mail_notification'])

        ## Calling the 'edit()' method does not trigger notification.
        document.edit(title='New title')
        self.failUnlessSent(0)
        mh.clearSentList()

        ## Calling a field mutator does not trigger notification.
        document.setTitle('New title')
        self.failUnlessSent(0)
        mh.clearSentList()

        ## However, editing the item through the edit form does
        ## trigger notification.
        document.processForm(data=1, values={'title': 'New title'})
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Publish document so that other users can view it (and thus
        ## receive notification).
        wtool.doActionFor(document, 'publish')
        document.processForm(data=1, values={'title': 'New title'})
        self.failUnlessSent(3)
        mh.clearSentList()

        ## Disable notification
        changeProperty('item_modification_notification_enabled', False)
        document.processForm(data=1, values={'title': 'New title'})
        self.failUnlessSent(0)
        mh.clearSentList()

        ## Enable notification but set the notified users list to []
        changeProperty('item_modification_notification_enabled', True)
        changeProperty('on_item_modification_users',
                       ['* :: python: []'])
        document.processForm(data=1, values={'title': 'New title'})
        self.failUnlessSent(0)
        mh.clearSentList()

        ## Set the notified users list to <everybody> but ask for a
        ## missing mail template
        changeProperty('on_item_modification_users', ['* :: *'])
        changeProperty('on_item_modification_mail_template',
                       ['* :: string:does_not_exist'])
        document.processForm(data=1, values={'title': 'New title'})
        self.failUnlessSent(0)
        mh.clearSentList()


    def testOnWorkflowTransition(self):
        """Test notification on workflow transition."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        document = portal.folder.document1
        mh = portal.MailHost
        self.login('manager')

        ## Set correct rules so that 3 mails should be sent.
        changeProperty('wf_transition_notification_enabled', True)
        changeProperty('on_wf_transition_users',
                       ['* :: *'])
        changeProperty('on_wf_transition_mail_template',
                       ['* :: string:workflow_mail_notification'])
        wtool.doActionFor(document, 'publish')
        self.failUnlessSent(3)
        mh.clearSentList()

        ## Retract 'document' and thus hide it from everybody except
        ## manager
        wtool.doActionFor(document, 'retract')
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Disable notification
        changeProperty('wf_transition_notification_enabled', False)
        wtool.doActionFor(document, 'publish')
        self.failUnlessSent(0)
        wtool.doActionFor(document, 'retract')
        mh.clearSentList()

        ## Enable notification but set the notified users list to []
        changeProperty('wf_transition_notification_enabled', True)
        changeProperty('on_wf_transition_users',
                       ['* :: python: []'])
        wtool.doActionFor(document, 'publish')
        self.failUnlessSent(0)
        wtool.doActionFor(document, 'retract')
        mh.clearSentList()

        ## Set the notified users list to <everybody> but ask for a
        ## missing mail template
        changeProperty('on_wf_transition_users', ['* :: *'])
        changeProperty('on_wf_transition_mail_template',
                       ['* :: string:does_not_exist'])
        wtool.doActionFor(document, 'publish')
        self.failUnlessSent(0)
        wtool.doActionFor(document, 'retract')
        mh.clearSentList()


    def testOnMemberRegistration(self):
        """Test notification on member registration."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        rtool = getToolByName(portal, 'portal_registration')
        mtool = getToolByName(portal, 'portal_membership')
        deleteMember = lambda userid: mtool.deleteMembers([userid, ])
        mh = portal.MailHost
        userid = 'a_new_member'
        self.login('manager')

        ## Set correct rules so that 3 mails should be sent.
        changeProperty('member_registration_notification_enabled', True)
        changeProperty('on_member_registration_users', ['* :: *'])
        changeProperty('on_member_registration_mail_template',
                       ['* :: string:registration_mail_notification'])
        rtool.addMember(userid, 'password', properties=None)
        self.failUnlessSent(3)
        deleteMember(userid)
        mh.clearSentList()

        ## Disable notification
        changeProperty('member_registration_notification_enabled', False)
        rtool.addMember(userid, 'password', properties=None)
        self.failUnlessSent(0)
        deleteMember(userid)
        mh.clearSentList()

        ## Enable notification but set the notified users list to []
        changeProperty('member_registration_notification_enabled', True)
        changeProperty('on_member_registration_users',
                       ['* :: python: []'])
        rtool.addMember(userid, 'password', properties=None)
        self.failUnlessSent(0)
        deleteMember(userid)
        mh.clearSentList()

        ## Set the notified users list to <everybody> but ask for a
        ## missing mail template
        changeProperty('on_member_registration_users', ['* :: *'])
        changeProperty('on_member_registration_mail_template',
                       ['* :: string:does_not_exist'])
        rtool.addMember(userid, 'password', properties=None)
        self.failUnlessSent(0)
        deleteMember(userid)
        mh.clearSentList()


    def testOnMemberModification(self):
        """Test notification on member modification."""
        pass ## FIXME: implement me! (Damien)


    def testOnDiscussionItemCreation(self):
        """Test notification on discussion item creation."""
        return ## FIXME: test deactivated until feature is implemented
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        wtool = getToolByName(portal, 'portal_workflow')
        document = portal.folder.document1
        document.allow_discussion = True
        mh = portal.MailHost
        addDiscussionItem = lambda obj: obj.discussion_reply('Subject',
                                                             'Body text')
        self.login('manager')

        ## Set correct rules so that 1 e-mail should be sent.
        changeProperty('on_discussion_item_creation_notification_enabled',
                       True)
        changeProperty('on_discussion_item_creation_users',
                       ['* :: *'])
        changeProperty('on_discussion_item_creation_mail_template',
                       ['* :: string:discussion_mail_notification'])
        addDiscussionItem(document)
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Publish 'document' so that everybody can view it (and thus
        ## receive a notification)
        wtool.doActionFor(document, 'publish')
        addDiscussionItem(document)
        self.failUnlessSent(3)
        mh.clearSentList()

        ## Reply to a discussion item
        discussion_item = document.talkback.objectValues()[0]
        discussion_item = discussion_item.__of__(document.talkback)
        addDiscussionItem(discussion_item)
        self.failUnlessSent(3)
        mh.clearSentList()

        ## Disable notification
        changeProperty('on_discussion_item_creation_notification_enabled',
                       False)
        addDiscussionItem(document)
        self.failUnlessSent(0)
        mh.clearSentList()

        ## Enable notification but set the notified users list to []
        changeProperty('discussion_item_creation_notification_enabled',
                       True)
        changeProperty('on_discussion_item_creation_users',
                       ['* :: python: []'])
        addDiscussionItem(document)
        self.failUnlessSent(0)
        mh.clearSentList()

        ## Set the notified users list to <everybody> but ask for a
        ## missing mail template
        changeProperty('on_discussion_item_creation_users', ['* :: *'])
        changeProperty('on_discussion_item_creation_mail_template=',
                       ['* :: string:does_not_exist'])
        addDiscussionItem(document)
        self.failUnlessSent(0)
        mh.clearSentList()


    def testHandlersDoNotOverlap(self):
        """Test that handlers do not overlap themselves, i.e. that at
        most one handler is called for any event.
        """
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        wtool = getToolByName(portal, 'portal_workflow')
        rtool = getToolByName(portal, 'portal_registration')
        mtool = getToolByName(portal, 'portal_membership')
        mh = portal.MailHost
        document = portal.folder.document1

        self.login('manager')

        ## Enable everything
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
        ntool.manage_changeProperties(properties)

        ## Test item creation
        portal.invokeFactory('Document', 'document')
        event.notify(ObjectInitializedEvent(portal['document']))
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Test item modification
        document.processForm(data=1, values={'title': 'New title'})
        self.failUnlessSent(1)
        mh.clearSentList()

        ## Test workflow transition
        wtool.doActionFor(document, 'publish')
        self.failUnlessSent(3)
        wtool.doActionFor(document, 'retract')
        mh.clearSentList()

        ## Test member registration
        userid = 'a_new_member'
        rtool.addMember(userid, 'password', properties=None)
        self.failUnlessSent(3)
        mtool.deleteMembers([userid, ])
        mh.clearSentList()

        ## FIXME: Test member modification

        ## Test discussion item creation
        ## FIXME: uncomment when implemented
        #document.allow_discussion = True
        #document.discussion_reply('Subject', 'Body text')
        #self.failUnlessSent(1)
        #mh.clearSentList()


    def testLabels(self):
        """Test template selection with labels."""
        portal = self.portal
        ntool = getToolByName(portal, NTOOL_ID)
        changeProperty = lambda key, value: \
            ntool.manage_changeProperties(**{key: value})
        modifyItem = lambda obj: obj.processForm(data=1,
                                                 values={'title': 'New title'})
        wtool = getToolByName(portal, 'portal_workflow')
        rtool = getToolByName(portal, 'portal_registration')
        mtool = getToolByName(portal, 'portal_membership')
        mh = portal.MailHost
        document = portal.folder.document1

        ## We will only test labels on item modification.
        self.login('manager')
        wtool.doActionFor(document, 'publish')
        changeProperty('item_modification_notification_enabled', True)

        ## A simple configuration with two labels.
        users = ['* :: python: ["manager"] :: one',
                 '* :: python: ["manager", "member1", "member2"] :: two']
        templates = ['python: label == "one" :: string:modification_mail_notification',
                     'python: label == "two" :: string:modification_mail_notification']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(4) # 2 for manager; 1 for member1; 1 for member2
        mh.clearSentList()

        ## A special case, where the first rule match all users, which
        ## disable next rules. I (Damien) am not particularly
        ## convinced that this is really the behaviour than an user
        ## would expect, but I do not have any strong argument against
        ## it, neither. :)
        users = ['* :: * :: one',
                 '* :: python: ["manager", "member1"] :: two']
        templates = ['python: label == "one" :: string:modification_mail_notification',
                     'python: label == "two" :: string:modification_mail_notification']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(3) # 1 for each user
        mh.clearSentList()

        ## A configuration with a non-existent rule.
        users = ['* :: python: ["manager"] :: one',
                 '* :: python: ["manager", "member1"] :: two']
        templates = ['python: label == "one" :: string:modification_mail_notification',
                     'python: label == "non-existente" :: string:modification_mail_notification']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(1) # 1 for manager
        mh.clearSentList()

        ## A configuration with an error in a rule.
        users = ['* :: python: ["manager"] :: one',
                 '* :: python: ["manager", "member1"] :: two']
        templates = ['python: label == "one" :: string:modification_mail_notification',
                     'python: label == "two" :: string:non_existent']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(1) # 1 for manager
        mh.clearSentList()

        ## A configuration with a label that is used twice.
        users = ['* :: python: ["manager"] :: one',
                 '* :: python: ["manager", "member1"] :: one']
        templates = ['python: label == "one" :: string:modification_mail_notification',
                     'python: label == "two" :: string:modification_mail_notification']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(2) # 1 for manager; 1 for member1
        mh.clearSentList()

        ## Test that manually subscribed users are available under the
        ## empty label.
        changeProperty('extra_subscriptions_enabled', True)
        ntool._subscriptions[ntool._getPath(document)] = {'member1': 1}
        users = []
        templates = ['python: label == "one" :: string:modification_mail_notification']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(0)
        mh.clearSentList()
        templates = ['python: label == "one" :: string:modification_mail_notification',
                     'python: label == "" :: string:modification_mail_notification']
        changeProperty('on_item_modification_users', users)
        changeProperty('on_item_modification_mail_template', templates)
        modifyItem(document)
        self.failUnlessSent(1)
        mh.clearSentList()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNotification))
    return suite
