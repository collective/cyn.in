###############################################################################
##cyn.in is an open source Collaborative Knowledge Management Appliance that 
##enables teams to seamlessly work together on files, documents and content in 
##a secure central environment.
##
##cyn.in v2 an open source appliance is distributed under the GPL v3 license 
##along with commercial support options.
##
##cyn.in is a Cynapse Invention.
##
##Copyright (C) 2008 Cynapse India Pvt. Ltd.
##
##This program is free software: you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software 
##Foundation, either version 3 of the License, or any later version and observe 
##the Additional Terms applicable to this program and must display appropriate 
##legal notices. In accordance with Section 7(b) of the GNU General Public 
##License version 3, these Appropriate Legal Notices must retain the display of 
##the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
##received a copy of the detailed Additional Terms License with this program.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of 
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
##Public License for more details.
##
##You should have received a copy of the GNU General Public License along with 
##this program.  If not, see <http://www.gnu.org/licenses/>.
##
##You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
##For any queries regarding the licensing, please send your mails to 
## legal@cynapse.com
##
##You can also contact Cynapse at:
##802, Building No. 1,
##Dheeraj Sagar, Malad(W)
##Mumbai-400064, India
###############################################################################
## Script (Python) "discussion_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subject,body_text,text_format='plain',username=None,password=None
##title=Reply to content

from Products.PythonScripts.standard import url_quote_plus
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
mtool = getToolByName(context, 'portal_membership')
dtool = getToolByName(context, 'portal_discussion')
req = context.REQUEST

if username or password:
    # The user username/password inputs on on the comment form were used,
    # which might happen when anonymous commenting is enabled. If they typed
    # something in to either of the inputs, we send them to 'logged_in'.
    # 'logged_in' will redirect them back to this script if authentication
    # succeeds with a query string which will post the message appropriately
    # and show them the result.  if 'logged_in' fails, the user will be
    # presented with the stock login failure page.  This all depends
    # heavily on cookiecrumbler, but I believe that is a Plone requirement.
    came_from = '%s?subject=%s&amp;body_text=%s' % (req['URL'], subject, body_text)
    came_from = url_quote_plus(came_from)
    portal_url = context.portal_url()

    return req.RESPONSE.redirect(
        '%s/logged_in?__ac_name=%s'
        '&amp;__ac_password=%s'
        '&amp;came_from=%s' % (portal_url,
                               url_quote_plus(username),
                               url_quote_plus(password),
                               came_from,
                               )
        )

# if (the user is already logged in) or (if anonymous commenting is enabled and
# they posted without typing a username or password into the form), we do
# the following

creator = mtool.getAuthenticatedMember().getId()
tb = dtool.getDiscussionFor(context)
id = tb.createReply(title=subject, text=body_text, Creator=creator)
reply = tb.getReply(id)
if reply <> None:
    from ubify.cyninv2theme import triggerAddOnDiscussionItem
    triggerAddOnDiscussionItem(reply)

# TODO THIS NEEDS TO GO AWAY!
if hasattr(dtool.aq_explicit, 'cookReply'):
    dtool.cookReply(reply, text_format='plain')

parent = tb.aq_parent

# return to the discussable object.
redirect_target = context.plone_utils.getDiscussionThread(tb)[0]
view = redirect_target.getTypeInfo().getActionInfo('object/view',
                                                   redirect_target)['url']
anchor = reply.getId()

from Products.CMFPlone.utils import transaction_note
transaction_note('Added comment to %s at %s' % (parent.title_or_id(),
                                                reply.absolute_url()))

context.plone_utils.addPortalMessage(_(u'Comment added.'))
target = '%s#%s' % (view, anchor)
return req.RESPONSE.redirect(target)
