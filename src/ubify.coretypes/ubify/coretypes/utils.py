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
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.utils import getToolByName

from archetypes.schemaextender.interfaces import ISchemaModifier

from archetypes.schemaextender.extender import set_schema_order
from archetypes.schemaextender.extender import get_schema_order

from Products.ATContentTypes.interface import IATContentType

from Products.Archetypes.public import Schema
from Products.Archetypes.public import ManagedSchema
from Products.Archetypes.utils import OrderedDict
from Products.Archetypes import atapi

from widgets import TagSuggestWidget

from config import content_location_label_name,content_categories_label_name

from ubify.policy import CyninMessageFactory as _

class SchemaExtender(object):
    implements(ISchemaModifier)
    adapts(IATContentType)

    def __init__(self,context):
        self.context = context

    def fiddle(self,schema):

        if schema.has_key('location'):
            schema.changeSchemataForField('location', 'settings')
        if schema.has_key('language'):
            schema.changeSchemataForField('language', 'settings')
        if schema.has_key('rights'):
            schema.changeSchemataForField('rights', 'settings')
            schema['rights'].widget.visible = {'edit': 'invisible', 'view': 'visible'}

        fields = [i for i in schema.values() if isinstance(i,atapi.LinesField) and
                                       isinstance(i.widget, atapi.KeywordWidget)]

        for field in fields:
            oldlabel = content_categories_label_name
            olddesc  = field.widget.description
            field.widget = TagSuggestWidget(label=oldlabel,description = _(u'Enter comma (,) separated tags. Example: \"important, related to productx, basic, advanced\". If an autohint selection tip appears, press tab to select the first one, or type further to shorten the hint list.'),role_based_add = True)

        if schema.has_key('contributors'):
            schema['contributors'].widget.visible = {'edit': 'invisible', 'view': 'visible'}

        if schema.has_key('creators'):
            schema['creators'].widget.visible = {'edit': 'invisible', 'view': 'visible'}

        if schema.has_key('tableContents'):
            schema['tableContents'].default = 1;

        if schema.has_key('excludeFromNav'):
            schema['excludeFromNav'].widget.visible = {'edit': 'invisible', 'view': 'visible'}

        if schema.has_key('location') and self.context.portal_type != 'Event':
            schema['location'].widget.label = content_location_label_name

        if self.context.portal_type == 'Blog Entry':
            if schema.has_key('image'):
                schema['image'].widget.visible = {'edit': 'invisible', 'view': 'visible'}
            if schema.has_key('imageCaption'):
                schema['imageCaption'].widget.visible = {'edit': 'invisible', 'view': 'visible'}

        if schema.has_key('eventType'):
            schema.changeSchemataForField('eventType', 'categorization')
            schema.moveField('eventType', before='relatedItems')

        if schema.has_key('remoteUrl'):
            schema['remoteUrl'].widget.maxlength = False

        if self.context.portal_type in ('ContentSpace','MemberSpace','ContentRoot') and schema.has_key('allowDiscussion'):
            schema['allowDiscussion'].widget.visible = {'edit': 'invisible', 'view': 'visible'}
            
        if self.context.portal_type in ('ContentSpace','ContentRoot'):
            if schema.has_key('effectiveDate'):
                schema['effectiveDate'].widget.visible = {'edit': 'invisible', 'view': 'visible'}
            if schema.has_key('expirationDate'):
                schema['expirationDate'].widget.visible = {'edit': 'invisible', 'view': 'visible'}
            if schema.has_key('location'):
                schema['location'].widget.visible = {'edit': 'invisible', 'view': 'visible'}
            if schema.has_key('language'):
                schema['language'].widget.visible = {'edit': 'invisible', 'view': 'visible'}
            
        if self.context.portal_type in ('Discussion',):
            try:
                portal_url = getToolByName(self.context,'portal_url')
                if portal_url <> None:                    
                    portal = portal_url.getPortalObject()
                    if portal <> None:
                        portal_prop = portal.portal_properties
                        if hasattr(portal_prop,'site_properties'):
                            site_prop = getattr(portal_prop,'site_properties')
                            if hasattr(site_prop,'allow_discussion_title') and getattr(site_prop,'allow_discussion_title') == True:                        
                                if schema['title'] <> None and schema['title'].widget <> None:
                                    schema["title"].widget.visible = {"edit": "visible", "view": "invisible"}
                                    schema['title'].required = True
            except:
                pass
