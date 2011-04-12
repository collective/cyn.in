## Controller Python Script ""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters= description=None, file=None, contributors=None, IMS=0, overwrite=0 
##title=Get Course Contents
##

# setting checkAndCleanHtml to 1 means that all uploaded documents will be passed through
# tidy.  This is now the default behavior for all documents since they derive from ATContent types.
checkHtml = 0
checkAndCleanHtml = 1
logOutput=''

from string import split

zt = context.portal_zipfiletool


status,msg = zt.importContent(file=file, context=context, description=description, contributors=contributors, overwrite=overwrite)

if status=='success':
  portal_status_message = ''
else:
  portal_status_message = 'Zip File Error'
  state.setError('file',msg)
  
title = zt.GenerateSafeFileName(file.filename) + ':Log'
title = title.replace('.','_')
title = title.replace(':','_')
logId = zt.getTime(title)

description = ''

if hasattr(context,'WriteLog'):
  context.WriteLog(logId, title, description, msg)
else:
  logId = ''

return state.set(status=status, context=context, portal_status_message=portal_status_message, logfileid=logId)