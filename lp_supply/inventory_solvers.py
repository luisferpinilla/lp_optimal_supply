# Autor: Luis Fernando Pinilla

import numpy as np
import pulp as pu
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable

def multi_product_period_capacited(placing_order_cost:float, leadtime:int, supplier_capacity:list,  initial_inventory:list, product_holding_cost:list, mininum_batch_size:list, product_capacity_consume:list, forecast:list, arrivals: list, inventory_goals:list, penalty_cost_inventory_goal:list):
    c_parameter = placing_order_cost
    l_parameter = leadtime
    t_parameter = supplier_capacity
    q_parameter = initial_inventory
    h_parameter = product_holding_cost
    s_parameter = mininum_batch_size
    w_parameter = product_capacity_consume
    f_parameter = forecast 
    a_parameter = arrivals
    o_parameter = inventory_goals
    d_parameter = penalty_cost_inventory_goal
    m_parameter = np.sum(f_parameter)**2

    p_sets =[]
    t_sets = []
    # variables
    x_variable = [[LpVariable(f'X(p={p};t={t})', lowBound=0.0, cat='Continuous') for p in p_sets] for t in t_sets]
    k_variable = [[LpVariable(f'K(p={p};t={t})', cat='Continuous') for p in p_sets] for t in t_sets]
    p_variable = [LpVariable(f'P(t={t})', lowBound=0, cat='Integer') for t in t_sets]
    r_variable = [[LpVariable(f'R(p={p};t={t})', cat='Binary') for p in p_sets] for t in t_sets]
    e_variable = [[LpVariable(f'E(p={p};t={t})', cat='Binary') for p in p_sets] for t in t_sets]

    model = LpProblem(name="Inventory-policies-problem", sense=LpMinimize)

    # objetive function
    model += lpSum([h_parameter[p] * k_variable[t][p] for t in t_sets for p in p_sets] + [c_parameter * p_variable[t] for t in t_sets] + [d_parameter[p] * e_variable[t][p] for t in t_sets for p in p_sets])

    # inventory balance
    for p in p_sets:
        model += (k_variable[0][p] == q_parameter[p] + a_parameter[0][p] - f_parameter[0][p], 
              f'balanceInvProduct{p}_at_t={0}')

    for p in p_sets:
        for t in t_sets[1:l_parameter]:
            model += (k_variable[t][p] == k_variable[t-1][p] + a_parameter[t][p] - f_parameter[t][p],
                  f'balanceInvProduct{p}_at_t={t}')      

    for p in p_sets:
        for t in t_sets[l_parameter:]:
            model += (k_variable[t][p] == k_variable[t-1][p] + a_parameter[t][p] - f_parameter[t][p] + x_variable[t-l_parameter][p],
                f'balanceInvProduct{p}_at_t={t}')   
    # keept inventory over goal
    for p in p_sets:
        for t in t_sets[l_parameter:]:
            model += (k_variable[t][p] >= o_parameter[t][p] ,f'Inventario del producto {p} sobre la meta en el periodo {t}')

    # minimo lote y capacidad
    for p in p_sets:
        for t in t_sets:
            model += (x_variable[t][p] <= m_parameter * r_variable[t][p] ,f'máxima cantidad a pedir del producto {p} en el periodo {t}')
            model += (x_variable[t][p] >= s_parameter[p] * r_variable[t][p] ,f'mínima cantidad a ordenar del producto {p} en el periodo {t} cumpliendo el lóte minimo')

    # Capacidad de carga del contenedor
    for t in t_sets:
        model += (lpSum([w_parameter[p] * x_variable[t][p] for p in p_sets]) <= t_parameter[t] * p_variable[t],
            f'Capacidad del proveedor/contenedores en el periodo{t}')        

    model.solve()

    print(f"status: {model.status}, {LpStatus[model.status]}")
    print(f"objective: {model.objective.value()}")
    for var in model.variables():
        print(f"{var.name}: {var.value()}")


def mono_product_multiperiod_multi_location(holding_cost:float, order_cost:float, initial_inventory:list, safety_stock:list, min_batch_size:float, min_po:float, forecast:list, arrivals:list, leadtime:list, max_time_seconds=0):
    """Calcula los pedidos óptimos a colocar a un proveedor teniendo múltiples bodegas a donde se debe despachar el producto. Se tiene en cuenta el safety stock definido para cada bodega, 
    el pedido mínimo que debe colocarse en conjunto para las tres bodegas, el mínimo pedido que debe llegar a cada bodega, el pronóstico de venta, las llegadas programadas con antelación y
    diferentes lead time a desde el proveedor a cada bodega

    Args:
        holding_cost (float): costo financiero por mantener un producto en inventario. Se puede calcular a partir de una tasa de interés y el costo unitario del producto
        order_cost (float): costo de colocar una orden de abastecimiento al proveedor.
        initial_inventory (list): inventario inicial en bodega
        safety_stock (list): cantidad mínima a mantener en bodega.
        min_batch_size (float): cantidad mínima que se puede pedir al proveedor
        min_po (float): mínimo pedido que puede colocar una bodega
        forecast (list): presupuesto de ventas de cada producto en cada bodega
        arrivals (list): llegadas programadas a cada bodega
        leadtime (list): lead time a cada bodega
        max_time_seconds (int, optional): máximo tiempo a esperar por ejecusión del modelo. Por defecto es 0 que significa que es ilimitado.

    Returns:
        tuple: pedidos a colocar, inventario proyectado, presupuesto de ventas, llegadas aproximadas
    """
    
    bigM = np.sum(forecast)

    # variable Xbt: Cantidad pedida para la bodega b durante el periodo t
    Xbt = [[pu.LpVariable(name=f'Xb{b}t{t}',lowBound=0, upBound=bigM) for t in range(len(forecast[0]))] for b in range(len(forecast))]
    
    # variable Pbt: 1 si se coloca pedido durante el periodo t; 0 en otro caso
    Pt = [pu.LpVariable(f'Pt{t}', cat='Binary') for t in range(len(forecast[0]))]
    
    Mbt = [[pu.LpVariable(name=f'Mb{b}t{t}', cat='Binary') for t in range(len(forecast[0]))] for b in range(len(forecast))]
    
    # variable Ibt: cantidad de inventario en la bodega b al final del periodo t
    Ibt = [[pu.LpVariable(name=f'Ib{b}t{t}') for t in range(len(forecast[b]))] for b in range(len(forecast))]
    
    # declarar el problema
    prob = pu.LpProblem("Suggested_PO", pu.LpMinimize)
    # Colocar funcion objetivo
    prob += (pu.lpSum([order_cost*Pt[t] for t in range(len(forecast[0]))] + 
                      [holding_cost*Ibt[b][t] for t in range(len(forecast[0])) for b in range(len(forecast))]),
                       'Costo total relevante')
    
    #prob += (pu.lpSum([Ibt[b][t] for t in range(len(forecast[0])) for b in range(len(forecast))]), 'Metros almacenados')

    # restriccion para evitar quedar bajo el SS
    # para cada bodega
    for b in range(len(forecast)):
        # para cada periodo
        for t in range(leadtime[b], len(forecast[b])):
            # obligat a que Ibt termine sobre el SS
            prob += (Ibt[b][t] >= safety_stock[b], 
                     f'terminar inventario al final de {t} sobre {safety_stock[b]} en la bodega {b}')

    # restriccion de flujo de inventarios
    # para cada bodega
    for b in range(len(forecast)):
        
        # el inventario final es el inicial menos el forecast + las llegadas programadas
        prob += (Ibt[b][0] == initial_inventory[b] - forecast[b][0] + arrivals[b][0], 
                 f'inventario en la bodega {b} al final del periodo {0}')        
        
        # para cada periodo
        for t in range(1, len(forecast[0])):
            if t < leadtime[b]:
                # el inventario final es el cierre del periodo anterior menos el forecast + las llegadas programadas
                prob += (Ibt[b][t] == Ibt[b][t-1] - forecast[b][t] + arrivals[b][t],
                         f'inventario en la bodega {b} al final del periodo {t}')
            else:
                # el inventario final es el cierre del periodo anterior menos el forecast + las llegadas programadas + pedidos colocados un lead time antes
                prob += (Ibt[b][t] == Ibt[b][t-1] - forecast[b][t] + arrivals[b][t] + Xbt[b][t-leadtime[b]], 
                         f'inventario en la bodega {b} al final del periodo {t}') 

    # restricciones de pedidos mínimos
    
    # para cada bodega
    for b in range(len(forecast)):
        # para cada periodo
        for t in range(len(forecast[0])):        
            # pedir sobre el pedido mínimo
            prob += (Xbt[b][t] >= min_po*Mbt[b][t], f'pedir sobre el pedido minimo durante {t} en la bodega {b}')
            # habilitar capacidad
            prob += (Xbt[b][t] <= 10000*Mbt[b][t], f'pedir menos de la capacidad durante {t} en la bodega {b}')
    
    # La suma de los pedidos debe superar el lote minimo de producción
    for t in range(len(forecast[b])):        
        prob += (pu.lpSum([Xbt[b][t] for b in range(len(forecast))]) >= min_batch_size*Pt[t], 
                 f'superar el lote minimo de produccion durante {t}')  
        prob += (pu.lpSum([Xbt[b][t] for b in range(len(forecast))]) <= 10000*Pt[t], 
                 f'No emitir pedido si no se activa el pedidodurante {t}') 
    
    #print(prob)
    
    # prob.solve(pu.PULP_CBC_CMD(timeLimit=max_time_seconds))
    if max_time_seconds != 0:
        prob.solve(pu.GLPK_CMD(options=['--mipgap', '0.35', f'--tmlim {max_time_seconds}']))
    else:
        prob.solve(pu.GLPK_CMD(options=['--mipgap', '0.35']))
    
    pedidos = [[Xbt[b][t].value() for t in range(len(forecast[b]))] for b in range(len(forecast))]    
    inventario = [[Ibt[b][t].value() for t in range(len(forecast[b]))] for b in range(len(forecast))]
    
    return pedidos, inventario, forecast


class PlaneacionAgregada(object):
    def __init__(self, leadtime: int, initialinventory: float, minpurchasequantiry: float, purchasecost: float,
                 holdingcost: float, forecast: list[float], arrivals: list[float], maxCapacity: [float], safetystock = 0.0):

        if len(arrivals) != leadtime:
            print("Error: la cantidad de arrivals no concuerda con el leadtime dado")

        self._leadTime = leadtime
        self._initialInventory = initialinventory
        self._minPurchaseQuantity = minpurchasequantiry
        self._purchaseCost = purchasecost
        self._holdingCost = holdingcost
        self._forecast = forecast
        self._arrivals = arrivals
        self._safetystock = safetystock
        self._maxCapacity = maxCapacity
        self._purchaseQuantities = {}  # cantidad a pedir
        self._finalInventory = {}  # inventarios finales
        self._purchaseOrders = {}  # binary: si se pide en un periodo o no
        self._totalDemand = sum(self._forecast)
        self._totalArrivals = sum(self._arrivals)

    def solve(self, verbose = False):
        # Declarar el problema
        periods = len(self._forecast)

        # Crear variable par el problema
        prob = LpProblem(name="PurchasePlanning")

        # crear variables
        for t in range(periods):
            namefi = "InventoryAt{0}".format(t)
            namepq = "PurchaseQuantity{0}".format(t)
            namepo = "PlacePO{0}".format(t)
            self._finalInventory[t] = LpVariable(namefi,
                                                    lowBound=-self._totalDemand - self._initialInventory,
                                                    upBound=self._totalDemand + self._initialInventory + self._totalArrivals)
            self._purchaseQuantities[t] = LpVariable(namepq, lowBound=0.0, upBound=self._totalDemand)
            self._purchaseOrders[t] = LpVariable(namepo, lowBound=0.0, upBound=1.0, cat='Binary')

        # objetive: costo de las compras más el costo del inventario final en cada periodo

        fobj = self._purchaseCost * self._purchaseOrders[0] + self._finalInventory[0] * self._holdingCost
        for i in range(1, periods):
            fobj += self._purchaseCost * self._purchaseOrders[i] + self._finalInventory[i] * self._holdingCost

        prob += fobj

        # subject to:
        for t in range(periods):

            namebi = "balanceEnT{0}".format(t)
            namebk = "noBackOrderT{0}".format(t)
            currentinventory = self._finalInventory[t]            
            forecast = self._forecast[t]
            
            if t == 0:
                arrivals = self._arrivals[t]
                prob.add(currentinventory == self._initialInventory + arrivals - forecast, name=namebi)
            else:
                previousinventory = self._finalInventory[t - 1]
                if t < self._leadTime:                    
                    arrivals = self._arrivals[t]
                    # balance del inventario antes del leadtime
                    prob.add(currentinventory == previousinventory + arrivals - forecast, name=namebi)
                else:
                    cantidadpedida = self._purchaseQuantities[t - self._leadTime]
                    # balance de inventrio post Leadtime
                    prob.add(currentinventory == previousinventory + cantidadpedida - forecast, name=namebi)
                    prob.add(currentinventory >= self._safetystock, name=namebk)

        #restricciones de cantidad minima y máxima
        for t in range(periods):
            namemx = "MaxPedidoT{0}".format(t)
            namemn = "MinPedidoT{0}".format(t)
            # Cantidad minima
            cantidadpedida = self._purchaseQuantities[t]
            pedido = self._purchaseOrders[t]
            prob.add(cantidadpedida <= pedido * self._maxCapacity[t], name=namemx)
            prob.add(cantidadpedida >= pedido * self._minPurchaseQuantity, name=namemn)

        prob.solve()
        if verbose:
            print(prob)
        
        # Solution
        #for v in prob.variables():
        #    print(v.name, "=", v.varValue)

        pedidos = []
        proyinv = []
        for i in self._finalInventory.keys():
            pedidos.append(self._purchaseQuantities[i].varValue)
            proyinv.append(self._finalInventory[i].varValue)
        return pedidos, proyinv, prob.objective


