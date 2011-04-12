import BTrees
import datetime
import calendar
from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from p4a.calendar import interfaces

from zope.i18n.locales import locales
from zope.i18n.interfaces import  IUserPreferredLanguages

from ubify.policy import CyninMessageFactory as _


DAYS = [
        _(u'Monday'),
        _(u'Tuesday'),
        _(u'Wednesday'),
        _(u'Thursday'),
        _(u'Friday'),
        _(u'Saturday'),
        _(u'Sunday'),
        ]

MONTHS = [
          _(u'N/A'),
          _(u'January'),
          _(u'February'),
          _(u'March'),
          _(u'April'),
          _(u'May'),
          _(u'June'),
          _(u'July'),
          _(u'August'),
          _(u'September'),
          _(u'October'),
          _(u'November'),
          _(u'December'),
          ]

ONEDAY = datetime.timedelta(days=1)

def hour_time_formatter(self, timeobj):
    """uses zope.i18n.locales to determine hour/min format
    """

    #grab locale from request
    languages = IUserPreferredLanguages(self.request)
    langs = languages.getPreferredLanguages()
    if langs:
        parts = (langs[0].split('-') + [None,None])[:3]
    else:
        parts = (None,None,None)
    locale = locales.getLocale(*parts)

    #create formatted hour minute string
    formatter = locale.dates.getFormatter('time', 'short')
    return formatter.format(timeobj)

def monthweeks(year=None, month=None, daydate=None, firstweekday=None):
    """Return an iterable of week tuples where each element in the week
    tuple is an instance of *datetime.date*.  If *daydate* is ommitted
    then the date chosen is based on the *year* and *month*.

    The following are equivalent.

      >>> from datetime import date
      >>> import calendar

    Using a daydate means the actual day gets ignored.

      >>> list(monthweeks(2006, 2)) == \\
      ...     list(monthweeks(daydate=date(2006, 2, 13)))
      True

    Now lets check out some week day values.

      >>> weeks = list(monthweeks(2006, 2, firstweekday=calendar.SUNDAY))
      >>> weeks[0][0]
      datetime.date(2006, 1, 29)

    The last day of the first week will be February 4, 2006.

      >>> weeks[0][-1]
      datetime.date(2006, 2, 4)

    The first day of the last week will be February 26, 2006.

      >>> weeks[-1][0]
      datetime.date(2006, 2, 26)

    The last day of the last week will be March 4, 2006.

      >>> weeks[-1][-1]
      datetime.date(2006, 3, 4)

    For a month where the last day of the month is the last day of the
    week.

      >>> weeks = list(monthweeks(2006, 9, firstweekday=calendar.SUNDAY))
      >>> weeks[-1][-1]
      datetime.date(2006, 9, 30)

    At one point when you used the last month while retrieving the weeks
    it would send the mechanism into an infinite loop until it raised
    OverflowError.  Lets make sure that doesn't happen again.

      >>> weeks = list(monthweeks(daydate=date(2006, 12, 1),
      ...                         firstweekday=calendar.SUNDAY))
      >>> weeks[0][0]
      datetime.date(2006, 11, 26)
      >>> weeks[-1][-1]
      datetime.date(2007, 1, 6)

    And now for testing another year.

      >>> weeks = list(monthweeks(2007, 1, firstweekday=calendar.SUNDAY))
      >>> weeks[0][0]
      datetime.date(2006, 12, 31)

    One last test, lets cycle through the months over a multi-year period
    and make sure we don't get any OverflowError's.

      >>> count = 0
      >>> for year in range(2002, 2006):
      ...     for month in range(1, 13):
      ...         x = monthweeks(year, month, firstweekday=calendar.SUNDAY)
      ...         x = monthweeks(year, month, firstweekday=calendar.MONDAY)
      ...         count += 1
      >>> count
      48

    """

    if firstweekday == None:
        firstweekday = calendar.firstweekday()

    if firstweekday == 0:
        lastweekday = 6
    else:
        lastweekday = firstweekday - 1

    if daydate is None:
        today = datetime.date.today()
        y = year or today.year
        m = month or today.month
        firstdate = datetime.date(y, m, 1)
    else:
        firstdate = datetime.date(daydate.year,
                                  daydate.month,
                                  1)

    firstcalday = firstdate
    while calendar.weekday(firstcalday.year,
                           firstcalday.month,
                           firstcalday.day) != firstweekday:
        firstcalday -= ONEDAY

    done = False
    weeks = []
    day = firstcalday
    nextday = day + ONEDAY
    weekday = calendar.weekday(day.year, day.month, day.day)

    # see if block at bottom of while block for break conditions
    max = 100
    count = 0
    while count < max:
        if weekday == firstweekday:
            week = []
            weeks.append(week)
        week.append(day)

        if weekday == lastweekday:
            if nextday.month > firstdate.month or \
                  nextday.year > firstdate.year:
                break

        day += ONEDAY
        nextday = day + ONEDAY
        weekday = calendar.weekday(day.year, day.month, day.day)

        count += 1

    if count == max:
        raise OverflowError('Counted %i days for this interval which is '
                            'not possible, something went wrong' % max)

    return (tuple(x) for x in weeks)

class ViewableDay(object):

    def __init__(self, daydate):
        self._eventset = None
        self.extrastyleclass = ''
        self.daydate = daydate

    def add(self, obj):
        # lazily set the eventset as a BTree
        if self._eventset is None:
            self._eventset = BTrees.OOBTree.OOTreeSet()
        self._eventset.insert(obj)

    @property
    def allevents(self):
        if self._eventset is None:
            return []
        all = list(self._eventset)
        return all

    @property
    def events(self):
        return self.allevents[:2]

    @property
    def datestr(self):
        return '%04i-%02i-%02i' % (self.daydate.year,
                                   self.daydate.month,
                                   self.daydate.day)

    @property
    def day(self):
        return self.daydate.day

    @property
    def has_more(self):
        return len(self._eventset) > 2


class MonthView(object):
    """View for a month.
    """

    def __init__(self, context=None, request=None):
        if context is not None:
            self.context = context
        if request is not None:
            self.request = request

        self._cached_weeks = {}
        self._cached_alldays = {}

    def __set_default_day(self, defaultday):
        self._default_day = defaultday
    def __get_default_day(self):
        if hasattr(self, '_default_day'):
            return self._default_day

        if not hasattr(self, 'request'):
            self._default_day = datetime.datetime.today()
            return self._default_day

        year = self.request.form.get('year', None)
        month = self.request.form.get('month', None)

        if month is None:
            return datetime.datetime.today().date()

        year = year or datetime.datetime.today().year
        year = int(year)
        month = int(month)

        self._default_day = datetime.datetime(year, month, 1)

        return self._default_day

    default_day = property(__get_default_day, __set_default_day)

    def __set_firstweekday(self, firstweekday):
        self._firstweekday = firstweekday
    def __get_firstweekday(self):
        first = getattr(self, '_firstweekday', None)
        if first is not None:
            return first
        first = int(self.request.form.get('firstweekday',
                                          calendar.firstweekday()))
        self._firstweekday = first
        return first

    firstweekday = property(__get_firstweekday, __set_firstweekday)

    def standard_week_days(self, firstweekday=None):
        """Return the standard days of the week starting with the day
        that is most appropriate as the start day for the current locale.

        As an example, make sure using 6 as the first work day chooses a
        week starting with Sunday.

          >>> mt = MonthView()
          >>> days = mt.standard_week_days(6)
          >>> days[0]
          {'extrastyleclass': 'first-week-day', 'day': u'Sunday'}
          >>> days[-1]
          {'extrastyleclass': 'last-week-day', 'day': u'Saturday'}
        """

        if firstweekday is None:
            firstweekday = self.firstweekday

        days = [{'day': x,
                 'extrastyleclass': ''} for x in DAYS[firstweekday:]]
        days += [{'day': x,
                  'extrastyleclass': ''} for x in DAYS[0:firstweekday]]

        days[0]['extrastyleclass'] = 'first-week-day'
        days[-1]['extrastyleclass'] = 'last-week-day'

        return days

    def weeks(self, daydate=None, firstweekday=None):
        """Return as a list of of the (partial or full) weeks of the
        month which contains the datetime instance, *day*.  Each item
        in this list is a dict containing a key representing the day
        of the month (or in the case of a day that's not in that month,
        None).

        Start out by making sure we're able to get some weeks for today's
        date.

          >>> import calendar
          >>> mt = MonthView()

        Now lets query known dates.

          >>> from datetime import datetime
          >>> weeks = mt.weeks(datetime(2006, 2, 23), calendar.MONDAY)
          >>> len(weeks)
          5

        First day of the week period should be an outside month day.

          >>> weeks[0]['days'][0].extrastyleclass
          ' outside-month first-week-day'
          >>> weeks[0]['days'][0].day
          30

          >>> weeks[4]['days'][0].extrastyleclass
          ' first-week-day'
          >>> weeks[4]['days'][0].day
          27

        Inspect the last day.  Should be outside the month as well.

          >>> weeks[-1]['days'][-1].extrastyleclass
          ' outside-month last-week-day last-month-day'
          >>> weeks[-1]['days'][-1].day
          5

        Make sure if we use a different weekday things still work.

          >>> weeks = mt.weeks(datetime(2006, 2, 23), calendar.MONDAY)
          >>> weeks[0]['days'][0].day
          30

        """

        if daydate is None:
            daydate = self.default_day

        today = datetime.datetime.today().date()

        if firstweekday is None:
            firstweekday = self.firstweekday

        weeks = self._cached_weeks.get((daydate, firstweekday), None)
        if weeks is not None:
            return weeks

        weektuples = list(monthweeks(daydate=daydate, firstweekday=firstweekday))
        weeks = []
        alldays = {}
        for weekpos, weektuple in enumerate(weektuples):
            week = {'days': []}
            weeks.append(week)

            week['extrastyleclass'] = ''

            if weekpos == 0:
                week['extrastyleclass'] += ' first-week'
            elif weekpos == len(weektuples)-1:
                week['extrastyleclass'] += ' last-week'

            for daypos, weekdate in enumerate(weektuple):
                day = ViewableDay(weekdate)
                week['days'].append(day)

                alldays[weekdate] = day

                if weekdate == today:
                    day.extrastyleclass += ' today'

                if weekdate.month != daydate.month:
                    day.extrastyleclass += ' outside-month'

                if daypos == 0:
                    day.extrastyleclass += ' first-week-day'
                elif daypos == 6:
                    day.extrastyleclass += ' last-week-day'

                if weekdate.month == daydate.month and weekdate.day == 1:
                    day.extrastyleclass += ' first-month-day'

        # find the last day of the month and give it extra style class
        for day in reversed(weeks[-1]['days']):
            if day.day is not None:
                day.extrastyleclass += ' last-month-day'
                break

        self._fill_events(alldays)

        self._cached_weeks[(daydate, firstweekday)] = weeks
        self._cached_alldays[(daydate, firstweekday)] = alldays

        return weeks

    def alldays(self, daydate=None, firstweekday=None):
        if daydate is None:
            daydate = self.default_day

        if firstweekday is None:
            firstweekday = self.firstweekday

        # kick the day generation
        self.weeks(daydate, firstweekday)
        return self._cached_alldays[(daydate, firstweekday)].values()

    @property
    def _events(self):
        events = getattr(self, '_cached_events', None)
        if events is not None:
            return events

        if not hasattr(self, 'context'):
            self._cached_events = []
            return self._cached_events

        default = self.default_day

        start = datetime.datetime(default.year, default.month, 1, 0, 0)

        if default.month < 12:
            end = datetime.datetime(default.year, default.month+1, 1, 23, 59)
            end -= datetime.timedelta(days=1)
        elif default.month == 12:
            end = datetime.datetime(default.year, default.month, 31, 23, 59)

        provider = interfaces.IEventProvider(self.context)

        self._cached_events = provider.gather_events(start, end,
                                                     **self.request.form)
        return self._cached_events

    def _fill_events(self, days, description_length=250, ellipsis='...'):
        for event in self._events:
            dt = datetime.date(event.start.year,
                               event.start.month,
                               event.start.day)
            dtend = datetime.date(event.end.year,
                                  event.end.month,
                                  event.end.day)

            dt_list = dt in days and [dt] or []
            while dt != dtend:
                dt = dt + datetime.timedelta(1)
                if dt in days:
                    # Don't append the date if it's outside the list of visible days
                    dt_list.append(dt)

            for dt in dt_list:
                day = days.get(dt, None)
                if day is None:
                    # basically the date wasn't in our active month so
                    # we set the date to the first day of the month
                    randomday = days.itervalues().next().daydate
                    newdate = datetime.date(randomday.year, randomday.month, 1)
                    day = days[newdate]

                description = event.description

                if len(description)>description_length:
                    description = description[:description_length]
                    l = description.rfind(' ')
                    if l > description_length/2:
                        description = description[:l+1]
                    description += ellipsis

                timespan = '%s to %s %s' % (hour_time_formatter(self, event.start),
                                            hour_time_formatter(self, event.end),
                                            event.timezone)

                event_dict = {'label': hour_time_formatter(self,event.start) + ' ' + event.title,
                              'timespan': timespan,
                              'local_url': event.local_url,
                              'title': event.title,
                              'location': event.location,
                              'description': description,
                              'type': event.type}
                day.add(event_dict)

    def month(self):
        return MONTHS[self.default_day.month]

    def year(self):
        return '%04i' % self.default_day.year

    def _link(self, dt):
        return '%s?year=%s&month=' % (self.context.absolute_url(),
                                      next.year,
                                      next.month)

    def next_month_link(self):
        year = self.default_day.year
        month = self.default_day.month

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

        return '%s?year=%s&month=%s' % (self.context.absolute_url(),
                                        year,
                                        month)

    def prev_month_link(self):
        year = self.default_day.year
        month = self.default_day.month

        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1

        return '%s?year=%s&month=%s' % (self.context.absolute_url(),
                                        year,
                                        month)

    def render_filter(self):
        provider = queryMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, 'eventfilter')
        if provider is None:
            return ''
        provider.update()
        return provider.render()

    def event_creation_link(self, start=None, stop=None):
        provider = interfaces.IEventProvider(self.context)
        return provider.event_creation_link(start, stop)
