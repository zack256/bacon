def add_directed_edge_to_graph(graph, x, y, r):
    if x not in graph:
        graph[x] = {y : r}
    else:
        '''
        if y not in graph[x]:
            graph[x][y] = r
        else:
            graph[x][y] = min(r, graph[x][y])   # can be multiple paths with different weights.
        '''
        graph[x][y] = r # in this scenario there can't be multiple paths connecting the same pair of nodes.

def build_graph(edges):
    graph = {}
    for edge_list in edges:
        x, y, r = edge_list
        add_directed_edge_to_graph(graph, x, y, r)
        add_directed_edge_to_graph(graph, y, x, r)
    return graph

def shortest_path (edges, source, dest = None):
    # if dest == None, then will find the shortest paths to all nodes. else, will find the shortest distance to dest as well as the previous node on the shortest path.
    # edges is a list of lists. each list contains [x, y, r]; three ints, x and y are nodes while r is the weight between them.
    graph = build_graph(edges)
    unvisited = {source : [0, None]}    # each value of both the unvisited and visited dicts are [distance, previous node].
    visited = {}
    focus = source
    while True:
        if focus == dest:
            return [unvisited[dest], visited]
        connections = graph[focus]
        for node in connections:
            if node in visited:
                continue
            weight = connections[node]
            if node not in unvisited:
                unvisited[node] = [unvisited[focus][0] + weight, focus]
            else:
                #unvisited[node] = min(unvisited[focus] + weight, unvisited[node])
                if unvisited[focus][0] + weight < unvisited[node][0]:
                    unvisited[node] = [unvisited[focus][0] + weight, focus]
        visited[focus] = unvisited[focus]
        del unvisited[focus]
        if not unvisited:
            break
        focus = min(unvisited, key = lambda x : unvisited[x][0])
    return visited







