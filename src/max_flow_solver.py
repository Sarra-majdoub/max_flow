
"""import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def ford_fulkerson(edges, source, sink):




    Implémentation de l'algorithme de Ford-Fulkerson pour calculer le flot maximal
    
    Args:
        edges: Liste de tuples (u, v, capacité)
        source: Nœud source
        sink: Nœud puits
        
    Returns:
        (max_flow, flows): Valeur du flot maximal et dictionnaire des flux

"""
"""

    # Construction du graphe résiduel
    graph = nx.DiGraph()
    
    # Ajouter tous les arcs au graphe
    for u, v, capacity in edges:
        graph.add_edge(u, v, capacity=capacity, flow=0)
        
        # Ajouter les arcs retour s'ils n'existent pas
        if not graph.has_edge(v, u):
            graph.add_edge(v, u, capacity=0, flow=0)
    
    # Fonction pour trouver un chemin augmentant par DFS
    def find_path(graph, source, sink, path=None, visited=None):
        if path is None:
            path = []
        if visited is None:
            visited = set()
            
        if source == sink:
            return path
            
        visited.add(source)
        
        for u, v, data in graph.out_edges(source, data=True):
            residual_capacity = data['capacity'] - data['flow']
            if residual_capacity > 0 and v not in visited:
                result = find_path(graph, v, sink, path + [(u, v, residual_capacity)], visited)
                if result:
                    return result
                    
        return None
    
    # Algorithme principal de Ford-Fulkerson
    max_flow = 0
    
    while True:
        path = find_path(graph, source, sink)
        
        if not path:
            break
            
        # Trouver le flot maximal qui peut être envoyé sur ce chemin
        flow = min(capacity for _, _, capacity in path)
        max_flow += flow
        
        # Mettre à jour les capacités résiduelles
        for u, v, _ in path:
            graph[u][v]['flow'] += flow
            graph[v][u]['flow'] -= flow
    
    # Extraire les flux finaux pour retourner le résultat
    flows = {}
    for u, v, data in graph.edges(data=True):
        if data['flow'] > 0 and data['capacity'] > 0:  # Ne considérer que les arcs originaux avec flux positif
            flows[(u, v)] = data['flow']
    
    return max_flow, flows

def solve_max_flow(edges, source, sink):

    Fonction de résolution utilisée par l'application
    Cette version utilise Ford-Fulkerson directement au lieu de Gurobi
    
    Args:
        edges: Liste de tuples (u, v, capacité)
        source: Nœud source
        sink: Nœud puits
        
    Returns:
        (max_flow, flows): Valeur du flot maximal et dictionnaire des flux


    try:
        # Pour des raisons éducatives, nous utilisons Ford-Fulkerson directement
        return ford_fulkerson(edges, source, sink)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la résolution : {str(e)}")
    


# Si vous préférez continuer à utiliser Gurobi, voici la version Gurobi:

"""



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
