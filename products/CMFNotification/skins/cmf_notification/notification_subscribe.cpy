## Controller Python Script "notification_subscribe"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subscribe_to_parent=False
##title=Subscribe the user to an item

from Products.CMFCore.utils import getToolByName
try:
    from Products.CMFPlone import MessageFactory
    USE_MESSAGE_FACTORY = True
except ImportError:
    ## FIXME: backward compatibility code should be removed
    USE_MESSAGE_FACTORY = False

if USE_MESSAGE_FACTORY:
    mf = MessageFactory('cmfnotification')
else:
    mf = lambda msgid, default: context.translate(msgid, default=default,
                                                  domain='cmfnotification')

item = context
if subscribe_to_parent:
    item = context.aq_parent
    msg = mf('success_subscribed_parent',
             'You have been subscribed to the parent folder of this item.')
else:
    msg = mf('success_subscribed',
             'You have been subscribed to this item.')

ntool = getToolByName(context, 'portal_notification')
ntool.subscribeTo(item)

kwargs = {}
if USE_MESSAGE_FACTORY:
    context.plone_utils.addPortalMessage(msg)
else:
    kwargs = {'portal_status_message': msg}

return state.set(**kwargs)
