import os

# 要移除的完整节名（包括方括号）
target_sections = [
    "[TextureOverrideJuFufu.BodyA.LightMap.1024]",
    "[TextureOverrideJuFufu.Body.IB]"
]

def should_skip(filename):
    return os.path.basename(filename).lower().startswith("disabled")

def process_ini_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"❌ 无法读取文件: {filepath} - 错误: {e}")
        return

    print(f"\n📄 正在处理文件: {filepath}")
    output_lines = []
    inside_target_section = False
    section_name = None
    modified = False
    found_sections = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section_name = stripped
            inside_target_section = section_name in target_sections
            if inside_target_section:
                found_sections.append(section_name)
                modified = True
                print(f"  🔴 移除节: {section_name}")
                continue  # 跳过节头本身
        if inside_target_section:
            continue  # 跳过节内容
        output_lines.append(line)

    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.writelines(output_lines)
            print(f"  ✅ 已修改并保存文件: {filepath}")
        except Exception as e:
            print(f"  ❌ 写入失败: {filepath} - 错误: {e}")
    else:
        print(f"  ⚪ 未发现目标节，文件未修改")

def scan_and_process(folder='.'):
    file_count = 0
    for root, dirs, files in os.walk(folder):
        for name in files:
            if name.lower().endswith('.ini') and not should_skip(name):
                file_count += 1
                process_ini_file(os.path.join(root, name))
    return file_count

if __name__ == '__main__':
    print("=" * 60)
    print("📁 开始扫描当前目录及子目录中的 .ini 文件...")
    print("🚫 跳过文件名以 disabled 开头的文件（不区分大小写）")
    print("🔍 查找并删除以下目标节：")
    for sec in target_sections:
        print(f"   - {sec}")
    print("=" * 60)
    count = scan_and_process()
    print("\n" + "=" * 60)
    print(f"✅ 全部处理完成，共扫描了 {count} 个 .ini 文件。")
    print("按任意键退出...")
    input()
