# pdf_sorter_gui.py
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import shutil
import threading
import os
import tkinter as tk
from tkinter import filedialog, messagebox

PDF_SUFFIX = ".pdf"
MAX_WORKERS_DEFAULT = min(32, (os.cpu_count() or 4) * 2)

# === 处理策略 ===
# 重复文件名：仅挑一份代表（最近修改时间最大），拷到 output/duplicates/，若已存在则跳过
# 独有文件：拷到 output/unique_子文件夹名/，如重名冲突则自动在目标名后加 __from_子文件夹

_copy_lock = threading.Lock()

def safe_copy(src: Path, dst: Path, on_conflict: str = "suffix"):
    """
    复制文件到 dst。
    on_conflict:
      - 'skip'      : 目标已存在则跳过
      - 'overwrite' : 覆盖
      - 'suffix'    : 目标已存在则在文件名后追加 __from_子文件夹（用于独有文件极少数冲突）
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _copy_lock:
        if dst.exists():
            if on_conflict == "skip":
                return None
            elif on_conflict == "overwrite":
                shutil.copy2(src, dst)
                return dst
            elif on_conflict == "suffix":
                alt = dst.parent / f"{src.stem}__from_{src.parent.name}{src.suffix}"
                i = 2
                cur = alt
                while cur.exists():
                    cur = dst.parent / f"{src.stem}__from_{src.parent.name}({i}){src.suffix}"
                    i += 1
                shutil.copy2(src, cur)
                return cur
        else:
            shutil.copy2(src, dst)
            return dst

def collect_tasks(root_dir: Path, output_dir: Path):
    """
    生成复制任务：(src, dst, policy)
    """
    name_to_paths = defaultdict(list)
    subdirs = [d for d in root_dir.iterdir() if d.is_dir()]
    for sd in subdirs:
        for p in sd.iterdir():
            if p.is_file() and p.suffix.lower() == PDF_SUFFIX:
                name_to_paths[p.name].append(p)

    tasks = []
    for fname, paths in name_to_paths.items():
        if len(paths) == 1:
            src = paths[0]
            tasks.append((src, output_dir / f"unique_{src.parent.name}" / fname, "suffix"))
        else:
            representative = max(paths, key=lambda x: x.stat().st_mtime)
            tasks.append((representative, output_dir / "duplicates" / fname, "skip"))
    return tasks

def run_job(root_dir: Path, output_dir: Path, max_workers: int, clean_duplicates_before_run: bool = True):
    if clean_duplicates_before_run:
        shutil.rmtree(output_dir / "duplicates", ignore_errors=True)

    tasks = collect_tasks(root_dir, output_dir)
    if not tasks:
        print("未发现需要处理的 PDF 文件。")
        return 0

    with ThreadPoolExecutor(max_workers=max_workers) as ex, tqdm(total=len(tasks), desc="处理进度", unit="文件") as pbar:
        futures = [ex.submit(safe_copy, src, dst, policy) for src, dst, policy in tasks]
        for _ in as_completed(futures):
            pbar.update(1)

    print(f"完成：共计划处理 {len(tasks)} 个文件。")
    print(f"独有文件已保存到 {output_dir}/unique_*/")
    print(f"重复文件（每个文件名仅一份）已保存到 {output_dir}/duplicates/")
    return len(tasks)

def choose_directory(title: str) -> Path:
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    path = filedialog.askdirectory(title=title)
    root.destroy()
    return Path(path) if path else None

def main():
    # 1) 选择主文件夹
    root_dir = choose_directory("请选择主文件夹（包含若干子文件夹，每个子文件夹内是 PDF）")
    if not root_dir:
        messagebox.showwarning("提示", "未选择主文件夹，已取消。")
        return

    # 2) 选择输出文件夹
    output_dir = choose_directory("请选择输出文件夹（将创建 unique_* 与 duplicates）")
    if not output_dir:
        messagebox.showwarning("提示", "未选择输出文件夹，已取消。")
        return

    # 3) 可选：输入线程数
    max_workers = MAX_WORKERS_DEFAULT

    # 4) 二次确认
    confirm = messagebox.askyesno(
        "确认",
        f"主文件夹：{root_dir}\n输出文件夹：{output_dir}\n线程数：{max_workers}\n\n开始处理吗？"
    )
    if not confirm:
        return

    total = run_job(root_dir, output_dir, max_workers=max_workers, clean_duplicates_before_run=True)
    messagebox.showinfo("完成", f"处理完成！共计划处理 {total} 个文件。")

if __name__ == "__main__":
    main()
