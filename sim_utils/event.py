from event_type import EventType
class Event():
    def __init__(self, clock:int, type_of_event:EventType, event_name:str) -> None:
        self.clock = clock
        self.event_type = type_of_event
        self.event_name = event_name
    

        