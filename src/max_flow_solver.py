from gurobipy import Model, GRB, quicksum

def solve_max_flow(edges, source, sink):
    model = Model("MaxFlow")
    flow_vars = {}

    # Création des variables
    for u, v, c in edges:
        flow_vars[(u, v)] = model.addVar(lb=0, ub=c, name=f"f_{u}_{v}")

    # Fonction objectif
    model.setObjective(
        quicksum(flow_vars[(u, v)] for (u, v) in flow_vars if u == source),
        GRB.MAXIMIZE
    )

    # Contraintes de conservation
    nodes = {u for u, _, _ in edges} | {v for _, v, _ in edges}
    for node in nodes - {source, sink}:
        in_flow = quicksum(flow_vars[(u, node)] for (u, v) in flow_vars if v == node)
        out_flow = quicksum(flow_vars[(node, v)] for (u, v) in flow_vars if u == node)
        model.addConstr(in_flow == out_flow, f"cons_{node}")

    # Résolution
    model.optimize()

    if model.status == GRB.OPTIMAL:
        return (
            model.objVal,
            {(u, v): var.X for (u, v), var in flow_vars.items()}
        )
    else:
        raise RuntimeError("Aucune solution optimale trouvée")