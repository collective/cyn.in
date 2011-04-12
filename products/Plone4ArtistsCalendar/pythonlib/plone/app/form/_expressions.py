from AccessControl import getSecurityManager
from Acquisition import aq_chain
from Products.PageTemplates.Expressions import \
     SubPathExpr, PathExpr, \
     StringExpr, PythonExpr, \
     getEngine, installHandlers, restrictedTraverse
from Products.PageTemplates.TALES import _parse_expr
from Products.PageTemplates.DeferExpr import LazyWrapper
from Products.PageTemplates.DeferExpr import DeferWrapper
from Products.Five.browser.TrustedExpression import trustedTraverse
from Products.Five.browser.ReuseUtils import rebindFunction
from Products.Five.browser.ProviderExpression import ProviderExpr

class SubPathExpr(SubPathExpr):
    """A path expression which allows unrestricted access to attributes
    on the view, but restricted access to other attributes."""

    def _eval(self, econtext,
              list=list, isinstance=isinstance, StringType=type('')):
        vars = econtext.vars
        path = self._path
        if self._dp:
            path = list(path) # Copy!
            for i, varname in self._dp:
                val = vars[varname]
                if isinstance(val, StringType):
                    path[i] = val
                else:
                    # If the value isn't a string, assume it's a sequence
                    # of path names.
                    path[i:i+1] = list(val)
        __traceback_info__ = base = self._base
        if base == 'CONTEXTS' or not base:
            ob = econtext.contexts
        elif base == 'view':
            view = vars[base]
            # start security checking after the initial path element for view
            # attributes
            ob = trustedTraverse(view, [path.pop(0)], None)
        else:
            ob = vars[base]
        if isinstance(ob, DeferWrapper):
            ob = ob()
        if path:
            if vars['view'] in aq_chain(ob) or aq_chain(ob) == [ob]:
                # XXX: Allow unlimited access to things acquired from the view
                # and objects with no acquisition context
                traverse = trustedTraverse
            elif path[0].startswith('@@') or path[0].startswith('++'):
                # XXX: Any view or traversal adapter lookup should be
                # unrestricted, this is hacky, what are the other options.
                traverse = trustedTraverse
            else:
                traverse = restrictedTraverse
            ob = traverse(ob, path, getSecurityManager())
        return ob


class PathExpr(PathExpr):
  __init__ = rebindFunction(PathExpr.__init__.im_func,
                            SubPathExpr=SubPathExpr,
                            )

class StringExpr(StringExpr):
  __init__ = rebindFunction(StringExpr.__init__.im_func,
                            PathExpr=PathExpr,
                            )


installHandlers = rebindFunction(installHandlers,
                                 PathExpr=PathExpr,
                                 StringExpr=StringExpr,
                                 PythonExpr=PythonExpr,
                                 )

def installHandlers2(engine):
    installHandlers(engine)
    engine.registerType('provider', ProviderExpr)

_engine=None
getEngine = rebindFunction(getEngine,
                           _engine=_engine,
                           installHandlers=installHandlers2
                           )
