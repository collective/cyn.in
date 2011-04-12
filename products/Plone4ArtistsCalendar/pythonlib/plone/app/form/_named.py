import os
import new
import AccessControl
import Acquisition
from zope import interface
from zope import i18n
from zope.formlib import interfaces, namedtemplate
from Products.Five.browser import metaconfigure
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

try:
    from Products.Five.browser.ReuseUtils import rebindFunction
    from _expressions import getEngine
    try_portal_skins = True
except ImportError:
    try_portal_skins = False

def proper_name(filename):
    """Get the base name of a possibly full path and if it ends with
    .pt or .zpt, chop it off.
    """

    basepath, ext = os.path.splitext(filename)
    name = basepath
    if ext and ext.lower() not in ('.pt', '.zpt'):
        name += ext

    return os.path.basename(name)

class NamedTemplateAdapter(object):
    """A named template adapter implementation that has the ability
    to lookup the template portion from regular traversal (intended for
    being able to customize the template portion of a view component
    in the traditional portal_skins style).
    """

    interface.implements(namedtemplate.INamedTemplate)

    def __init__(self, context):
        self.context = context

    def __call__(self, *args, **kwargs):
        view = self.context.__of__(self.context.context)
        cleanup = []

        # basically this means we only do customized template lookups
        # for views defined with <browser:page template='foo'> 
        if isinstance(view, metaconfigure.ViewMixinForTemplates) and \
               try_portal_skins:
            index = getattr(view, 'index', None)
            if index is not None:
                name = proper_name(index.filename)
                try:
                    template = view.context.portal_url.getPortalObject().restrictedTraverse(name)
                except AttributeError:
                    # ok, we couldn't find a portal_skins defined item
                    # so we fall back to the defined page template
                    template = index
                else:
                    if isinstance(getattr(template, 'aq_base', object()), PageTemplate):
                        template = ViewTemplateFromPageTemplate(template,
                                                                view.context)
                        template = template.__of__(view)
                    else:
                        template = index

            result = template(*args, **kwargs)
            return result
        else:
            return self.default_template.__of__(view)(*args, **kwargs)

def named_template_adapter(template):
    """Return a new named template adapter which defaults the to given
    template.
    """

    new_class = new.classobj('GeneratedClass', 
                             (NamedTemplateAdapter,),
                             {})
    new_class.default_template = template

    return new_class

if try_portal_skins:
    class ViewTemplateFromPageTemplate(PageTemplate, Acquisition.Explicit):
        """A way to make a TTW created template work as a z3 style view template.
        This opens a potential security hole and is just a preliminary
        proof-of-concept.  DO NOT USE!!!"""

        def __init__(self, template, context):
            self._text = template._text
            self.context = context
            if hasattr(template, 'id'):
                self.id = template.id
                if hasattr(template, 'title'):
                    self.title = template.title

        # A trivial _getContext method as we always know how we are wrapped
        def _getContext(self):
            return getattr(self, 'aq_parent', None)

        # Borrow from Five (the methods from PageTemplateFile are inherited from
        # PageTemplate directly)
        _cook = rebindFunction(PageTemplate._cook,
                               getEngine=getEngine)
        pt_render = rebindFunction(PageTemplate.pt_render,
                                   getEngine=getEngine)
        _pt_getContext = ZopeTwoPageTemplateFile._pt_getContext.im_func
        pt_getContext = ZopeTwoPageTemplateFile.pt_getContext.im_func

        def getId(self):
            return self.id

        def __call__(self, *args, **kwargs):
            """Add the zope user to the security context, as done in
            PageTemplateFile"""
            if not kwargs.has_key('args'):
                kwargs['args'] = args
                bound_names = {'options': kwargs}
                security = AccessControl.getSecurityManager()
                bound_names['user'] = security.getUser()
                return self.pt_render(extra_context=bound_names)
