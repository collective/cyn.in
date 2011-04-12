#-*- coding: utf-8 -*-
# $Id: install.py 57531 2008-01-23 16:40:27Z glenfant $
"""OpenXml installation"""

from Products.OpenXml.setuphandlers import removeOpenXml

def uninstall(self):
    # Note that there is no GenericSetup support for uninstalling today.

    removeOpenXml(self)
    return
