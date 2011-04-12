##################################################################################
#    Copyright (C) 2007 Utah State University, All rights reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##################################################################################

__author__ = 'David Ray, Jon Thomas, Brent Lambert'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]


from zope.publisher.interfaces.browser import IBrowserView
from zope.app.file.interfaces import IFile
from zope.interface import Interface, Attribute
from zope import schema
from Products.ZipFileTransport.schemas import ZipFileLine

class IExport(Interface):
    """ Export Form """
    filename = schema.TextLine(title=u"Export file name",
                           description=u"The name of the exported zip file that will be generated for download.",
                           required=True)

class IImport(Interface):
    """ Import Form """

    description = schema.Text(title=u"Description",
                              description=u"A description which will be given to each file in the ZIP archive.",
                              required=False)

    categories = schema.Text(title=u"Tags",
                              description=u"Tags to be applied to each file in the ZIP file. Each tag should be on a separate line.",
                              required=False)


    overwrite = schema.Bool(title=u"Overwrite",
                            description=u"Check this box to overwrite existing files with the same name.",
                            default=False,
                            required=False)


    filename = ZipFileLine(title=u"Zip File",
                           description=u"Select the ZIP archive file to be uploaded by clicking the 'Browse' button.",
                           required=True)
