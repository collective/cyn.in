## Controller Python Script "notification_unsubscribe_above"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Unsubscribe the user from the item and from everything above

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

ntool = getToolByName(context, 'portal_notification')
ntool.unSubscribeFromObjectAbove(context)

msg = mf('success_unsubscribed_above',
         'You have been unsubscribed from the first parent folder above.')

kwargs = {}
if USE_MESSAGE_FACTORY:
    context.plone_utils.addPortalMessage(msg)
else:
    kwargs = {'portal_status_message': msg}

return state.set(**kwargs)
