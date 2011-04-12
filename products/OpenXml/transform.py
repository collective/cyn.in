#-*- coding: utf-8 -*-
# $Id: transform.py 67356 2008-06-27 10:01:12Z glenfant $
"""
Our transform (most job is done by openxmllib)
"""
import mimetypes
import openxmllib
from openxmllib import contenttypes as ct
from Products.PortalTransforms.interfaces import itransform
from config import SITE_CHARSET, TRANSFORM_NAME
from Products.OpenXml import logger

class openxml_to_text:
    __implements__ = itransform
    __name__ = TRANSFORM_NAME

    inputs = (
        # Wordprocessing formats
        ct.CT_WORDPROC_DOCX_PUBLIC,
        ct.CT_WORDPROC_DOCM_PUBLIC,
        ct.CT_WORDPROC_DOTX_PUBLIC,
        ct.CT_WORDPROC_DOTM_PUBLIC,

        # Spreadsheet formats
        ct.CT_SPREADSHEET_XLSX_PUBLIC,
        ct.CT_SPREADSHEET_XLSM_PUBLIC,
        ct.CT_SPREADSHEET_XLTX_PUBLIC,
        ct.CT_SPREADSHEET_XLTM_PUBLIC,
        # FIXME: note sure we can honour below types...
#        '*.xlam': ct.CT_SPREADSHEET_XLAM_PUBLIC,
#        '*.xlsb': ct.CT_SPREADSHEET_XLSB_PUBLIC

        # Presentation formats
        ct.CT_PRESENTATION_PPTX_PUBLIC,
        ct.CT_PRESENTATION_PPTM_PUBLIC,
        ct.CT_PRESENTATION_POTX_PUBLIC,
        ct.CT_PRESENTATION_POTM_PUBLIC,
        ct.CT_PRESENTATION_PPSX_PUBLIC,
        ct.CT_PRESENTATION_PPSM_PUBLIC,
        # FIXME: Not sure we can honour below types
#        '*.ppam': ct.CT_PRESENTATION_PPAM_PUBLIC
        )

    output = 'text/plain'

    output_encoding = SITE_CHARSET

    def __init__(self,name=None):
        if name:
            self.__name__=name
        return

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):

        #orig_file = kwargs.get('filename') or 'unknown.xxx'
        mimetype = kwargs.get('mimetype')
        filename = kwargs.get('filename') or 'unknown.xxx'
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0]
        try:
            doc = openxmllib.openXmlDocument(orig, mimetype)
            data.setData(doc.indexableText().encode(SITE_CHARSET, 'replace'))
        except ValueError, e:
            # Crappy data provided to the transform.
            logger.error("Crappy file provided, returning empty text", exc_info=True)
            data.setData('')
        return data

def register():
    return openxml_to_text()
