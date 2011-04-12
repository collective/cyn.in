import unittest
from zope.testing import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite
import Products.PloneTestCase.layer

from Products.PloneTestCase import PloneTestCase
PloneTestCase.installProduct('Plone4ArtistsSubtyper')
PloneTestCase.setupPloneSite()

def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    fsuite = unittest.TestSuite(())
    try:
        # this is to make sure the tests only run in a plone 2.5 / zope 2.9 environment
        import zope.app.annotation.tests
        fsuite.append(FunctionalDocFileSuite('browser.txt',
                                             package='p4a.subtyper.contentmenu',
                                             optionflags=flags),)
        fsuite.layer = Products.PloneTestCase.layer.PloneSite
    except ImportError, err:
        # this is ok
        pass

    return fsuite
