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

from ubify.smartview.interfaces import ISmartView
from ubify.policy import CyninMessageFactory as _

        
project_form_fields = form.Fields(ISmartView)

class SmartViewAddForm(base.AddForm):
    """Add form for smart view
    """
    
    form_fields = project_form_fields
    
    label = _(u"Add Advanced View")
    form_name = _(u"Advanced view settings")
    
    #def setUpWidgets(self, ignore_request=False):
    #    
    #    self.widgets = form.setUpWidgets(
    #        self.form_fields, self.prefix, self.context, self.request,
    #        data=dict(),
    #        ignore_request=ignore_request)
    
    def create(self, data):
        smartview = createObject(u"ubify.smartview.SmartView")
        form.applyChanges(smartview, self.form_fields, data)
        return smartview
    
class SmartViewEditForm(base.EditForm):
    """Edit form for smart view
    """
    
    form_fields = project_form_fields
    
    label = _(u"Edit Advanced View")
    form_name = _(u"Advanced view settings")