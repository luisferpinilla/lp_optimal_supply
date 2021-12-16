import numpy as np
from event_queue import EventQueue
from event_type import EventType

class SimpleSimulator(object):
    def __init__(self, initial_inventory=0.0, lead_time=1, capacity=np.inf)  -> None:
        super().__init__()
        self.clock = 0
        self.event_queue = EventQueue(self.clock)       
        self.initial_inventory=initial_inventory
        self.lead_time = lead_time


    
    def advance_time(self):

        pass

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


