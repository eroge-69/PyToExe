# -*- coding: utf-8 -*-
"""
Ten skrypt w Pythonie generuje plik HTML zawierający edytowalną tabelę,
z tłem Rias Gremory i żółtą czcionką, zgodnie z wcześniejszymi specyfikacjami.
"""

def generate_html_table():
    """
    Generuje pełny kod HTML edytowalnej tabeli.
    """
    html_content = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edytowalna Tabela Google Arkusze z przezroczystym tłem</title>
    <!-- Ładowanie Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Ustawienie domyślnej czcionki Inter */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5; /* Delikatne tło awaryjne */
            display: flex;
            justify-content: center;
            align-items: flex-start; /* Wyrównanie do góry */
            min-height: 100vh;
            padding: 20px;
            box-sizing: border-box;

            /* Tło z Rias Gremory */
            /* Zaktualizowany URL obrazka. Jeśli ten nie działa, wklej swój własny, stabilny URL obrazka Rias Gremory. */
            background-image: url('https://a.allegroimg.com/original/11870f/12698fba460c9c20afcc90ca7eed/Plakat-A3-High-School-DxD-Anime-Rias-Gremory');
            background-size: cover; /* Pokryj całe tło */
            background-position: center; /* Wyśrodkuj obrazek */
            background-attachment: fixed; /* Tło pozostaje nieruchome podczas scrollowania */
            position: relative; /* Potrzebne dla nakładki */
        }

        /* Nakładka na tło dla lepszej czytelności tekstu */
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5); /* Półprzezroczysta czarna nakładka */
            z-index: -1; /* Umieść pod zawartością */
        }

        /* Styl dla edytowalnych komórek */
        td[contenteditable="true"]:focus {
            outline: 2px solid #34D399; /* Zielona ramka po kliknięciu */
            background-color: rgba(249, 250, 251, 0.7); /* Lekkie półprzezroczyste tło po kliknięciu */
        }
        td {
            min-width: 120px; /* Minimalna szerokość komórek dla lepszej czytelności */
        }
    </style>
</head>
<body>
    <div class="container mx-auto p-4 bg-transparent shadow-lg rounded-lg max-w-5xl w-full">
        <!-- Nagłówek tabeli -->
        <div class="flex items-center justify-between p-3 bg-gray-100 bg-opacity-70 rounded-t-lg border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-800">Tabela1</h2>
            <!-- Ikony mogą być dodane tutaj, np. za pomocą Lucide Icons lub SVG -->
            <div>
                <!-- Przykładowe ikony SVG, można zastąpić prawdziwymi -->
                <svg class="inline-block w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
                <svg class="inline-block w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            </div>
        </div>

        <!-- Główna część tabeli -->
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-emerald-700 bg-opacity-80"> <!-- Kolor nagłówka jak na zrzucie ekranu, z lekką przezroczystością -->
                    <tr>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[#fcec03] uppercase tracking-wider rounded-tl-md">
                            CZAS
                            <span class="inline-block ml-1 text-[#fcec03]">&#9660;</span> <!-- Strzałka w dół dla filtra -->
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[#fcec03] uppercase tracking-wider">
                            LDZ
                            <span class="inline-block ml-1 text-[#fcec03]">&#9660;</span>
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[#fcec03] uppercase tracking-wider">
                            WRO
                            <span class="inline-block ml-1 text-[#fcec03]">&#9660;</span>
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[#fcec03] uppercase tracking-wider rounded-tr-md">
                            CZAS WRO
                            <span class="inline-block ml-1 text-[#fcec03]">&#9660;</span>
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-transparent divide-y divide-gray-200">
                    <!-- Wiersze danych będą generowane przez JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Funkcja do formatowania daty i czasu
        function formatDateTime(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        }

        // Funkcja do obsługi edycji komórek
        function handleCellEdit(event) {
            const cell = event.target;
            const row = cell.dataset.row; // Pobiera indeks wiersza z atrybutu data-row
            const col = cell.dataset.col; // Pobiera indeks kolumny z atrybutu data-col
            const newValue = cell.textContent;

            console.log(`Cell [${row}, ${col}] changed to: ${newValue}`);

            let timestampCell = null;

            // Sprawdź, która kolumna danych została edytowana i ustaw odpowiednią komórkę czasu
            if (col === '1') { // Kolumna "LDZ" (indeks 1)
                timestampCell = document.querySelector(`[data-row="${row}"][data-col="0"]`); // Kolumna "CZAS" (indeks 0)
            } else if (col === '2') { // Kolumna "WRO" (indeks 2)
                timestampCell = document.querySelector(`[data-row="${row}"][data-col="3"]`); // Kolumna "CZAS WRO" (indeks 3)
            }

            if (timestampCell) {
                // Jeśli edytowana komórka ma jakąś wartość, ustaw znacznik czasu
                if (newValue.trim() !== '') {
                    // Sprawdź, czy znacznik czasu już istnieje
                    if (timestampCell.textContent.trim() === '') {
                        timestampCell.textContent = formatDateTime(new Date());
                    }
                } else {
                    // Jeśli edytowana komórka jest pusta, wyczyść znacznik czasu
                    timestampCell.textContent = '';
                }
            }
        }

        // Dodaj słuchacze zdarzeń do wszystkich edytowalnych komórek po załadowaniu DOM
        document.addEventListener('DOMContentLoaded', () => {
            const tbody = document.querySelector('tbody');
            const numRows = 14; // Liczba wierszy danych (od wiersza 2 do 15)
            const numCols = 4; // Liczba kolumn (CZAS, LDZ, WRO, CZAS WRO)

            for (let i = 0; i < numRows; i++) {
                const rowElement = document.createElement('tr');
                for (let j = 0; j < numCols; j++) {
                    const cell = document.createElement('td');
                    // Zmieniono kolor tekstu na #fcec03
                    cell.classList.add('px-6', 'py-3', 'whitespace-nowrap', 'text-sm', 'text-[#fcec03]');

                    // Dodaj prawą ramkę do wszystkich kolumn oprócz ostatniej
                    if (j < numCols - 1) {
                        cell.classList.add('border-r', 'border-gray-200');
                    }

                    cell.setAttribute('data-row', i + 1); // Indeks wiersza (od 1)
                    cell.setAttribute('data-col', j);     // Indeks kolumny (od 0)

                    // Ustaw komórki kolumn 'LDZ' (1) i 'WRO' (2) jako edytowalne
                    if (j === 1 || j === 2) {
                        cell.setAttribute('contenteditable', 'true');
                        cell.classList.add('editable-cell'); // Dodaj klasę dla łatwego dostępu w JS
                    } else {
                        // Kolumny 'CZAS' (0) i 'CZAS WRO' (3) nie są edytowalne ręcznie
                        cell.setAttribute('contenteditable', 'false');
                    }

                    rowElement.appendChild(cell);
                }
                tbody.appendChild(rowElement);
            }

            // Po wygenerowaniu wszystkich komórek, dodaj słuchacze zdarzeń
            const cells = document.querySelectorAll('.editable-cell');
            cells.forEach(cell => {
                cell.addEventListener('blur', handleCellEdit); // Użyj 'blur' aby wykryć zakończenie edycji
                cell.addEventListener('keydown', (event) => {
                    if (event.key === 'Enter') {
                        event.preventDefault(); // Zapobiegaj nowej linii po naciśnięciu Enter
                        event.target.blur(); // Zakończ edycję
                    }
                });
            });
        });
    </script>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    html_output = generate_html_table()
    file_name = "table_with_rias_gremory.html"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_output)
        print(f"Plik '{file_name}' został pomyślnie wygenerowany.")
        print("Otwórz plik w przeglądarce, aby zobaczyć tabelę.")
    except IOError as e:
        print(f"Wystąpił błąd podczas zapisu pliku: {e}")

