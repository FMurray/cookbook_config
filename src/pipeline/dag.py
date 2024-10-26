def detect_cycles(nodes, edges):
    from collections import defaultdict

    graph = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)

    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False


def topological_sort(nodes, edges):
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = {node: 0 for node in nodes}

    for src, dst in edges:
        graph[src].append(dst)
        in_degree[dst] += 1

    queue = deque([node for node in nodes if in_degree[node] == 0])
    sorted_list = []

    while queue:
        node = queue.popleft()
        sorted_list.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_list) != len(nodes):
        raise ValueError("Cycle detected in the pipeline DAG")

    return sorted_list
