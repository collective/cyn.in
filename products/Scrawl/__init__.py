from Products.CMFCore.DirectoryView import registerDirectory
from Products.Scrawl.config import GLOBALS

registerDirectory('skins', GLOBALS)

# Parts of the installation process depend on the version of Plone.
# This release supports Plone 2.5 and Plone 3.0
try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True

def initialize(context):
    pass