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
## Script (Python) "prefs_user_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, portrait='',delete_portrait=''
##title=Edit user
##

from Products.CMFPlone import PloneMessageFactory as _
from ubify.viewlets.utils import scaleandcrop_image
from OFS.Image import Image
from ubify.cyninv2theme import SetPortrait

#update portrait
REQUEST=context.REQUEST
portal_membership = context.portal_membership
member=portal_membership.getMemberById(userid)
if portrait:
    portrait.seek(0)
    scaled, mimetype = scaleandcrop_image(portrait,(40,40))
    portrait = Image(id=userid, file=scaled, title='')
    membertool = context.portal_memberdata
    SetPortrait(membertool,portrait,userid)

if delete_portrait:
    context.portal_membership.deletePersonalPortrait(member.getId())

processed={}
for id, property in context.portal_memberdata.propertyItems():
    if id == 'last_login_time':
        continue
    if REQUEST.has_key(id):
        processed[id] = REQUEST.get(id)

if not processed.get('ext_editor'):
    processed['ext_editor'] = ''

if not processed.get('listed'):
    processed['listed'] = ''

if not processed.get('visible_ids'):
    processed['visible_ids'] = 0

context.plone_utils.setMemberProperties(member, REQUEST=REQUEST, **processed)

context.plone_utils.addPortalMessage(_(u'Changes made.'))
return state
