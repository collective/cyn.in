from Products.Scrawl.tests.base import ScrawlTestCase
from Products.Scrawl.config import BLOG_ENTRY_NAME
from Products.Scrawl import HAS_PLONE30
import string

class TestProductInstallation(ScrawlTestCase):
    """ Ensure that our product installs properly
    """
    def afterSetUp(self):
        self.portal_types = self.portal.portal_types

    def testBlogEntryInstalled(self):
        self.failUnless(BLOG_ENTRY_NAME in self.portal_types.objectIds())

    def testBlogViewAvailable(self):
        self.failUnless('blog_view' in self.portal_types.Topic.view_methods)

    def testBlogEntryViewAvailable(self):
        """If the default view method isn't listed in the available view methods
        Plone 3.0's type settings protests."""
        be = getattr(self.portal_types, BLOG_ENTRY_NAME)
        self.failUnless('blogentry_view' in be.view_methods)

    def testPortalFactorySetup(self):
        self.failUnless('Blog Entry' in self.portal.portal_factory.getFactoryTypes(),
                        '"Blog Entry" is not available in the portal factory.')

    def testSkinsTool(self):
        """Test that file system directory views have
           been registered with the skins tool.
        """
        if HAS_PLONE30:
            goodSkin = 'scrawl_30'
            badSkin  = 'scrawl'
        else:
            goodSkin = 'scrawl'
            badSkin  = 'scrawl_30'
        portal_skins = self.portal.portal_skins
        skins = portal_skins.getSkinSelections()
        for skin in skins:
            path = portal_skins.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))

            self.failUnless(goodSkin in path,
                    "The skin %s was part of the '%s' skin" % (goodSkin, skin))
            self.failIf(badSkin in path,
                    "The skin %s was registered with the '%s' skin but shouldn't have been" % (badSkin, skin))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstallation))
    return suite