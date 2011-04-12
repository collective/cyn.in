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
## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=visible_ids=None, portrait=None, listed=None, REQUEST=None, ext_editor=None
##title=Personalization Handler.

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from ubify.viewlets.utils import scaleandcrop_image
from OFS.Image import Image
from ubify.cyninv2theme import SetPortrait

member=context.portal_membership.getAuthenticatedMember()
member.setProperties(properties=context.REQUEST, REQUEST=REQUEST)
member_context=context.portal_membership.getHomeFolder(member.getId())
context.portal_skins.updateSkinCookie()

if member_context is None:
    member_context=context.portal_url.getPortalObject()

if visible_ids is None and REQUEST is not None:
    visible_ids=0
else:
    visible_ids=1
REQUEST.set('visible_ids', visible_ids)

if listed is None and REQUEST is not None:
    listed=0
else:
    listed=1
REQUEST.set('listed', listed)

if ext_editor is None and REQUEST is not None:
    ext_editor=0
else:
    ext_editor=1
REQUEST.set('ext_editor', ext_editor)

if (portrait and portrait.filename):
    member_id = member.getId()
    if portrait and portrait.filename:
        scaled, mimetype = scaleandcrop_image(portrait,(40,40))
        portrait = Image(id=member_id, file=scaled, title='')
        membertool = context.portal_memberdata
        SetPortrait(membertool,portrait,member_id)

delete_portrait = context.REQUEST.get('delete_portrait', None)
if delete_portrait:
    context.portal_membership.deletePersonalPortrait(member.getId())


member.setProperties(listed=listed, ext_editor=ext_editor, visible_ids=visible_ids)

tmsg='Edited personal settings for %s' % member.getId()
transaction_note(tmsg)

context.plone_utils.addPortalMessage(_(u'Your personal settings have been saved.'))
return state
