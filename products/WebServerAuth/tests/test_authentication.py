"""Unit tests for authentication plugin"""

from Products.PloneTestCase import PloneTestCase
from Products.CMFCore.utils import getToolByName
from Products.WebServerAuth.utils import firstInstanceOfClass
from Products.WebServerAuth.plugin import usernameKey
from Products.WebServerAuth.tests.base import WebServerAuthTestCase


PloneTestCase.installProduct('WebServerAuth')
PloneTestCase.setupPloneSite(products=['WebServerAuth'])

testLogin = 'guido'
testUserId = 'someCrazyUserIdForGuido'

class TestAuthentication(WebServerAuthTestCase):
    def afterSetUp(self):
        self._source_users().addUser(testUserId, testLogin, 'password')
    
    def beforeTearDown(self):
        self._source_users().removeUser(testUserId)
    
    def _source_users(self):
        """Return the default ZODBUserManager within the acl_users folder."""
        return self._acl_users()['source_users']
    
    def testFindUserByLogin(self):
        """Make sure our authentication plugin finds any existing user with the given login name, in case login names and user IDs aren't equal."""
        self.failUnlessEqual(self._plugin().authenticateCredentials({usernameKey: testLogin}), (testUserId, testLogin))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAuthentication))
    return suite
