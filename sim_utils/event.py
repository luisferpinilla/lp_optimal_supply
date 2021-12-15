from event_type import EventType
class Event():
    def __init__(self, clock:int, type_of_event:EventType, event_name:str) -> None:
        self.clock = clock
        self.event_type = type_of_event
        self.event_name = event_name
    
    @property
    def get_clock(self)-> int:
        """get the time when the event occurs

        Returns:
            int: time when the event occurs
        """
        return self.clock

    @property
    def get_event_type(self)->EventType:
        """Get the event type

        Returns:
            EventType: Type of the event
        """
        return self.event_type
    
    @property
    def get_event_name(self)->str:
        """get the name of the event

        Returns:
            str: event name
        """
        return self.event_name

        

        