# Calendaring is a simple CMF/Plone calendaring implementation.
# Copyright (C) 2004 Enfold Systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
$Id: config.py,v 1.2 2004/10/19 01:59:55 nateaune Exp $
"""


import logging
from Products.CMFCore.permissions import AddPortalContent

PROJECTNAME = 'Calendaring'
TOOLIDS = ['portal_calendar']
GLOBALS = globals()
ADD_CONTENT_PERMISSION = AddPortalContent
INSTALL_CALENDAR_TYPE = False
logger = logging.getLogger(PROJECTNAME)

def log(msg, level=logging.DEBUG):
    logger.log(level=level, msg=msg)
