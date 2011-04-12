"""A browser-view for subscriptions features.

$Id: subscription.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import MessageFactory

from kss.core import KSSView
from kss.core import kssaction

from Products.CMFNotification.NotificationTool import ID as TOOL_ID


MF = mf = MessageFactory('cmfnotification')

class Subscription(BrowserView):
    """A browser view for subscription features.

    It is actually only a wrapper around the main methods of the tool.
    """

    def subscribe(self, subscribe_to_parent=False):
        item = self.context.aq_inner
        if subscribe_to_parent:
            item = item.aq_parent
            msg = MF(u'success_subscribed_parent',
                     u'You have been subscribed to the parent folder of this item.')
        else:
            msg = MF(u'success_subscribed',
                     u'You have been subscribed to this item.')

        ntool = getToolByName(item, TOOL_ID)
        ntool.subscribeTo(item)

        utool = getToolByName(item, 'plone_utils')
        utool.addPortalMessage(msg)
        self.request.RESPONSE.redirect(self.context.absolute_url() + '/view')


    def unsubscribe(self):
        item = self.context.aq_inner
        ntool = getToolByName(item, TOOL_ID)
        ntool.unSubscribeFrom(item)

        msg = MF(u'success_unsubscribed',
                 u'You have been unsubscribed from this item.')
        utool = getToolByName(item, 'plone_utils')
        utool.addPortalMessage(msg)
        self.request.RESPONSE.redirect(item.absolute_url() + '/view')


    def unsubscribeFromAbove(self):
        item = self.context.aq_inner
        ntool = getToolByName(item, TOOL_ID)
        ntool.unSubscribeFromObjectAbove(item)
        msg = mf(u'success_unsubscribed_above',
                 u'You have been unsubscribed from the first parent '\
                 u'folder above.')
        utool = getToolByName(item, 'plone_utils')
        utool.addPortalMessage(msg)
        self.request.RESPONSE.redirect(item.absolute_url() + '/view')


class KSSActions(KSSView):
    """A class that holds all KSS actions related to the subscription
    portlet.
    """
    @kssaction
    def subscribe(self, portlet_hash, subscribe_to_parent=False):
        ## We provide a default value for 'subscribe_to_parent'
        ## because KSS will not pass it to the method is the checkbox
        ## is not checked.
        item = self.context.aq_inner
        if subscribe_to_parent:
            item = item.aq_parent
        ntool = getToolByName(item, TOOL_ID)
        ntool.subscribeTo(item)
        self._refreshPortlet(portlet_hash)


    @kssaction
    def unsubscribe(self, portlet_hash):
        item = self.context.aq_inner
        ntool = getToolByName(item, TOOL_ID)
        ntool.unSubscribeFrom(item)
        self._refreshPortlet(portlet_hash)


    @kssaction
    def unsubscribeFromAbove(self, portlet_hash):
        item = self.context.aq_inner
        ntool = getToolByName(item, TOOL_ID)
        ntool.unSubscribeFromObjectAbove(item)
        self._refreshPortlet(portlet_hash)


    def _refreshPortlet(self, portlet_hash):
        commands = self.getCommandSet('plone')
        commands.refreshPortlet(portlet_hash)
