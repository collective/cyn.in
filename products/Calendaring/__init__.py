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
$Id: __init__.py,v 1.3 2004/09/17 13:58:25 dreamcatcher Exp $
"""

import os
import sys
from Globals import package_home
from Products.Archetypes.public import *
from Products.CMFCore import utils as cmf_utils
from Products.CMFPlone import utils as plone_utils

from Products.Calendaring.config import *

try:
    # Add our internal copy of icalendar to PYTHONPATH if it's not
    # found in the system.
    import icalendar
except ImportError:
    packages = os.path.join(package_home(globals()), 'lib', 'icalendar')
    log('iCalendar python package not found in your system. '
        'Using internal copy at: %s' % packages)
    sys.path.append(packages)

try:
    # Add our internal copy of dateutil to PYTHONPATH if it's not
    # found in the system.
    import dateutil
except ImportError:
    packages = os.path.join(package_home(globals()), 'lib', 'dateutil')
    log('DateUtil python package not found in your system. '
        'Using internal copy at: %s' % packages)
    sys.path.append(packages)

from Products.Calendaring.marshaller import CalendarMarshaller
from Products.Calendaring.marshaller import EventMarshaller

# Kickstart Extensions.
from Products.Calendaring.Extensions import Install as _Install
del _Install

# If Marshall is available, register the marshallers.
try:
    from Products.Marshall.registry import registerComponent
    registerComponent('calendaring_calendar', 'Calendar Marshaller',
                      CalendarMarshaller)
    registerComponent('calendaring_event', 'Event Marshaller',
                      EventMarshaller)
except ImportError:
    pass

def initialize(context):
    from Products.Calendaring.tools import calendar
    from Products.Calendaring.common import DT2dt

    try:
        from Products.ATContentTypes.content import event
        event.DT2dt = DT2dt
        log('Patching ATContentTypes to return UTC datetime.')
    except ImportError:
        pass

    tools = (calendar.CalendarTool,)

    plone_utils.ToolInit('%s Tools' % PROJECTNAME, 
                         tools=tools, 
                         icon='tool.gif',
                         ).initialize(context)
    del calendar

    from Products.Calendaring.content import calendar

    # register archetypes content with the machinery
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                      PROJECTNAME)
    cmf_utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis).initialize(context)
