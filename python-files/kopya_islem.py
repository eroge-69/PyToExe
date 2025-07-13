def copy_lines_after_zero(input_file_path, output_file_path):
    """
    Belirtilen girdi dosyas�nda '0' ile biten her sat�rdan sonraki 6 sat�r�
    ��kt� dosyas�na kopyalar.

    Args:
        input_file_path (str): Girdi dosyas�n�n yolu (okunacak dosya).
        output_file_path (str): ��kt� dosyas�n�n yolu (yaz�lacak dosya).
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:
            
            lines = infile.readlines()
            copy_mode = False
            lines_to_copy_count = 0

            for line in lines:
                if copy_mode:
                    outfile.write(line)
                    lines_to_copy_count -= 1
                    if lines_to_copy_count == 0:
                        copy_mode = False
                
                if line.strip().endswith('0'):
                    copy_mode = True
                    lines_to_copy_count = 6
        
        print(f"��lem tamamland�! '{input_file_path}' dosyas�ndaki '0' ile biten sat�rlardan sonraki 6 sat�r '{output_file_path}' dosyas�na kopyaland�.")

    except FileNotFoundError:
        print(f"Hata: Belirtilen dosya bulunamad�: '{input_file_path}' veya '{output_file_path}'")
    except Exception as e:
        print(f"Bir hata olu�tu: {e}")
