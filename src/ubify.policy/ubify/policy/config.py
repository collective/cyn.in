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
"""
Contains constants used by setuphandler.py
"""
from ubify.policy import CyninMessageFactory as _
GLOBALS = globals()

PROJECTNAME = 'ubify.policy'

newgroups = ('SiteAdmins',
             )
siteadmingroup = "SiteAdmins"
siteadmin = "siteadmin"
siteadminpass = "secret"
testuserpass = "secret"
createtestusers = False
createtestspaces = False
user_my_folder_name = 'My Space'

# spaces default addable types
spacesdefaultaddabletypes = ('Blog',
                             'Calendar',
                             'FileRepository',
                             'GenericContainer',
                             'Folder',
                             'Gallery',
                             'LinkDirectory',
                             'Space',
                             'Topic',
                             'Wiki',
                             'SmartView',
                             )

# spaces default addable non folderish types
spacesdefaultaddablenonfolderishtypes = ('Document',
                                         'Event',
                                         'File',
                                         'Image',
                                         'Link',
                                         'Blog Entry',
                                         'Video',
                                         'Discussion',
                                         'Audio',
                                        )

sitetabs = ({'id':'central',
             'name':'Central',
             'url_expr':'string:$portal_url/spaces/central',
             'condition':'',
             'permission':'',
             'category':'',
             'visible':True,
             },
            {'id':'spaces',
             'name':'Spaces',
             'url_expr':'string:$portal_url/spaces',
             'condition':'',
             'permission':'',
             'category':'',
             'visible':True,
             },
            {'id':'people',
             'name':'People',
             'url_expr':'string:$portal_url/Members',
             'condition':'',
             'permission':'',
             'category':'',
             'visible':True,
             },
            )
mailhostconfiguration = {'configure':True,
                         'smtphost':'localhost',
                         'smtpport':25,
                         'fromemailname':'Site Administrator',
                         'fromemailaddress':'siteadmin@yourdomain.com'
                        }

PRODUCT_DEPENDENCIES = ('Calendaring',
                        'plone.app.iterate',
                        'Marshall',
                        'CMFPlacefulWorkflow',
                        'CMFNotification',
                        'ZipFileTransport',
                        'Scrawl',
                        'ubify.coretypes',
                        'ubify.smartview',
                        'ubify.spaces',
                        'ubify.viewlets',
                        'ubify.cyninv2theme',
                        'ubify.recyclebin',
                        'ubify.xmlrpc',
                        'Products.OpenXml',
                        'ATRatings',
                        'ubify.ffxmpp',
                        )

UNINSTALL_PRODUCTS = ('PloneSlimbox',
                      'PloneFlashUpload',
                     )

EXTENSION_PROFILES = ('ubify.policy:default',
)

ALLOWEDROLESTOADDKEYWORDS = ('Owner',
                             'Editor',
                             'Contributor',
                            )

kuputoolbaroptions = ('bg-subsuper',
                  'subscript-button',
                  'superscript-button',
                  'embed-tab',
                  'toc-tab',
                  'bg-undo',
                  'undo-button',
                  'redo-button',
                 )

defaultlistspaceicons = (
                        {'id':'aaspace-icon.png','name':'A Space',},
                        {'id':'private2.png','name':'Private',},
                        {'id':'workspace1.png','name':'Workspace 1',},
                        {'id':'folder50.png','name':'Folder',},
                        {'id':'warning2.png','name':'Warning 2',},
                        {'id':'drive_graphite.png','name':'Drive graphite',},
                        {'id':'sync1.png','name':'Sync 1',},
                        {'id':'chat_bubble.png','name':'Chat bubble',},
                        {'id':'lock1.png','name':'Lock 1',},
                        {'id':'stop.png','name':'Stop',},
                        {'id':'info2.png','name':'Info 2',},
                        {'id':'drive_blue.png','name':'Drive blue',},
                        {'id':'warning1.png','name':'Warning 1',},
                        {'id':'drive_green.png','name':'Drive green',},
                        {'id':'under_construction.png','name':'Under construction',},
                        {'id':'space_key.png','name':'Key',},
                        {'id':'question2.png','name':'Question 2',},
                        {'id':'sync3.png','name':'Sync 3',},
                        {'id':'workspace2.png','name':'Workspace 2',},
                        {'id':'screen.png','name':'Screen',},
                        {'id':'tick2.png','name':'Tick 2',},
                        {'id':'drive_red.png','name':'Drive red',},
                        {'id':'buddies.png','name':'Buddies',},
                        {'id':'alert_bell.png','name':'Alert bell',},
                        {'id':'globe.png','name':'Globe',},
                        {'id':'lock2.png','name':'Lock 2',},
                        {'id':'collaboration.png','name':'Collaboration',},
                        {'id':'sync2.png','name':'Sync 2',},
                        {'id':'star.png','name':'Star',},
                        {'id':'Info1.png','name':'Info 1',},
                        {'id':'question1.png','name':'Question 1',},
                        {'id':'network.png','name':'Network',},
                        {'id':'private1.png','name':'Private 1',},
                        {'id':'hazard.png','name':'Hazard',},
                        {'id':'tick1.png','name':'Tick 1',},
                        {'id':'help.png','name':'Help',},
                        )

custommindmapshowabletypes = ('ContentRoot',
                              'SmartviewFolder',
                              'ContentSpace',
                              )

defaulttitles = ({'id':'spaces',
                  'type':'SpacesFolder',
                  'title':'spaces',
                  'description':'',
                 },
                 {'id':'views',
                  'type':'SmartviewFolder',
                  'title':'views',
                  'description':'',
                 },
                )

defaultsmartviews = ({'id':'allitems',
                      'title':'All Items',
                      'description':'All content items of this site.',
                      'query':{'sort_on':'modified','sort_order':'descending'}
                     },
                    )

default_categories = ('company assets',
                        'reports',
                        'collateral',
                        'stock photos',
                        'templates',
                        'presentations',
                        'catalogues',
                        'minutes of meetings',
                        'plans',
                        'policies',
                        'events',
                        'article',
                     )
kupu_table_styles = ("fancy|Styled Table",
                     "invisible|Invisible grid",
                    )
kupu_paragraph_styles = ("Heading|h2",
                        "Subheading|h3",
                        "Subheading 2|h4",
                        "Subheading 3|h5",
                        "Subheading 4|h6",
                        "Literal|pre",
                        "Discreet|p|discreet",
                        "Pull-quote|div|pullquote",
                        "Call-out|p|callout",
                        "Block-quote|blockquote",
                        "Highlight|span|visualHighlight",
                        "Odd row|tr|odd",
                        "Even row|tr|even",
                        "Heading cell|th|",
                        "Page break (print only)|div|pageBreak",
                        "Clear floats|div|visualClear",
                        "Notice - Attention|div|attention",
                        "Notice - Yes|div|yes",
                        "Notice - No|div|no",
                        "Notice - Information|div|information",
                        "Notice - Thumbs Up|div|thumbsup",
                        "Notice - Rosette|div|rosette",
                        "Notice - Idea|div|idea",
                        "Notice - Smiley|div|smiley",
                        "Notice - Note|div|note",
                        "Notice - Warning|div|warning",
                        )

approval_space = {'createspace':False,
                     'id':'reviewed-content',
                     'title':'Reviewed Content',
                     'description':'This space demonstrates Approval workflow.',
                     'Viewers':('Customers',),
                     'Contributors':('Engineering',),
                     'Reviewers':('Management',),
                     'Editors':('Operations',),
                    }

MEMBERS_PLACEFUL_WORKFLOW_POLICY = 'ubify_publish_keep_private'
MEMBERS_PLACEFUL_WORKFLOW_POLICY_BELOW = 'ubify_private_keep_publish'
USER_SPACEFOLDER_WORKFLOW_POLICY = 'ubify_user_spaces_folder_workflow'
USER_PRIVATE_SPACE_POLICY = 'ubify_user_private_workflow'
USER_PUBLIC_SPACE_POLICY = 'ubify_user_public_workflow'
USER_PUBLIC_SPACE_BELOW_POLICY = 'ubify_publish_spaces_content_workflow'


spacecontentworkflowtypes = spacesdefaultaddabletypes + spacesdefaultaddablenonfolderishtypes

default_sitehome_smartviews = (
                    {
                        'id':'allblogentries',
                        'title':'All Blog Posts',
                        'description':'All blog posts of this cyn.in site.',
                        'type': ('Blog Entry',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Blog Posts',
                    },
                    {
                        'id':'allwikipages',
                        'title':'All Wiki Pages',
                        'description':'All wiki pages of this cyn.in site.',
                        'type': ('Wiki Page',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Wiki Pages',
                    },
                    {
                        'id':'allevents',
                        'title':'All Events',
                        'description':'All events of this cyn.in site.',
                        'type': ('Event',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Events',
                    },
                    {
                        'id':'allfiles',
                        'title':'All Files',
                        'description':'All files of this cyn.in site.',
                        'type': ('File',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Files',
                    },
                    {
                        'id':'allimages',
                        'title':'All Images',
                        'description':'All images of this cyn.in site.',
                        'type': ('Image',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Images',
                    },
                    {
                        'id':'alllinks',
                        'title':'All Links',
                        'description':'All links of this cyn.in site.',
                        'type': ('WebLink',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Links',
                    },
                    {
                        'id':'allcomments',
                        'title':'All Comments',
                        'description':'All comments of this cyn.in site.',
                        'type': ('Comment',),
                        'limitnumber': False,
                        'itemcount': 10,
                        'limit':5,
                        'displaytitle':'Comments',
                    },
                    )

user_private_space_items = (
                            {
                                'id':'myfiles',
                                'title':'My Personal Files',
                                'type':'FileRepository',
                            },
                            {
                                'id':'myphotos',
                                'title':'My Personal Photos',
                                'type':'Gallery',
                            },
                            {
                                'id':'mywiki',
                                'title':'My Personal Wiki',
                                'type':'Wiki',
                            },
                            {
                                'id':'mycalendar',
                                'title':'My Personal Calendar',
                                'type':'Calendar',
                            },
                            {
                                'id':'mycheckouts',
                                'title':'My Checkouts',
                                'type':'GenericContainer',
                            }
)

user_public_space_items = (
                            {
                                'id':'files',
                                'title':'Files',
                                'type':'FileRepository',
                            },
                            {
                                'id':'gallery',
                                'title':'Gallery',
                                'type':'Gallery',
                            },
                            {
                                'id':'wiki',
                                'title':'Wiki',
                                'type':'Wiki',
                            },
                            {
                                'id':'calendar',
                                'title':'Calendar',
                                'type':'Calendar',
                            },
                            {
                                'id':'links',
                                'title':'Links',
                                'type':'LinkDirectory',
                            },
                            {
                                'id':'blog',
                                'title':'Blog',
                                'type':'Blog',
                            }
)

list_of_portletmanagers_for_stackerportlet_assignment = (
                            'plone.rightcolumn',
                          )

cynin_desktop_left_column_text = """
<table>
<tbody>
<tr>
<td>Get your cyn.in notifications, search and instant discussions, direct to your desktop.</td>
</tr>
<tr>
<td align="center"><a class="nourlicon" href="http://cyn.in/cynin-desktop"><img class="image-inline image-inline" src="/get-cyniin-desktop.png" alt="Get Cyni.in Desktop" /></a></td>
</tr>
<tr>
<td>Supports: <img src="/windows_icon.png" alt="Windows XP / Vista" /> Windows XP / Vista, <img src="/apple_icon.png" alt="Mac OS X" />Mac OS X, <img class="image-inline image-inline" src="/linux_icon.png" alt="" /> Linux.</td>
</tr>
</tbody>
</table>        """

space_defined_applications = (
                                {
                                    'id':'blog',
                                    'title':'Blog',
                                    'type':'Blog',
                                },
                                {
                                    'id':'calendar',
                                    'title':'Calendar',
                                    'type':'Calendar',
                                },
                                {
                                    'id':'files',
                                    'title':'Files',
                                    'type':'FileRepository',
                                },
                                {
                                    'id':'gallery',
                                    'title':'Gallery',
                                    'type':'Gallery',
                                },
                                {
                                    'id':'links',
                                    'title':'Links',
                                    'type':'LinkDirectory',
                                },
                                {
                                    'id':'wiki',
                                    'title':'Wiki',
                                    'type':'Wiki',
                                },

)

contentroot_details = {
                        'id':'home',
                        'title':'Home',
                        'oldid': 'root',
                        'oldtitle': 'Main',
}

collection_details = {
                        'id':'views',
                        'title':'Collections'
}

custom_site_properties = (
                            {
                                'name':'logout_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'login_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'register_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'webdav_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'rss_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'ical_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'desktop_login_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'email_verification_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'base_rss_url',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'allow_discussion_title',
                                'value':False,
                                'type':'boolean'
                            }
)

custom_cynin_properties = (
                            {
                                'name':'web_custom_header',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'web_custom_header_anonymous',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'web_custom_footer',
                                'value':'',
                                'type':'string'
                            },
                            {
                                'name':'web_custom_footer_anonymous',
                                'value':'',
                                'type':'string'
                            },
)
versionable_content_types = ('Document',
                            'File',
                            'Image',
                            'Blog Entry',
                            'Video',                            
                            'Audio',
)

kupu_linkable_types = ('ContentRoot','ContentSpace','MemberSpace','SmartView','SmartviewFolder','StatuslogItem',) + spacesdefaultaddablenonfolderishtypes
