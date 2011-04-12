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
from ubify.policy import CyninMessageFactory as _
PROJECTNAME = 'ubify.coretypes'

GLOBALS = globals()
SKINS_DIR = 'skins'

TYPES_TO_MIGRATE = (
    'LinkBase',
    )

TYPES_NEW = (
    'Gallery',
    'Blog',
    'Wiki',
    'LinkDirectory',
    'SpacesFolder',
    'FileRepository',
    'GenericContainer',
    'Calendar',
    'LinkBase',
    'SmartviewFolder',
    'StatuslogFolder',
    'StatuslogItem',
    'ContentRoot',
    'ContentSpace',
    'MemberSpace',
    'Video',
    'Discussion',
    'Audio'
    )

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

cynin_applications = (
    'Gallery',
    'Blog',
    'Wiki',
    'LinkDirectory',
    'FileRepository',
    'GenericContainer',
    'Calendar',
    'Space',
    'SpacesFolder',
    'SmartviewFolder',
    'Large Plone Folder',
    'StatuslogFolder',
    'StatuslogItem',
)

cynin_applications_type_ignore = (
    'Large Plone Folder',
    'SpacesFolder',
    'SmartviewFolder',
    'Space'
)

applications = [
    {
    'title':_(u'generic_views',u'Generic Views'),
    'url':'-',
    'icon':'',
    'selected':False,
    'visible':True,
    'id':'genericseparator',
    },
    {
    'title':_(u'dashboard',u'Dashboard'),
    'url':'',
    'icon':'icon-application_view_tile.png',
    'selected':False,
    'visible':True,
    'id':'dashboard',
    },
    {
    'title':_(u'activity_stream',u'Activity Stream'),
    'url':'app_all',
    'icon':'icon-asterisk_yellow.png',
    'selected':False,
    'visible':True,
    'id':'activitystream',
    },
    {
    'title':_(u'application_views',u'Application Views'),
    'url':'-',
    'icon':'',
    'selected':False,
    'visible':True,
    'id':'appviewseparator',
    },
    {
    'title':_(u'menu_audios',u'Audio Library'),
    'url':'app_audios',
    'icon':'icon-sound.png',
    'selected':False,
    'visible':True,
    'id':'audio',
    },
    {
    'title':_(u'menu_blog',u'Blog'),
    'url':'app_blog',
    'icon':'blog.png',
    'selected':False,
    'visible':True,
    'id':'blog',
    },
    {
    'title':_(u'menu_links',u'Bookmark Directory'),
    'url':'app_links',
    'icon':'link_icon.png',
    'selected':False,
    'visible':True,
    'id':'link',
    },
    {
    'title':_(u'menu_discussions',u'Discussions Board'),
    'url':'app_discussions',
    'icon':'icon-comments.png',
    'selected':False,
    'visible':True,
    'id':'discussion',
    },
    {
    'title':_(u'menu_calendar',u'Event Calendar'),
    'url':'app_calendar',
    'icon':'event_icon.png',
    'selected':False,
    'visible':True,
    'id':'calendar',
    },
    {
    'title':_(u'menu_files',u'File Repository'),
    'url':'app_files',
    'icon':'file_icon.png',
    'selected':False,
    'visible':True,
    'id':'file',
    },
    {
    'title':_(u'menu_images',u'Image Gallery'),
    'url':'app_images',
    'icon':'image_icon.png',
    'selected':False,
    'visible':True,
    'id':'image',
    },
    {
    'title':_(u'menu_status_log',u'Status Log'),
    'url':'app_statuslog',
    'icon':'status_online.png',
    'selected':False,
    'visible':True,
    'id':'statusmessage',
    },
    {
    'title':_(u'menu_videos',u'Video Library'),
    'url':'app_videos',
    'icon':'icon-film.png',
    'selected':False,
    'visible':True,
    'id':'video',
    },
    {
    'title':_(u'menu_wiki',u'Wiki'),
    'url':'app_wiki',
    'icon':'wiki.png',
    'selected':False,
    'visible':True,
    'id':'wiki',
    },
    ]

content_location_label_name = 'Geo-Location'
content_categories_label_name = 'Tags'
