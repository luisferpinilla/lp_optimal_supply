import numpy as np
from event_queue import EventQueue
from event_type import EventType
from event import Event


class SimpleSimulator(object):
    def __init__(self, initial_inventory=0.0, lead_time=1, reorder_point=10, quantity_to_order=10, safety_Stock=0.0) -> None:
        super().__init__()
        self.clock = 0
        self.event_queue = EventQueue()
        self.inventory = initial_inventory
        self.lead_time = lead_time
        self.quantity_ordered = 0
        self.reorder_point = reorder_point
        self.quantity_to_order = quantity_to_order
        self.safety_stock = safety_Stock

    @property
    def inventory_position(self) -> int:
        """return the current inventory position

        Returns:
            int: curent inventory position
        """
        return self.inventory + self.quantity_ordered

    def advance_time(self):
        # Obtener la lista de eventos para el time en clock
        event_list = self.event_queue.pop_up_events(self.clock)
        # Para cada evento, ejecutar sus acciones
        for event in event_list:
            if event.get_event_type == EventType.DEMAND:
                self.handle_demand_event(event)
            elif event.get_event_type == EventType.PURCHASE_ORDER:
                pass
            elif event.get_event_type == EventType.ARRIVAL:
                self.handle_arrival_event(event=event)
            else:
                pass

        self.clock += 1

        print(self.clock, ':', 'Inventario:', self.inventory, 'ordered:',
              self.quantity_ordered, 'inventory_position', self.inventory_position)

    def add_demand_event(self, time_clock: int, quantity: int):
        print(f'\tventa por {quantity}')
        event = Event(clock=time_clock, type_of_event=EventType.DEMAND,
                      event_name='Pedido', document={'qty': quantity})
        self.event_queue.add_event(event=event)

    def add_purchase_order(self):

        qty_to_order = self.safety_stock + self.quantity_to_order - self.inventory_position
        print('\tordenando', qty_to_order)
        event = Event(clock=self.clock + self.lead_time,
                      type_of_event=EventType.ARRIVAL,
                      event_name='Pedido',
                      document={'qty': qty_to_order})
        self.quantity_ordered += qty_to_order
        self.event_queue.add_event(event=event)

    def handle_arrival_event(self, event: Event):
        qty = event.get_document['qty']
        print(f'\tLlegada por {qty}')
        self.inventory += qty
        self.quantity_ordered -= qty

    def handle_demand_event(self, event: Event):
        # Obtener inforamciòn del pedido
        qty = event.get_document['qty']
        print(
            f'\tatendiendo venta por {qty} con inventario de {self.inventory}')
        self.inventory -= qty
        if self.inventory_position <= self.reorder_point:
            self.add_purchase_order()


sim = SimpleSimulator(initial_inventory=20, lead_time=3,
                      reorder_point=12, quantity_to_order=25, safety_Stock=5)

for i in range(200):
    sim.event_queue.add_event(Event(clock=i, type_of_event=EventType.DEMAND,
                              event_name='Pedido', document={'qty': np.random.randint(low=1, high=20)}))


for t in range(200):
    sim.advance_time()
