import os
import time
import PySimpleGUI as sg
from PIL import Image, ImageOps

# ----------------- 配置 -----------------
SIZE_MAP = {
    'XS':     (2.6, 52),
    'S':      (2.6, 62),
    'S-wide': (3.1, 62),
    'M':      (3.1, 77),
    'L':      (3.1, 87),
    'XL':     (3.1, 97),
}
DPI = 300
PAGE_WIDTH_CM = 29.7       # 固定宽度 29.7 cm
STRIP_SPACING_CM = 0.5     # 条与条之间间隔
MIRROR_GAP_CM = 0          # 原图与镜像之间无间隙
MARGIN_CM = 2              # 上下各保留 2 cm 白边
MAX_PER_PAGE = { 'XS':5, 'S':5, 'S-wide':4, 'M':4, 'L':4, 'XL':4 }

PREVIEW_W, PREVIEW_H = 600, 300  # 预览画布像素尺寸

sg.theme('LightGrey1')

layout = [
    [sg.Text('根目录:'), sg.Input(key='-ROOT-', size=(40,1), enable_events=True), sg.FolderBrowse('浏览目录')],
    [sg.Text('文件夹:'), sg.Combo([], key='-FOLDER-', size=(12,1), enable_events=True),
     sg.Text('图案:'),   sg.Combo([], key='-PATTERN-', size=(12,1)),
     sg.Text('尺寸:'),   sg.Combo(list(SIZE_MAP.keys()), key='-SIZE-', size=(6,1)),
     sg.Button('添加', key='-ADD-'), sg.Button('删除选中', key='-REMOVE-')],
    [sg.Text('已选列表（可多选后删除）：')],
    [sg.Listbox(values=[], key='-LIST-', size=(60,6), enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
    [sg.Button('◀ 上一页'), sg.Text('第0/0页', key='-PAGE-'), sg.Button('下一页 ▶')],
    [sg.Graph(
        canvas_size=(PREVIEW_W, PREVIEW_H),
        graph_bottom_left=(0, 0),
        graph_top_right=(PAGE_WIDTH_CM, max(h for w,h in SIZE_MAP.values()) + MARGIN_CM),
        background_color='white',
        key='-GRAPH-'
    )],
    [sg.Button('导出所有PNG'), sg.Button('清空列表'), sg.Button('退出')],
]

window = sg.Window('热转印排版工具 vFinal', layout, finalize=True)

entries = []   # 存放 (full_path, size)
cur_page = 0

def update_folders(root):
    if os.path.isdir(root):
        subs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
        window['-FOLDER-'].update(values=subs)

def update_patterns(root, fld):
    path = os.path.join(root, fld)
    if os.path.isdir(path):
        pts = sorted(os.path.splitext(f)[0] for f in os.listdir(path)
                     if f.lower().endswith(('.png','.jpg','.jpeg')))
        window['-PATTERN-'].update(values=pts)

def paginate(items):
    pages = []
    i = 0
    while i < len(items):
        cnt = MAX_PER_PAGE[items[i][1]]
        pages.append(items[i:i+cnt])
        i += cnt
    return pages

def draw_page(idx):
    pages = paginate(entries)
    total = len(pages)
    window['-PAGE-'].update(f'第{idx+1}/{total}页' if total else '第0/0页')
    g = window['-GRAPH-']; g.erase()
    if total == 0:
        return
    page = pages[idx]
    # 计算当页最高条的高度（cm）
    max_h = max(SIZE_MAP[s][1] for _,s in page)
    # 计算当页总宽度（cm）
    total_w = sum(2*SIZE_MAP[s][0] for _,s in page) + (len(page)-1)*STRIP_SPACING_CM
    # 居中起始 X（cm）
    x = (PAGE_WIDTH_CM - total_w) / 2
    for p, s in page:
        w_cm, h_cm = SIZE_MAP[s]
        # 顶部对齐：y = 上边距 + (max_h - 当前高度)
        y = MARGIN_CM + (max_h - h_cm)
        # 原图条
        g.draw_rectangle((x, y), (x + w_cm, y + h_cm), fill_color='tan', line_color='black')
        # 镜像条
        g.draw_rectangle((x + w_cm + MIRROR_GAP_CM, y),
                         (x + 2*w_cm + MIRROR_GAP_CM, y + h_cm),
                         fill_color='bisque', line_color='black')
        x += 2*w_cm + STRIP_SPACING_CM

while True:
    event, vals = window.read()
    if event in (sg.WIN_CLOSED, '退出'):
        break

    if event == '-ROOT-':
        update_folders(vals['-ROOT-'])
    if event == '-FOLDER-':
        update_patterns(vals['-ROOT-'], vals['-FOLDER-'])

    if event == '-ADD-':
        root, fld, pat, sz = vals['-ROOT-'], vals['-FOLDER-'], vals['-PATTERN-'], vals['-SIZE-']
        if not all([root, fld, pat, sz]):
            sg.popup_error('请完整选择：根目录、文件夹、图案、尺寸')
            continue
        base = os.path.join(root, fld, pat)
        full = None
        for ext in ('.png', '.jpg', '.jpeg'):
            if os.path.isfile(base + ext):
                full = base + ext
                break
        if not full:
            sg.popup_error(f'未找到文件：{pat}.*')
            continue
        entries.append((full, sz))
        window['-LIST-'].update([f"{os.path.basename(p)} ({s})" for p,s in entries])
        cur_page = 0
        draw_page(cur_page)

    if event == '-REMOVE-':
        sels = window['-LIST-'].get()
        if sels:
            # 过滤掉所有选中的项
            entries[:] = [
                (p,s) for p,s in entries
                if f"{os.path.basename(p)} ({s})" not in sels
            ]
            window['-LIST-'].update([f"{os.path.basename(p)} ({s})" for p,s in entries])
            # 重置分页
            cur_page = 0
            draw_page(cur_page)

    if event == '◀ 上一页':
        pages = paginate(entries)
        if pages and cur_page > 0:
            cur_page -= 1
            draw_page(cur_page)

    if event == '下一页 ▶':
        pages = paginate(entries)
        if pages and cur_page < len(pages)-1:
            cur_page += 1
            draw_page(cur_page)

    if event == '清空列表':
        entries.clear()
        window['-LIST-'].update([])
        window['-GRAPH-'].erase()
        window['-PAGE-'].update('第0/0页')
        cur_page = 0

    if event == '导出所有PNG':
        if not entries:
            sg.popup_error('列表为空，请先添加图案！')
            continue
        out_dir = os.path.join(vals['-ROOT-'], 'Output')
        os.makedirs(out_dir, exist_ok=True)
        pages = paginate(entries)
        for idx, page in enumerate(pages, start=1):
            # 最高条高 + 上下边距
            max_h = max(SIZE_MAP[s][1] for _,s in page)
            height_cm = max_h + 2*MARGIN_CM
            w_px = int(PAGE_WIDTH_CM / 2.54 * DPI)
            h_px = int(height_cm / 2.54 * DPI)
            canvas = Image.new('RGB', (w_px, h_px), 'white')
            # 计算居中起始cm
            total_w = sum(2*SIZE_MAP[s][0] for _,s in page) + (len(page)-1)*STRIP_SPACING_CM
            used_cm = (PAGE_WIDTH_CM - total_w) / 2
            for p,s in page:
                w_cm,h_cm = SIZE_MAP[s]
                w1 = int(w_cm/2.54 * DPI)
                h1 = int(h_cm/2.54 * DPI)
                img = Image.open(p).resize((w1, h1), Image.LANCZOS)
                mir = ImageOps.mirror(img)
                x_px = int(used_cm / 2.54 * DPI)
                y_px = int((MARGIN_CM + (max_h - h_cm)) / 2.54 * DPI)
                canvas.paste(img, (x_px, y_px))
                canvas.paste(mir, (x_px + w1, y_px))
                used_cm += 2*w_cm + STRIP_SPACING_CM
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'Page_{idx:02d}_{timestamp}.png'
            canvas.save(os.path.join(out_dir, filename))
        sg.popup('完成', f'已导出 {len(pages)} 页 PNG，保存至：\n{out_dir}')

window.close()
