###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that 
#enables teams to seamlessly work together on files, documents and content in 
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license 
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software 
#Foundation, either version 3 of the License, or any later version and observe 
#the Additional Terms applicable to this program and must display appropriate 
#legal notices. In accordance with Section 7(b) of the GNU General Public 
#License version 3, these Appropriate Legal Notices must retain the display of 
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with 
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
#For any queries regarding the licensing, please send your mails to 
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
README for the 'browser/images/' directory
==========================================

This folder is a Zope 3 Resource Directory acting as a repository for images.

Its declaration is located in 'browser/configure.zcml':

    <!-- Resource directory for images -->
    <browser:resourceDirectory
        name="ubify.smartview.images"
        directory="images"
        layer=".interfaces.IThemeSpecific"
        />

An image placed in this directory (e.g. 'logo.png') can be accessed from
this relative URL:

    "++resource++ubify.smartview.images/logo.png"

Note that it might be better to register each of these resources separately if
you want them to be overridable from zcml directives.

The only way to override a resource in a resource directory is to override the
entire directory (all elements have to be copied over).

A Zope 3 browser resource declared like this in 'browser/configure.zcml':

    <browser:resource
        name="logo.png"
        file="images/logo.png"
        layer=".interfaces.IThemeSpecific"
        />

can be accessed from this relative URL:

    "++resource++logo.png"

Notes
-----

* Whatever the way they are declared (in bulk inside a resource directory or
  as separate resources), images registered as Zope 3 browser resources don't
  have all the attributes that Zope 2 image objects have (i.e. the 'title'
  property and the 'tag()' and 'get_size()' methods).
  This means that if you want the html tag of your image to be auto-generated
  (this is the case by default for the portal logo), you should store it in a
  directory that is located in the 'skins/' folder of your package, registered
  as a File System Directory View in the 'portal_skins' tool, and added to the
  layers of your skin.

* Customizing/overriding images that are originally accessed from the
  'portal_skins' tool (e.g. Plone default logo and icons) can be done inside
  that tool only. There is no known way to do it with Zope 3 browser
  resources.
  Vice versa, there is no known (easy) way to override a Zope 3 browser
  resource from a skin layer in 'portal_skins'.
