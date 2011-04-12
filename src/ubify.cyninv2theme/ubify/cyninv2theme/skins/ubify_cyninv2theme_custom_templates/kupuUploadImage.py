## Script (Python) "kupuUploadImage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node_prop_title, node_prop_desc, node_prop_image

from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote, newline_to_br
from ubify.cyninv2theme import notifyobjectinitialization
request = context.REQUEST
RESPONSE =  request.RESPONSE

TEMPLATE = """
<html>
<head></head>
<body onload="window.parent.drawertool.current_drawer.%s('%s');">%s
</body>
</html>
"""

def Error(fmt, *args):
    msg = fmt % args
    script = TEMPLATE % ('cancelUpload', msg.replace("'", "\\'"), newline_to_br(html_quote(printed)))
    return script

def cleanupFilename(name):
    """Generate a unique id which doesn't match
    the system generated ids.
    The reason being that setImage will blow up if we have a system
    generated id and the id it generates from the filename is already in use.
    """
    id = ''
    name = name.replace('\\', '/') # Fixup Windows filenames
    name = name.split('/')[-1] # Throw away any path part.
    for c in name:
        if c.isalnum() or c in '._':
            id += c

    # Race condition here, but not a lot we can do about that
    if context.check_id(id) is None and getattr(context,id,None) is None:
        return id

    # Now make the id unique
    parts = id.split('.')
    if len(parts)==1: parts.append('')
    count = 1
    while 1:
        if count==1:
            sc = ''
        else:
            sc = str(count)
        id = "copy%s_of_%s" % (sc, id)
        if context.check_id(id) is None and getattr(context,id,None) is None:
            return id
        count += 1

kupu_tool = getToolByName(context, 'kupu_library_tool')
ctr_tool = getToolByName(context, 'content_type_registry')

id = request['node_prop_image'].filename
linkbyuid = kupu_tool.getLinkbyuid();
base = context.absolute_url()

# MTR would also do content-based classification, alas, we don't want it as a dependency here
# content_type= getToolByName(context,'mimetypes_registry').classify(node_prop_image)

content_type = request['node_prop_image'].headers["Content-Type"]
typename = ctr_tool.findTypeName(id, content_type, "")

# Permission checks based on code by Danny Bloemendaal

# 1) check if we are allowed to create an Image in folder 
if not typename in [t.id for t in context.getAllowedTypes()]: 
   return Error("Creation of '%s' content is not allowed in %s", typename, context.title_or_id())

# 2) check if the current user has permissions to add stuff 
if not context.portal_membership.checkPermission('Add portal content',context): 
    return Error("You do not have permission to add content in %s", context.getId())

# Get an unused filename without path
id = cleanupFilename(id)

newid = context.invokeFactory(type_name=typename, id=id,
    title=node_prop_title,
    description=node_prop_desc,
    )

if newid is None or newid == '':
   newid = id 

obj = getattr(context,newid, None)
obj.setImage(node_prop_image)
    
if not obj:
   return Error("Could not create %s with %s as id and %s as title!", typename,newid, node_prop_title)
notifyobjectinitialization(obj)
obj.reindexObject() 
if linkbyuid and hasattr(obj, 'UID'):
    url = base+'/resolveuid/%s' % obj.UID()
else:
    url = obj.absolute_url()

print "Uploaded image"
# print "content_type", content_type
# print "typename", typename
# print "RESPONSE=", RESPONSE
return TEMPLATE % ('finishUpload', url, newline_to_br(html_quote(printed)))


