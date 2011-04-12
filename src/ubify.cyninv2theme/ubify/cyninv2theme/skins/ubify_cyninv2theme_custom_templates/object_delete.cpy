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
## Controller Python Script "object_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
if REQUEST.get('REQUEST_METHOD', 'GET').upper() == 'GET':
    raise Unauthorized, 'This method can not be accessed using a GET request'

parent = context.aq_inner.aq_parent
title = safe_unicode(context.title_or_id())

try:
    lock_info = context.restrictedTraverse('@@plone_lock_info')
except AttributeError:
    lock_info = None

if lock_info is not None and lock_info.is_locked():
    message = _(u'${title} is locked and cannot be deleted.',
            mapping={u'title' : title})
    context.plone_utils.addPortalMessage(message, type='error')
    return state.set(status = 'failure')
else:
    authenticator = context.restrictedTraverse('@@authenticator', None)
    if not authenticator.verify():
        raise 'Forbidden'
    from ubify.recyclebin import movetotrash
    movetotrash(context)
    parent.manage_delObjects(context.getId())
    message = _(u'${title} has been deleted.',
                mapping={u'title' : title})
    transaction_note('Deleted %s' % context.absolute_url())
    context.plone_utils.addPortalMessage(message)
    return state.set(status = 'success')
