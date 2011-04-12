from Products.Scrawl.tests.base import ScrawlTestCase
from Products.Scrawl.config import BLOG_ENTRY_NAME
import string

class TestProductUninstallation(ScrawlTestCase):
    """ Ensure we leave no trace.
    """
    def afterSetUp(self):
        self.portal_types = self.portal.portal_types
        qi = self.portal.portal_quickinstaller
        if qi.isProductInstalled('Scrawl'):
            qi.uninstallProducts(products=['Scrawl',])
    
    def test_types_restored(self):
        qi = self.portal.portal_quickinstaller
        qi.uninstallProducts(products=['Scrawl',])
        # no more Blog Entry
        self.failIf(BLOG_ENTRY_NAME in self.portal_types.objectIds())

    def test_topic_fti_restored(self):
        # no more blog_view
        qi = self.portal.portal_quickinstaller
        qi.uninstallProducts(products=['Scrawl',])
        self.failIf('blog_view' in self.portal_types.Topic.view_methods)

    def test_portal_factory_restored(self):
        self.failIf('Blog Entry' in self.portal.portal_factory.getFactoryTypes(),
                    '"Blog Entry" still in the portal factory, post uninstall.')

    def test_skins_restored(self):
        # no more skins
        qi = self.portal.portal_quickinstaller
        qi.uninstallProducts(products=['Scrawl',])
        skin_names = ('scrawl', 'scrawl_30',)
        portal_skins = self.portal.portal_skins
        all_skins = portal_skins.getSkinSelections()
        for skin in all_skins:
            path = portal_skins.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))
            for skin_name in skin_names:
                self.failIf(skin_name in path,
                    "The skin %s was part of the '%s' skin after uninstall" % (skin_name, skin))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductUninstallation))
    return suite