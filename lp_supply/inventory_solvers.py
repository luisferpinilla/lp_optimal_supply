# Autor: Luis Fernando Pinilla

import numpy as np
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

        prob.solve(prob)
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
        #print(lp.value(prob.objective))
        return pedidos, proyinv, lp.value(prob.objective)


