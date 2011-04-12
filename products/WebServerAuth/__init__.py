from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService import registerMultiPlugin
from Products.WebServerAuth.plugin import MultiPlugin
from Products.WebServerAuth.utils import wwwDirectory
from Products.WebServerAuth.zmi import manage_addWebServerAuthForm, manage_addWebServerAuth

try:
    registerMultiPlugin(MultiPlugin.meta_type)
except RuntimeError:
    # Don't explode upon re-registering the plugin:
    pass


def initialize(context):
    context.registerClass(MultiPlugin,
                          permission=add_user_folders,
                          constructors=(manage_addWebServerAuthForm,
                                        manage_addWebServerAuth),
                          visibility=None,
                          icon='%s/multiplugin.gif' % wwwDirectory
                         )
