from event_type import EventType
class Event():
    def __init__(self, clock:int, type_of_event:EventType, event_name:str) -> None:
        self.clock = clock
        self.event_type = type_of_event
        self.event_name = event_name
    
    @property
    def get_clock(self)-> int:
        return self.clock

    @property
    def get_event_type(self)->EventType:
        return self.event_type
    
    @property
    def get_event_name(self)->str:
        return self.event_name

        

        