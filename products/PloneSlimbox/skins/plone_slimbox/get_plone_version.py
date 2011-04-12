## Script (Python) "get_plone_version"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
version = context.portal_migration.getInstanceVersion().split('.')
return version[0] + version[1]
