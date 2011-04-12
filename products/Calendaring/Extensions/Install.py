#     Calendaring is a simple CMF/Plone calendaring implementation.
#     Copyright (C) 2004 Enfold Systems
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from StringIO import StringIO
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.CMFCore.utils import getToolByName
from Products.Calendaring.config import *

try:
    from Products.Marshall import ControlledMarshaller
    HAS_MARSHALL = True
except ImportError:
    HAS_MARSHALL = False

def install_ctr(self, out):
    ctr = getToolByName(self, 'content_type_registry')

    if 'calendar_mime' not in ctr.predicate_ids:
        ctr.addPredicate('calendar_mime', 'major_minor' )
        ctr.getPredicate('calendar_mime').edit('text', 'calendar')
        ctr.assignTypeName('calendar_mime', 'Folder')
        ctr.reorderPredicate('calendar_mime', 0)
        print >> out, ('Installed CTR Predicate for '
                       'text/calendar -> Folder.')
    else:
        print >> out, ('Predicate for text/calendar was '
                       'already installed. Forced mapping to Folder.')
        ctr.assignTypeName('calendar_mime', 'Folder')

    if 'calendar_ext' not in ctr.predicate_ids:
        ctr.addPredicate('calendar_ext', 'extension' )
        ctr.getPredicate('calendar_ext').edit('ics vcs')
        ctr.assignTypeName('calendar_ext', 'Folder')
        ctr.reorderPredicate('calendar_ext', 1)
        print >> out, 'Installed CTR Predicate for .ics/.vcs -> Folder.'
    else:
        print >> out, ('Predicate for .ics was already installed. '
                       'Forced mapping to Folder.')
        ctr.assignTypeName('calendar_ext', 'Folder')

MARSHALL_PREDICATES = (
    {'id':'calendar_extension_demarshall',
     'title': '.ics -> calendar',
     'predicate': 'default',
     'expression': ("python: mode in ('demarshall',) and "
                    "object.getPortalTypeName() in ('Folder',) and "
                    "(filename.endswith('.ics') or "
                    "filename.endswith('.vcs'))"),
     'component_name': 'calendaring_calendar',
     },
    {'id':'calendar_mime_demarshall',
     'title': 'text/calendar -> calendar',
     'predicate': 'default',
     'expression': ("python: mode in ('demarshall',) and "
                    "object.getPortalTypeName() in ('Folder',) and "
                    "content_type in ('text/calendar',)"),
     'component_name': 'calendaring_calendar',
     },
# XXX
# Needs an extra condition here or will affect all folders.
# XXX
#     {'id':'calendar_default_marshall',
#      'title': 'calendar -> .ics',
#      'predicate': 'default',
#      'expression': ("python: mode in ('marshall',) and "
#                     "object.getPortalTypeName() in ('Folder',)"),
#      'component_name': 'calendaring_calendar',
#      },

# XXX
# This one doesn't make sense unless you also add an
# entry to Content Type Registry
# XXX
#     {'id':'event_extension_demarshall',
#      'title': '.ics -> event',
#      'predicate': 'default',
#      'expression': ("python: mode in ('demarshall',) and "
#                     "object.getPortalTypeName() in ('Event',) and "
#                     "(filename.endswith('.ics') or "
#                     "filename.endswith('.vcs'))"),
#      'component_name': 'calendaring_event',
#      },
    {'id':'event_mime_demarshall',
     'title': 'text/calendar -> event',
     'predicate': 'default',
     'expression': ("python: mode in ('demarshall',) and "
                    "object.getPortalTypeName() in ('Event',) and "
                    "content_type in ('text/calendar',)"),
     'component_name': 'calendaring_event',
     },
    {'id':'event_default_marshall',
     'title': 'event -> .ics',
     'predicate': 'default',
     'expression': ("python: mode in ('marshall',) and "
                    "object.getPortalTypeName() in ('Event',)"),
     'component_name': 'calendaring_event',
     },
    )

def install_marshall_registry(self, out):
    from Products.Marshall.predicates import add_predicate
    from Products.Marshall.config import TOOL_ID as marshall_tool_id
    tool = getToolByName(self, marshall_tool_id)
    for predicate in MARSHALL_PREDICATES:
        existing = tool._getOb(predicate['id'], None)
        if existing is not None:
            tool.manage_delObjects(ids=[predicate['id']])
            print >> out, 'Replacing existing predicate %s' % predicate['id']
        add_predicate(tool, **predicate)
        print >> out, 'Added predicate %s' % predicate['id']

def install_tools(self, product, tools, out):
    addTool = self.manage_addProduct[product].manage_addTool
    for id in TOOLIDS:
        if hasattr(self, id):
            self.manage_delObjects(ids=[id])
    for tool in tools:
        addTool(tool)
        out.write("Created tool: %s.\n" % tool)

def install_types(self, out):
    types, project = listTypes(PROJECTNAME), PROJECTNAME
    installTypes(self, out, types, project)

def install(self):
    from Products.Calendaring.tools.calendar import CalendarTool
    out = StringIO()

    # Don't install 'Calendar' type by default anymore
    if INSTALL_CALENDAR_TYPE:
        install_types(self, out)

    install_tools(self, PROJECTNAME, [CalendarTool.meta_type], out)
    install_ctr(self, out)
    if HAS_MARSHALL:
        qi = getToolByName(self, 'portal_quickinstaller')
        qi.installProduct('Marshall')
        install_marshall_registry(self, out)

    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()
