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
$Id: common.py,v 1.2 2004/09/17 13:58:25 dreamcatcher Exp $
"""

import datetime
from time import localtime
from dateutil.tz import tzutc, gettz
from DateTime import DateTime

__metaclass__ = type

def GMT4dt(date):
    if not isinstance(date, datetime.datetime):
        return 'UTC'
    offset = date.utcoffset()
    minutes = (offset.days*24*60)+(offset.seconds/60)
    if minutes == 0:
        return 'UTC'
    return 'GMT%+03i%02i' % divmod(minutes,60)

def dt2DT(date, tzname=None, local=False):
    """Convert a python datetime to DateTime, in local timezone at the
    specified time.

    >>> import os
    >>> os.environ['TZ'] = 'Brazil/East'
    >>> brt = gettz()

    No timezone information, assume local timezone at the time.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0))
    DateTime('2005/11/07 20:00:00 Universal')

    Provide a default TZID:

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0), tzname='Brazil/East')
    DateTime('2005/11/07 20:00:00 Universal')

    Ask for a local timezone:

    >>> dt2DT(datetime.datetime(2005, 07, 07, 18, 0, 0), local=True)
    DateTime('2005/07/07 18:00:00 GMT-3')

    UTC timezone.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=tzutc()))
    DateTime('2005/11/07 18:00:00 Universal')

    BRST timezone (GMT-2 on this day).

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=brt))
    DateTime('2005/11/07 20:00:00 Universal')

    BRT timezone (GMT-3 on this day).

    >>> dt2DT(datetime.datetime(2005, 07, 07, 18, 0, 0, tzinfo=brt))
    DateTime('2005/07/07 21:00:00 Universal')

    """
    offset = datetime.timedelta(0)
    if isinstance(date, datetime.datetime):
        # Convert to UTC if has a timezone, otherwise assume it's in
        # local time.
        if date.tzinfo is None:
            tz = gettz(tzname)
            date = date.replace(tzinfo=tz)
        if local:
            date = date.astimezone(gettz())
        else:
            date = date.astimezone(tzutc())
    args = date.timetuple()[:6] + (GMT4dt(date),)
    value = DateTime(*args)
    return value

def DT2dt(date):
    """Convert a DateTime to python's datetime in UTC.

    >>> DT2dt(DateTime('2005/11/07 18:00:00 UTC'))
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=tzutc())

    >>> DT2dt(DateTime('2005/11/07 18:00:00 Brazil/East'))
    datetime.datetime(2005, 11, 7, 20, 0, tzinfo=tzutc())

    >>> DT2dt(DateTime('2005/11/07 18:00:00 GMT-2'))
    datetime.datetime(2005, 11, 7, 20, 0, tzinfo=tzutc())

    >>> DT2dt(DateTime('2005/07/07 18:00:00 Brazil/East'))
    datetime.datetime(2005, 7, 7, 21, 0, tzinfo=tzutc())

    >>> DT2dt(DateTime('2005/07/07 18:00:00 GMT-3'))
    datetime.datetime(2005, 7, 7, 21, 0, tzinfo=tzutc())
    """
    value = datetime.datetime.utcfromtimestamp(int(date))
    return value.replace(tzinfo=tzutc())

def toTime(date):
    if isinstance(date, datetime.datetime):
        date = dt2DT(date)
    return date.toZone('UTC').Time()

def toSeconds(td):
    """ Converts a timedelta to an integer
    representing the number of minutes
    """
    return td.seconds + td.days * 86400

def utc_strftime(date, strftime):
    if isinstance(date, datetime.datetime):
        # Convert to UTC if has a timezone, otherwise assume it's in
        # local time.
        if date.tzinfo is None:
            date = date.replace(tzinfo=gettz())
        date = date.astimezone(tzutc())
    elif isinstance(date, DateTime):
        date = date.toZone('UTC')
    return date.strftime(strftime)
