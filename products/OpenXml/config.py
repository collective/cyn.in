#-*- coding: utf-8 -*-
# $Id: config.py 67354 2008-06-27 09:48:00Z glenfant $
"""Configuration data"""

from openxmllib import contenttypes as ct
import mimetypes

PROJECTNAME = 'OpenXml'
PROJECT_GLOBALS = globals()
I18N_DOMAIN = 'openxml' # FIXME: potentially useless for that kind of product
SITE_CHARSET = 'UTF-8'
TRANSFORM_NAME = 'openxml_to_words'

# New MIME types data for mimetypes_registry
# Source:
# * http://technet2.microsoft.com/Office/en-us/library/e077da98-0216-45eb-b6a7-957f9c510a851033.mspx
office_mimetypes = (
    {'name': 'Office Word 2007 XML macro enabled document',
     'mimetypes': (ct.CT_WORDPROC_DOCM_PUBLIC,),
     'extensions': ('docm',)
     },
    {'name': 'Office Word 2007 XML document',
     'mimetypes': (ct.CT_WORDPROC_DOCX_PUBLIC,),
     'extensions': ('docx',)
    },
    {'name': 'Office Word 2007 XML macro-enabled template',
     'mimetypes': (ct.CT_WORDPROC_DOTM_PUBLIC,),
     'extensions': ('dotm',)
    },
    {'name': 'Office Word 2007 XML template',
     'mimetypes': (ct.CT_WORDPROC_DOTX_PUBLIC,),
     'extensions': ('dotx',)
    },
    {'name': 'Office Powerpoint 2007 macro-enabled XML template',
     'mimetypes': (ct.CT_PRESENTATION_POTM_PUBLIC,),
     'extensions': ('potm',)
    },
    {'name': 'Office Powerpoint 2007 XML template',
     'mimetypes': (ct.CT_PRESENTATION_POTX_PUBLIC,),
     'extensions': ('potx',)
    },
    {'name': 'Office Powerpoint 2007 macro-enabled XML add-in',
     'mimetypes': (ct.CT_PRESENTATION_PPAM_PUBLIC,),
     'extensions': ('ppam',)
     },
    {'name': 'Office Powerpoint 2007 macro-enabled XML show',
     'mimetypes': (ct.CT_PRESENTATION_PPSM_PUBLIC,),
     'extensions': ('ppsm',)
     },
    {'name': 'Office Powerpoint 2007 XML show',
     'mimetypes': (ct.CT_PRESENTATION_PPSX_PUBLIC,),
     'extensions': ('ppsx',)
     },
    {'name': 'Office Powerpoint 2007 macro-enabled XML presentation',
     'mimetypes': (ct.CT_PRESENTATION_PPTM_PUBLIC,),
     'extensions': ('pptm',)
     },
    {'name': 'Office Powerpoint 2007 XML presentation',
     'mimetypes': (ct.CT_PRESENTATION_PPTX_PUBLIC,),
     'extensions': ('pptx',)
     },
    {'name': 'Office Excel 2007 XML macro-enabled add-in',
     'mimetypes': (ct.CT_SPREADSHEET_XLAM_PUBLIC,),
     'extensions': ('xlam',)
     },
    {'name': 'Office Excel 2007 binary workbook (BIFF12)',
     'mimetypes': (ct.CT_SPREADSHEET_XLSB_PUBLIC,),
     'extensions': ('xlsb',)
     },
    {'name': 'Office Excel 2007 XML macro-enabled workbook',
     'mimetypes': (ct.CT_SPREADSHEET_XLSM_PUBLIC,),
     'extensions': ('xlsm',)
     },
    {'name': 'Office Excel 2007 XML workbook',
     'mimetypes': (ct.CT_SPREADSHEET_XLSX_PUBLIC,),
     'extensions': ('xlsx',)
     },
    {'name': 'Office Excel 2007 XML macro-enabled template',
     'mimetypes': (ct.CT_SPREADSHEET_XLTM_PUBLIC,),
     'extensions': ('xltm',)
     },
    {'name': 'Office Excel 2007 XML template',
     'mimetypes': (ct.CT_SPREADSHEET_XLTX_PUBLIC,),
     'extensions': ('xltx',)
     },
    )

for mt in office_mimetypes:
    mt['globs'] = tuple(['*.' + ext for ext in mt['extensions']])
    mt['icon_path'] = '++resource++openxml-icons/%s.png' % mt['extensions'][0]
    # Adding to standard mimetypes
    mimetypes.add_type(mt['mimetypes'][0], '.' + mt['extensions'][0])

del ct
del mimetypes
