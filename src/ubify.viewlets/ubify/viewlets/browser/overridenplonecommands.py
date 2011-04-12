from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.i18n import translate
from zope.i18nmessageid.message import Message as i18nmessage

from Products.statusmessages.message import Message

from plone.portlets.interfaces import IPortletManager, IPortletRenderer
from plone.portlets.utils import unhashPortletInfo

from plone.app.portlets.interfaces import IDeferredPortletRenderer
from plone.app.portlets.utils import assignment_from_key

from kss.core import CommandSet
from plone.app.kss.commands.interfaces import IPloneCommands
from plone.app.kss.commands.plonecommands import PloneCommands

class CyninPloneCommands(PloneCommands):
    implements(IPloneCommands)
    
    def issuePortalMessage(self, message, msgtype='info'):
        if message is None:
            message = ''

        if isinstance(message, Message):
            msgtype = message.type
            # The translation domain of the message is not known.  We
            # can only assume that it is 'plone'.
            message = translate(message.message, domain='plone',
                                context=self.request)
        elif isinstance(message, i18nmessage):
            # Here the message has a domain itself, which is good.
            message = translate(message, context=self.request)

        # The 'dt' of the definition list we generate should contain
        # something like Info, Warning or Error.  Those messages are
        # available in the plone domain.
        msgtype_name = translate(msgtype.capitalize(), domain='plone',
                                 context=self.request)

        # XXX The macro has to take in account that there might be more than
        # one status message.
        ksscore = self.getCommandSet('core')

        # We hide the standard Plone Portal Message
        standard_portal_message_selector = ksscore.getCssSelector('.portalMessage')
        ksscore.setStyle(standard_portal_message_selector, 'display','none')

        # Now there is always a portal message but it has to be
        # rendered visible or invisible, accordingly
        
        selector = ksscore.getHtmlIdSelector('kssportalmessagetype')
        ksscore.replaceInnerHTML(selector, msgtype_name)
        selector = ksscore.getHtmlIdSelector('kssportalmessagedetail')
        ksscore.replaceInnerHTML(selector, message)
        selector = ksscore.getHtmlIdSelector('kssPortalMessage')
        ksscore.setAttribute(selector, 'class', "portalMessage %s" % msgtype)
        ksscore.setStyle(selector, 'display', message and 'block' or 'none')
