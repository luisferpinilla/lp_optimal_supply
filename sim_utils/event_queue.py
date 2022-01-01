from event import Event
from event_type import EventType



class EventQueue():
    def __init__(self) -> None:
        self.queue = dict()

    def add_event(self, time_clock:int, event_name:str, event_type:EventType):
        """Add an event to event queue

        Args:
            time_clock (int): time when the event will ocuur
            event_name (str): name of the event
            event_type (EventType): event type: Arrival/delivery
        """
        event = Event(clock=time_clock,type_of_event=event_type, event_name=event_name)
        if not time_clock in self.queue.keys():
            self.queue[time_clock] = list()
        
        self.queue[time_clock].append(event)

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
