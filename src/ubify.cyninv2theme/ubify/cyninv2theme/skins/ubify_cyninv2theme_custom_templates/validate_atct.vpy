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
## Script (Python) "validate_atct"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

errors  = {}
request = context.REQUEST
form    = request.form
from Products.ATContentTypes import ATCTMessageFactory as _

## It's hacky and not nice but it's working
# Set the title from the filename of uploaded image or field
# The title has to be set before the validation. This is the only place to do it
# right although it's looking hackish.

pfield = context.getPrimaryField()
if pfield:
    pfname = pfield.getName()
    title = form.get('title', context.Title())
    file = form.get('%s_file' % pfname, None)
    titlefromfile = False

    if not title and file:
        if file:
            filename = getattr(file, 'filename', None)

        if filename:
            newfilename = filename.split('\\')[-1]
            newfilename = newfilename.replace('_',' ')
            form['title'] = newfilename
            titlefromfile = True
    
    if file and context.portal_type == 'Video':
        filename = getattr(file, 'filename', None)
        fileext = filename.split('.')[-1]
        if fileext not in context.assocFileExt:
	    errors['file'] = '%s file extension is not allowed.' % (fileext,)
            if titlefromfile:
                form['title'] = ''
    elif file and context.portal_type == 'Audio':
        filename = getattr(file, 'filename', None)
        fileext = filename.split('.')[-1]
        if fileext not in context.assocFileExt:
	    errors['file'] = '%s file extension is not allowed.' % (fileext,)
            if titlefromfile:
                form['title'] = ''
    
        
## eoXXX

errors  = context.validate(REQUEST=request, errors=errors, data=1, metadata=0)

if errors:
    msg = _(u'Please correct the indicated errors.')
    context.plone_utils.addPortalMessage(msg, 'error')
    return state.set(status='failure', errors=errors)

msg = _(u'Changes saved.')
context.plone_utils.addPortalMessage(msg)
return state
