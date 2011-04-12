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
$Id: __init__.py,v 1.1.1.1 2004/06/19 14:53:54 dreamcatcher Exp $
"""

# Make sure we pretend we are in Brazil when running these tests:
from time import time, localtime
from DateTime.DateTime import _findLocalTimeZoneName, DateTime

DateTime._localzone0 = 'GMT-3'
DateTime._localzone1 = 'GMT-2'
DateTime._multipleZones = (DateTime._localzone0 != DateTime._localzone1)
DateTime._isDST = localtime(time())[8]
DateTime._localzone  = DateTime._isDST and DateTime._localzone1 or DateTime._localzone0
