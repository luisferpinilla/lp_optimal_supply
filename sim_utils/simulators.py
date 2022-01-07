import numpy as np
from sim_utils.events import EventType, Event, EventQueue


class ReorderPointSimpleSimulator(object):
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

    @property
    def inventory_on_hand(self) -> int:
        """return the inventory on hand. If there are backorder, it returns 0

        Returns:
            int: inventory on hand
        """
        return max(self.inventory, 0)

    @property
    def backorder(self) -> int:
        """returns the backorder when the inventory on hand < 0

        Returns:
            int: Backorder
        """
        return min(self.inventory, 0)

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

        print(self.clock, ':', 'Inventario on hand:', self.inventory_on_hand, 'Backorder:', self.backorder,  'ordered:', self.quantity_ordered, 'inventory_position', self.inventory_position)

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


class ReviewPeriodicSimpleSimulator(object):
    def __init__(self, initial_inventory=0.0, lead_time=1, order_up_to_level=100, review_period=3, initial_time_po=0) -> None:
        super().__init__()
        self.clock = 0
        self.event_queue = EventQueue()
        self.inventory = initial_inventory
        self.lead_time = lead_time
        self.quantity_ordered = 0
        self.order_up_to_level = order_up_to_level
        self.review_period = review_period
        self.statistics = {'clock': [], 'Inventory_on_hand':[], 'backorder': [], 'Quantity_ordered': [], 'inventory_position':[] }
        # agregar el primer evento de revisión
        self.event_queue.add_event(Event(clock=initial_time_po, type_of_event=EventType.PURCHASE_ORDER, event_name='Initial PO'))


    @property
    def inventory_position(self) -> int:
        """return the current inventory position

        Returns:
            int: curent inventory position
        """
        return self.inventory + self.quantity_ordered

    @property
    def inventory_on_hand(self) -> int:
        """return the inventory on hand. If there are backorder, it returns 0

        Returns:
            int: inventory on hand
        """
        return max(self.inventory, 0)

    @property
    def backorder(self) -> int:
        """returns the backorder when the inventory on hand < 0

        Returns:
            int: Backorder
        """
        return min(self.inventory, 0)*-1

    @property
    def statistics_dataframe(self)->pd.DataFrame:
        df = pd.DataFrame(self.statistics)
        df['oul'] = self.order_up_to_level
        return df

    def advance_time(self):
        
       
        # Obtener la lista de eventos para el time en clock
        event_list = self.event_queue.pop_up_events(self.clock)
        # Para cada evento, ejecutar sus acciones
        for event in event_list:
            if event.get_event_type == EventType.DEMAND:
                self.handle_demand_event(event=event)
            elif event.get_event_type == EventType.PURCHASE_ORDER:
                self.handle_review_period_event(event=event)
            elif event.get_event_type == EventType.ARRIVAL:
                self.handle_arrival_event(event=event)
            else:
                pass

        self.clock += 1

        print(self.clock, ':', 'Inventario on hand:', self.inventory_on_hand, 'Backorder:', self.backorder,  'ordered:', self.quantity_ordered, 'inventory_position', self.inventory_position)
        self.statistics['clock'].append(self.clock) 
        self.statistics['Inventory_on_hand'].append(self.inventory_on_hand) 
        self.statistics['backorder'].append(self.backorder) 
        self.statistics['Quantity_ordered'].append(self.quantity_ordered) 
        self.statistics['inventory_position'].append(self.inventory_position) 

    def add_demand_event(self, time_clock: int, quantity: int):
        print(f'\tventa por {quantity}')
        event = Event(clock=time_clock, type_of_event=EventType.DEMAND,
                      event_name='Pedido', document={'qty': quantity})
        self.event_queue.add_event(event=event)

    def add_purchase_order(self, qty_to_order):
       
        print('\tordenando', qty_to_order)
        event = Event(clock=self.clock + self.lead_time,
                      type_of_event=EventType.ARRIVAL,
                      event_name='Pedido',
                      document={'qty': qty_to_order})
        self.quantity_ordered += qty_to_order
        self.event_queue.add_event(event=event)

    
    def handle_review_period_event(self, event: Event):
        # Place a new purchase order
        print('\tReview Period')
        if (self.inventory_position < self.order_up_to_level):
            qty = self.order_up_to_level - self.inventory_position
            self.add_purchase_order(qty_to_order=qty)

        # schedule the next review period event
        next_review_period = self.clock + self.review_period
        new_event = Event(clock=next_review_period, type_of_event=EventType.PURCHASE_ORDER, event_name=f'Review Period {next_review_period}')
        self.event_queue.add_event(new_event)
    
    
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