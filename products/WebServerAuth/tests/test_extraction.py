"""Unit tests for extraction plugin"""

from Products.PloneTestCase import PloneTestCase
from Products.CMFCore.utils import getToolByName
from Products.WebServerAuth.utils import firstInstanceOfClass
from Products.WebServerAuth.plugin import usernameKey, defaultUsernameHeader, stripDomainNamesKey, usernameHeaderKey
from Products.WebServerAuth.tests.base import WebServerAuthTestCase


PloneTestCase.installProduct('WebServerAuth')
PloneTestCase.setupPloneSite(products=['WebServerAuth'])


_username = 'someUsername'
_domain = 'example.com'
_userAtDomain = '%s@%s' % (_username, _domain)

class _MockRequest(object):
    def __init__(self, environ=None):
        self.environ = environ or {}

class TestExtraction(WebServerAuthTestCase):
    def afterSetUp(self):
        self.plugin = self._plugin()
    
    def testDefaultExtraction(self):
        """Assert default behavior of extraction works."""
        request = _MockRequest()
        self.failUnless(self.plugin.extractCredentials(request) is None, msg="Found credentials to extract, even though we shouldn't have.")
        
        request.environ[defaultUsernameHeader] = _username
        self.failUnlessEqual(self.plugin.extractCredentials(request), {usernameKey: _username})
        
        # Make sure the domain name gets stripped off the end of the username by default:
        request.environ[defaultUsernameHeader] = _userAtDomain
        self.failUnlessEqual(self.plugin.extractCredentials(request), {usernameKey: _username})
    
    def testUsernameHeaderCustomization(self):
        """Assert the name of the header in which the username is passed can be changed."""
        alternateHeader = 'HTTP_REMOTE_USER'
        request = _MockRequest(environ={alternateHeader: _username})
        saveHeader = self.plugin.config[usernameHeaderKey]
        self.plugin.config[usernameHeaderKey] = alternateHeader
        try:
            self.failUnlessEqual(self.plugin.extractCredentials(request), {usernameKey: _username})
        finally:
            self.plugin.config[usernameHeaderKey] = saveHeader
    
    def testDomainStripping(self):
        """Assert choosing to not strip the domain off the end of a whatever@here.com username works."""
        request = _MockRequest(environ={defaultUsernameHeader: _userAtDomain})
        saveStrip = self.plugin.config[stripDomainNamesKey]
        self.plugin.config[stripDomainNamesKey] = False
        try:
            self.failUnlessEqual(self.plugin.extractCredentials(request), {usernameKey: _userAtDomain})
        finally:
            self.plugin.config[stripDomainNamesKey] = saveStrip


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtraction))
    return suite
