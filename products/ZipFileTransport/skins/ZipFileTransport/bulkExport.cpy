##Python Script "Course_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None,IMS=0,obj_paths=None
##title=Export a course
##


filename = context.REQUEST['export_filename']
#ensure the filename has a .zip extension

if string.find(filename,'.zip') == -1:
    filename += ".zip"

if context.portal_membership.isAnonymousUser() != 0 or 'Member' in context.portal_membership.getAuthenticatedMember().getRoles():
    return

zipfilename = context.portal_zipfiletool.GenerateSafeFileName(filename)
content = context.portal_zipfiletool.exportContent(context=context,obj_paths=obj_paths, filename=filename)

context.REQUEST.RESPONSE.setHeader('content-type', 'application/zip')
context.REQUEST.RESPONSE.setHeader('content-length', len(content))
context.REQUEST.RESPONSE.setHeader('Content-Disposition',' attachment; filename='+zipfilename)
# Write out zip file data.
#context.REQUEST.RESPONSE.write(str(content))

return content

