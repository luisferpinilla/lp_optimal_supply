from event import Event
from sim_utils.event_type import EventType



class EventQueue():
    def __init__(self, initial_clock=0) -> None:
        self.current_clock = initial_clock
        self.queue = dict()

    def add_event(self, time_clock:int, event_name:str):
        
        event = Event(clock=time_clock,type_of_event=EventType.ARRIVAL, event_name=event_name)

        if time_clock <= self.current_clock:
            raise Exception('you cannot create an event in the past')
        else:
            if not time_clock in self.queue.keys():
                self.queue[time_clock] = list()
        
            self.queue[time_clock].append(event)

    def pop_up_events(self)->tuple:
        event_list_times = self.queue.keys()
        event_list_times = sorted(event_list_times, reverse=False)
        if len(event_list_times)>0:
            event = self.queue[event_list_times[0]]
            self.queue.pop(event)

        return 
