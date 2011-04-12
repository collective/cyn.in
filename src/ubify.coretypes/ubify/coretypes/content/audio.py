###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that 
#enables teams to seamlessly work together on files, documents and content in 
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license 
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software 
#Foundation, either version 3 of the License, or any later version and observe 
#the Additional Terms applicable to this program and must display appropriate 
#legal notices. In accordance with Section 7(b) of the GNU General Public 
#License version 3, these Appropriate Legal Notices must retain the display of 
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with 
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
#For any queries regarding the licensing, please send your mails to 
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
from Products.Archetypes.atapi import *

from Products.ATContentTypes.content.file \
     import ATFile as BaseClass
from Products.ATContentTypes.content.file \
     import ATFileSchema as DefaultSchema

from Products.ATContentTypes.content.base import registerATCT

from zope.interface import implements
from ubify.coretypes.config import PROJECTNAME
from ubify.coretypes.interfaces import IAudio
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent

from ubify.policy import CyninMessageFactory as _

schema = DefaultSchema.copy()


class Audio(BaseClass):
    implements(IAudio)

    __doc__ = BaseClass.__doc__ + "(customizable version)"

    portal_type = "Audio"
    archetype_name = BaseClass.archetype_name
    
    assocFileExt   = ('ogg', 'wav', 'mp3')
    if schema['file'] <> None:
        schema['file'].widget.label = _(u'Audio')
        schema['file'].widget.description = _(u'Select a .mp3 or .wav audio file.')
        
    schema = schema
    
    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,filename, REQUEST, RESPONSE):
        is_new = False
        title = self.Title()
        if not title:
            is_new = True
        BaseClass.manage_afterPUT(self, data, marshall_data, file, context, mimetype, filename, REQUEST, RESPONSE)
        if is_new:
            notify(ObjectInitializedEvent(self))
        else:
            notify(ObjectEditedEvent(self))

registerATCT(Audio, PROJECTNAME)

