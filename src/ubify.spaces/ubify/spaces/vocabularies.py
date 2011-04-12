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
from zope.interface import implementer

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

from ubify.spaces.config import PLACEFUL_WORKFLOW_POLICY
from ubify.spaces import SpaceMessageFactory as _

from ubify.policy.config import spacesdefaultaddabletypes
from ubify.policy.config import defaultlistspaceicons

@implementer(IVocabularyFactory)
def workflow_policies(context):
    context = getattr(context, 'context', context)
    placeful_workflow = getToolByName(context, 'portal_placeful_workflow', None)
    items = []
    if placeful_workflow is not None:
        if PLACEFUL_WORKFLOW_POLICY in placeful_workflow.objectIds():
            items.append((_(u"Default project workflow"), PLACEFUL_WORKFLOW_POLICY))
    items.sort()
    return SimpleVocabulary.fromItems(items)

@implementer(IVocabularyFactory)
def globally_allowed_types(context):
    #import pdb;pdb.set_trace()
    context = getattr(context, 'context', context)
    portal_types = getToolByName(context, 'portal_types')
    items = []
    for fti in portal_types.listTypeInfo():
        if getattr(fti, 'globalAllow', lambda: False)() == True and fti.title and fti.getId() in spacesdefaultaddabletypes:                    
            items.append((fti.title, fti.getId(),))
    return SimpleVocabulary.fromItems(items)

@implementer(IVocabularyFactory)
def listspaceicons(context):
    items=[]
    for s in defaultlistspaceicons:
        items.append((s["name"],s["id"]))
    items.sort()
    return SimpleVocabulary.fromItems(items)