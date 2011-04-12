import os.path
from Globals import package_home
import Products.CMFCore

from Products.CMFCore import permissions as CMFCorePermissions 
from Products.CMFCore.DirectoryView import registerDirectory
from config import *

import indexableattributes

registerDirectory(SKINS_DIR, GLOBALS)

def getVersion():
    src_path = package_home(GLOBALS)
    f =  file(os.path.join(src_path, 'version.txt'))
    return f.read()


VERSION = getVersion()

def initialize(context):
    ##Import Types here to register them
    import RatingsTool

    Products.CMFCore.utils.ToolInit('Ratings Tool', tools=( RatingsTool.RatingsTool, ),
                   icon='tool.gif',
                   ).initialize(context)
#                   icon='../CMFPlone/skins/plone_images/favorite_icon.gif'
