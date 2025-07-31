"Anime reaction URL opener"
"Add to the list"

import webbrowser

file_name = r"C:\Users\Jehmary\Desktop\Anime-Reaction-URL-List.txt"

try:
    with open(file_name, 'r') as file:
        urls = file.readlines()
    print(urls)
except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found.")
    
for url in urls:
    webbrowser.open(url)