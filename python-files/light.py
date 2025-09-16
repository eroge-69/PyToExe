#作者 Ekirynn https://gamebanana.com/members/2476279
#Author Ekirynn https://gamebanana.com/members/2476279
import os
import json
import hashlib
import shutil
import re
import tempfile
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("texture_optimizer.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 纹理文件匹配模式
TEXTURE_PATTERNS = [
    re.compile(r'.*Diffuse.*\.dds', re.IGNORECASE),
    re.compile(r'.*Map.*\.dds', re.IGNORECASE),
    re.compile(r'.*\.jpg.*', re.IGNORECASE),
]

# 回退信息文件
MANIFEST_FILE = "texture_manifest.json"

@dataclass
class TextureInfo:
    """纹理信息"""
    path: str               # 纹理完整路径
    mod_name: str           # 所在mod名称
    mod_index: int          # 所在mod的序号（计数）
    relative_path: str      # INI中记录的相对路径
    dir_name: str           # 所在目录名
    filename: str           # 文件名
    hash: str               # 文件哈希值

@dataclass
class ModInfo:
    """Mod信息"""
    name: str               # mod名称
    path: str               # mod路径
    ini_path: str           # ini文件路径
    index: int              # mod的序号（按扫描顺序计数）
    textures: List[TextureInfo]  # 包含的纹理

@dataclass
class INIUpdate:
    """INI文件更新记录"""
    path: str               # INI文件路径
    original_texture: str   # 原始纹理名
    new_texture: str        # 新纹理名

class TextureOptimizer:
    """纹理优化器"""
    
    def __init__(self):
        self.base_dir = os.getcwd()  # 当前工作目录
        self.mods: List[ModInfo] = []
        self.textures: List[TextureInfo] = []
        self.hash_map: Dict[str, List[TextureInfo]] = {}  # 哈希到纹理的映射
        self.manifest: Dict[str, Any] = {
            "operation_time": "",
            "moved_textures": [],
            "updated_inis": []
        }
        self.temp_dir = None
        
    def scan_mods(self) -> None:
        """扫描所有mod文件夹和纹理文件，为每个mod分配序号"""
        logger.info(f"开始扫描mod文件夹，基准目录: {self.base_dir}")
    
        # 创建res目录（如果不存在）
        res_dir = os.path.join(self.base_dir, "res")
        os.makedirs(res_dir, exist_ok=True)
    
        mod_index = 1  # 为mod分配序号，从1开始
    
        # 递归扫描mod文件夹
        for root, dirs, _ in os.walk(self.base_dir):
            for dir in dirs:
                if dir.lower() != "res":
                    item_path = os.path.join(root, dir)
                    # 检查是否包含ini文件
                    ini_files = [f for f in os.listdir(item_path) 
                                if f.endswith(".ini") and not f.lower().startswith("disabled")]
                
                    if ini_files:
                        ini_path = os.path.join(item_path, ini_files[0])
                        mod_info = ModInfo(
                            name=dir,
                            path=item_path,
                            ini_path=ini_path,
                            index=mod_index,  # 分配序号
                            textures=[]
                        )
                        self.mods.append(mod_info)
                        logger.info(f"找到mod[{mod_index}]: {dir}, ini文件: {ini_files[0]}")
                    
                        # 扫描纹理文件
                        self._scan_textures_in_mod(mod_info)
                        mod_index += 1  # 序号递增
    
        logger.info(f"扫描完成，共找到 {len(self.mods)} 个mod文件夹")
        logger.info(f"共找到 {len(self.textures)} 个纹理文件")
    
    def _scan_textures_in_mod(self, mod_info: ModInfo) -> None:
        """扫描mod文件夹中的纹理文件"""
        for root, _, files in os.walk(mod_info.path):
            for file in files:
                # 检查是否为纹理文件
                if any(pattern.match(file) for pattern in TEXTURE_PATTERNS):
                    texture_path = os.path.join(root, file)
                    
                    # 计算相对路径（相对于mod目录）
                    relative_path = os.path.relpath(texture_path, mod_info.path)
                    # 转换为INI中的格式
                    relative_path_ini = ".\\" + relative_path.replace("/", "\\")
                    
                    # 提取目录名
                    dir_name = os.path.dirname(relative_path)
                    
                    # 计算哈希
                    file_hash = self._calculate_file_hash(texture_path)
                    if not file_hash:
                        continue  # 哈希计算失败则跳过
                    
                    texture_info = TextureInfo(
                        path=texture_path,
                        mod_name=mod_info.name,
                        mod_index=mod_info.index,  # 记录mod的序号
                        relative_path=relative_path_ini,
                        dir_name=dir_name,
                        filename=file,
                        hash=file_hash
                    )
                    
                    mod_info.textures.append(texture_info)
                    self.textures.append(texture_info)
                    
                    # 更新哈希映射
                    if texture_info.hash not in self.hash_map:
                        self.hash_map[texture_info.hash] = []
                    self.hash_map[texture_info.hash].append(texture_info)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件的SHA-256哈希值"""
        hash_obj = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败: {file_path}, 错误: {str(e)}")
            return ""
    
    def find_duplicate_textures(self) -> Dict[str, List[TextureInfo]]:
        """查找重复的纹理"""
        duplicates = {}
        for hash_value, textures in self.hash_map.items():
            if len(textures) > 1:
                duplicates[hash_value] = textures
                logger.info(f"找到重复纹理，哈希: {hash_value[:8]}..., 数量: {len(textures)}")
        return duplicates
    
    def generate_new_texture_names(self, duplicates: Dict[str, List[TextureInfo]]) -> Dict[str, str]:
        """生成新的纹理名称（基于mod序号计数）"""
        new_names = {}
        
        for hash_value, textures in duplicates.items():
            # 找到最短的文件名作为基础
            base_names = [os.path.splitext(t.filename)[0] for t in textures]
            shortest_name = min(base_names, key=len)
            
            # 获取使用该纹理的mod序号
            mod_indices = sorted({t.mod_index for t in textures})  # 使用mod的序号
            mod_suffix = "".join(str(i) for i in mod_indices)  # 拼接序号为字符串
            
            # 检查是否有同名但不同哈希的纹理（避免命名冲突）
            same_base_textures = [t for t in self.textures 
                                 if os.path.splitext(t.filename)[0] == shortest_name]
            
            # 如果有多个同名纹理，添加计数器前缀（0表示第一个，1表示第二个，以此类推）
            if len(same_base_textures) > 1:
                # 找到当前纹理在同名纹理中的索引
                texture_index = next((i for i, t in enumerate(same_base_textures) if t.hash == hash_value), 0)
                prefix = str(texture_index)
            else:
                prefix = "0"
            
            # 生成新名称（基础名 + 前缀 + mod序号后缀 + 扩展名）
            extension = os.path.splitext(textures[0].filename)[1]
            new_name = f"{shortest_name}{prefix}{mod_suffix}{extension}"
            new_names[hash_value] = new_name
            
            logger.info(f"哈希 {hash_value[:8]}... 的纹理将重命名为: {new_name}")
        
        return new_names
    
    def backup_ini_files(self) -> None:
        """备份INI文件"""
        for mod in self.mods:
            if os.path.exists(mod.ini_path):
                backup_path = os.path.join(
                    os.path.dirname(mod.ini_path), 
                    f"DISABLED_Light_{os.path.basename(mod.ini_path)}"
                )
                
                # 检查备份文件是否已存在
                if not os.path.exists(backup_path):
                    try:
                        shutil.copy2(mod.ini_path, backup_path)
                        logger.info(f"备份INI文件: {mod.ini_path} -> {backup_path}")
                    except Exception as e:
                        logger.error(f"备份INI文件失败: {mod.ini_path}, 错误: {str(e)}")
                        raise
    
    def move_textures_to_res(self, duplicates: Dict[str, List[TextureInfo]], 
                             new_names: Dict[str, str]) -> None:
        """将重复纹理移动到res目录，并删除其他差分目录中的重复纹理"""
        res_dir = os.path.join(self.base_dir, "res")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(dir=self.base_dir)
        logger.info(f"创建临时目录: {self.temp_dir}")
        
        try:
            for hash_value, textures in duplicates.items():
                new_name = new_names[hash_value]
                target_path = os.path.join(res_dir, new_name)
                
                # 选择第一个纹理作为保留文件（复制到res）
                keep_texture = textures[0]
                
                # 记录移动信息（用于回退）
                moved_texture_info = {
                    "original_path": keep_texture.path,
                    "relative_path": keep_texture.relative_path,
                    "new_name": new_name,
                    "used_mods": [t.mod_name for t in textures],
                    "used_mod_indices": [t.mod_index for t in textures]
                }
                self.manifest["moved_textures"].append(moved_texture_info)
                
                # 复制保留的纹理到临时目录
                temp_target = os.path.join(self.temp_dir, new_name)
                shutil.copy2(keep_texture.path, temp_target)
                logger.info(f"复制主纹理到临时目录: {keep_texture.path} -> {temp_target}")
                
                # 删除重复纹理
                for texture in textures:
                        if os.path.exists(texture.path):
                            os.remove(texture.path)
                            logger.info(f"删除冗余纹理: {texture.path}")
                        else:
                            logger.warning(f"冗余纹理不存在，跳过删除: {texture.path}")
                
                # 记录所有重复纹理的原始路径（用于回退）
                for texture in textures[1:]:  
                    moved_texture_info = {
                        "original_path": texture.path,
                        "relative_path": texture.relative_path,
                        "new_name": new_name,
                        "used_mods": [t.mod_name for t in textures],
                        "used_mod_indices": [t.mod_index for t in textures]
                    }
                    self.manifest["moved_textures"].append(moved_texture_info)
            
            # 将临时目录中的纹理移动到res目录
            for item in os.listdir(self.temp_dir):
                temp_item_path = os.path.join(self.temp_dir, item)
                res_item_path = os.path.join(res_dir, item)
                shutil.move(temp_item_path, res_item_path)
                logger.info(f"移动主纹理到res目录: {temp_item_path} -> {res_item_path}")
            
            # 清理临时目录
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            logger.info("临时目录清理完成")
            
        except Exception as e:
            logger.error(f"处理纹理时出错: {str(e)}")
            # 出错时回滚：删除临时目录和可能生成的res文件
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            # 删除可能已生成的res文件
            for item in os.listdir(res_dir):
                if item in [os.path.basename(p) for p in os.listdir(self.temp_dir)]:
                    os.remove(os.path.join(res_dir, item))
            self.temp_dir = None
            raise
    
    def update_ini_files(self, duplicates: Dict[str, List[TextureInfo]], 
                         new_names: Dict[str, str]) -> None:
        """更新INI文件引用"""
        # 创建INI更新记录
        ini_updates: Dict[str, List[INIUpdate]] = {}
        
        # 收集所有需要更新的INI文件
        for hash_value, textures in duplicates.items():
            new_name = new_names[hash_value]
            
            for texture in textures:
                mod_info = next((m for m in self.mods if m.name == texture.mod_name), None)
                if mod_info:
                    if mod_info.ini_path not in ini_updates:
                        ini_updates[mod_info.ini_path] = []
                    
                    ini_updates[mod_info.ini_path].append(INIUpdate(
                        path=mod_info.ini_path,
                        original_texture=texture.filename,
                        new_texture=new_name
                    ))
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(dir=self.base_dir)
        
        try:
            # 更新每个INI文件
            for ini_path, updates in ini_updates.items():
                # 读取INI文件
                with open(ini_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 创建临时文件
                temp_ini_path = os.path.join(temp_dir, os.path.basename(ini_path))
                
                # 记录更新内容
                updated = False
                with open(temp_ini_path, 'w', encoding='utf-8') as f:
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        
                        # 检查是否是[Resource...]部分
                        if line.startswith("[Resource"):
                            resource_name = line.strip("[]")
                            # 查找下一行的filename
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                if next_line.startswith("filename"):
                                    # 提取当前纹理名（只取文件名，忽略路径）
                                    current_texture_full = next_line.split("=")[1].strip()
                                    current_texture = os.path.basename(current_texture_full)
                                    
                                    # 检查是否需要更新
                                    for update in updates:
                                        if current_texture.lower() == update.original_texture.lower():
                                            # 更新filename行
                                            new_line = f"filename = ..\\res\\{update.new_texture}\n"
                                            f.write(line + "\n")
                                            f.write(new_line)
                                            i += 2
                                            updated = True
                                            
                                            # 记录更新（用于回退）
                                            self.manifest["updated_inis"].append({
                                                "ini_path": ini_path,
                                                "original_texture": update.original_texture,
                                                "new_texture": update.new_texture
                                            })
                                            break
                                    else:
                                        # 无匹配更新，写入原始行
                                        f.write(line + "\n")
                                        f.write(lines[i + 1])
                                        i += 2
                                else:
                                    f.write(line + "\n")
                                    i += 1
                            else:
                                f.write(line + "\n")
                                i += 1
                        else:
                            f.write(line + "\n")
                            i += 1
                
                # 替换原始INI文件（原子操作）
                if updated:
                    shutil.copy2(temp_ini_path, ini_path)
                    logger.info(f"更新INI文件: {ini_path}")
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"更新INI文件失败: {str(e)}")
            shutil.rmtree(temp_dir)
            raise
    
    def save_manifest(self) -> None:
        """保存操作记录（用于回退）"""
        import datetime
        self.manifest["operation_time"] = datetime.datetime.now().isoformat()
        
        manifest_path = os.path.join(self.base_dir, MANIFEST_FILE)
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"操作记录已保存到: {manifest_path}")
    
    def optimize_textures(self) -> None:
        """执行纹理优化"""
        try:
            logger.info("===== 开始纹理优化 =====")
            
            # 1. 扫描mod和纹理
            self.scan_mods()
            
            # 2. 查找重复纹理
            duplicates = self.find_duplicate_textures()
            if not duplicates:
                logger.info("未找到重复纹理，无需优化")
                return
            
            # 3. 生成新纹理名称
            new_names = self.generate_new_texture_names(duplicates)
            
            # 4. 备份INI文件
            self.backup_ini_files()
            
            # 5. 移动主纹理到res，并删除其他重复纹理
            self.move_textures_to_res(duplicates, new_names)
            
            # 6. 更新INI文件中的纹理引用
            self.update_ini_files(duplicates, new_names)
            
            # 7. 保存操作记录（用于回退）
            self.save_manifest()
            
            logger.info("===== 纹理优化完成 =====")
            print("纹理优化完成！冗余纹理已删除，详情请查看texture_optimizer.log")
            
        except Exception as e:
            logger.error(f"纹理优化失败: {str(e)}")
            print(f"纹理优化失败: {str(e)}")
            # 出错时清理临时文件
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    @staticmethod
    def rollback_changes() -> None:
        """回退所有更改（恢复原始纹理和INI）"""
        base_dir = os.getcwd()
        manifest_path = os.path.join(base_dir, MANIFEST_FILE)
        
        if not os.path.exists(manifest_path):
            print(f"未找到操作记录文件，无法回退: {manifest_path}")
            return
        
        try:
            logger.info("===== 开始回退操作 =====")
            
            # 读取操作记录
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 创建临时目录用于原子操作
            temp_dir = tempfile.mkdtemp(dir=base_dir)
            
            try:
                # 1. 恢复纹理文件
                res_dir = os.path.join(base_dir, "res")
                moved_textures = manifest.get("moved_textures", [])
                
                # 按新名称分组纹理（避免重复复制）
                textures_by_new_name = {}
                for texture_info in moved_textures:
                    new_name = texture_info["new_name"]
                    if new_name not in textures_by_new_name:
                        textures_by_new_name[new_name] = []
                    textures_by_new_name[new_name].append(texture_info)
                
                # 复制纹理到原始位置
                for new_name, texture_infos in textures_by_new_name.items():
                    source_path = os.path.join(res_dir, new_name)
                    if os.path.exists(source_path):
                        for texture_info in texture_infos:
                            original_path = texture_info["original_path"]
                            original_dir = os.path.dirname(original_path)
                            os.makedirs(original_dir, exist_ok=True)  # 确保目录存在
                            
                            # 先复制到临时目录（确保原子性）
                            temp_path = os.path.join(temp_dir, f"temp_{os.path.basename(original_path)}")
                            shutil.copy2(source_path, temp_path)
                            
                            # 移动到原始位置
                            shutil.move(temp_path, original_path)
                            logger.info(f"已恢复纹理: {original_path}")
                    else:
                        logger.warning(f"源纹理不存在，无法恢复: {source_path}")
                
                # 2. 恢复INI文件（使用备份的DISABLED_Light_文件）
                updated_inis = manifest.get("updated_inis", [])
                ini_files = set(ini_info["ini_path"] for ini_info in updated_inis)
                
                for ini_path in ini_files:
                    backup_path = os.path.join(
                        os.path.dirname(ini_path), 
                        f"DISABLED_Light_{os.path.basename(ini_path)}"
                    )
                    
                    if os.path.exists(backup_path):
                        # 恢复原始INI文件
                        shutil.copy2(backup_path, ini_path)
                        logger.info(f"已恢复INI文件: {ini_path}")
                        # 删除备份文件
                        os.remove(backup_path)
                        logger.info(f"已删除备份INI: {backup_path}")
                    else:
                        logger.warning(f"INI备份文件不存在，无法恢复: {backup_path}")
                
                # 3. 清理res目录中的纹理
                for new_name in textures_by_new_name:
                    res_file_path = os.path.join(res_dir, new_name)
                    if os.path.exists(res_file_path):
                        os.remove(res_file_path)
                        logger.info(f"已删除res目录中的纹理: {res_file_path}")
                
                # 4. 删除空的res目录
                if os.path.exists(res_dir) and not os.listdir(res_dir):
                    os.rmdir(res_dir)
                    logger.info("已删除空的res目录")
                
                # 5. 删除操作记录文件
                os.remove(manifest_path)
                logger.info(f"已删除操作记录: {manifest_path}")
                
                logger.info("===== 回退操作完成 =====")
                print("回退完成！所有纹理和INI已恢复原始状态")
                
            except Exception as e:
                logger.error(f"回退过程中出错: {str(e)}")
                print(f"回退过程中出错: {str(e)}")
                raise
            finally:
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
        except Exception as e:
            logger.error(f"回退失败: {str(e)}")
            print(f"回退失败: {str(e)}")

def main():
    """主函数"""
    print("纹理优化工具")
    print("1. 简化贴图（Remove Duplicate）")
    print("2. 执行回退（Rollback）")
    
    try:
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            optimizer = TextureOptimizer()
            optimizer.optimize_textures()
        elif choice == "2":
            TextureOptimizer.rollback_changes()
        else:
            print("无效的选择，请输入1或2")
            
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()