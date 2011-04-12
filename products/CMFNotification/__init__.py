"""Product initialization.

$Id: __init__.py 67204 2008-06-24 06:09:50Z dbaty $
"""

from Products.PlacelessTranslationService.utility import PTSTranslationDomain

from Products.CMFCore import utils as CMFCoreUtils
from Products.CMFCore import DirectoryView

import Products.CMFNotification.patches
from Products.CMFNotification.config import GLOBALS

## It seems that this is required for 'notification_[un]subscribe.cpy'
## to work. Looks awkward, though...
## See also the utility registration in 'configure.zcml'
cmfnotification_domain = PTSTranslationDomain('cmfnotification')


def initialize(context):
    import NotificationTool

    tools = (NotificationTool.NotificationTool, )
    CMFCoreUtils.ToolInit(NotificationTool.META_TYPE,
                          tools=tools,
                          icon='tool.gif').initialize(context)
