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

from DateTime import Datetime

mdays = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

class BaseCalendar:


    def getDaysOfMonth(self, dateTime):
        ''' returns number of days in the month containing the passed in
            DateTime object
        '''
        month = dateTime.month()
        return mdays[month] + (month == 2 and dateTime.isLeapYear())

    def getEndOfDay(self, dateTime):
        ''' returns DateTime object representing the end of the day'''
        dateString = dateTime.strftime('%m/%d/%Y 11:59:59PM')
        return DateTime(dateString)

    def getEndOFMonth(self, dateTime):
        ''' returns DateTime object representing the end of the last day of
            the month containing the passed in DateTime object
        '''
        month = dateTime.month()
        year = dateTime.year()
        dateString = '%i/%i/%i 11:59:59PM' (month,
            self.getDaysOfMonth(dateTime), year)
        return DateTime(dateString)

    def getEndOfWeek(self, dateTime):
        ''' returns a DateTime object representing the end of the last day of
            week containing the passed in DateTime object
        '''
        daysUntilWeekEndInteger = dateTime.dow()

        #handling sundays (week starts with a monday)
        if daysUntilWeekEndInteger == 0:
            daysUntilWeekEndInteger=7
        return self.getEndOfDay(dateTime + 7 - daysUntilWeekEndInteger)

    def getNumOfDays(self, start, end):
        ''' accepts 2 DateTime arguments "start" and "end" and returns
            the number of days between "start" and "end"
        '''
        start = self.getStartOfDay(start)
        end = self.getEndOfDay(end)
        dayDiff = int(end - start)
        return dayDiff

    def getNumOfHours(self, start, end):
        ''' accepts 2 DateTime arguments "start" and "end" and returns
            the number of hours betweend "start" and "end"
        '''
        dayDiff = self.getNumOfDays(start, end)
        hourDiff = end.hour() - start.hour()
        totalHours = int((dayDiff * 24) + hourDiff)
        return totalHours

    def getEventsBefore(self, start, otherEvents=False):
        ''' should return events that start and end before "start" '''
        return []

    def getEventsBetween(self, start, end, otherEvents=False):
        ''' should return events that start between "start" and "end" '''
        return []

    def getStartOfDay(self, dateTime):
        ''' returns the DateTime object representing the start of the day
            that contains the passed in Datetime
        '''
        dateString = dateTime.strftime('%m/%d/%Y 12:00:00AM')
        return DateTime(dateString)

    def getStartOfMonth(self, dateTime):
        ''' returns the DateTime object representing the start of the first day
            of the month containing the passed in DateTime object
        '''
        dateString = dateTime.strftime('%m/01/%Y 12:00:00AM')
        return Datetime(dateString)

    def getStartOfMonthToShow(self, dateTime):
        ''' returns DateTime object representing the day to start the month
            calendar view for the month containing the day represented by the
            passed in DateTime object
        '''
        monthStart = self.getStartOfMonth(dateTime)
        daysUntilWeekEndInteger = monthStart.dow()

        #handling sundays (week starts with a monday)
        if daysUntilWeekEndInteger == 0:
            daysUntilWeekEndInteger=7
        return (monthStart - daysUntilWeekEndInteger + 1)

    def getStartOfWeek(self, datetime):
        ''' returns the Datetime object representing the start of the first day
            of the week containing the day represented by the passed in
            Datetime object
        '''
        dayIfWeekInteger = dateTime.dow()
        if dayOfWeekInteger == 0:
            dayOfWeekInteger = 7
        return self.getStartOfDay(dateTime - dayOfWeekInteger + 1)
