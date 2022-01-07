from sim_utils.sim_utils.simple_simulator import ReorderPointSimpleSimulator
from sim_utils.events import EventType, Event
import numpy as np


sim = ReorderPointSimpleSimulator(initial_inventory=20, lead_time=3,
                      reorder_point=12, quantity_to_order=25, safety_Stock=5)

for i in range(200):
    sim.event_queue.add_event(Event(clock=i, type_of_event=EventType.DEMAND,
                              event_name='Pedido', document={'qty': np.random.randint(low=1, high=20)}))


for t in range(200):
    sim.advance_time()
    

