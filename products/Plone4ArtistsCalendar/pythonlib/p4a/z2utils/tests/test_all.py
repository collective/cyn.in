import unittest
from zope.testing import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('pkgloader.txt',
                             package='p4a.z2utils'),
        doctest.DocTestSuite('p4a.z2utils.pkgloader',
                             optionflags=doctest.ELLIPSIS),
        doctest.DocTestSuite('p4a.z2utils.utils',
                             optionflags=doctest.ELLIPSIS),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
