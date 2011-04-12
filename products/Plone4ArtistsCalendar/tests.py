from unittest import TestSuite

def test_suite():
    suite = TestSuite()
    
    for x in ('p4a.calendar.browser.tests',
              'p4a.plonecalendar.tests',
              'p4a.subtyper.tests',):
        m = __import__(x, (), (), x)
        try:
            suite.addTest(m.test_suite())
        except AttributeError, e:
            raise AttributeError(m.__name__+': '+str(e))
        
    return suite
