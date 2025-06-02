def find_articulation_points(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    visited = [False] * n
    tin = [-1] * n
    low = [-1] * n
    articulation_points = set()
    timer = [0]

    def dfs(v, parent=-1):
        visited[v] = True
        tin[v] = low[v] = timer[0]
        timer[0] += 1
        children = 0

        for to in adj[v]:
            if to == parent:
                continue
            if visited[to]:
                # Обратное ребро
                low[v] = min(low[v], tin[to])
            else:
                dfs(to, v)
                low[v] = min(low[v], low[to])
                if low[to] >= tin[v] and parent != -1:
                    articulation_points.add(v)
                children += 1

        # Отдельная проверка для корня DFS
        if parent == -1 and children > 1:
            articulation_points.add(v)

    for i in range(n):
        if not visited[i]:
            dfs(i)

    return articulation_points


def main():
    print("Поиск шарниров в неориентированном графе")
    n = int(input("Введите количество вершин: "))
    m = int(input("Введите количество рёбер: "))
    edges = []
    print("Введите рёбра (по два номера вершин через пробел, с нумерацией от 0):")
    for _ in range(m):
        u, v = map(int, input().split())
        edges.append((u, v))
    articulation_points = find_articulation_points(n, edges)
    if articulation_points:
        print("Шарниры графа (номера вершин):", sorted(articulation_points))
    else:
        print("В графе нет шарниров.")


if __name__ == "__main__":
    main()
