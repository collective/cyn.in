plone.app.form
==========

Overview
--------

The plone.app.form package gives Plone the ability to better adapt common
Zope 3 UI style functionality to a more appropriate Plone style.

Features
--------

  - **Better integration with zope.formlib.**  The default templates
    distributed with zope.formlib are table-based and don't follow
    common Plone UI patterns, plone.app.form addresses this.  Also,
    plone.app.form patches zope.formlib so that the base classes from
    there can be used as-is.

  - **Traditional portal_skins defineable custom templates.**  Currently
    this means that if a view component is defined with with
    ``<browser:page template="foo.pt">`` then when that view is displayed
    it will lookup "foo" via portal_skins first and only use the default
    foo.pt if no overridden foo can be found.  This currently means
    the view class must define a 'template' attribute which uses
    a named template (which in the case of zope.formlib is always the
    case) ... this logic is currently in the process of refinement.
