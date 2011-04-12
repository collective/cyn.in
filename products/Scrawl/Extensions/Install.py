from Products.CMFCore.utils import getToolByName
from Products.Scrawl.config import BLOG_ENTRY_NAME, GLOBALS
from Products.Scrawl import HAS_PLONE30
from Products.Archetypes.Extensions.utils import install_subskin
import string
from StringIO import StringIO

def install(portal):
    out = StringIO()

    # copy the News Item for our blog entry
    portal_types = getToolByName(portal, 'portal_types')
    if BLOG_ENTRY_NAME not in portal_types.objectIds():
        cb_copy_data = portal_types.manage_copyObjects(['News Item'])
        paste_data = portal_types.manage_pasteObjects(cb_copy_data)
        temp_id = paste_data[0]['new_id']
        portal_types.manage_renameObject(temp_id, BLOG_ENTRY_NAME)
        getattr(portal_types, BLOG_ENTRY_NAME).title = BLOG_ENTRY_NAME
        getattr(portal_types, BLOG_ENTRY_NAME).i18n_domain = 'cynin'
        out.write("Duplicated 'News Item' FTI info as '%s'" % BLOG_ENTRY_NAME)

    # tweak Blog Entry FTI settings
    blog = getattr(portal_types, BLOG_ENTRY_NAME)
    blog.default_view = 'blogentry_view'
    blog.immediate_view = 'blogentry_view'
    view = 'blogentry_view'
    if view not in blog.view_methods:
        blog._updateProperty('view_methods', blog.view_methods + (view,))
    blog.allow_discussion = True
    out.write("Tweaked %s FTU settings" % BLOG_ENTRY_NAME)

    # make Blog Entry use portal factory, so we don't have any blog entry skeletons
    factory = getToolByName(portal, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    if 'Blog Entry' not in types:
        types.append('Blog Entry')
        factory.manage_setPortalFactoryTypes(listOfTypeIds=types)
        print >> out, "Added Blog Entry to portal factory"

    # install our skins
    install_subskin(portal, out, GLOBALS)
    skins_tool = getToolByName(portal, "portal_skins")
    if HAS_PLONE30:
        bad_skin = "scrawl"
    else:
        bad_skin = "scrawl_30"

    # Iterate over all existing skins and remove the one we don't want
    skins = skins_tool.getSkinSelections()
    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if bad_skin in path:
            path.remove(bad_skin)
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skins_tool.addSkinSelection(skin, path)


    # make blog view available to Smart Folders
    view = 'blog_view'
    topic = portal_types.Topic
    if view not in topic.view_methods:
        topic._updateProperty('view_methods', topic.view_methods + (view,))
        print >> out, "Made %s available for topics.\n" % view

    return out.getvalue()

def uninstall(portal, reinstall=False):
    # remove skins
    skins_tool = getToolByName(portal, "portal_skins")
    skin_names = ("scrawl","scrawl_30")
    skins = skins_tool.getSkinSelections()
    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        path = [s for s in path if s not in skin_names]
        path = string.join(path, ', ')
        skins_tool.addSkinSelection(skin, path)

    # remove blog_view from Topics
    view = 'blog_view'
    portal_types = getToolByName(portal, 'portal_types')
    topic = portal_types.Topic
    if view in topic.view_methods:
        view_methods = [v for v in topic.view_methods if v != view]
        topic._updateProperty('view_methods', view_methods)

    # remove Blog Entry from portal factory
    factory = getToolByName(portal, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    if 'Blog Entry' in types:
        types.remove('Blog Entry')
        factory.manage_setPortalFactoryTypes(listOfTypeIds=types)
