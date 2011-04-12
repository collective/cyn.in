from zope import interface
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from plone.app.contentmenu.interfaces import IActionsSubMenuItem

class SubtypesSubMenuItem(BrowserSubMenuItem):
    interface.implements(IActionsSubMenuItem)

    title = u'Sub-types'
    description = u''
    submenuId = u'subtypes'
    order = 9
    extra = {'id': 'subtypes'}

    @property
    def action(self):
        return self.context.absolute_url()+ '/subtypes'

    def available(self):
        return True
