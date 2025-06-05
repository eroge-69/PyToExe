import os

if not os.path.exists('ExceptionManagement.xml'):
    input('ExceptionManagement.xml not found')
else:
    with open('ExceptionManagement.xml', 'r') as file, open('ExceptionManagement-new.xml', 'w') as file_new:
        pending_id_line = None  # 暫存 <ID> 的那一行
        id_prefix = '01'        # 預設為 Common

        for line in file:
            stripped_line = line.strip()

            if stripped_line.startswith('<ID>'):
                pending_id_line = line  # 暫存，等看到 Module 再決定寫入內容
                continue

            elif stripped_line.startswith('<Module>'):
                # 根據 Module 的內容決定 prefix 與標籤
                if 'Left' in line:
                    id_prefix = '11'
                    line = line.replace('<Module> ', '<Module> ***ModuleLeft***')
                elif 'Right' in line:
                    id_prefix = '21'
                    line = line.replace('<Module> ', '<Module> ***ModuleRight***')
                else:
                    id_prefix = '01'
                    line = line.replace('<Module> ', '<Module> ***Common***')

                # 現在可以處理剛剛的 <ID> 行
                if pending_id_line:
                    id_str = pending_id_line.strip().replace('<ID>', '').replace('</ID>', '').strip()
                    id_str = id_str.zfill(6)  # 補滿6碼
                    new_id_line = f'        <ID> {id_prefix}{id_str} </ID>\n'
                    file_new.write(new_id_line)
                    pending_id_line = None  # 清除暫存

                file_new.write(line)

            else:
                if pending_id_line:
                    # 如果沒有對應 Module，仍用預設 prefix 處理 ID
                    id_str = pending_id_line.strip().replace('<ID>', '').replace('</ID>', '').strip()
                    id_str = id_str.zfill(6)
                    new_id_line = f'        <ID> {id_prefix}{id_str} </ID>\n'
                    file_new.write(new_id_line)
                    pending_id_line = None

                file_new.write(line)

    input('New file exported to ExceptionManagement-new.xml')
