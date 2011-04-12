###############################################################################
##cyn.in is an open source Collaborative Knowledge Management Appliance that 
##enables teams to seamlessly work together on files, documents and content in 
##a secure central environment.
##
##cyn.in v2 an open source appliance is distributed under the GPL v3 license 
##along with commercial support options.
##
##cyn.in is a Cynapse Invention.
##
##Copyright (C) 2008 Cynapse India Pvt. Ltd.
##
##This program is free software: you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software 
##Foundation, either version 3 of the License, or any later version and observe 
##the Additional Terms applicable to this program and must display appropriate 
##legal notices. In accordance with Section 7(b) of the GNU General Public 
##License version 3, these Appropriate Legal Notices must retain the display of 
##the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
##received a copy of the detailed Additional Terms License with this program.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of 
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
##Public License for more details.
##
##You should have received a copy of the GNU General Public License along with 
##this program.  If not, see <http://www.gnu.org/licenses/>.
##
##You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
##For any queries regarding the licensing, please send your mails to 
## legal@cynapse.com
##
##You can also contact Cynapse at:
##802, Building No. 1,
##Dheeraj Sagar, Malad(W)
##Mumbai-400064, India
###############################################################################
## Script (Python) "computeReferencedItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=relationship=None,type='incoming'
##title=find related items for an object
##

from AccessControl import Unauthorized
from Products.CMFPlone.utils import base_hasattr

res = []

results = []

if relationship == 'links':
    if type == 'incoming':
        results = context.getBRefs('isReferencing') + context.getRefs('Backlink->Source Doc')
    elif type == 'outgoing':
        results = context.getRefs('isReferencing') + context.getBRefs('Backlink->Source Doc')
    else:
        results = []
elif relationship == 'relateditems':
    if type == 'incoming':
        results = context.getBRefs('relatesTo')
    else:
        results = []
else:
    results = []

mtool = context.portal_membership

for d in range(len(results)):
    try:
        obj = results[d]
    except Unauthorized:
        continue
    if obj <> None and obj not in res and obj <> context:
        if mtool.checkPermission('View', obj):
            res.append(obj)

res.sort(lambda x,y: cmp(x.title,y.title),reverse=False)
return res
