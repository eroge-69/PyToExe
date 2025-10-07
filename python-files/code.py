def read_input(filename):
    """Читает граф из файла input.txt"""
    edges = []
    vertices = set()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    v1, v2 = map(int, line.split(','))
                    vertices.add(v1)
                    vertices.add(v2)
                    if v1 != v2:  # Не добавляем петли как рёбра
                        edges.append((min(v1, v2), max(v1, v2)))
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return [], set()
    
    # Удаляем дубликаты рёбер
    edges = list(set(edges))
    return edges, vertices

def find_minimum_vertex_cover(edges, vertices):
    """
    Находит минимальное вершинное покрытие.
    Использует жадный алгоритм с оптимизациями.
    """
    if not edges:
        return list(vertices)  # Если нет рёбер, возвращаем все изолированные вершины
    
    # Для малых графов можем использовать полный перебор
    if len(vertices) <= 20:
        return find_exact_minimum_vertex_cover(edges, vertices)
    
    # Для больших графов используем приближённый алгоритм
    return greedy_vertex_cover(edges, vertices)

def find_exact_minimum_vertex_cover(edges, vertices):
    """Точный алгоритм для малых графов"""
    from itertools import combinations
    
    vertices_list = sorted(list(vertices))
    n = len(vertices_list)
    
    # Проверяем покрытия от минимального размера
    for size in range(1, n + 1):
        for cover in combinations(vertices_list, size):
            cover_set = set(cover)
            if all(v1 in cover_set or v2 in cover_set for v1, v2 in edges):
                return list(cover)
    
    return vertices_list

def greedy_vertex_cover(edges, vertices):
    """Жадный алгоритм для больших графов"""
    # Подсчитываем степени вершин
    degree = {v: 0 for v in vertices}
    edge_set = set(edges)
    
    for v1, v2 in edges:
        degree[v1] += 1
        degree[v2] += 1
    
    cover = set()
    remaining_edges = edge_set.copy()
    
    # Сначала добавляем вершины, которые обязательны
    # (например, если есть вершина, соединённая только с одной другой)
    while remaining_edges:
        # Находим вершину с максимальной степенью среди оставшихся рёбер
        vertex_degrees = {}
        for v1, v2 in remaining_edges:
            if v1 not in cover:
                vertex_degrees[v1] = vertex_degrees.get(v1, 0) + 1
            if v2 not in cover:
                vertex_degrees[v2] = vertex_degrees.get(v2, 0) +