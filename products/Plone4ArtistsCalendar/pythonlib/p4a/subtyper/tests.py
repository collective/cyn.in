import unittest
from zope.testing import doctest
from zope.component import testing
from Testing.ZopeTestCase import FunctionalDocFileSuite
import Products.PloneTestCase.layer

from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()

def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS

    unitsuite = unittest.TestSuite((
        doctest.DocFileSuite('subtyping.txt',
                             setUp=testing.setUp,
                             tearDown=testing.tearDown,
                             optionflags=flags),
        ))

    fsuite = unittest.TestSuite((
        FunctionalDocFileSuite('browser.txt',
                               package='p4a.subtyper',
                               optionflags=flags,
                               test_class=PloneTestCase.FunctionalTestCase),
        ))
    fsuite.layer = Products.PloneTestCase.layer.PloneSite

    return unittest.TestSuite((unitsuite, fsuite))
