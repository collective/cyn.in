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
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

class ItemMetaDataViewlet(ViewletBase):

    render = ViewPageTemplateFile('item_metadata.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal_membership = getToolByName(self.context,'portal_membership')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

        current_object = self.context.aq_inner
        self.cportal_url = portal_state.portal_url()

        #import pdb;pdb.set_trace()
        #start type
        typetool= getToolByName(self.context, 'portal_types')

        self.type_name = ""
        self.has_type = False
        self.has_type_icon = False
        self.item_icon = None
        try:
            object_type = getattr(current_object, 'portal_type')
            fti = current_object.getTypeInfo()
            self.type_name = fti.title
            if fti.title <> '':
                self.has_type = True
                object_typename = current_object.portal_type
                object_typeobj = typetool[object_typename]
                self.item_icon = object_typeobj.content_icon
            else:
                self.has_type = False
        except AttributeError:
            self.type_name = ""
            self.has_type = False
        #end type

        #size starts
        self.has_size = False
        self.size = ""
        try:
            self.size = current_object.get_size()
            self.has_size = self.size > 1 ####DKG: Folderishes come up with size 1 and we don't want to show *that*
        except:
            self.has_size = False
        #size ends
        #dates start
        self.creationDate = ""
        self.modifiedDate = ""
        self.expirationDate = ""
        self.publishingDate = ""
        self.has_effectiveDate = False
        self.has_expiryDate = False
        try:
            self.creationDate = current_object.toLocalizedTime(current_object.CreationDate(),True)
            self.modifiedDate = current_object.toLocalizedTime(current_object.ModificationDate(),True)

            if current_object.ExpirationDate() <> 'None':
                self.has_expiryDate = True
                self.expirationDate = current_object.toLocalizedTime(current_object.ExpirationDate(),True)

            if current_object.EffectiveDate() <> 'None':
                self.has_effectiveDate = True
                self.publishingDate = current_object.toLocalizedTime(current_object.EffectiveDate(),True)

        except:
            _ = current_object
        #dates end

        #item state
        self.item_state = ""
        self.raw_item_state = ""
        self.has_state = False
        workflow_tool = tools.workflow()
        workflow_def = None
        current_workflow = None
        try:
            self.item_state = self.raw_item_state = workflow_tool.getInfoFor(current_object,'review_state')
            self.has_state = True

            workflow_def = workflow_tool.getWorkflowsFor(current_object)
            if len(workflow_def) > 0:
                current_workflow = workflow_def[0]
                wf_states = current_workflow.states

                current_state = wf_states[self.item_state]
                self.item_state = current_state.title
                self.has_state = True
            else:
                self.item_state = ""
        except WorkflowException:
            workflow_def = workflow_tool.getWorkflowsFor(current_object)
            if len(workflow_def) > 0:
                current_workflow = workflow_def[0]
                wf_states = current_workflow.states
                self.item_state = workflow_def.initial_state
                current_state = wf_states[self.item_state]
                self.item_state = current_state.title
                self.has_state = True
            else:
                self.item_state = ""
                self.has_state = False
        #item state ends

        #Location starts
        self.location = ""
        self.has_location = False
        try:
            self.location = current_object.getLocation()
            if self.location <> '':
                self.has_location = True
        except:
            self.has_location = False
        #Location ends

        #Language Starts
        self.lang = ""
        self.has_lang = False
        try:
            self.lang = current_object.Language()
            if self.lang <> '':
                self.lang = current_object.languages().getValue(self.lang)
                if self.lang <> None:
                    self.has_lang = True
        except:
            self.has_lang = False
        #Language Ends

        #Rights start
        self.has_rights = False
        self.rights = ""
        try:
            if current_object.Rights() <> '':
                self.has_rights = True
                self.rights = current_object.Rights()
        except:
            self.has_rights = False

        #end Rights

        #modified by
        self.has_modifiedby = False
        owner = current_object.getOwner().getUserName()
        from ubify.viewlets.utils import getObjectModifiedBy
        self.modifiedby = getObjectModifiedBy(current_object)

        if owner.lower() != self.modifiedby.lower():
            self.has_modifiedby = True
