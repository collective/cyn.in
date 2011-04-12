import unittest
from zope import component
from zope.component import testing
from zope.testing import doctestunit

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('formlib.txt',
                                 package='plone.app.form',
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),
        ))
