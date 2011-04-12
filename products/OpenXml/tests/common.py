#-*- coding: utf-8 -*-
# $Id: common.py 57531 2008-01-23 16:40:27Z glenfant $
"""OpenXml testing package: testing resources"""

from Products.PloneTestCase import PloneTestCase
from Products.OpenXml.config import PROJECTNAME

PloneTestCase.installProduct(PROJECTNAME)
PloneTestCase.setupPloneSite(products=[PROJECTNAME])

