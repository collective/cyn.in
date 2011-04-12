from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.WebServerAuth.plugin import MultiPlugin
from Products.WebServerAuth.utils import wwwDirectory


manage_addWebServerAuthForm = PageTemplateFile('add.pt', wwwDirectory)

def manage_addWebServerAuth(self, id, title='', REQUEST=None):
    """Add a WebServerAuth plugin to a Pluggable Authentication Service."""
    plugin = MultiPlugin(id, title)
    self._setObject(plugin.getId(), plugin)
    
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_workspace?manage_tabs_message=WebServerAuth+added.' % self.absolute_url())
