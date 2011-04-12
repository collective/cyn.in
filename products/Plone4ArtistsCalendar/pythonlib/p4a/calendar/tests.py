class EventProviderTestMixin(object):
    """Tests that the EventProvider API is correctly implemented
    Since IEventProvider has no implementation in this product
    these tests must be mixed in with a text that provides an
    event provider as self.provider in the setUp.
    """
    
    def test_gather_all(self):
        all_events = list(self.provider.all_events())
        gathered_events = list(self.provider.gather_events())

        self.failUnlessEqual(len(all_events), len(gathered_events))
        
        for i in all_events:
            exists = 0
            for j in gathered_events:
                if (i.title == j.title and 
                    i.start == j.start and
                    i.end   == j.end):
                    exists = True
                    break
            self.failUnless(exists, "Event lists are not equal")
                    
        
    def test_gather_future(self):
        all_events = list(self.provider.all_events())
        if len(all_events) < 2:
            raise ValueError(
                "This test requires you to have at least two events "
                "with non overlapping start and end times.")
        
        # Pick out all the end datetimes for the events:
        end_times = [x.end for x in all_events]
        end_times.sort()
        # Pick an end date in the middle:
        dt = end_times[len(all_events)/2]
        
        # Get all dates starting at or after this middle date
        gathered_events = list(self.provider.gather_events(start=dt))
        
        for i in all_events:
            # The event should be returned if the start_date is above
            # or equal the date given as a start date.
            # (It may be expected that events that start before the expected
            # date but continues after it should be included, but this is
            # generally more complicated).
            should_exist = i.end >= dt
            
            # Now check if it exists:
            exists = False
            for j in gathered_events:
                if (i.title == j.title and 
                    i.start == j.start and
                    i.end   == j.end):
                    exists = True
                    break
            self.failUnlessEqual(exists, should_exist, 
                                 "Event lists are not as expected")
        
    def test_title_search(self):
        # This test assumes at least one event, but not all of them
        # has the text "event" in the title.
        all_events = list(self.provider.all_events())
        gathered_events = list(self.provider.gather_events(title='event'))

        # Make sure something is returned
        self.failUnless(gathered_events)
        # But not everything
        self.failIfEqual(len(all_events), len(gathered_events))
        
        for i in gathered_events:
            self.failIf(i.title.lower().find('event') == -1)
        
