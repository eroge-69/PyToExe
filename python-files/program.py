import pdfplumber
import json

def parse_items(lines):
    items = []
    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines):
            break
        line1 = lines[i]
        line2 = lines[i + 1]

        def get(line, idx):
            return line[idx] if line and len(line) > idx and line[idx] else ""

        # Phân tích field tên sản phẩm
        name_field = get(line1, 3)
        name_en, quy_cach, name_vn = "", "", ""
        if name_field:
            name_parts = name_field.split("\n")
            name_en = name_parts[0] if len(name_parts) > 0 else ""
            # Nếu có ít nhất 3 dòng: EN, QC, VN
            if len(name_parts) > 2:
                quy_cach = name_parts[1]
                name_vn = name_parts[2]
            # Nếu chỉ có 2 dòng: EN, VN (không có quy cách)
            elif len(name_parts) == 2:
                quy_cach = ""
                name_vn = name_parts[1]
            else:
                quy_cach = ""
                name_vn = ""

        # Tách ĐVT, SL/ĐV, SL mua từ cột [4] (ví dụ 'EA 1 8')
        dvt, sl_dv, sl_mua = "", "", ""
        qc_field = get(line1, 4)
        if qc_field:
            qc_parts = qc_field.split()
            dvt = qc_parts[0] if len(qc_parts) > 0 else ""
            sl_dv = qc_parts[1] if len(qc_parts) > 1 else ""
            sl_mua = qc_parts[2] if len(qc_parts) > 2 else ""

        item = {
            "STT": get(line1, 0),
            "ma_vach": get(line1, 1),
            "barcode": get(line2, 1),
            "ten_san_pham": {
                "en": name_en,
                "vi": name_vn
            },
            "quy_cach": quy_cach,
            "dvt": dvt,
            "sl_dv": sl_dv,
            "sl_mua": sl_mua,
            "don_gia": get(line1, 6),
            "thanh_tien": get(line1, 7),
            "ghi_chu": get(line1, 9),
        }
        items.append(item)
    return items

if __name__ == "__main__":
    with pdfplumber.open("Text.pdf") as pdf:
        page = pdf.pages[0]
        table = page.extract_table()
        if table:
            lines = table[6:]  # Bỏ header
            items = parse_items(lines)
            with open("chobani_items.json", "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            print("Đã xuất file chobani_items.json!")