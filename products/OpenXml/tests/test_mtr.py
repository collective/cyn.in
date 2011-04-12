#-*- coding: utf-8 -*-
# $Id: test_mtr.py 57531 2008-01-23 16:40:27Z glenfant $
"""Testing mimetypes_registry settings"""
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.interfaces import IMimetype
from Products.PloneTestCase import PloneTestCase
from Products.OpenXml.config import office_mimetypes
import common

class MTRTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):

        portal = self.getPortal()
        self.mtr = getToolByName(portal, 'mimetypes_registry')


    def testInstallation(self):
        """Checking installation of our Mime types"""

        mtr = self.mtr
        for mt_dict in office_mimetypes:
            mt_string = mt_dict['mimetypes'][0]
            mimetype = mtr.lookup(mt_string)
            self.failUnless(
                len(mimetype) > 0,
                "Didn't find MimeType obj for %s" % mt_string)
            if len(mimetype) > 0:
                self.failUnless(
                    IMimetype.isImplementedBy(mtr.lookup(mt_string)[0]),
                    "Didn't find MimeType obj for %s" % mt_string)
        return


    def testExtensions(self):
        """Finding mimetypes by extension"""

        mtr = self.mtr
        for mt_dict in office_mimetypes:
            ext = mt_dict['extensions'][0]
            expected = mt_dict['mimetypes'][0]
            got = mtr.lookupExtension(ext).normalized()
            self.failUnlessEqual(expected, got)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(MTRTestCase))
    return suite

