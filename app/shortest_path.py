import numpy as np
import networkx as nx
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.heuristics import solve_tsp_simulated_annealing
from datetime import datetime
import functools


def shortest_route(destinations):

    begin_time = datetime.now()

    # Calculate path weight between two nodes
    def path_cost(G, path):
        return sum(
            [G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)]
        )

    def simulate_travel_path(G, visit):
        temp_Graph = nx.Graph()
        temp_Graph.add_nodes_from(visit)
        c = list(temp_Graph.nodes)
        with open('Shortest Path Between Each Pair of Nodes.txt', 'w') as f:
            for n in range(len(c)):
                for n1 in range(len(c)):
                    if n == n1:
                        continue
                    # try:
                    # if not temp_Graph.has_edge(c[n], c[n1]):
                    cool_dist = list(nx.dijkstra_path(G, c[n], c[n1]))
                    total_weight = path_cost(G, cool_dist)
                    temp_Graph.add_edge(
                        c[n], c[n1], weight=total_weight
                    )
                    f.write(
                        c[n] + ' & ' + c[n1] + ': ' + str(total_weight) + '\n'
                    )
                    f.write(
                        str(cool_dist) + '\n\n'
                    )
                        
                    # except Exception as e:
                    #     print(e)
        return temp_Graph

    # My array of nodes, columns A, B, C are present for now
    warehouse_col = [
        'A',
        'B', 'C',
        'D', 'E',
        'F', 'G',
        'H', 'I',
        'J', 'K',
        'L'
    ]
    warehouse_edges = []
    warehouse_endpoint_edges = []
    myArray = np.array(['Start'])

    # Automatically adding the nodes A0 to C0,
    for col in warehouse_col:
        # Number of rows in each warehouse column
        for num in range(0, 14):
            location = col + str(num)
            if num == 0:
                # Linking the start position to starting point of each
                # warehouse column E.g. A0, B0, C0 etc...
                warehouse_edges.append([myArray[0], location])
                warehouse_endpoint_edges.append(location)

            myArray = np.append(myArray, location)
            array_length = len(myArray)

            if num > 0:
                # Linking each node in each column to each other E.g. A0 -> A1,
                # A1 -> A2
                warehouse_edges.append([myArray[array_length-2], location])
            if num == 13:
                warehouse_endpoint_edges.append(location)

    # Link up columns B & C E.g. B0 -> C0, B1 -> C1 ... B10 -> C10
    for nodes in myArray:
        if nodes[0] == 'A':
            hack = 'B' + nodes[1:]
            warehouse_edges.append([nodes, hack])
        elif nodes[0] == 'C':
            hack = 'D' + nodes[1:]
            warehouse_edges.append([nodes, hack])
        elif nodes[0] == 'E':
            hack = 'F' + nodes[1:]
            warehouse_edges.append([nodes, hack])
        elif nodes[0] == 'G':
            hack = 'H' + nodes[1:]
            warehouse_edges.append([nodes, hack])
        elif nodes[0] == 'I':
            hack = 'J' + nodes[1:]
            warehouse_edges.append([nodes, hack])
        elif nodes[0] == 'K':
            hack = 'L' + nodes[1:]
            warehouse_edges.append([nodes, hack])

    # Link the edges of warehouse col E.g. A0 -> B0, A10 -> B10, B0 -> C0,
    # B10 -> C10
    for idx in range(len(warehouse_endpoint_edges)):
        if idx + 2 < len(warehouse_endpoint_edges):
            warehouse_edges.append(
                [
                    warehouse_endpoint_edges[idx],
                    warehouse_endpoint_edges[idx+2]
                ]
            )

    set_dist = 0
    # Giving a weight to each edges
    for edges in warehouse_edges:
        if(edges[0] == 'Start'):
            set_dist += 3
            edges.append(set_dist)
            continue
        weight = 2
        edges.append(weight)

    # networkX
    myGraph = nx.Graph()
    # Adding nodes stored in the array to the graph
    myGraph.add_nodes_from(myArray)
    myGraph.add_weighted_edges_from(warehouse_edges)

    # So now add nodes are interconnected
    # We only want to go to a few particular nodes so..
    # Under the assumption there will always be a custom point of 'Start'
    # travel_log = [
    #     'Start', 'A7', 'A11', 'B2', 'C6', 'D3',
    #     'D9', 'E12', 'F2', 'H10', 'J8', 'L12'
    # ]
    travel_log = destinations

    # Nodes in travel_log are points one wishes to travel to.
    # Using simulate_travel_path, the weights are
    travel_Graph = simulate_travel_path(myGraph, travel_log)

    b = nx.to_numpy_matrix(travel_Graph)

    if len(travel_log) <= 15:
        permutation, distance = solve_tsp_dynamic_programming(b)
    else:
        permutation, distance = solve_tsp_simulated_annealing(b)

        before_zero = []
        n = 0
        if permutation[n] != 0:
            while permutation[n] != 0:
                before_zero.append(permutation[n])
                permutation.pop(n)
                if permutation[n] == 0:
                    after_zero = permutation
                    break
            permutation = after_zero + before_zero

    the_way = []
    for n in range(len(permutation)):
        the_way.append(travel_log[permutation[n]])

    time_taken = datetime.now() - begin_time
    time_taken_in_hrs = str(time_taken).split(':')[0]
    time_taken_in_mins = str(time_taken).split(':')[1]
    time_taken_in_secs = str(time_taken).split(':')[2]

    # print("\nThis is the shortest path to take: ")
    return(the_way, distance, time_taken_in_hrs, time_taken_in_mins, time_taken_in_secs)


# if __name__ == "__main__":

    # begin_time = datetime.now()

    # with open('nodes.txt', 'r') as nodes_f:
    #     lines = nodes_f.readlines()
    #     nodes = []
    #     for line in lines:
    #         nodes.append(line.strip('\n'))

    #     all_routes = []
    #     all_routes_costs = []
    #     first_route = shortest_route(nodes)
    #     all_routes.append(first_route[0])
    #     all_routes_costs.append(first_route[1])

    #     for i in range(10):
    #         test_route = shortest_route(nodes)
    #         test_list2 = test_route[0]
    #         check_identical = []
    #         for each_route in all_routes:
    #             test_list1 = each_route
    #             if functools.reduce(lambda i, j: i and j, map(lambda m, k: m == k, test_list1, test_list2), True):
    #                 check_identical.append('Y')
    #             else:
    #                 check_identical.append('N')
    #         if 'Y' in check_identical:
    #             pass
    #         else:
    #             all_routes.append(test_list2)
    #             all_routes_costs.append(test_route[1])

    #     with open('all_routes.txt','w') as all_routes_f:
    #         for (route, distance_cost) in zip(all_routes, all_routes_costs):
    #             all_routes_f.write(', '.join(route) + ': ')
    #             all_routes_f.write(str(distance_cost))
    #             all_routes_f.write('\n')

    # print(
    #     shortest_route(
    #         [
    #             'Start', # 'A7'
    #             'A11', 'A7',
    #             'B2',
    #             # 'C6',
    #             # 'D3', 'D9',
    #             # 'E12',
    #             # 'F2',
    #             # 'H10',
    #             # 'J8',
    #             # 'L12',
    #             # 'G0', 'G3', 'G5', 'G7'
    #         ]
    #     )[0]
    # )

    # print(datetime.now() - begin_time)
