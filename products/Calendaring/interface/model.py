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
$Id: model.py,v 1.1.1.1 2004/06/19 14:53:32 dreamcatcher Exp $
"""
from Interface import Interface, Attribute

class ICalendarModel(Interface):
    """ A model for a calendar view """

    start = Attribute('Start Date')
    end = Attribute('End Date')
    resolution = Attribute('Resolution')
    parts = Attribute('Iterator of subdivisions of this model')
    current = Attribute('The model is for the current date')
    today = Attribute('Current date')

    def next():
        """ Creates a model for the next date range """

    def previous():
        """ Creates a model for the previous date range """

    def next_url():
        """ URL for the model of the next date range """

    def previous_url():
        """ URL for the model fo the previous date range """

class IHourModel(ICalendarModel):

    events = Attribute('Iterator for the events of this day')
