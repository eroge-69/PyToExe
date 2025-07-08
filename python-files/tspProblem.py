import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# --- 1. Problem Modelleme ---

n_cities = 8  # Şehir sayısı
np.random.seed(42)
random.seed(42)

# Şehirler arası mesafe matrisi (rastgele oluşturuluyor)
distance_matrix = np.random.randint(10, 51, size=(n_cities, n_cities))
np.fill_diagonal(distance_matrix, 0)  # Aynı şehir arası mesafe 0

# Pil tüketimi matrisi (mesafenin %10-20'si kadar, rastgele)
battery_matrix = (distance_matrix * np.random.uniform(0.1, 0.2, size=(n_cities, n_cities))).astype(int)
np.fill_diagonal(battery_matrix, 0)

# Zaman matrisi (mesafenin 2-3 katı kadar, rastgele)
time_matrix = (distance_matrix * np.random.uniform(2, 3, size=(n_cities, n_cities))).astype(int)
np.fill_diagonal(time_matrix, 0)

# --- MATRİSLERİ YAZDIR ---
print("Mesafe Matrisi (distance_matrix):\n", distance_matrix, "\n")
print("Pil Tüketimi Matrisi (battery_matrix):\n", battery_matrix, "\n")
print("Zaman Matrisi (time_matrix):\n", time_matrix, "\n")

# --- 2. Fitness Fonksiyonu ---

def calculate_fitness(route, distance_matrix, battery_matrix, time_matrix, w1=1, w2=1, w3=1):
    """
    Verilen bir rotanın toplam maliyetini (mesafe, pil, zaman) hesaplar.
    """
    total_distance = 0
    total_battery = 0
    total_time = 0
    n = len(route)
    for i in range(n):
        from_city = route[i]
        to_city = route[(i + 1) % n]  # Son şehirden tekrar başlangıca dönüş
        total_distance += distance_matrix[from_city][to_city]
        total_battery += battery_matrix[from_city][to_city]
        total_time += time_matrix[from_city][to_city]
    fitness = w1 * total_distance + w2 * total_battery + w3 * total_time
    return fitness, total_distance, total_battery, total_time

# --- 3.1 Genetik Algoritma (GA) ---

def create_route(n_cities):
    """
    Rastgele bir rota (şehir sırası) oluşturur.
    """
    route = list(range(n_cities))
    random.shuffle(route)
    return route

def initial_population(pop_size, n_cities):
    """
    Başlangıç popülasyonunu (rastgele rotalar) oluşturur.
    """
    return [create_route(n_cities) for _ in range(pop_size)]

def crossover(parent1, parent2):
    """
    İki ebeveyn rotadan yeni bir çocuk rota üretir (çaprazlama).
    """
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None]*size
    child[start:end] = parent1[start:end]
    pointer = 0
    for city in parent2:
        if city not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = city
    return child

def mutate(route):
    """
    Rastgele iki şehrin yerini değiştirerek mutasyon uygular.
    """
    a, b = random.sample(range(len(route)), 2)
    route[a], route[b] = route[b], route[a]
    return route

def select(population, fitnesses, k=3):
    """
    Turnuva seçimi ile en iyi bireyi seçer.
    """
    selected = random.sample(list(zip(population, fitnesses)), k)
    selected.sort(key=lambda x: x[1])
    return selected[0][0]

def genetic_algorithm(distance_matrix, battery_matrix, time_matrix, pop_size=50, generations=100, w1=1, w2=1, w3=1):
    """
    Genetik Algoritma ile en iyi rotayı bulur.
    """
    n_cities = len(distance_matrix)
    population = initial_population(pop_size, n_cities)
    best_route = None
    best_fitness = float('inf')
    convergence = []
    for gen in range(generations):
        # Her bireyin fitness'ını hesapla
        fitnesses = [calculate_fitness(route, distance_matrix, battery_matrix, time_matrix, w1, w2, w3)[0] for route in population]
        new_population = []
        for _ in range(pop_size):
            parent1 = select(population, fitnesses)
            parent2 = select(population, fitnesses)
            child = crossover(parent1, parent2)
            if random.random() < 0.2:
                child = mutate(child)
            new_population.append(child)
        population = new_population
        min_fitness = min(fitnesses)
        convergence.append(min_fitness)
        if min_fitness < best_fitness:
            best_fitness = min_fitness
            best_route = population[fitnesses.index(min_fitness)]
    return best_route, best_fitness, convergence

# --- 3.2 Parçacık Sürü Optimizasyonu (PSO) ---

def pso(distance_matrix, battery_matrix, time_matrix, pop_size=50, generations=100, w1=1, w2=1, w3=1):
    """
    Parçacık Sürü Optimizasyonu ile en iyi rotayı bulur.
    """
    n_cities = len(distance_matrix)
    population = [create_route(n_cities) for _ in range(pop_size)]
    personal_best = population.copy()
    personal_best_scores = [calculate_fitness(route, distance_matrix, battery_matrix, time_matrix, w1, w2, w3)[0] for route in population]
    global_best = personal_best[np.argmin(personal_best_scores)]
    global_best_score = min(personal_best_scores)
    convergence = []
    for gen in range(generations):
        for i in range(pop_size):
            # Rastgele iki şehrin yerini değiştir (swap)
            if random.random() < 0.8:
                a, b = random.sample(range(n_cities), 2)
                population[i][a], population[i][b] = population[i][b], population[i][a]
            score = calculate_fitness(population[i], distance_matrix, battery_matrix, time_matrix, w1, w2, w3)[0]
            if score < personal_best_scores[i]:
                personal_best[i] = population[i][:]
                personal_best_scores[i] = score
        min_idx = np.argmin(personal_best_scores)
        if personal_best_scores[min_idx] < global_best_score:
            global_best = personal_best[min_idx][:]
            global_best_score = personal_best_scores[min_idx]
        convergence.append(global_best_score)
    return global_best, global_best_score, convergence

# --- 4. Deneyler ve Analizler ---

def run_experiments(algorithm, n_runs=10):
    """
    Belirtilen algoritmayı n_runs kadar çalıştırır ve sonuçları döndürür.
    """
    best_fitnesses = []
    best_routes = []
    all_convergences = []
    for _ in range(n_runs):
        if algorithm == "GA":
            route, fitness, convergence = genetic_algorithm(distance_matrix, battery_matrix, time_matrix)
        elif algorithm == "PSO":
            route, fitness, convergence = pso(distance_matrix, battery_matrix, time_matrix)
        best_fitnesses.append(fitness)
        best_routes.append(route)
        all_convergences.append(convergence)
    return best_fitnesses, best_routes, all_convergences

# Her algoritma için 10 kez çalıştır
ga_fitnesses, ga_routes, ga_convergences = run_experiments("GA")
pso_fitnesses, pso_routes, pso_convergences = run_experiments("PSO")

# --- 5. Sonuçların Görselleştirilmesi ve İstatistiksel Analiz ---

# Yakınsama eğrileri (her algoritmanın ortalama yakınsaması)
plt.figure(figsize=(10,5))
plt.plot(np.mean(ga_convergences, axis=0), label="GA")
plt.plot(np.mean(pso_convergences, axis=0), label="PSO")
plt.xlabel("Jenerasyon")
plt.ylabel("En İyi Fitness")
plt.title("Yakınsama Eğrisi")
plt.legend()
plt.show()

# Boxplot (her algoritmanın en iyi fitness dağılımı)
plt.figure(figsize=(7,5))
plt.boxplot([ga_fitnesses, pso_fitnesses], labels=["GA", "PSO"])
plt.ylabel("En İyi Fitness")
plt.title("Algoritmaların Sonuçlarının Boxplot'u")
plt.show()

# --- Sonuçların Yazdırılması ---

def diversity(routes):
    """
    Popülasyondaki farklı rotaların oranını (çeşitliliği) hesaplar.
    """
    unique_routes = set(tuple(r) for r in routes)
    return len(unique_routes) / len(routes)

def print_route_details(route, distance_matrix, battery_matrix, time_matrix):
    """
    Bir rotanın detaylı analizini ekrana yazdırır.
    """
    fitness, total_distance, total_battery, total_time = calculate_fitness(
        route, distance_matrix, battery_matrix, time_matrix)
    print(f"  Rota: {route}")
    print(f"  Toplam Mesafe: {total_distance}")
    print(f"  Toplam Pil Tüketimi: {total_battery}")
    print(f"  Toplam Zaman: {total_time}")
    print(f"  Fitness (Maliyet): {fitness}\n")

best_ga_idx = np.argmin(ga_fitnesses)
best_pso_idx = np.argmin(pso_fitnesses)

print("==== GENETİK ALGORİTMA (GA) SONUÇLARI ====")
print(f"Ortalama Fitness: {np.mean(ga_fitnesses):.2f}")
print(f"Standart Sapma: {np.std(ga_fitnesses):.2f}")
print(f"En İyi Fitness: {np.min(ga_fitnesses):.2f}")
print(f"En Kötü Fitness: {np.max(ga_fitnesses):.2f}")
print(f"Diversity (Çeşitlilik): {diversity(ga_routes):.2f}")
print("En iyi GA rotasının detayları:")
print_route_details(ga_routes[best_ga_idx], distance_matrix, battery_matrix, time_matrix)

print("==== PARÇACIK SÜRÜ OPTİMİZASYONU (PSO) SONUÇLARI ====")
print(f"Ortalama Fitness: {np.mean(pso_fitnesses):.2f}")
print(f"Standart Sapma: {np.std(pso_fitnesses):.2f}")
print(f"En İyi Fitness: {np.min(pso_fitnesses):.2f}")
print(f"En Kötü Fitness: {np.max(pso_fitnesses):.2f}")
print(f"Diversity (Çeşitlilik): {diversity(pso_routes):.2f}")
print("En iyi PSO rotasının detayları:")
print_route_details(pso_routes[best_pso_idx], distance_matrix, battery_matrix, time_matrix)

# p-değeri (istatistiksel anlamlılık)
t_stat, p_value = ttest_ind(ga_fitnesses, pso_fitnesses)
print("==== İSTATİSTİKSEL ANLAM (p-değeri) ====")
print(f"GA ve PSO sonuçları arasındaki p-değeri: {p_value:.4f}")
