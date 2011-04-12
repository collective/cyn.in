## Controller Python Script "validate_FileUpload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=file=''
##title=Validates file upload
##

if not file or file == '':
    state.setError('file', 'No filename was entered.')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state