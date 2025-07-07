import pandas as pd
import random
import time
from itertools import product
import os
from openpyxl import load_workbook

# User Input for Parameters
excel_path = input("Masukkan path file Excel (misal: C:\\SKRIPSI\\Optimasi_GA.xlsx): ")
# Remove any double quotes from the input
excel_path = excel_path.replace('"', '')
population_size = int(input("Masukkan ukuran populasi (misal: 100): "))
max_iterations = int(input("Masukkan jumlah iterasi maksimum (misal: 10000): "))
max_runtime = int(input("Masukkan waktu maksimum dalam menit (misal: 30): ")) * 60  # Convert to seconds
k = max(1, population_size // 10)  # Ensure k is at least 1


# Data Input
data_mahasiswa = pd.read_excel(excel_path, sheet_name="Input_MHS")
data_ruang = pd.read_excel(excel_path, sheet_name="Ruang")
data_dosen = pd.read_excel(excel_path, sheet_name="Dosen")

print(f"Jumlah mahasiswa: {len(data_mahasiswa)}")

jam_list = ('08.40-09.30', '09.30-10.20', '10.20-11.10', '11.10-12.00', '12.30-13.20', '13.20-14.10', '14.10-15.00', '15.00-15.50')
ruang_list = data_ruang.iloc[0, 3:].tolist()
hari_list = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT']
paket = [jam_list[i:i + 2] for i in range(0, len(jam_list), 2) if i + 1 < len(jam_list)]

# Menarik nilai dosen berdasarkan nama yang diinput
def cari_dosen(nama):
    return data_mahasiswa.loc[data_mahasiswa['Nama Mahasiswa'] == nama, 
                            ['Dosen Pembimbing 1', 'Dosen Pembimbing 2', 
                                'Dosen Penguji 1', 'Dosen Penguji 2', 
                                'Dosen Penguji 3']].values.flatten().tolist()

# Fungsi untuk mencari jam dan hari dari dosen berdasarkan nama
def cari_jam(nama):
    filtered_data = data_dosen[data_dosen.iloc[:, 2:].apply(lambda x: x.str.contains(nama, case=False, na=False)).any(axis=1)]
    return [(row.iloc[0], row.iloc[1]) for _, row in filtered_data.iterrows()]

def buat_kromosom():
    used_slots = set()
    used_dosen_slots = set()
    populasi = []

    all_time_slots = list(product(paket, ruang_list, hari_list))
    random.shuffle(all_time_slots) 
    for nama in data_mahasiswa['Nama Mahasiswa']:
        dosen = cari_dosen(nama)
        
        found = False
        for paket_waktu, ruang, hari in all_time_slots:
            if (tuple(paket_waktu), ruang, hari) in used_slots:
                continue
            
            if any((dosen[i], tuple(paket_waktu), hari) in used_dosen_slots for i in range(len(dosen))):
                continue
            
            used_slots.add((tuple(paket_waktu), ruang, hari))
            used_dosen_slots.update((dosen[i], tuple(paket_waktu), hari) for i in range(len(dosen)))
            
            populasi.append((nama, paket_waktu, ruang, hari))
            found = True
            break
            
        if not found:
            print(f"Warning: Tidak menemukan slot yang valid untuk {nama}")
    
    return populasi

# Membuat generasi individu berdasarkan nama mahasiswa
def buat_generasi():
    return [buat_kromosom() for _ in range(population_size)]

def uji_fitness(individu):
    fitness = 0
    used_slots = set()
    used_dosen_slots = set()

    for kromosom in individu:
        info_dosen = cari_dosen(kromosom[0])
        jam_dos = [cari_jam(dosen) for dosen in info_dosen]
        
        # Cek konflik ruang dan waktu
        if (tuple(kromosom[1]), kromosom[2], kromosom[3]) in used_slots:
            fitness += 1  # Penalize for slot conflict
        
        for d in info_dosen:
            if (d, tuple(kromosom[1]), kromosom[3]) in used_dosen_slots:
                fitness += 1  # Penalize for dosen conflict

        used_slots.add((tuple(kromosom[1]), kromosom[2], kromosom[3]))
        for d in info_dosen:
            used_dosen_slots.add((d, tuple(kromosom[1]), kromosom[3]))

    return 1 / (1 + fitness)

# Seleksi k-Tournament
def k_tournament_selection(populasi):
    selected_individuals = []
    for _ in range(len(populasi)): 
        tournament = random.sample(populasi, k)  
        tournament_fitness = [uji_fitness(individu) for individu in tournament]
        best_individual = tournament[tournament_fitness.index(max(tournament_fitness))]  
        selected_individuals.append(best_individual) 
    return selected_individuals

def one_point_crossover(populasi):
    offspring = []
    for i in range(0, len(populasi), 2):
        if i + 1 >= len(populasi): 
            break
        
        individu_1, individu_2 = populasi[i], populasi[i + 1]
        crossover_point = random.randint(1, len(individu_1) - 1)

        offspring_1 = individu_1[:crossover_point] + individu_2[crossover_point:]
        offspring_2 = individu_2[:crossover_point] + individu_1[crossover_point:]

        offspring.append(validasi_offspring(offspring_1))
        offspring.append(validasi_offspring(offspring_2))

    return offspring

def validasi_offspring(offspring):
    used_slots = set()
    used_dosen_slots = set()
    final = []
    
    for kromosom in offspring:
        nama = kromosom[0]
        dosen = cari_dosen(nama)
        valid_combination_found = False
        
        for jam, ruang, hari in product(paket, ruang_list, hari_list):
            # Cek konflik ruang dan waktu
            if (tuple(jam), ruang, hari) in used_slots:
                continue
                
            # Cek konflik dosen
            if any((d, tuple(jam), hari) in used_dosen_slots for d in dosen):
                continue
                
            # Jika valid, tambahkan ke hasil
            used_slots.add((tuple(jam), ruang, hari))
            for d in dosen:
                used_dosen_slots.add((d, tuple(jam), hari))
                
            final.append((nama, tuple(jam), ruang, hari))
            valid_combination_found = True
            break
            
        if not valid_combination_found:
            print(f"Warning: Tidak menemukan kombinasi valid untuk {nama}")
    
    return final

def scramble_mutation(populasi, mutation_rate=0.2):
    mutated_population = []
    
    for individu in populasi:
        if random.random() < mutation_rate:
            if len(individu) > 1:
                mutated_individu = individu.copy()
                max_attempts = 10
                for _ in range(max_attempts):
                    start = random.randint(0, len(mutated_individu) - 2)
                    end = random.randint(start + 1, len(mutated_individu) - 1)
                    segment = mutated_individu[start:end+1]
                    random.shuffle(segment)
                    temp_individu = mutated_individu[:start] + segment + mutated_individu[end+1:]
                    
                    # Validasi individu hasil mutasi
                    if validasi_offspring([temp_individu]):
                        mutated_individu = temp_individu
                        break
                
                mutated_population.append(mutated_individu)
            else:
                mutated_population.append(individu)
        else:
            mutated_population.append(individu)
    
    return mutated_population

def replacement(generasi, offspring):
    selected_individuals = []
    gabungan_populasi = generasi + offspring
    remaining_population = gabungan_populasi.copy()

    for _ in range(len(generasi)):
        tournament = random.sample(remaining_population, k)
        tournament_fitness = [uji_fitness(individu) for individu in tournament]
        best_individual = tournament[tournament_fitness.index(max(tournament_fitness))]
        selected_individuals.append(best_individual)
        remaining_population.remove(best_individual)

    return selected_individuals

def run_genetic_algorithm(generasi):
    start_time = time.time() 
    iteration = 0 
    best_individual = None  
    best_fitness = float('-inf')  
    all_best_individuals = []  

    print("Sudah membuat kromosom")
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > max_runtime: 
            print("Algoritma berhenti karena waktu lebih dari batas yang ditentukan.")
            break

        if iteration >= max_iterations:
            print("Algoritma berhenti karena telah mencapai jumlah iterasi maksimum.")
            break

        selected_individuals = k_tournament_selection(generasi)
        offspring = one_point_crossover(selected_individuals)
        offspring = scramble_mutation(offspring, mutation_rate=0.2)
        generasi = replacement(generasi, offspring)
        
        for individu in generasi:
            fitness = uji_fitness(individu)
            if fitness == 1: 
                print("Algoritma berhenti karena ditemukan solusi optimal (fitness = 1).")
                return individu, all_best_individuals  # Return immediately if optimal solution is found

            if fitness > best_fitness:
                best_fitness = fitness
                best_individual = individu

        all_best_individuals.append(best_individual)
        iteration += 1 
        print(f"Iterasi: {iteration}, Waktu berjalan: {elapsed_time / 60:.2f} menit")

    return best_individual, all_best_individuals

# Main execution
generasi = buat_generasi()
hasil, all_best_individuals = run_genetic_algorithm(generasi)

for idx, best in enumerate(all_best_individuals):
    print(f"Generasi {idx + 1}: Individu Terbaik: {best}")

# Buat DataFrame
df = pd.DataFrame(hasil, columns=["Nama Mahasiswa", "Jam", "Ruang", "Hari"])
# Fungsi untuk menyimpan DataFrame ke Excel
sheet_name = "Hasil_GA"
def save_to_excel(df, excel_path):
    global sheet_name  # Declare sheet_name as global
    if os.path.exists(excel_path):
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(excel_path) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

# Simpan DataFrame ke Excel
save_to_excel(df, excel_path)
print(f"Data berhasil disimpan di sheet '{sheet_name}' pada file '{excel_path}'")
