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
## Controller Python Script "setConstrainTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Set the options for constraining addable types on a per-folder basis

from Products.CMFPlone import PloneMessageFactory as _
from ubify.cyninv2theme import getAvailableAppViews
#plone_log=context.plone_log

available_app_views = getAvailableAppViews(context)
constrainTypesMode = context.REQUEST.get('constrainTypesMode', [])
currentPrefer = context.REQUEST.get('currentPrefer', [])
currentAllow = context.REQUEST.get('currentAllow', [])

default_appview = context.REQUEST.get('defaultAppView',[])
allowed_appviews = context.REQUEST.get('allowedAppView',[])
all_allowed_appviews = context.REQUEST.get('hiddenallselected','0')

#plone_log( "SET: currentAllow=%s, currentPrefer=%s" % ( currentAllow, currentPrefer ) )

# due to the logic in #6151 we actually need to do the following:
# - if a type is in "currentPrefer", then it's automatically
#   also an "locallyAllowedTypes" type.
# - types which are in "currentAllow" are to be removed from the
#   "immediatelyAddableTypes" list.
#
# That means:
# - users select types which they want to see in the menu using the
#   "immediatelyAddableTypes" list
# - if the user wants to see a certain type _only_ in the "more ..."
#   form, then they select it inside the "locallyAllowedTypes" list.

immediatelyAddableTypes = [ t for t in currentPrefer if not t in currentAllow ]
locallyAllowedTypes = [ t for t in currentPrefer ]

#plone_log( "SET: immediatelyAddableTypes=%s, locallyAllowedTypes=%s" % ( immediatelyAddableTypes, locallyAllowedTypes ) )

context.setConstrainTypesMode(constrainTypesMode)
context.setLocallyAllowedTypes(locallyAllowedTypes)
context.setImmediatelyAddableTypes(immediatelyAddableTypes)

defappview = ''
if len(default_appview) > 0:
    defappview = default_appview[0]
    if defappview != '':
        context.setLayout(defappview)    
    else:
        if context.hasProperty('layout'):
            context.manage_delProperties(('layout',))

if all_allowed_appviews == '0':
    tempobj = [k for k in available_app_views if k.url_expr.lstrip('string:') == defappview]
    if len(tempobj) > 0 and tempobj[0].getId() not in allowed_appviews:
        allowed_appviews.append(tempobj[0].getId())

if context.hasProperty('availableappviews') == 0:
    context.manage_addProperty('availableappviews',allowed_appviews,'lines')
else:
    context.manage_changeProperties({'availableappviews':allowed_appviews})

if context.portal_type in ('ContentSpace',):
    try:
        path = {}
        path['path'] = {'query':"/".join(context.getPhysicalPath()),'depth':-1}
        path['portal_type'] = 'ContentSpace'
        
        results = context.portal_catalog(**(path))
        for eobj in results:
            eobj.getObject().reindexObject()
    except:
        pass

context.reindexObject()
context.plone_utils.addPortalMessage(_(u'Changes made.'))
return state
