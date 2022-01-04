from enum import Enum

class EventType(Enum):
    """Type of event

    Args:
        Enum ([type]): describes event
    """
    DEMAND=0
    PURCHASE_ORDER=1
    ARRIVAL=2
    REVIEW=3


class Event():
    """Contains an event including information about when occurs and witch object is attached
    """
    def __init__(self, clock:int, type_of_event:EventType, event_name:str, document=None) -> None:
        self.clock = clock
        self.event_type = type_of_event
        self.event_name = event_name
        self.document = document
    
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

    @property
    def get_document(self)->object:
        """returns a document attached

        Returns:
            object: Document attached to the event
        """
        return self.document


class EventQueue():
    """Event Queue that uses Events and put them togetter
    """
    def __init__(self) -> None:
        self.queue = dict()

    def add_event(self, event:Event):
        """add an event to the queue

        Args:
            event (Event): event to add
        """
        if not event.get_clock in self.queue.keys():
            self.queue[event.get_clock] = list()
        
        self.queue[event.get_clock].append(event)

    def pop_up_events(self, time_clock:int)->list:
        """returns an event list at the time_clock
        Args:
            time_clock (int): time_clock when the events occurs

        Returns:
            list: list of events that occurs
        """
        if time_clock in self.queue.keys():
            eventos = self.queue[time_clock]
            # sacar los eventos de la lista
            return self.queue.pop(time_clock, list())
        else:
            return list()

    @property
    def has_more_events(self)->int:
        return len(self.queue)        
