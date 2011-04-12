
##################################################################################
#
#    Copyright (C) 2006 Utah State University, All rights reserved.
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

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

from zope.formlib.form import  FormFields, action
from Products.Five.formlib.formbase import EditForm
from zope.component import getUtility
from zope.interface import implements
from zope.app.form.browser.textwidgets import FileWidget
from Products.ZipFileTransport.utilities.interfaces import IZipFileTransportUtility
from Products.ZipFileTransport.browser.interfaces import IImport
from Products.CMFPlone import PloneMessageFactory as _
import string


class ImportFormAdapter(object):
    """ Adapter for the import form """

    implements(IImport)

    def __init__(self,context):
        self.context = context

    def get_zipfile_name(self):
        pass

    def set_zipfile_name(self, title):
        pass

    def get_description(self):
        pass

    def set_description(self):
        pass

    def get_overwrite(self):
        pass

    def set_overwrite(self):
        pass

    def get_contributors(self):
        pass

    def set_contributors(self):
        pass

    def get_categories(self):
        pass

    def set_categories(self):
        pass

    filename = property(get_zipfile_name, set_zipfile_name)
    contributors = property(get_contributors, set_contributors)
    description = property(get_description, set_description)
    categories = property(get_categories, set_categories)
    overwrite = property(get_overwrite, set_overwrite)


class ImportForm(EditForm):
    """ Render the import form  """

    implements(IImport)
    form_fields = FormFields(IImport)
    form_fields['filename'].custom_widget = FileWidget
    label = u"Import Zip File"
    description = u"This form will import content from files contained in a .zip file. From the zip file: Folders will become Spaces, Image files (.jpg, .png, .gif, etc.) will become Images and HTML files (.html) will become Wiki Pages."

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.zft_util = getUtility(IZipFileTransportUtility)

    @action(_(u'label_import', default=u'Import'), name=u'Import')
    def action_import(self, action, data):
        file_obj = self.context.REQUEST['form.filename']
        description = self.context.REQUEST['form.description']
        contributors = ''
        overwrite = self.context.REQUEST.has_key('form.overwrite')
        categories = self.context.REQUEST['form.categories']

        self.zft_util.importContent(file=file_obj, context=self.context, description=description, contributors=contributors, overwrite=overwrite, categories=categories )

        self.request.response.redirect('./folder_contents')
