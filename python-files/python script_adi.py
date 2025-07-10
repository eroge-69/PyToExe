def process_tiger_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    results = []
    for i in range(len(lines) - 1):
        line = lines[i].rstrip('\n')
        next_line = lines[i + 1].rstrip('\n')

        # Satır '0' ile bitiyorsa, bir sonraki satırı al
        if line.endswith('0'):
            results.append(next_line)

    # Son satırdan sonra satır olmayabileceği için kontrol etmedik

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for res_line in results:
            outfile.write(res_line + '\n')

if __name__ == '__main__':
    input_file = 'input.tiger'   # Girdi dosyanızın adı
    output_file = 'output.txt'   # Çıktı dosyasının adı
    process_tiger_file(input_file, output_file)
    print(f"İşlem tamamlandı. '{output_file}' dosyasına yazıldı.")
