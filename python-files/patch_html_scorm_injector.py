#!/usr/bin/env python3
"""
SCORM kodu ekleyici
- Belirtilen HTML dosyasını açar
- <script src="scorm-comm.js"> ekler (yoksa)
- Puan öğesini bulur (id: *score/skor/puan*), id yoksa atar
- Belirtilen buton id'sine tıklama işlevi ekler:
    const puan=Number(score.textContent)||0;
    window.etkinligiTamamlaVeRaporla({puan:puan, toplamPuan:TOPLAM_PUAN});
  (burada "score" otomatik olarak bulunan id adına çevrilir ve kullanım öncesinde const <id>=document.getElementById("<id>") tanımı eklenir)
- Yeni dosyayı çıktı olarak yazar
"""
import re
import sys
from pathlib import Path

def sanitize_var(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if not re.match(r'[A-Za-z_]', name):
        name = '_' + name
    return name

def ensure_scorm_script(html: str) -> str:
    if 'scorm-comm.js' in html:
        return html
    return re.sub(r'(<\s*body\b)', '<script src="scorm-comm.js"></script>\\1', html, flags=re.IGNORECASE, count=1)

def find_or_assign_score_id(html: str):
    m = re.search(r'id\s*=\s*"([^"]*(?:score|skor|puan)[^"]*)"', html, flags=re.IGNORECASE)
    if m:
        return html, m.group(1)
    m2 = re.search(r'<([a-zA-Z][\w:-]*)\b([^>]*?(?:data-role|data-score|class)\s*=\s*"[^"]*(?:score|skor|puan)[^"]*"[^>]*)>', html, flags=re.IGNORECASE)
    if m2:
        tag = m2.group(1)
        full_attrs = m2.group(2)
        new_id = 'score_auto'
        opening = f'<{tag}{full_attrs}>'
        if re.search(r'\bid\s*=', full_attrs, flags=re.IGNORECASE):
            idm = re.search(r'\bid\s*=\s*"([^"]+)"', full_attrs, flags=re.IGNORECASE)
            if idm:
                return html, idm.group(1)
        new_opening = f'<{tag}{full_attrs} id="{new_id}">'
        html = html.replace(opening, new_opening, 1)
        return html, new_id
    new_id = 'score'
    injection = f'<span id="{new_id}" style="display:none">0</span>'
    if re.search(r'</\s*body\s*>', html, flags=re.IGNORECASE):
        html = re.sub(r'(</\s*body\s*>)', injection + r'\\1', html, flags=re.IGNORECASE, count=1)
    else:
        html += injection
    return html, new_id

def ensure_button(html: str, button_id: str) -> str:
    if re.search(rf'id\s*=\s*"{re.escape(button_id)}"', html):
        return html
    btn = f'<button id="{button_id}">Etkinliği Bitir</button>'
    if re.search(r'</\s*body\s*>', html, flags=re.IGNORECASE):
        return re.sub(r'(</\s*body\s*>)', btn + r'\\1', html, flags=re.IGNORECASE, count=1)
    return html + btn

def inject_handler(html: str, button_id: str, score_id: str, toplam_puan_value: int = 100) -> str:
    var_name = sanitize_var(score_id)
    handler_js = f"""
<script>
(function(){{ 
  const TOPLAM_PUAN = {toplam_puan_value};
  const {var_name} = document.getElementById("{score_id}");
  document.getElementById("{button_id}").addEventListener("click", function(){{ 
    const puan=Number({var_name}.textContent)||0; 
    window.etkinligiTamamlaVeRaporla({{puan:puan, toplamPuan:TOPLAM_PUAN}});
  }});
}})();
</script>
""".strip()
    if re.search(r'</\s*body\s*>', html, flags=re.IGNORECASE):
        html = re.sub(r'(</\s*body\s*>)', handler_js + r'\\1', html, flags=re.IGNORECASE, count=1)
    else:
        html += handler_js
    return html

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python patch_html_scorm_injector.py <girdi.html> [butonId] [toplamPuan] [cikti.html]")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    button_id = sys.argv[2] if len(sys.argv) > 2 else "finishBtn"
    toplam_puan_value = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    output_path = Path(sys.argv[4]) if len(sys.argv) > 4 else input_path.with_name(input_path.stem + "_patched.html")

    html = input_path.read_text(encoding="utf-8")
    html = ensure_scorm_script(html)
    html, score_id = find_or_assign_score_id(html)
    html = ensure_button(html, button_id)
    html = inject_handler(html, button_id, score_id, toplam_puan_value)
    output_path.write_text(html, encoding="utf-8")
    print(f"Tamam: skor id='{score_id}' bulundu/atanıp, buton='{button_id}' işlem bağlandı -> {output_path}")

if __name__ == "__main__":
    main()
