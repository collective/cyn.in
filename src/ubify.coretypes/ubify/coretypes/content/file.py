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

from ubify.coretypes.config import PROJECTNAME
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent
from ubify.coretypes.content.video import Video
from ubify.coretypes.content.audio import Audio

schema = DefaultSchema.copy()


class ATFile(BaseClass):

    __doc__ = BaseClass.__doc__ + "(customizable version)"

    portal_type = BaseClass.portal_type
    archetype_name = BaseClass.archetype_name
    
    schema = schema

    def is_video_type(self,filename):
        is_video_type = False
        try:
            arrFile = filename.split('.')
            ext = arrFile[-1]
            if ext in Video.assocFileExt:
                is_video_type = True
        except:
            pass
        return is_video_type
    
    def is_audio_type(self,filename):
        is_audio_type = False
        try:
            arrFile = filename.split('.')
            ext = arrFile[-1]
            if ext in Audio.assocFileExt:
                is_audio_type = True
        except:
            pass
        return is_audio_type
    
    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,filename, REQUEST, RESPONSE):
        is_video_type = self.is_video_type(filename)
        is_audio_type = self.is_audio_type(filename)
        if is_video_type:
            self.__class__ = Video
            self._p_changed = 1
            self.portal_type = 'Video'
        elif is_audio_type:
            self.__class__ = Audio
            self._p_changed = 1
            self.portal_type = 'Audio'
        
        is_new = False
        title = self.Title()
        if not title:
            is_new = True
        BaseClass.manage_afterPUT(self, data, marshall_data, file, context, mimetype, filename, REQUEST, RESPONSE)
        if is_new:
            notify(ObjectInitializedEvent(self))
        else:
            notify(ObjectEditedEvent(self))
        
registerATCT(ATFile, PROJECTNAME)

