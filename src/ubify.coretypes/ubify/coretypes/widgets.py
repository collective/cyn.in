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

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.atapi import Vocabulary, DisplayList

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import unique

class TagSuggestWidget(TypesWidget):
    
    _properties = TypesWidget._properties.copy()
    _properties.update({    
                            'macro'              : 'tagsuggest',
                            'helper_js'         : ('cyninautocomplete.js',),
                            
                            # Only some roles can add new items?
                            'role_based_add'    : 0,
                           
                            # Property in site_properties listing which roles
                            #  can add new items
                            'add_role_property' : 'allowRolesToAddKeywords',
                            
                            # Does the keyword vocab come from somewhere other
                            #  than portal_catalog?
                            'vocab_source'      : 'portal_catalog',

                            # Size (num items) and width (measurement) of boxes
                            # Set width_absolute to 1 make width be fixed; else
                            #  it defines the min-width only.
                            'size'              : '15',
                            'width'             : '50em',
                            'width_absolute'    : 0,
                         },)
    
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """If a value was typed in the box, use this, else use the selected
        value.
        """        
        name = field.getName()
        value = form.get(name, empty_marker)
        if value == '' or value == [''] and emptyReturnsMarker:
            return empty_marker
        
        try:            
            values = value.split(",")
            values = [val.strip().lower() for val in values]
            values = [k.lower() for k in list(unique(values)) if k]            
        except AttributeError:
            return empty_marker
        else:
            return values, {}
    
    def is_keyword_field(self, field, source):        
        """Returns whether or not a given field has a corresponding KeywordIndex
        in the specified catalog (source).
        """        
        catalog = getToolByName(self,source)
        idxs = catalog.index_objects()
        filtered = [idx for idx in idxs if idx.id == field.accessor and
                    idx.meta_type == 'KeywordIndex' ]
        return filtered != []
    
    def makeVocab(self,list):
        """Takes in a list (of keywords) and returns a Vocabulary without a
        translation domain.
        """        
        dl = DisplayList()
        for i in list:
            dl.add(i,i)
        return Vocabulary(dl,None,None)

registerWidget(TagSuggestWidget,
                title = 'Tag Suggest widget',
                description= ('Renders a HTML widget with textbox',),
                used_for = ('Products.Archetypes.Field.LinesField',)
                )