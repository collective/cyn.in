
patches = {}

def apply_formlib_request_locale_patch():
    """Default zope.formlib EditFormBase tries to access the locale
    attribute on the request.  In the case of a Zope 2 request, this 
    does not exist.  Lets fix that.
    """

    from zope.formlib import form
    from Products.Five.formlib import formbase
    action = form.EditFormBase.actions[u'actions.apply']
    patched = getattr(action, '_plone_form_patched', False)
    if not patched:
        # lets replace formlib's builtin default apply success handler
        # with the one provided by Five
        patches['formlib_request_locale'] = (action, 'success_handler',
                                             action.success_handler)
        five_action = formbase.EditFormBase.actions[u'actions.apply']
        action.success_handler = five_action.success_handler
        action._plone_form_patched = True
        return True
    return False

def remove_formlib_request_locale_patch():
    patch = patches.get('formlib_request_locale', None)
    if patch is not None:
        obj, attr_name, orig = patch
        setattr(obj, attr_name, orig)
        delattr(obj, '_plone_form_patched')
        del patches['formlib_request_locale']
        return True
    return False

def apply_formlib_update_patch():
    """Formlib (and all of zope3's widget machinery) expects input
    values to already have been converted to unicode objects.  ZPublisher
    (zope2) doesn't take care of this so Five introduced a method in
    its formlib overriding mixin to remedy this.  Lets make sure
    zope.formlib.FormBase has Five's update method.
    """
    
    from zope.formlib import form
    from Products.Five.browser import decode
    patched = patches.get('formlib_formbase_update', None) is not None
    if not patched:
        orig = form.FormBase.update
        patches['formlib_formbase_update'] = (form.FormBase, 'update', 
                                              orig)
        def update(self):
            decode.processInputs(self.request)
            decode.setPageEncoding(self.request)
            orig(self)
            
        form.FormBase.update = update
        return True
    return False

def remove_formlib_update_patch():
    patch = patches.get('formlib_formbase_update', None)
    if patch is not None:
        obj, attr_name, orig = patch
        setattr(obj, attr_name, orig)
        del patches['formlib_formbase_update']
        return True
    return False
