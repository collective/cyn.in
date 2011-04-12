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
## Controller Python Script "send_feedback_site"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send feedback to portal administrator
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

##
## This may change depending on the called (portal_feedback or author)
state_success = "success"
state_failure = "failure"

plone_utils = getToolByName(context, 'plone_utils')
urltool = getToolByName(context, 'portal_url')
portal = urltool.getPortalObject()
url = urltool()

## make these arguments?
subject = REQUEST.get('subject', '')
message = REQUEST.get('message', '')
sender_from_address = REQUEST.get('sender_from_address', '')
sender_fullname = REQUEST.get('sender_fullname', '')

send_to_address = portal.getProperty('email_from_address')
envelope_from = portal.getProperty('email_from_address')

state.set(status=state_success) ## until proven otherwise

host = context.MailHost # plone_utils.getMailHost() (is private)
encoding = portal.getProperty('email_charset')

variables = {'sender_from_address' : sender_from_address,
             'sender_fullname'     : sender_fullname,             
             'url'                 : url,
             'subject'             : subject,
             'message'             : message
             }

try:
    message = context.site_feedback_template(context, **variables)
    result = host.secureSend(message, send_to_address, envelope_from, subject=subject, subtype='plain', charset=encoding, debug=False, From=sender_from_address)
except ConflictError:
    raise
except: # TODO Too many things could possibly go wrong. So we catch all.
    exception = plone_utils.exceptionString()
    message = _(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    plone_utils.addPortalMessage(message, 'error')
    return state.set(status=state_failure)

## clear request variables so form is cleared as well
REQUEST.set('message', None)
REQUEST.set('subject', None)
REQUEST.set('sender_from_address', None)
REQUEST.set('sender_fullname', None)

plone_utils.addPortalMessage(_(u'Mail sent.'))
return state
