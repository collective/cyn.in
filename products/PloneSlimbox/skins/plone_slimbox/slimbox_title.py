## Script (Python) "slimbox_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=image
##title=
##
title = "<strong>%s</strong>" % image.pretty_title_or_id()
desc = image.Description()
if desc:
    title += " - %s" % desc
title += "<br/>"
url = image.absolute_url()

label = context.translate(domain='slimbox', msgid='full-size')
desc = context.translate(domain='slimbox', msgid='Click to view full-size image...')

title += '<a href="%s/image_view_fullscreen" title="%s">%s</a> ' % (url, desc, label)

label = context.translate(domain='slimbox', msgid='Normal view')
desc = context.translate(domain='slimbox', msgid='Click to open Normal view...')
title += '<a href="%s/view" title="%s">%s</a>' % (url, desc, label)

return title
