import argparse
import json
import os
import shutil
import hashlib
import base64
import hmac
import hashlib
import requests
from datetime import datetime, timezone

# 阿里云OSS配置
OSS_CONFIG = {
    'bucket_name': 'oss-jianying-resource',
    'endpoint': 'https://oss-cn-hangzhou.aliyuncs.com',
    'host': 'oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com'  # 添加host配置
}

def get_file_hash(file_path):
    """计算文件的MD5哈希值"""
    if os.path.isdir(file_path):
        # 如果是目录，使用目录名作为哈希的一部分
        return hashlib.md5(file_path.encode()).hexdigest()
    else:
        # 如果是文件，计算文件内容的哈希值
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

def is_archive_file(file_path):
    """检查文件是否为已知的压缩文件格式"""
    # 检查文件扩展名
    extensions = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]
    return any(file_path.lower().endswith(ext) for ext in extensions)

def process_path(original_path, target_path, output_dir):
    """处理单个路径，根据是文件夹还是文件决定处理方式"""
    # 确保目标目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 如果原始路径不存在但目标路径存在，则使用目标路径
    source_path = original_path if os.path.exists(original_path) else target_path
    
    if not os.path.exists(source_path):
        print(f"警告: 路径不存在: {source_path}")
        return None
    
    # 获取文件名（不带路径）
    file_name = os.path.basename(source_path)
    
    # 判断是文件夹还是文件
    if os.path.isdir(source_path):
        # 如果是文件夹，创建zip
        # 移除可能的文件扩展名，避免重复的.zip后缀
        base_name = os.path.splitext(os.path.join(output_dir, file_name))[0]
        
        # shutil.make_archive会自动添加.zip后缀
        output_file = shutil.make_archive(base_name, 'zip', source_path)
        processed_type = "zipped_directory"
    else:
        # 如果是文件
        if is_archive_file(source_path):
            # 如果已经是压缩文件，直接复制
            output_file = os.path.join(output_dir, file_name)
            shutil.copy2(source_path, output_file)
            processed_type = "copied_archive"
        else:
            # 如果是普通文件，直接复制
            output_file = os.path.join(output_dir, file_name)
            shutil.copy2(source_path, output_file)
            processed_type = "copied_file"
    
    # 将target_path简化为只保留最后一个部分（文件名）
    relative_target_path = os.path.basename(target_path)
    
    return {
        "original_path": original_path,
        "target_path": relative_target_path,  # 只使用文件名
        "processed_file": output_file,
        "processed_type": processed_type
    }

def get_text_template_effect_id(draft_content_path):
    """从draft_content.json文件中提取text_templates的effect_id"""
    try:
        with open(draft_content_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 提取text_templates中的effect_id
        if 'materials' in data and 'text_templates' in data['materials']:
            for item in data['materials']['text_templates']:
                effect_id = item.get('effect_id')
                if effect_id:
                    return effect_id
    except Exception as e:
        print(f"从draft_content.json提取effect_id失败: {e}")
    
    return None

def extract_materials_fields(draft_content_path):
    """从draft_content.json文件中提取materials字段下的多个关键字段"""
    try:
        with open(draft_content_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = {}
        
        # 提取materials.text_templates字段
        if 'materials' in data and 'text_templates' in data['materials']:
            result['text_templates'] = data['materials']['text_templates']
        
        # 提取materials.texts字段
        if 'materials' in data and 'texts' in data['materials']:
            result['texts'] = data['materials']['texts']
        
        # 提取materials.material_animations字段
        if 'materials' in data and 'material_animations' in data['materials']:
            result['material_animations'] = data['materials']['material_animations']
        
        # 提取materials.effects字段
        if 'materials' in data and 'effects' in data['materials']:
            result['effects'] = data['materials']['effects']
        
        # 提取materials.flowers字段
        if 'materials' in data and 'flowers' in data['materials']:
            result['flowers'] = data['materials']['flowers']
        
        return result
    except Exception as e:
        print(f"从draft_content.json提取字段失败: {e}")
        return None

def extract_paths_from_draft(draft_content_path):
    """从draft_content.json文件中提取所有路径"""
    paths_data = []
    
    try:
        with open(draft_content_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取text_templates中的路径
        if 'materials' in data and 'text_templates' in data['materials']:
            for item in data['materials']['text_templates']:
                # 提取主路径
                item_path = item.get('path')
                if item_path:
                    paths_data.append({
                        "original_path": item_path,
                        "target_path": item_path
                    })

                # 提取resources中的路径
                resources = item.get('resources', [])
                for resource in resources:
                    resource_path = resource.get('path')
                    if resource_path:
                        paths_data.append({
                            "original_path": resource_path,
                            "target_path": resource_path
                        })
                
                # 提取aigc_config.font_item中的路径
                font_item = item.get('aigc_config', {}).get('font_item', {})
                font_path = font_item.get('path')
                if font_path:
                    paths_data.append({
                        "original_path": font_path,
                        "target_path": font_path
                    })
        
        # 提取texts中的路径
        if 'materials' in data and 'texts' in data['materials']:
            for text_item in data['materials']['texts']:
                # 提取caption_template_info中的路径
                caption_info = text_item.get('caption_template_info', {})
                caption_path = caption_info.get('path')
                if caption_path:
                    paths_data.append({
                        "original_path": caption_path,
                        "target_path": caption_path
                    })
                
                # 提取content中的路径（需要解析JSON字符串）
                content = text_item.get('content')
                if content and isinstance(content, str):
                    try:
                        content_data = json.loads(content)
                        # 提取font中的path
                        font_path = content_data.get('font', {}).get('path')
                        if font_path:
                            paths_data.append({
                                "original_path": font_path,
                                "target_path": font_path
                            })
                        
                        # 提取effectStyle中的path
                        effect_path = content_data.get('effectStyle', {}).get('path')
                        if effect_path:
                            paths_data.append({
                                "original_path": effect_path,
                                "target_path": effect_path
                            })
                        
                        # 提取fonts数组中的path
                        fonts = content_data.get('fonts', [])
                        for font in fonts:
                            font_path = font.get('path')
                            if font_path:
                                paths_data.append({
                                    "original_path": font_path,
                                    "target_path": font_path
                                })
                    except json.JSONDecodeError:
                        print(f"警告: 无法解析content字段的JSON: {content[:100]}...")
        
        # 提取effects中的路径
        if 'materials' in data and 'effects' in data['materials']:
            for effect in data['materials']['effects']:
                effect_path = effect.get('path')
                if effect_path:
                    paths_data.append({
                        "original_path": effect_path,
                        "target_path": effect_path
                    })
        
        # 提取flowers中的路径
        if 'materials' in data and 'flowers' in data['materials']:
            for flower in data['materials']['flowers']:
                flower_path = flower.get('path')
                if flower_path:
                    paths_data.append({
                        "original_path": flower_path,
                        "target_path": flower_path
                    })
        
        # 提取material_animations中的路径
        if 'materials' in data and 'material_animations' in data['materials']:
            for animation in data['materials']['material_animations']:
                # material_animations中包含animations数组
                animations = animation.get('animations', [])
                for anim in animations:
                    anim_path = anim.get('path')
                    if anim_path:
                        paths_data.append({
                            "original_path": anim_path,
                            "target_path": anim_path
                        })
    
    except FileNotFoundError:
        print(f"错误: JSON文件 '{draft_content_path}' 未找到。")
    except json.JSONDecodeError:
        print(f"错误: 文件 '{draft_content_path}' 不是一个有效的JSON文件。")
    except Exception as e:
        print(f"提取路径时出错: {e}")
    
    return paths_data

def process_paths(paths_data, output_dir):
    """处理所有提取的路径"""
    results = []
    
    # 处理每个路径
    for item in paths_data:
        original_path = item.get("original_path")
        target_path = item.get("target_path")
        
        if not original_path or not target_path:
            continue
        
        result = process_path(original_path, target_path, output_dir)
        if result:
            results.append(result)
    
    # 将处理结果保存到新的JSON文件
    output_json = os.path.join(output_dir, "processed_paths.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"处理完成! 共处理 {len(results)} 个文件/文件夹")
    print(f"结果已保存到: {output_json}")
    return results

def extract_text_template_segment(draft_content_path):
    """从draft_content.json文件中提取tracks数组中type为text的track，
    并找到material_id与text_templates[0].id相匹配的segment"""
    try:
        with open(draft_content_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 首先获取text_templates[0].id作为目标material_id
        target_material_id = None
        if 'materials' in data and 'text_templates' in data['materials'] and data['materials']['text_templates']:
            target_material_id = data['materials']['text_templates'][0].get('id')
            
        if not target_material_id:
            print("未找到text_templates[0].id，无法提取segment")
            return None
            
        # 遍历tracks数组
        if 'tracks' in data:
            for track in data['tracks']:
                # 找到type为text的track
                if track.get('type') == 'text':
                    # 遍历segments
                    for segment in track.get('segments', []):
                        # 找到指定material_id的segment
                        if segment.get('material_id') == target_material_id:
                            return segment
    except Exception as e:
        print(f"从draft_content.json提取text segment失败: {e}")
    
    return None

# 在process_draft_content函数中，修改上传部分的代码
def process_draft_content(draft_content_path, access_key_id, access_key_secret):
    """处理draft_content.json文件，提取路径、材料字段和文本模板segment，并上传到阿里云OSS
    
    Args:
        draft_content_path: draft_content.json文件的路径
        access_key_id: 阿里云Access Key ID
        access_key_secret: 阿里云Access Key Secret
    
    Returns:
        output_dir: 输出目录路径
    """
    # 提取路径
    paths_data = extract_paths_from_draft(draft_content_path)
    
    if not paths_data:
        print("未找到任何路径，退出处理")
        return None
    
    # 从draft_content.json中提取text_templates的effect_id
    effect_id = get_text_template_effect_id(draft_content_path)
    
    if not effect_id:
        print("未找到text_templates的effect_id，将使用默认目录名")
        effect_id = "text_template_resources"
    else:
        print(f"找到text_templates的effect_id: {effect_id}")
    
    # 确定输出目录
    base_dir = "./extracted_resources"
    os.makedirs(base_dir, exist_ok=True)
    output_dir = os.path.join(base_dir, effect_id)
    
    # 处理所有路径
    process_paths(paths_data, output_dir)
    
    # 提取materials.text_templates和materials.texts字段并保存到新的JSON文件
    materials_fields = extract_materials_fields(draft_content_path)
    if materials_fields:
        materials_json = os.path.join(output_dir, "materials_fields.json")
        with open(materials_json, 'w', encoding='utf-8') as f:
            json.dump(materials_fields, f, ensure_ascii=False, indent=2)
        print(f"材料字段已保存到: {materials_json}")
    
    # 提取与text_templates[0].id匹配的text segment并保存到新的JSON文件
    text_segment = extract_text_template_segment(draft_content_path)
    if text_segment:
        segment_json = os.path.join(output_dir, "text_template_segment.json")
        with open(segment_json, 'w', encoding='utf-8') as f:
            json.dump(text_segment, f, ensure_ascii=False, indent=2)
        print(f"文本模板segment已保存到: {segment_json}")
    
    # 上传临时文件到阿里云OSS
    # print("开始上传临时文件到阿里云OSS...")
    upload_temp_files_to_oss(output_dir, effect_id, access_key_id, access_key_secret)
    
    # 将整个文件夹打包成一个zip文件
    zip_file_path = f"{output_dir}.zip"
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    
    print(f"开始将文件夹 {output_dir} 打包成zip文件...")
    shutil.make_archive(output_dir, 'zip', os.path.dirname(output_dir), os.path.basename(output_dir))
    print(f"文件夹已打包为: {zip_file_path}")
    
    # 上传zip文件到阿里云OSS
    print(f"开始上传zip文件 {zip_file_path} 到阿里云OSS...")
    upload_success = upload_zip_to_oss(zip_file_path, effect_id, access_key_id, access_key_secret)
    if upload_success:
        print(f"zip文件已成功上传到阿里云OSS: https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/text_template/{effect_id}.zip")
    else:
        print("上传到阿里云OSS失败")
    
    return output_dir

def generate_oss_signature(access_key_id, access_key_secret, method, content_type, resource, content_md5=""):
    """
    生成阿里云OSS RESTful API的签名
    
    Args:
        access_key_id: 访问密钥ID
        access_key_secret: 访问密钥密码
        method: HTTP方法（GET, PUT, POST等）
        content_type: 内容类型
        resource: OSS资源路径
        content_md5: 内容的MD5值（可选）
        
    Returns:
        str: 授权字符串
    """
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    string_to_sign = f"{method}\n{content_md5}\n{content_type}\n{date}\n/{resource}"
    
    # 计算HMAC-SHA1签名
    h = hmac.new(
        access_key_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha1
    )
    signature = base64.b64encode(h.digest()).decode('utf-8')
    
    # 构建授权字符串
    authorization = f"OSS {access_key_id}:{signature}"
    
    return authorization, date

def check_object_exists(object_name, access_key_id, access_key_secret):
    """
    检查OSS对象是否存在
    
    Args:
        object_name: OSS对象名称
        access_key_id: 阿里云Access Key ID
        access_key_secret: 阿里云Access Key Secret
        
    Returns:
        bool: 对象是否存在
    """
    bucket_name = OSS_CONFIG['bucket_name']
    host = OSS_CONFIG['host']
    
    # 生成签名
    resource = f"{bucket_name}/{object_name}"
    authorization, date = generate_oss_signature(
        access_key_id, access_key_secret, "HEAD", "", resource
    )
    
    # 构建请求URL和头部
    url = f"https://{host}/{object_name}"
    headers = {
        'Host': host,
        'Date': date,
        'Authorization': authorization
    }
    
    # 发送HEAD请求检查对象是否存在
    response = requests.head(url, headers=headers)
    
    return response.status_code == 200

def upload_temp_files_to_oss(local_dir, effect_id, access_key_id, access_key_secret):
    """
    将临时文件上传到阿里云OSS（使用RESTful API）
    
    Args:
        local_dir: 本地临时文件目录
        effect_id: 效果ID，用于构建OSS路径
        access_key_id: 阿里云Access Key ID
        access_key_secret: 阿里云Access Key Secret
    
    Returns:
        bool: 上传是否成功
    """
    if not os.path.exists(local_dir) or not os.path.isdir(local_dir):
        print(f"错误: 临时文件目录不存在: {local_dir}")
        return False
        
    try:
        bucket_name = OSS_CONFIG['bucket_name']
        host = OSS_CONFIG['host']
        
        # 检查OSS上是否已存在file_exist标记文件
        file_exist_path = f"text_template/{effect_id}/file_exist"
        
        if check_object_exists(file_exist_path, access_key_id, access_key_secret):
            print(f"错误: OSS上已存在相同名称的文件夹: text_template/{effect_id}/")
            return False
        
        # 首先上传file_exist标记文件
        content = "This file indicates that the folder exists"
        content_type = "text/plain"
        resource = f"{bucket_name}/{file_exist_path}"
        
        # 生成签名
        authorization, date = generate_oss_signature(
            access_key_id, access_key_secret, "PUT", content_type, resource
        )
        
        # 构建请求URL和头部
        url = f"https://{host}/{file_exist_path}"
        headers = {
            'Host': host,
            'Date': date,
            'Content-Type': content_type,
            'Content-Length': str(len(content)),
            'Authorization': authorization
        }
        
        # 发送PUT请求上传标记文件
        response = requests.put(url, headers=headers, data=content)
        
        if response.status_code != 200:
            print(f"错误: 上传标记文件失败: {response.status_code} {response.text}")
            return False
            
        print(f"已上传标记文件: {file_exist_path}")
        
        # 遍历目录中的所有文件
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                # 计算相对路径，用于构建OSS对象名
                relative_path = os.path.relpath(local_file_path, os.path.dirname(local_dir))
                # 确保OSS对象名使用正斜杠，不管操作系统是什么
                oss_object_name = f"text_template/{relative_path.replace(os.sep, '/')}"
                
                # 读取文件内容
                with open(local_file_path, 'rb') as f:
                    file_content = f.read()
                
                # 确定内容类型
                content_type = "application/octet-stream"
                if local_file_path.endswith('.json'):
                    content_type = "application/json"
                elif local_file_path.endswith('.txt'):
                    content_type = "text/plain"
                elif local_file_path.endswith('.png'):
                    content_type = "image/png"
                elif local_file_path.endswith('.jpg') or local_file_path.endswith('.jpeg'):
                    content_type = "image/jpeg"
                
                # 生成签名
                resource = f"{bucket_name}/{oss_object_name}"
                authorization, date = generate_oss_signature(
                    access_key_id, access_key_secret, "PUT", content_type, resource
                )
                
                # 构建请求URL和头部
                url = f"https://{host}/{oss_object_name}"
                headers = {
                    'Host': host,
                    'Date': date,
                    'Content-Type': content_type,
                    'Content-Length': str(len(file_content)),
                    'Authorization': authorization
                }
                
                # 发送PUT请求上传文件
                response = requests.put(url, headers=headers, data=file_content)
                
                if response.status_code == 200:
                    print(f"已上传临时文件: {local_file_path} -> {oss_object_name}")
                else:
                    print(f"上传文件失败: {local_file_path} -> {oss_object_name}, 状态码: {response.status_code}")
                    return False
        
        return True
    except Exception as e:
        print(f"上传临时文件到OSS时出错: {str(e)}")
        return False

def upload_zip_to_oss(local_zip_path, effect_id, access_key_id, access_key_secret):
    """
    将zip文件上传到阿里云OSS（使用RESTful API）
    
    Args:
        local_zip_path: 本地zip文件路径
        effect_id: 效果ID，用作OSS中的文件名
        access_key_id: 阿里云Access Key ID
        access_key_secret: 阿里云Access Key Secret
    
    Returns:
        bool: 上传是否成功
    """
    if not os.path.exists(local_zip_path) or not os.path.isfile(local_zip_path):
        print(f"错误: zip文件不存在: {local_zip_path}")
        return False
        
    try:
        bucket_name = OSS_CONFIG['bucket_name']
        host = OSS_CONFIG['host']
        
        # 检查OSS上是否已存在zip文件
        file_exist_path = f"text_template/{effect_id}/{effect_id}.zip"
        
        if check_object_exists(file_exist_path, access_key_id, access_key_secret):
            print(f"错误: OSS上已存在相同名称zip: text_template/{effect_id}/{effect_id}.zip")
            return False
        
        # 读取zip文件内容
        with open(local_zip_path, 'rb') as f:
            file_content = f.read()
        
        # 生成签名
        content_type = "application/zip"
        resource = f"{bucket_name}/{file_exist_path}"
        authorization, date = generate_oss_signature(
            access_key_id, access_key_secret, "PUT", content_type, resource
        )
        
        # 构建请求URL和头部
        url = f"https://{host}/{file_exist_path}"
        headers = {
            'Host': host,
            'Date': date,
            'Content-Type': content_type,
            'Content-Length': str(len(file_content)),
            'Authorization': authorization
        }
        
        # 发送PUT请求上传zip文件
        response = requests.put(url, headers=headers, data=file_content)
        
        if response.status_code == 200:
            print(f"已上传: {local_zip_path} -> {file_exist_path}")
            print(f"zip文件已成功上传到OSS，路径为: text_template/{effect_id}/{effect_id}.zip")
            return True
        else:
            print(f"上传zip文件失败: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"上传zip文件到OSS时出错: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="上传文字模板，使用说明：https://docs.capcutapi.top/7350425m0.")
    parser.add_argument("-path", dest="draft_content_path", required=True, help="Path to the draft_content.json file.")
    parser.add_argument("-id", dest="access_key_id", required=True, help="Aliyun Access Key ID.")
    parser.add_argument("-secret", dest="access_key_secret", required=True, help="Aliyun Access Key Secret.")
    
    args = parser.parse_args()
    
    # 调用函数处理draft_content.json
    process_draft_content(args.draft_content_path, args.access_key_id, args.access_key_secret)
