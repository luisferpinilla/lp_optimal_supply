import numpy as np
from sim_utils import event_queue as eq


class PeriodicInventorySim():
    def __init__(self, oul_level:float,  review_period:int, initial_clock=0, seed=0) -> None:

        '''
        Periodic inventtory sim places an order every T periods, the order placed is equal to the
        OUL_level - Inventory_Position and the expected arrival time is lt
        PARAMETERS:
        oul_level: Ordert up to level
        review_period: integer. positive number, periods between orders
        initial_clock: integer. initialices the simulation clock in an especific time
        seed: random numpy seed used to generate the next event
        '''
        self.oul = oul_level
        self.review_period = review_period
        self.clock = initial_clock
        # event queue
        self.event_queue = eq.EventQueue()
        

    def add_event(self, clock_time:int, event_name):
        '''
        Adds an event to a queue manager
        parameters:
        clock_time: time when the event will be triggered
        event_name: a name used to identify an event
        '''
        self.event_queue.add_event(time_clock=clock_time, event_name=event_name)

    def advace_time(self)->eq.EventQueue:
        '''
        move the clock tick fordware
        '''

        event = self.event_queue.pop_up_event()

        

        

    def period_review_event_handler(self):
        pass

