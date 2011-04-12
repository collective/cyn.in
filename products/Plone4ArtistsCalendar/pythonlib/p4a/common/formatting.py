from datetime import datetime
from datetime import timedelta

ONE_DAY = timedelta(days=1)

def day_suffix(day):
    """
    Return correct English suffix (i.e. 'st', 'nd' etc.)

      >>> day_suffix(1)
      u'st'
      >>> day_suffix(6)
      u'th'
      >>> day_suffix(21)
      u'st'
      >>> day_suffix(26)
      u'th'

    """

    if 4 <= day <= 20 or 24 <= day <= 30:
        return u'th'
    else:
        return [u'st', u'nd', u'rd'][day % 10 - 1]

def same_day(*dates):
    """Return True if and only if each date in *dates represents the exact
    same date.

      >>> from datetime import date
      >>> same_day(date(2006, 1, 29))
      True

      >>> same_day(date(2006, 1, 29), date(2006, 1, 29))
      True

      >>> same_day(date(2006, 1, 29), date(2006, 1, 29), date(2006, 3, 22))
      False

    """
    onedate = dates[0]
    for x in dates[1:]:
        if x.year != onedate.year or x.month != onedate.month \
               or x.day != onedate.day:
            return False

    return True

def same_month(*dates):
    """Return True if and only if each date in *dates represents the exact
    same month and year.

      >>> from datetime import date
      >>> same_month(date(2006, 1, 29))
      True

      >>> same_month(date(2006, 1, 29), date(2006, 1, 29))
      True

      >>> same_month(date(2006, 1, 29), date(2006, 1, 29), date(2006, 1, 22))
      True

      >>> same_month(date(2006, 1, 29), date(2006, 5, 29))
      False

    """
    onedate = dates[0]
    for x in dates[1:]:
        if x.year != onedate.year or x.month != onedate.month:
            return False

    return True

def fancy_date_interval(start, end=None):
    """
    If dates share month and year, format it so the month
    is only displayed once.

    >>> from datetime import datetime, timedelta
    >>> fancy_date_interval(datetime(2006, 1, 29), datetime(2006, 1, 30))
    u'Jan 29th-30th, 2006'

    >>> fancy_date_interval(datetime(2006, 1, 29), datetime(2006, 2, 1))
    u'Jan 29th-Feb 1st, 2006'

    >>> fancy_date_interval(datetime(2006, 1, 29), datetime(2006, 1, 29))
    u'Jan 29th, 2006'

    >>> fancy_date_interval(datetime.today())
    u'Today'

    >>> fancy_date_interval(datetime.today()-timedelta(days=1))
    u'Yesterday'

    """

    if end is None or same_day(start, end):
        if same_day(start, datetime.today()):
            return u'Today'
        if same_day(start, datetime.today() - ONE_DAY):
            return u'Yesterday'
        return u'%s %s%s, %s' % (start.strftime("%b"),
                                 start.day,
                                 day_suffix(start.day),
                                 start.year)
    elif same_month(start, end):
        return u'%s %s%s-%s%s, %s' % (start.strftime("%b"),
                                      start.day,
                                      day_suffix(start.day),
                                      end.day,
                                      day_suffix(end.day),
                                      start.year)
    else:
        return u'%s %s%s-%s %s%s, %s' % (start.strftime("%b"),
                                         start.day,
                                         day_suffix(start.day),
                                         end.strftime("%b"),
                                         end.day,
                                         day_suffix(end.day),
                                         start.year)

def fancy_time_amount(v, show_legend=True):
    """Produce a friendly representation of the given time amount.  The
    value is expected to be in seconds as an int.

      >>> fancy_time_amount(391)
      u'06:31 (mm:ss)'

      >>> fancy_time_amount(360)
      u'06:00 (mm:ss)'

      >>> fancy_time_amount(6360)
      u'01:46:00 (hh:mm:ss)'

      >>> fancy_time_amount(360, False)
      u'06:00'

    """

    remainder = v
    hours = remainder / 60 / 60
    remainder = remainder - (hours * 60 * 60)
    mins = remainder / 60
    secs = remainder - (mins * 60)

    if hours > 0:
        val = u'%02i:%02i:%02i' % (hours, mins, secs)
        legend =  u' (hh:mm:ss)'
    else:
        val = u'%02i:%02i' % (mins, secs)
        legend = u' (mm:ss)'

    if show_legend:
        full = val + legend
    else:
        full = val

    return full

def fancy_data_size(v):
    """Produce a friendly reprsentation of the given value.  The value
    Is expected to be in bytes as an int or long.
    
      >>> fancy_data_size(54)
      u'54 B'
      
      >>> fancy_data_size(37932)
      u'37.0 KB'

      >>> fancy_data_size(1237932)
      u'1.2 MB'
    
      >>> fancy_data_size(2911237932)
      u'2.7 GB'
    """
    
    suffix = 'B'
    
    format = u'%i %s'
    if v > 1024:
        suffix = 'KB'
        v = float(v) / 1024.0
        format = u'%.1f %s'
    
    if v > 1024:
        suffix = 'MB'
        v = v / 1024.0
    
    if v > 1024:
        suffix = 'GB'
        v = v / 1024.0

    return format % (v, suffix)

def _test():
    import doctest
    doctest.testmod()
    
if __name__ == "__main__":
    _test()
