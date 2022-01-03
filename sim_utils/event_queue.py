from event import Event
from event_type import EventType


@DeprecationWarning
class EventQueue():
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
