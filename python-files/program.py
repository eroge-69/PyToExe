class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
            
        return self.parent[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)

        if root_u != root_v:
            if self.rank[root_u] > self.rank[root_v]:
                self.parent[root_v] = root_u
            elif self.rank[root_u] < self.rank[root_v]:
                self.parent[root_u] = root_v
            else:
                self.parent[root_v] = root_u
                self.rank[root_u] += 1

def kruskal(graph):
    edges = []
    n = len(graph)

    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] != 0:
                edges.append((graph[i][j], i, j))

    edges.sort()
    ds = DisjointSet(n)
    mst_weight = 0
    mst_edges = []

    for weight, u, v in edges:
        if ds.find(u) != ds.find(v):
            ds.union(u, v)
            mst_edges.append((u, v, weight))
            mst_weight += weight

    return mst_edges, mst_weight


def main():
    with open('graph.txt', 'r') as file:
        graph = [list(map(int, line.split())) for line in file.readlines()]

    mst_edges, mst_weight = kruskal(graph)

    print("Рёбра остова минимального веса:")
    
    for u, v, weight in mst_edges:
        print(f"({u}, {v}) с весом {weight}")

    print(f"Вес остова: {mst_weight}")
    input("Нажмите любую клавишу для завершения программы.")

if __name__ == "__main__":
    main()