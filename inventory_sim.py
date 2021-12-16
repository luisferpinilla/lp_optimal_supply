import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Simulation:
    def __init__(self, order_cutoff: float, order_target: float, lead_time: float, nombre='s1'):
        self.nombre = nombre
        self.inventory = order_target
        self.number_orderer = 0
        self.clock = 0
        self.t_customer = self.generate_interarrival()
        self.t_delivery = float('inf')

        self.revenue = 0.0
        self.cost_orders = 0.0
        self.cost_holing = 0.0

        self.order_cutoff = order_cutoff
        self.order_target = order_target

        print(f'iniciamos con {self.inventory} unidades en inventario')

    def advance_time(self):
        # obtener el siguiente
        t_event = min(self.t_customer, self.t_delivery)
        # Actualizar el hodling cost
        self.cost_holing += self.inventory*2*(t_event - self.clock)
        # Actualizar el reloj
        self.clock = t_event
        # manejar las llegadas
        print(f'Trabajando con el simulador {self.nombre}')
        if self.t_delivery <= self.t_customer:

            self.handle_delivery_event()
        else:
            self.handle_customer_event()

    def handle_customer_event(self):
        demand = self.generate_demand()

        if demand < self.inventory:
            print(
                f'{self.clock}: inventario {self.inventory}; se han vendido {demand} unidades')
            # actualizar revenue
            self.revenue += demand*100
            # actualizar inventario
            self.inventory -= demand
        else:
            print(f'Se han vendido las últimas {self.inventory} unidades')
            self.revenue += self.inventory*100
            self.inventory = 0.0

        # manejar pedidos
        if self.inventory < self.order_cutoff and self.number_orderer == 0:
            self.number_orderer = self.order_target - self.inventory
            self.cost_orders += 50*self.number_orderer
            self.t_delivery = self.clock + 2
            print(
                f'se ha colocado una orden por {self.number_orderer} unidades que llegarán en {self.t_delivery}, lo que deja el costo de ordenar en {self.cost_orders}')

        # agendar la siguiente llegada de cliente
        self.t_customer = self.clock + self.generate_interarrival()

    def handle_delivery_event(self):

        print(f'ha llegado una orden por{self.number_orderer}')
        # sumar la llegada
        self.inventory += self.number_orderer
        # actualizar el valor en pedido
        self.number_orderer = 0
        # programar la siguiente llegada en el infinito
        self.t_delivery = float('inf')

        print(f'inventario en {self.inventory}')

    def generate_interarrival(self):
        return np.random.exponential(scale=1/5)

    def generate_demand(self):
        return np.random.randint(low=1, high=5)


np.random.seed(0)

print('-----------------------')
print('Iniciando simulación')

s = Simulation(order_cutoff=10, order_target=30, lead_time=1.0, nombre='s1')

q = Simulation(order_cutoff=10, order_target=30, lead_time=1.0, nombre='S2')

history = dict()
history['tiempo'] = list()
history['revenue'] = list()
history['inventario'] = list()

while s.clock < 20.0:
    s.advance_time()
    q.advance_time()
    history['tiempo'].append(s.clock)
    history['revenue'].append(s.revenue)
    history['inventario'].append(s.inventory)


plt.plot(history['inventario'])
plt.show()


print('Fin')
