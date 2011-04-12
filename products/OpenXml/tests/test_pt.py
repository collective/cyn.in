#-*- coding: utf-8 -*-
# $Id: test_pt.py 57531 2008-01-23 16:40:27Z glenfant $
"""Testing portal_transforms settings"""
import os
import StringIO
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase
from Products.OpenXml.config import TRANSFORM_NAME
import common

class PTTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):

        portal = self.getPortal()
        self.pt = getToolByName(portal, 'portal_transforms')


    def testInstallation(self):
        """Checking installation of our transform"""

        self.failUnless(TRANSFORM_NAME in self.pt.objectIds(spec='Transform'),
                        "%s transform expected" % TRANSFORM_NAME)
        return


    def testATfileSearchableText(self):
        """Do we index the text of an openxml office file"""

        self.loginAsPortalOwner()
        class fakefile(StringIO.StringIO):
            pass
        this_dir = os.path.dirname(os.path.abspath(__file__))
        test_filename = os.path.join(this_dir, 'wordprocessing1.docx')
        fakefile = fakefile(file(test_filename, 'rb').read())
        fakefile.filename = 'wordprocessing1.docx'
        file_id = self.portal.invokeFactory('File', fakefile.filename, file=fakefile)
        file_item = getattr(self.portal, file_id)
        # We sample some words from the file and its metadata
        words = ("The", "subject", "of", "the", "document", "custom_value_1",
                 "Lenfant", "example", "title")
        st = file_item.SearchableText()
        for word in words:
            self.failUnless(word in st, "Extected %s in indexable text" % word)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PTTestCase))
    return suite

