#######
OpenXml
#######

By `Gilles Lenfant <mailto:gilles.lenfant@gmail.com>`_

About OpenXml
#############

OpenXml provides Plone resources for OpenXml documents :

* A set of icons for Office 2007 documents
* A set of PortalTransforms plugins suitable to OpenXml documents
  indexing

Requirements
############

* Plone 2.5 or Plone 3 (note that indexing of OpenXml documents only
  works from Plone 3.0 due to AT changes in field indexing)

* openxmllib 1.0.0 (+) for Python:
  http://code.google.com/p/openxmllib/

* Note that openxmllib requires the - excellent - lxml. See the
  instructions provided in openxmllib documentation.


Install
#######

From now, OpenXml is an egg, but you already know it if you're reading
this browsing the pypi site. So to get the latest distro suitable to
your Plone, you only need to add ``Products.OpenXml`` to the eggs list
of your ``buildout.cfg``.

License
#######

This software is subject to the provisions of the GNU General Public
License, Version 2.0 (GPL).  A copy of the GPL should accompany this
distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

More details in the ``LICENSE`` file included in this package.

Testing
#######

Please read ``tests/README.txt' for unit tests.

Credits
#######

* Icons gracefully given by `Alexander Gross
  <http://www.therightstuff.de/2006/12/16/Office+2007+File+Icons+For+Windows+SharePoint+Services+20+And+SharePoint+Portal+Server+2003.aspx>`_

SVN repository
##############

Point your SVN client to
https://svn.plone.org/svn/collective/Products.OpenXml/...

Download
########

You may find newer versions of PloneArticle from
http://plone.org/products/openxml

Support
#######

Before asking for support, please make sure that your problem is not
described in the documentation that ships with OpenXml or any required
component (see Requirements_ above).

