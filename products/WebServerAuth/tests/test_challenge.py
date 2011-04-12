"""Unit tests for challenge plugin"""

import re
from Products.PloneTestCase import PloneTestCase
from Products.WebServerAuth.plugin import useCustomRedirectionKey, challengePatternKey, challengeReplacementKey
from Products.WebServerAuth.tests.base import MockRequestTestCase

PloneTestCase.installProduct('WebServerAuth')
PloneTestCase.setupPloneSite(products=['WebServerAuth'])


class ChallengeTestCase(MockRequestTestCase):
    def afterSetUp(self):
        MockRequestTestCase.afterSetUp(self)
        self.app.REQUEST.ACTUAL_URL = 'http://example.com/some/place'
    
    def beforeTearDown(self):
        MockRequestTestCase.beforeTearDown(self)


class TestChallenge(ChallengeTestCase):
    def testDefaultPattern(self):
        """Make sure the default regex works."""
        worked = self._plugin().challenge(self.app.REQUEST, self.app.REQUEST.response)
        self.failUnlessEqual(self.app.REQUEST.response.getHeader('Location'), 'https://example.com/some/place')
        self.failUnless(worked, msg="Challenge handler did the redirect but then passed control to the next challenge handler.")


class TestCustomChallenge(ChallengeTestCase):
    """Challenge handler tests with custom regexes on"""
    
    def afterSetUp(self):
        ChallengeTestCase.afterSetUp(self)
        self._plugin().config[useCustomRedirectionKey] = True
    
    def beforeTearDown(self):
        self._plugin().config[useCustomRedirectionKey] = False
        ChallengeTestCase.beforeTearDown(self)
            
    def testCustomPattern(self):
        """Make sure custom regexes work."""
        self._plugin().challenge(self.app.REQUEST, self.app.REQUEST.response)
        self.failUnlessEqual(self.app.REQUEST.response.getHeader('Location'), 'https://secure.example.com/some-site/some/place')
    
    def testBadCustomPattern(self):
        """Make sure bad custom regexes fail gracefully."""
        plugin = self._plugin()
        oldPattern = plugin.config[challengePatternKey]
        plugin.config[challengePatternKey] = re.compile('http://example.com/some-crap-that-doesnt-match')
        try:
            worked = plugin.challenge(self.app.REQUEST, self.app.REQUEST.response)
        finally:
            plugin.config[challengePatternKey] = oldPattern
        self.failIf(worked, msg="A nonmatching custom challenge regex made the challenge handler succeed.")
    
    def testBadCustomReplacement(self):
        """Make sure bad custom replacement patterns fail gracefully."""
        plugin = self._plugin()
        oldPattern = plugin.config[challengeReplacementKey]
        plugin.config[challengeReplacementKey] = r'https://\1\2'
        try:
            worked = plugin.challenge(self.app.REQUEST, self.app.REQUEST.response)
        finally:
            plugin.config[challengeReplacementKey] = oldPattern
        self.failIf(worked, msg="A bad custom replacement pattern made the challenge handler succeed.")    


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestChallenge))
    suite.addTest(makeSuite(TestCustomChallenge))
    return suite
