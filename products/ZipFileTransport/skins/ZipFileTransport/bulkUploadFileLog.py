## Controller Python Script ""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=logfileid=''
##title=Bulk upload File Log
##

if logfileid:
    context.REQUEST.RESPONSE.redirect('%s/.LogFiles/%s' %(context.absolute_url(), logfileid))
else:
    context.REQUEST.RESPONSE.redirect('folder_contents')
