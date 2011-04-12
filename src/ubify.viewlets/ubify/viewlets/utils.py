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
import re
from types import ClassType
from os.path import join, abspath, split
from cStringIO import StringIO
from PIL import Image

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer

import zope.interface
from zope.interface import implementedBy
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility

import OFS
import Globals
from Acquisition import aq_base, aq_inner, aq_parent
from DateTime import DateTime
from Products.Five import BrowserView as BaseView
from Products.Five.bridge import fromZ2Interface
from Products.CMFCore.utils import ToolInit as CMFCoreToolInit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.Translatable import ITranslatable
import transaction

from Products.PageTemplates.GlobalTranslationService import \
     getGlobalTranslationService
from AccessControl import allow_module
from AccessControl import ModuleSecurityInfo

# Canonical way to get at CMFPlone directory
PACKAGE_HOME = Globals.package_home(globals())
WWW_DIR = join(PACKAGE_HOME, 'www')


# Settings for member image resize quality
PIL_SCALING_ALGO = Image.ANTIALIAS
PIL_QUALITY = 88
MEMBER_IMAGE_SCALE = (75, 100)
IMAGE_SCALE_PARAMS = {'scale': MEMBER_IMAGE_SCALE,
                      'quality': PIL_QUALITY,
                      'algorithm': PIL_SCALING_ALGO,
                      'default_format': 'PNG'}

_marker = []

def scale_image(image_file, max_size=None, default_format=None):
    """Scales an image down to at most max_size preserving aspect ratio
    from an input file

        >>> import Products.CMFPlone
        >>> import os
        >>> from StringIO import StringIO
        >>> from Products.CMFPlone.utils import scale_image
        >>> from PIL import Image

    Let's make a couple test images and see how it works (all are
    100x100), the gif is palletted mode::

        >>> plone_path = os.path.dirname(Products.CMFPlone.__file__)
        >>> pjoin = os.path.join
        >>> path = pjoin(plone_path, 'tests', 'images')
        >>> orig_jpg = open(pjoin(path, 'test.jpg'), 'rb')
        >>> orig_png = open(pjoin(path, 'test.png'), 'rb')
        >>> orig_gif = open(pjoin(path, 'test.gif'), 'rb')

    We'll also make some evil non-images, including one which
    masquerades as a jpeg (which would trick OFS.Image)::

        >>> invalid = StringIO('<div>Evil!!!</div>')
        >>> sneaky = StringIO('\377\330<div>Evil!!!</div>')

    OK, let's get to it, first check that our bad images fail:

        >>> scale_image(invalid, (50, 50))
        Traceback (most recent call last):
        ...
        IOError: cannot identify image file
        >>> scale_image(sneaky, (50, 50))
        Traceback (most recent call last):
        ...
        IOError: cannot identify image file

    Now that that's out of the way we check on our real images to make
    sure the format and mode are preserved, that they are scaled, and that they
    return the correct mimetype::

        >>> new_jpg, mimetype = scale_image(orig_jpg, (50, 50))
        >>> img = Image.open(new_jpg)
        >>> img.size
        (50, 50)
        >>> img.format
        'JPEG'
        >>> mimetype
        'image/jpeg'

        >>> new_png, mimetype = scale_image(orig_png, (50, 50))
        >>> img = Image.open(new_png)
        >>> img.size
        (50, 50)
        >>> img.format
        'PNG'
        >>> mimetype
        'image/png'

        >>> new_gif, mimetype = scale_image(orig_gif, (50, 50))
        >>> img = Image.open(new_gif)
        >>> img.size
        (50, 50)
        >>> img.format
        'GIF'
        >>> img.mode
        'P'
        >>> mimetype
        'image/gif'

    We should also preserve the aspect ratio by scaling to the given
    width only unless told not to (we need to reset out files before
    trying again though::

        >>> orig_jpg.seek(0)
        >>> new_jpg, mimetype = scale_image(orig_jpg, (70, 100))
        >>> img = Image.open(new_jpg)
        >>> img.size
        (70, 70)

        >>> orig_jpg.seek(0)
        >>> new_jpg, mimetype = scale_image(orig_jpg, (70, 50))
        >>> img = Image.open(new_jpg)
        >>> img.size
        (50, 50)

    """
    if max_size is None:
        max_size = IMAGE_SCALE_PARAMS['scale']
    if default_format is None:
        default_format = IMAGE_SCALE_PARAMS['default_format']
    # Make sure we have ints
    size = (int(max_size[0]), int(max_size[1]))
    # Load up the image, don't try to catch errors, we want to fail miserably
    # on invalid images
    image = Image.open(image_file)
    # When might image.format not be true?
    format = image.format
    mimetype = 'image/%s'%format.lower()
    cur_size = image.size
    # from Archetypes ImageField
    # consider image mode when scaling
    # source images can be mode '1','L,','P','RGB(A)'
    # convert to greyscale or RGBA before scaling
    # preserve palletted mode (but not pallette)
    # for palletted-only image formats, e.g. GIF
    # PNG compression is OK for RGBA thumbnails
    original_mode = image.mode
    if original_mode == '1':
        image = image.convert('L')
    elif original_mode == 'P':
        image = image.convert('RGBA')
    # Rescale in place with an method that will not alter the aspect ratio
    # and will only shrink the image not enlarge it.
    image.thumbnail(size, resample=IMAGE_SCALE_PARAMS['algorithm'])    
    if original_mode == 'P' and format in ('GIF', 'PNG'):
        image = image.convert('P')
    # Save
    new_file = StringIO()
    image.save(new_file, format, quality=IMAGE_SCALE_PARAMS['quality'])
    new_file.seek(0)
    # Return the file data and the new mimetype
    return new_file, mimetype

def scaleandcrop_image(image_file, max_size=None, default_format=None):    
    if max_size is None:
        max_size = IMAGE_SCALE_PARAMS['scale']
    if default_format is None:
        default_format = IMAGE_SCALE_PARAMS['default_format']
    # Make sure we have ints
    size = (int(max_size[0]), int(max_size[1]))
    # Load up the image, don't try to catch errors, we want to fail miserably
    # on invalid images
    image = Image.open(image_file)
    # When might image.format not be true?
    format = image.format
    mimetype = 'image/%s'%format.lower()
    cur_size = image.size
    # from Archetypes ImageField
    # consider image mode when scaling
    # source images can be mode '1','L,','P','RGB(A)'
    # convert to greyscale or RGBA before scaling
    # preserve palletted mode (but not pallette)
    # for palletted-only image formats, e.g. GIF
    # PNG compression is OK for RGBA thumbnails
    original_mode = image.mode
    if original_mode == '1':
        image = image.convert('L')
    elif original_mode == 'P':
        image = image.convert('RGBA')
    
    src_width,sr_height = image.size
    src_width, src_height = image.size
    src_ratio = float(src_width) / float(src_height)
    dst_width = max_size[0]
    dst_height = max_size[1]
    dst_ratio = float(dst_width) / float(dst_height)

    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = float(src_height - crop_height) / 3
    
    image = image.crop((int(x_offset), int(y_offset), int(x_offset)+int(crop_width), int(y_offset)+int(crop_height)))
    image = image.resize((dst_width, dst_height), Image.ANTIALIAS)    # preserve palletted mode for GIF and PNG
    if original_mode == 'P' and format in ('GIF', 'PNG'):
        image = image.convert('P')
    # Save
    new_file = StringIO()
    image.save(new_file, format, quality=IMAGE_SCALE_PARAMS['quality'])
    new_file.seek(0)
    # Return the file data and the new mimetype
    return new_file, mimetype

def getObjectModifiedBy(object):
    
    portal = object.portal_url.getPortalObject()
    objModifiedBy = None
    try:
        object = object.getObject()
    except AttributeError:
        object = object
        
    if object.hasProperty('modifiedby') == 0:
        objModifiedBy = object.getOwner().getUserName()
    else:
        strmodifiedby = object.modifiedby
        objModifiedBy = strmodifiedby
        
    return objModifiedBy

