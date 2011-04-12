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
from zope.component import createObject
from zope.formlib import form

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget

from Acquisition import aq_inner

from ubify.spaces.interfaces import ISpace
from ubify.spaces import SpaceMessageFactory as _

from ubify.spaces.utils import default_addable_types
        
project_form_fields = form.Fields(ISpace)
#project_form_fields['managers'].custom_widget = UberMultiSelectionWidget
#project_form_fields['members'].custom_widget = UberMultiSelectionWidget
#project_form_fields['groups'].custom_widget = UberMultiSelectionWidget
#project_form_fields['viewers'].custom_widget = UberMultiSelectionWidget
#project_form_fields['viewergroups'].custom_widget = UberMultiSelectionWidget


class SpaceAddForm(base.AddForm):
    """Add form for spaces
    """
    
    form_fields = project_form_fields
    
    label = _(u"Add Space")
    form_name = _(u"Space settings")
    
    def setUpWidgets(self, ignore_request=False):
        default_addable = default_addable_types(aq_inner(self.context))
        
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=dict(addable_types=default_addable),
            ignore_request=ignore_request)
    
    def create(self, data):
        space = createObject(u"ubify.spaces.Space")
        form.applyChanges(space, self.form_fields, data)
        return space
    
class SpaceEditForm(base.EditForm):
    """Edit form for spaces
    """
    
    form_fields = project_form_fields
    
    label = _(u"Edit Space")
    form_name = _(u"Space settings")