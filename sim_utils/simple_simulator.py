import numpy as np
from event_queue import EventQueue
from event_type import EventType

class SimpleSimulator(object):
    def __init__(self, initial_inventory=0.0, lead_time=1, capacity=np.inf)  -> None:
        super().__init__()
        self.clock = 0
        self.event_queue = EventQueue()       
        self.initial_inventory=initial_inventory
        self.lead_time = lead_time


    
    def advance_time(self):
        # Obtener la lista de eventos para el time en clock
        event_list = self.event_queue.pop_up_events(self.clock)
        # Para cada evento, ejecutar sus acciones
        for event in event_list:
            if event:
                print('\t',event.get_event_type, event.get_event_name)

        self.clock += 1

    def add_purchase_order(self, time:int, quantity:float):
        """add a purchase order to the event queue.

        Args:
            time (int): time when the purchase order is created
            quantity (float): cuantity ordered
        """
        self.event_queue.add_event(time, event_name='PO', event_type=EventType.PURCHASE_ORDER)

        pass

    def handle_purchase_order(self):
        pass

    def handle_demand_event(self):
        pass


sim = SimpleSimulator(initial_inventory=100, lead_time=5)
sim.event_queue.add_event(time_clock=10, event_name='test llegada 10', event_type=EventType.PURCHASE_ORDER)
sim.event_queue.add_event(time_clock=12, event_name='test llegada 12', event_type=EventType.ARRIVAL)
sim.event_queue.add_event(time_clock=14, event_name='test llegada 14', event_type=EventType.ARRIVAL)
sim.event_queue.add_event(time_clock=11, event_name='test llegada 11', event_type=EventType.ARRIVAL)

for t in range(20):
    sim.advance_time()


