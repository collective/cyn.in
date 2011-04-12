#
# ActionsTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('ATRatings')
from Products.CMFPlone.tests import PloneTestCase


class TestRatingsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('Archetypes')
        qi.installProduct('ATRatings')

        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea('user1')
        self.createMemberarea('user2')


    def testAddRating(self):
        self.folder.invokeFactory('DDocument', id='foo')
        get_transaction().commit(1)
        foo = self.folder.foo
        rt = self.portal.portal_ratings

        self.assertEqual(rt.getRatingCount(foo.UID()), 0)
        self.assertEqual(rt.getRatingSum(foo.UID()), 0)
        self.assertEqual(rt.getRatingSumSquared(foo.UID()), 0)
        self.assertEqual(rt.getRatingMean(foo.UID()), None)
        self.assertEqual(rt.getRatingStdDev(foo.UID()), None)

        self.login('user1')
        rt.addRating(1, foo.UID())
        self.assertEqual(rt.getUserRating(foo.UID()), 1)
        self.assertEqual(rt.getRatingCount(foo.UID()), 1)
        self.assertEqual(rt.getRatingSum(foo.UID()), 1)
        self.assertEqual(rt.getRatingSumSquared(foo.UID()), 1)
        self.assertAlmostEqual(rt.getRatingMean(foo.UID()), 1.0)
        self.assertAlmostEqual(rt.getRatingStdDev(foo.UID()), 0.0)

        self.assertEqual(rt.getTotalRatingCount(), 1)
        self.assertEqual(rt.getRatingMeanCount(), 1)
        self.assertEqual(rt.getRatingMeanSum(), 1)
        self.assertEqual(rt.getRatingMeanSumSquared(), 1)
        self.assertAlmostEqual(rt.getRatingMeanMean(), 1.0)
        self.assertAlmostEqual(rt.getRatingMeanVariance(), 0.0)
        self.assertAlmostEqual(rt.getRatingMeanStdDev(), 0.0)

        self.login('user1')
        rt.addRating(3, foo.UID())
        self.assertEqual(rt.getUserRating(foo.UID()), 3)
        self.assertEqual(rt.getRatingCount(foo.UID()), 1)
        self.assertEqual(rt.getRatingSum(foo.UID()), 3)
        self.assertEqual(rt.getRatingSumSquared(foo.UID()), 9)
        self.assertAlmostEqual(rt.getRatingMean(foo.UID()), 3.0)
        self.assertAlmostEqual(rt.getRatingStdDev(foo.UID()), 0.0)

        self.login('user2')
        rt.addRating(1, foo.UID())
        self.assertEqual(rt.getUserRating(foo.UID()), 1)
        self.assertEqual(rt.getRatingCount(foo.UID()), 2)
        self.assertEqual(rt.getRatingSum(foo.UID()), 4)
        self.assertEqual(rt.getRatingSumSquared(foo.UID()), 10)
        self.assertAlmostEqual(rt.getRatingMean(foo.UID()), 2.0)
        self.assertAlmostEqual(rt.getRatingStdDev(foo.UID()), 1.0)


    def testAddRating2(self):
        self.folder.invokeFactory('DDocument', id='foo1')
        self.folder.invokeFactory('DDocument', id='foo2')
        get_transaction().commit(1)
        foo1 = self.folder.foo1
        foo2 = self.folder.foo2
        rt = self.portal.portal_ratings

        self.assertEqual(rt.getTotalRatingCount(), 0)
        self.assertEqual(rt.getRatingMeanCount(), 0)
        self.assertEqual(rt.getRatingMeanSum(), 0)
        self.assertEqual(rt.getRatingMeanSumSquared(), 0)
        self.assertEqual(rt.getRatingMeanMean(), None)
        self.assertEqual(rt.getRatingMeanVariance(), None)
        self.assertEqual(rt.getRatingMeanStdDev(), None)

        self.login('user1')
        rt.addRating(1, foo1.UID())
        rt.addRating(3, foo2.UID())
        self.login('user2')
        rt.addRating(3, foo1.UID())
        rt.addRating(1, foo2.UID())

        self.assertEqual(rt.getTotalRatingCount(), 4)
        self.assertEqual(rt.getRatingMeanCount(), 2)
        self.assertAlmostEqual(rt.getRatingMeanSum(), 4.0)
        self.assertAlmostEqual(rt.getRatingMeanSumSquared(), 8.0)
        self.assertEqual(rt.getRatingMeanMean(), 2.0)
        self.assertEqual(rt.getRatingMeanVariance(), 0.0)
        self.assertEqual(rt.getRatingMeanStdDev(), 0.0)


    def testAddRating3(self):
        self.folder.invokeFactory('DDocument', id='foo1')
        self.folder.invokeFactory('DDocument', id='foo2')
        get_transaction().commit(1)
        foo1 = self.folder.foo1
        foo2 = self.folder.foo2
        rt = self.portal.portal_ratings

        self.login('user1')
        rt.addRating(1, foo1.UID())
        rt.addRating(5, foo2.UID())

        self.assertEqual(rt.getTotalRatingCount(), 2)
        self.assertEqual(rt.getRatingMeanCount(), 2)
        self.assertAlmostEqual(rt.getRatingMeanSum(), 6.0)
        self.assertAlmostEqual(rt.getRatingMeanSumSquared(), 26.0)
        self.assertEqual(rt.getRatingMeanMean(), 3.0)
        self.assertEqual(rt.getRatingMeanVariance(), 4.0)
        self.assertEqual(rt.getRatingMeanStdDev(), 2.0)

        print rt.getEstimatedRating(foo1.UID())
        print rt.getEstimatedRating(foo2.UID())

    def testAddHit(self):
        self.folder.invokeFactory('DDocument', id='foo')
        get_transaction().commit(1)
        foo = self.folder.foo
        rt = self.portal.portal_ratings

        self.assertEqual(rt.getHitCount(foo.UID()), 0)
        rt.addHit(foo.UID())
        self.assertEqual(rt.getHitCount(foo.UID()), 1)
        rt.addHit(foo.UID())
        self.assertEqual(rt.getHitCount(foo.UID()), 2)


    def testAddHit2(self):
        self.folder.invokeFactory('DDocument', id='foo1')
        self.folder.invokeFactory('DDocument', id='foo2')
        get_transaction().commit(1)
        foo1 = self.folder.foo1
        foo2 = self.folder.foo2
        rt = self.portal.portal_ratings

        self.login('user1')
        rt.addHit(foo1.UID())
        rt.addHit(foo1.UID())
        rt.addHit(foo2.UID())

        self.assertEqual(rt.getHitCount(foo1.UID()), 2)
        self.assertEqual(rt.getHitCount(foo2.UID()), 1)
        self.assertAlmostEqual(rt.getHitRate(foo1.UID()), 2.0)
        self.assertAlmostEqual(rt.getHitRate(foo2.UID()), 1.0)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRatingsTool))
    return suite

if __name__ == '__main__':
    framework()
