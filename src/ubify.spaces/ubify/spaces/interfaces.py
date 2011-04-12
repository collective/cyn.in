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
from zope.interface import Interface
from zope import schema

from ubify.spaces import SpaceMessageFactory as _

from plone.app.vocabularies.users import UsersSource
from plone.app.vocabularies.groups import GroupsSource

class ISpace(Interface):
    """A space workspace, where special local roles may apply
    """
                         
    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"Name of the Space"),
                            required=True)
                            
    description = schema.Text(title=_(u"Description"),
                              description=_(u"A short summary for the Space"),
                              required=False)
    
    #managers = schema.List(title=_(u"Managers"),
    #                       description=_(u"The following users should be managers of this Space"),
    #                       value_type=schema.Choice(title=_(u"User id"),
    #                                               source=UsersSource,),
    #                       required=False)
    
    #members = schema.List(title=_(u"Members"),
    #                      description=_(u"The following users should be members of this Space"),
    #                      value_type=schema.Choice(title=_(u"User id"),
    #                                               source=UsersSource,),
    #                      required=False)
                                                   
    #groups = schema.List(title=_(u"Member groups"),
    #                     description=_(u"Members of the following groups should be members of this Space"),
    #                     value_type=schema.Choice(title=_(u"Group id"),
    #                                              source=GroupsSource,),
    #                     required=False)
    
    #viewers = schema.List(title=_(u"Viewers"),
    #                      description=_(u"The following users should be viewers of this Space"),
    #                      value_type=schema.Choice(title=_(u"User id"),
    #                                               source=UsersSource,),
    #                      required=False)
    
    #viewergroups = schema.List(title=_(u"Viewer groups"),
    #                     description=_(u"Members of the following groups should be viewers of this Space"),
    #                     value_type=schema.Choice(title=_(u"Group id"),
    #                                              source=GroupsSource,),
    #                     required=False)
    #
    #workflow_policy = schema.Choice(title=_(u"Workflow policy"),
    #                                description=_(u"Choose a workflow policy for this Space"),
    #                                vocabulary="ubify.spaces.WorkflowPolicies")
    #                                
    #addable_types = schema.Set(title=_(u"Addable types"),
    #                           description=_(u"These types will be addable by Space members"),
    #                           value_type=schema.Choice(title=_(u"Type id"),
    #                                                    vocabulary="ubify.spaces.AddableTypes"))

    space_icon = schema.Choice(title=_(u"Space Icon"),
                               description=_(u"Choose a space icon for this Space"),
                               vocabulary="ubify.spaces.ListSpaceIcons")

class IMindMappable(Interface):
    """ A Space can generate a Flash Browser for Freemind compatible .mm file(XML)
    """
    
class ISpaceDefaultDashboard(Interface):
    """ A Space need to have dashboard
    """