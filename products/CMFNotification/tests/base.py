"""Define a base class and prepare ZopeTestCase and PloneTestCase to
be used in CMFNotification tests.

Vaguely based on RichDocument tests.

$Id: base.py 55349 2007-12-12 09:38:43Z dbaty $
"""

## Import the base test case classes
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

from Products.Five.testbrowser import Browser

## Make ZopeTestCase aware of CMFNotification
ZopeTestCase.installProduct('CMFNotification')

## Set up a Plone site
PRODUCTS = ('CMFNotification', )
PloneTestCase.setupPloneSite(products=PRODUCTS)
PloneTestCase.installProduct('Five')


## Import statements for our own code
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFNotification import NotificationTool


## Monkey-patch logger so that we can test log messages (and not
## display them when tests are run).
from Products.CMFNotification.tests import fakelogger
fakelogger.patchLogging()
import logging
from Products.CMFNotification import NotificationTool
NotificationTool.LOG = logging.getLogger()


## A fake mail host which does not send emails but keep them in a
## list.
NotificationTool.MAIL_HOST_META_TYPES = ('FakeMailHost', )

class FakeMailHost(SimpleItem):
    meta_type = 'FakeMailHost'

    def __init__(self, *args, **kwargs):
        SimpleItem.__init__(self, *args, **kwargs)
        self.sent = []

    def send(self, message):
        self.sent.append(message)

    def getSentList(self):
        return self.sent

    def clearSentList(self):
        self.sent = []


class CMFNotificationBaseTestCase:
    """Base mixin for CMFNotification tests."""

    def createTestUsersAndContent(self):
        """Create some test users and content

        Three users are created:
        - a manager: 'manager'
        - two members: 'member1' and 'member2'

        The following items are created:
        + folder
        |--+-- document1
        |--+-- subfolder
        |-----+-- document2
        """
        ## Create users
        mtool = getToolByName(self.portal, 'portal_membership')
        users = ({'id': 'member1', 'roles': ('Member', )},
                 {'id': 'member2', 'roles': ('Member', )},
                 {'id': 'manager', 'roles': ('Manager', 'Member')})
        for user in users:
            email = user['id'] + '@example.com'
            mtool.addMember(user['id'], user['id'], user['roles'], [],
                            properties={'email': email})

        ## Create content
        self.login('manager')
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal.folder
        folder.unmarkCreationFlag()
        folder.invokeFactory('Document', 'document1')
        folder.document1.unmarkCreationFlag()
        folder.invokeFactory('Folder', 'subfolder')
        subfolder = folder.subfolder
        subfolder.unmarkCreationFlag()
        subfolder.invokeFactory('Document', 'document2')
        subfolder.document2.unmarkCreationFlag()


class CMFNotificationTestCase(CMFNotificationBaseTestCase,
                              PloneTestCase.PloneTestCase):
    pass ## Nothing special to do


class CMFNotificationBrowserTestCase(CMFNotificationBaseTestCase,
                                     PloneTestCase.FunctionalTestCase):
    """A special base class for browser tests."""
    pass ## Nothing special to do.
