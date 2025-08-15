import os
import json
import threading
import time
import sys
import re
import requests
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, request, send_file, url_for, render_template_string, Response, jsonify
from docx import Document
from docx.shared import Pt, RGBColor
from datetime import datetime
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import tiktoken
import openpyxl
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from lxml import etree
import zipfile
import tempfile
from copy import deepcopy
# 1. 引入SocketIO
# 移除所有WebSocket相关代码，只保留数据库进度写入和前端接口轮询
# update_progress只写数据库不推送WebSocket
# 前端只用/get_progress接口轮询显示进度，不包含socket.io相关JS
import logging
log = logging.getLogger('werkzeug')
# 移除关闭werkzeug日志的代码，恢复Flask访问日志

app = Flask(__name__)

# 基础配置
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 16MB 最大文件大小
app.config['SERVER_NAME'] = '45.207.205.60:5001'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translation_tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# API配置
API_URL = "https://api.deepseek.com/v1"
API_KEY = "sk-a765b6c0dfae46829e8368352513ec5b"
MODEL_NAME = "deepseek-chat"

# 全局变量
MAX_RETRIES = 5
RETRY_INTERVAL = 5  # Retry interval in seconds
progress_queues = {}
active_tasks = {}
active_tasks_lock = threading.Lock()
MAX_TOKENS = 7192
SAFE_MARGIN = 1000
encoding = tiktoken.get_encoding("cl100k_base")
migrate = Migrate(app, db)

# 数据库模型
class Task(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    token_stats = db.Column(db.JSON, default=dict)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('task.id'))
    message = db.Column(db.String(500))
    type = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


def update_progress(task_id, message, progress_type):
    try:
        progress = Progress(
            task_id=task_id,
            message=message,
            type=progress_type
        )
        db.session.add(progress)
        db.session.commit()
        print(message)
    except Exception as e:
        print(f"更新进度失败: {str(e)}")
        db.session.rollback()

def is_valid_excel_file(file):
    try:
        pd.read_excel(file, engine='openpyxl')
        return True
    except Exception as e:
        print(f"文件验证失败: {e}")
        return False

def get_relevant_terms(batch_texts, terminology):
    """从术语表中筛选出当前批次文本实际涉及的术语"""
    relevant_terms = {}
    for term, translation in terminology.items():
        # 如果术语出现在当前批次任意一个文本中
        if any(term.lower() in text.lower() for text in batch_texts):
            relevant_terms[term] = translation
    return relevant_terms

def get_document_summary(file_contents, task_id, api_url, api_key, model_name):
    """获取文档内容的摘要理解"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    all_text = []
    for file_content in file_contents:
        with BytesIO(file_content) as file:
            doc = Document(file)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            all_text.append(text)
    combined_text = '\n'.join(all_text)
    update_progress(task_id, "正在生成文档理解摘要...", "reading")
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一个专业的文档分析助手。请对提供的文本内容进行分析，生成一个300字左右的总体理解摘要，说清楚这个文本是什么类型文本，关于什么的，结构是什么样的。这个摘要将用于辅助后续的翻译工作。只回复文章摘要本身，不要回复多余解释说明内容，如好的，明白了等"},
            {"role": "user", "content": f"请分析以下文档内容并生成摘要：\n\n{combined_text[:8000]}"}
        ],
        "temperature": 0.4
    }
    for attempt in range(3):
        try:
            response = requests.post(f'{api_url}/chat/completions', headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                summary = result['choices'][0]['message']['content'].strip()
                update_progress(task_id, "文档理解摘要生成完成", "reading")
                return summary
            elif response.status_code == 503:
                update_progress(task_id, "503 服务暂时不可用. 等待 5 秒后重试...", "reading")
                time.sleep(5)
        except Exception as e:
            update_progress(task_id, f"生成摘要时出错: {str(e)}. 重试中...", "reading")
            time.sleep(5)
    return "无法生成文档摘要。"


def split_text(texts, max_tokens, safe_margin=100, token_encoder=None):
    """
    Split texts to ensure each segment does not exceed the token limit.
    If a single text is too long, it will be further split.
    """
    if token_encoder is None:
        token_encoder = encoding  # 默认使用 tiktoken 的 `cl100k_base` 编码

    split_texts = []  # 存储分割结果
    current_batch = []  # 当前批次文本
    current_tokens = 0  # 当前批次的 token 总数

    for text in texts:
        text_tokens = len(token_encoder.encode(text))

        # 处理单个过长的文本
        if text_tokens > max_tokens - safe_margin:
            # 切分超长文本
            sub_texts = divide_long_text(text, max_tokens - safe_margin, token_encoder)
            for sub_text in sub_texts:
                sub_text_tokens = len(token_encoder.encode(sub_text))
                if current_tokens + sub_text_tokens > max_tokens - safe_margin:
                    # 超出当前批次限制 -> 新建批次
                    split_texts.append(current_batch)
                    current_batch = []
                    current_tokens = 0
                current_batch.append(sub_text)
                current_tokens += sub_text_tokens
        else:
            # 处理短文本
            if current_tokens + text_tokens > max_tokens - safe_margin:
                # 超出当前批次限制时，结束当前批次
                split_texts.append(current_batch)
                current_batch = []
                current_tokens = 0
            current_batch.append(text)
            current_tokens += text_tokens

    # 添加最后的批次
    if current_batch:
        split_texts.append(current_batch)

    return split_texts


def divide_long_text(text, max_tokens, token_encoder):
    """
    Divide a single long text into smaller chunks based on max_tokens limit.
    This function ensures that even the longest text is split appropriately.
    """
    words = text.split()  # 使用空格分词，处理为单词或短语列表
    sub_texts = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = len(token_encoder.encode(word))
        
        # 检查当前词语是否会导致超出 token 限制
        if current_tokens + word_tokens > max_tokens:
            # 保存当前段落，并开始新的段落
            sub_texts.append(" ".join(current_chunk))
            current_chunk = []
            current_tokens = 0
        
        # 添加词语到当前段
        current_chunk.append(word)
        current_tokens += word_tokens

    # 添加最后的段
    if current_chunk:
        sub_texts.append(" ".join(current_chunk))

    return sub_texts

def analyze_terms(texts, term_types, task_id, api_url, api_key, model_name):
    """Analyze terms in the documents and return them in strict JSON format"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    term_types_text = "\n".join(term_types)
    system_message = {
        "role": "system",
        "content": (
            "你是一个专业的术语分析助手。请从给定的文本中提取术语，并返回 JSON 格式的术语信息。\n"
            "输出格式如下：\n"
            "[\n"
            "  {\n"
            "    \"term\": \"术语原文\",\n"
            "    \"translation\": \"对应中文翻译\",\n"
            "    \"sentence\": \"术语所在的句子\",\n"
            "    \"explanation\": \"术语的中文解释\",\n"
            "    \"type\": \"术语类型\"\n"
            "  }\n"
            "]\n"
            "不要添加任何多余说明或注释如好的，明白了，JSON 格式如下或者```json等，直接从 [ 开始返回！，不要从```json开始"
        )
    }
    user_message_template = "类别：{}\n\n文本内容：{}"
    text_batches = split_text(texts, MAX_TOKENS - SAFE_MARGIN)
    total_batches = len(text_batches)
    all_terms_info = []

    for batch_num, text_batch in enumerate(text_batches, 1):
        retry_count = 0
        update_progress(task_id, f"正在处理第 {batch_num}/{total_batches} 段文本的术语提取...", "info")
        while retry_count < MAX_RETRIES:
            try:
                user_message = {
                    "role": "user",
                    "content": user_message_template.format(
                        term_types_text,
                        "\n\n".join(text_batch)
                    )
                }
                data = {
                    "model": model_name,
                    "messages": [system_message, user_message],
                    "temperature": 0.4
                }
                response = requests.post(f'{api_url}/chat/completions', headers=headers, json=data)
                response_content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                # 容错处理：去除 ```json、```、空行等
                response_content = response_content.strip()
                if response_content.startswith('```json'):
                    response_content = response_content[len('```json'):].strip()
                if response_content.startswith('```'):
                    response_content = response_content[len('```'):].strip()
                if response_content.endswith('```'):
                    response_content = response_content[:-3].strip()
                # 去除首尾多余空行
                response_content = response_content.strip()
                terms_info = json.loads(response_content)  # Parse JSON to extract terms
                all_terms_info.extend(terms_info)
                break
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"API 返回了无效 JSON，内容：{response_content}")
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    print(f"{retry_count}次重试...")
                    time.sleep(RETRY_INTERVAL)
                else:
                    print("超过最大重试次数，任务终止！")
                    print(f"Exception: {e}")
                    raise ValueError("术语分析结果不是有效的 JSON 格式！")
            except Exception as e:
                retry_count += 1
                print(f"API调用失败：{str(e)}，重试 {retry_count}...")
                if retry_count < MAX_RETRIES:
                    time.sleep(RETRY_INTERVAL)
                else:
                    return f"API调用失败：{str(e)}"
    return all_terms_info

def process_term_analysis(task_id, contract_files_data, term_types, api_url, api_key, model_name):
    """Term analysis task: analyze the complete term list and generate a six-column table"""
    with app.app_context():
        thread = threading.current_thread()
        thread.do_run = True
        try:
            # Create a new task record
            new_task = Task(
                id=task_id,
                status='in_progress'
            )
            db.session.add(new_task)
            db.session.commit()
            download_links = {'terminology': None}
            # Aggregate the text content of all contract files for term analysis
            all_texts = []
            for file_data in contract_files_data:
                with BytesIO(file_data['content']) as file:
                    doc = Document(file)
                    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
                    all_texts.append(text)
            update_progress(task_id, "文件读取完成，开始分段处理文本...", "info")
            # Combine all texts into a single string
            combined_text = '\n'.join(all_texts)
            # Perform term analysis
            analyzed_terms = analyze_terms([combined_text], term_types, task_id, api_url, api_key, model_name)
            # Validate term analysis result
            if isinstance(analyzed_terms, str):
                try:
                    analyzed_terms = json.loads(analyzed_terms)
                except json.JSONDecodeError:
                    raise ValueError("术语分析结果不是有效的 JSON 格式！")
            if not isinstance(analyzed_terms, list):
                raise ValueError("术语分析结果不是列表，无法解析术语数据！")
            # Deduplicate terms and count frequency
            unique_terms = []
            term_frequency = {}
            seen_terms = set()
            for term in analyzed_terms:
                term_word = term.get('term', '').strip().lower()
                term_type = term.get('type', 'N/A')  # Default to 'N/A' if no type provided
                if not term_word:
                    continue
                term_count = sum(len(re.findall(rf'\b{re.escape(term_word)}\b', text.lower())) for text in all_texts)
                # 修正频率值：如果为零，改为 1
                term_frequency[term_word] = max(term_count, 1)
                if term_word not in seen_terms:
                    term['type'] = term_type  # Attach term type
                    unique_terms.append(term)
                    seen_terms.add(term_word)
            # Generate the term analysis report
            doc = Document()
            doc.add_heading('术语分析报告', level=1)
            # Create a table with six columns
            table = doc.add_table(rows=1, cols=6)
            table.style = 'Table Grid'
            # Header row
            header_cells = table.rows[0].cells
            headers = ['术语原文', '术语对应中文翻译', '所在句子', '中文解释', '术语类型', '出现频率']
            for idx, header in enumerate(headers):
                header_cells[idx].text = header
            # Add term data to the table
            for term in unique_terms:
                if not isinstance(term, dict):  # Ensure term is a dictionary
                    continue
                row_cells = table.add_row().cells
                row_cells[0].text = term.get('term', 'N/A')
                row_cells[1].text = term.get('translation', 'N/A')
                row_cells[2].text = term.get('sentence', 'N/A')
                row_cells[3].text = term.get('explanation', 'N/A')
                row_cells[4].text = term.get('type', 'N/A')  # Add term type
                # 使用修正后的频率统计值
                row_cells[5].text = str(term_frequency.get(term.get('term', '').lower(), 1))  # Default frequency to 1
            # Save the Word document
            # 新命名规则：术语报告_原始文件名.docx
            if contract_files_data and 'filename' in contract_files_data[0]:
                original_filename = contract_files_data[0]['filename']
                filename_base = os.path.splitext(os.path.basename(original_filename))[0]
                if not filename_base:
                    filename_base = "未命名"
            else:
                filename_base = "未命名"
            # 在process_term_analysis保存文件前，确保目录存在
            # 术语报告保存到"术语/"目录
            terminology_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '术语')
            os.makedirs(terminology_dir, exist_ok=True)
            report_filename = get_unique_filepath(terminology_dir, f'术语报告_{filename_base}.docx')
            doc.save(report_filename)
            # Update the download link
            download_links['terminology'] = f"已保存到本地：术语/{os.path.basename(report_filename)}"
            # Update task status
            task = Task.query.get(task_id)
            if task:
                task.status = 'completed'
                task.download_links = download_links
                db.session.commit()
            update_progress(task_id, f'术语报告已保存到本地：术语/{os.path.basename(report_filename)}', 'saving')
        except Exception as e:
            error_message = f"处理出错: {str(e)}"
            print(error_message)
            update_progress(task_id, error_message, "error")
            task = Task.query.get(task_id)
            if task:
                task.status = 'error'
                db.session.commit()
        finally:
            with active_tasks_lock:
                if task_id in active_tasks:
                    del active_tasks[task_id]

def add_dynamic_terminology_to_context(context, relevant_terms):
    """为上下文动态加入当前批次文本相关的术语"""
    if not relevant_terms:
        return context  # 如果没有相关术语，直接返回原始上下文

    # 将术语转换成术语列表
    terms_guide = "\n".join([f"{term}: {translation}" for term, translation in relevant_terms.items()])

    if "术语指南：" in context:
        # 替换已有术语指南部分
        parts = context.split("术语指南：")
        return parts[0] + f"术语指南：\n{terms_guide}\n" + parts[1]
    else:
        # 直接追加术语指南
        return context + f"\n术语指南：\n{terms_guide}\n"



def translate_single_text(text, context, task_id, api_url, api_key, model_name):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    retries = 5
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": f"请翻译以下内容，不要添加任何额外说明！如好的，明白了，文本1,等，尤其千万不要在翻译内容前添加文本1：文本2：这些内容，而是严格直接返回翻译结果内容：\n\n{text}"}
        ],
        "temperature": 0.4  # DeepSeek可能需要指定temperature
    }
    for attempt in range(retries):
        if not getattr(threading.current_thread(), "do_run", True):
            return None
        try:
            response = requests.post(f'{api_url}/chat/completions', headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                return translated_text
            else:
                update_progress(
                    task_id,
                    f"翻译片段失败，状态码:{response.status_code}，正在重试 ({attempt + 1}/{retries})",
                    "error"
                )
                time.sleep(5)
        except requests.Timeout:
            update_progress(task_id, f"翻译片段超时，正在重试 ({attempt + 1}/{retries})", "error")
            time.sleep(5)
        except Exception as e:
            update_progress(task_id, f"翻译片段发生异常: {str(e)}，正在重试 ({attempt + 1}/{retries})", "error")
            time.sleep(5)
    return None

def smart_split_translations(translated_text, expected_count):
    # 1. 尝试双换行
    parts = [p.strip() for p in translated_text.strip().split("\n\n") if p.strip()]
    if len(parts) == expected_count:
        return parts, "双换行"
    # 2. 尝试单换行
    parts = [p.strip() for p in translated_text.strip().split("\n") if p.strip()]
    if len(parts) == expected_count:
        return parts, "单换行"
    # 3. 尝试正则按Text编号分割
    regex_parts = re.split(r'(?:^|\n)Text \d+:', translated_text)
    regex_parts = [p.strip() for p in regex_parts if p.strip()]
    if len(regex_parts) == expected_count:
        return regex_parts, "Text编号"
    # 4. fallback
    return parts, "fallback-单换行"

def translate_with_fixed_length_batches(texts, context, task_id, terminology, api_url, api_key, model_name, batch_size=40):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    translations = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    update_progress(task_id, f"开始翻译，共 {total_batches} 批次...", "translation")
    
    for batch_num in range(total_batches):
        if not getattr(threading.current_thread(), "do_run", True):
            return None
            
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, len(texts))
        text_batch = texts[start_idx:end_idx]
        update_progress(task_id, f"处理第 {batch_num + 1}/{total_batches} 批次，包含 {len(text_batch)} 个片段", "translation")
        
        # 获取相关术语
        relevant_terms = get_relevant_terms(text_batch, terminology)
        batch_context = add_dynamic_terminology_to_context(context, relevant_terms)
        text_to_translate = "\n\n".join([f"Text {i + 1}: {txt}" for i, txt in enumerate(text_batch)])
        
        # 批量翻译数据
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": batch_context},
                {"role": "user", "content": f"请翻译以下内容，如果有原文摘要可以参考，有术语表的话严格按照术语对照表翻译专业术语，只直接返回翻译结果，不要添加任何说明，如好的，明白了，文本1等，尤其千万不要在翻译内容前添加文本1：文本2：这些说明内容，而是严格直接返回翻译内容：\n\n{text_to_translate}"}
            ],
            "temperature": 0.4
        }
        
        # 新增：记录批次请求内容
        print(f"批次 {batch_num + 1} 请求内容: {json.dumps({'messages': data['messages']}, ensure_ascii=False, indent=2)}")
        
        # 批量翻译重试（6次）
        batch_success = False
        for batch_attempt in range(6):
            if not getattr(threading.current_thread(), "do_run", True):
                return None
                
            try:
                response = requests.post(f'{api_url}/chat/completions', headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result['choices'][0]['message']['content'].strip()
                    print(f"批次 {batch_num + 1} 返回内容: {translated_text}")
                    batch_translations, split_mode = smart_split_translations(translated_text, len(text_batch))
                    print(f"分割方式: {split_mode}，分割数量: {len(batch_translations)}，期望数量: {len(text_batch)}")
                    
                    if len(batch_translations) == len(text_batch):
                        translations.extend(batch_translations)
                        update_progress(task_id, f"批次 {batch_num + 1} 翻译成功！", "translation")
                        batch_success = True
                        break
                    else:
                        update_progress(task_id, f"批次 {batch_num + 1} 翻译结果数量不匹配，重试中... ({batch_attempt + 1}/6)", "translation")
                        time.sleep(5)
                        
                elif response.status_code == 503:
                    update_progress(task_id, f"批次 {batch_num + 1} 服务暂时不可用，等待重试... ({batch_attempt + 1}/6)", "translation")
                    time.sleep(5)
                else:
                    update_progress(task_id, f"批次 {batch_num + 1} 请求失败 ({response.status_code})，等待重试... ({batch_attempt + 1}/6)", "translation")
                    time.sleep(5)
                    
            except Exception as e:
                update_progress(task_id, f"批次 {batch_num + 1} 发生错误: {str(e)}，等待重试... ({batch_attempt + 1}/6)", "translation")
                time.sleep(5)

        # 如果批量翻译失败，进行逐条翻译
        if not batch_success:
            update_progress(task_id, f"批次 {batch_num + 1} 批量翻译失败，开始逐条翻译...", "translation")
            batch_translations = []
            
            # 逐条翻译每个文本
            for text_idx, text in enumerate(text_batch):
                if not getattr(threading.current_thread(), "do_run", True):
                    return None
                    
                single_translation = None
                # 单条翻译重试（5次）
                for single_attempt in range(5):
                    single_translation = translate_single_text(text, batch_context, task_id, api_url, api_key, model_name)
                    if single_translation:
                        batch_translations.append(single_translation)
                        update_progress(task_id, f"批次 {batch_num + 1} 第 {text_idx + 1} 条翻译成功", "translation")
                        break
                    time.sleep(5)
                
                # 如果单条翻译失败
                if not single_translation:
                    update_progress(task_id, f"任务失败：批次 {batch_num + 1} 第 {text_idx + 1} 条翻译多次重试失败", "error")
                    with active_tasks_lock:
                        active_tasks.pop(task_id, None)
                    return None
            
            # 如果所有单条翻译成功，添加到总翻译结果中
            if len(batch_translations) == len(text_batch):
                translations.extend(batch_translations)
                update_progress(task_id, f"批次 {batch_num + 1} 逐条翻译完成", "translation")
            else:
                update_progress(task_id, f"任务失败：批次 {batch_num + 1} 逐条翻译结果数量不匹配", "error")
                with active_tasks_lock:
                    active_tasks.pop(task_id, None)
                return None

    return translations

def split_by_symbols(text, symbols=['►', '◄', '◇']):
    pattern = '(' + '|'.join(re.escape(s) for s in symbols) + ')'
    return [part for part in re.split(pattern, text) if part != '']

def trados_preserve_symbols_lxml(docx_path, ai_texts, symbols=['►', '◄', '◇']):
    import zipfile, tempfile, os
    from lxml import etree
    from copy import deepcopy
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        document_xml_path = os.path.join(temp_dir, 'word', 'document.xml')
        tree = etree.parse(document_xml_path)
        root = tree.getroot()
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tables = root.xpath('.//w:tbl', namespaces=ns)
        ai_idx = 0
        for table in tables:
            rows = table.xpath('.//w:tr[position()>1]', namespaces=ns)
            for row in rows:
                if ai_idx >= len(ai_texts):
                    break
                cells = row.xpath('.//w:tc', namespaces=ns)
                if len(cells) < 3:
                    continue
                src_cell = cells[1]
                tgt_cell = cells[2]
                # 1. 复制src_cell的所有内容到tgt_cell
                # 先清空tgt_cell
                for elem in list(tgt_cell):
                    tgt_cell.remove(elem)
                for elem in src_cell:
                    tgt_cell.append(deepcopy(elem))
                # 2. 替换普通文本<w:t>内容
                ai_text = ai_texts[ai_idx]
                parts = split_by_symbols(ai_text, symbols)
                # 遍历tgt_cell所有<w:t>，遇到符号<w:t>跳过，遇到普通文本<w:t>按AI译文顺序替换
                t_nodes = tgt_cell.xpath('.//w:t', namespaces=ns)
                part_idx = 0
                for t in t_nodes:
                    if part_idx >= len(parts):
                        break
                    # 跳过符号<w:t>
                    while part_idx < len(parts) and parts[part_idx] in symbols:
                        part_idx += 1
                    if part_idx >= len(parts):
                        break
                    # 只替换非符号<w:t>
                    if t.text not in symbols:
                        t.text = parts[part_idx]
                        part_idx += 1
                ai_idx += 1
        tree.write(document_xml_path, encoding='utf-8', xml_declaration=True)
        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)

def process_translation(task_id, trados_files_data, term_file_content, translation_requirements, original_files_data=None, api_url=None, api_key=None, model_name=None):
    with app.app_context():
        thread = threading.current_thread()
        thread.do_run = True
        try:
            new_task = Task(
                id=task_id,
                status='in_progress'
            )
            db.session.add(new_task)
            db.session.commit()
            download_links = {
                'translation': []
            }
            document_summary = ""
            if original_files_data:
                document_summary = get_document_summary(original_files_data, task_id, api_url, api_key, model_name)
            terminology = {}
            if term_file_content:
                try:
                    with BytesIO(term_file_content) as term_file:
                        if is_valid_excel_file(BytesIO(term_file.getvalue())):
                            term_file.seek(0)
                            term_data = pd.read_excel(term_file, engine='openpyxl')
                            terminology = {
                                str(row[0]).strip(): str(row[1]).strip()
                                for _, row in term_data.iterrows()
                                if not pd.isna(row[0]) and not pd.isna(row[1])
                            }
                            update_progress(task_id, f"加载了 {len(terminology)} 个术语", "reading")
                except Exception as e:
                    update_progress(task_id, f"处理术语表时出错: {str(e)}", "error")
            else:
                terminology = {}
            all_texts = []
            for idx, file_data in enumerate(trados_files_data, 1):
                with BytesIO(file_data['content']) as trados_file_bytes:
                    trados_doc = Document(trados_file_bytes)
                    texts = [
                        row.cells[1].text for table in trados_doc.tables for row in table.rows[1:]
                    ]
                    all_texts.extend(texts)
            context_parts = ["你是一个专业的翻译助手。不要回复多余的内容如好的，明白了，文本1等，尤其千万不要在翻译内容前添加文本1：文本2：这些说明内容，而是严格直接返回翻译内容。请注意以下要求：\n"]
            if document_summary:
                context_parts.append(f"文档背景理解：\n{document_summary}\n")
            context_parts.append("\n翻译要求：\n")
            context_parts.append(translation_requirements)
            context = "".join(context_parts)
            translations = translate_with_fixed_length_batches(all_texts, context, task_id, terminology, api_url, api_key, model_name)
            if translations is None:
                return
            update_progress(task_id, "正在写入翻译结果...", "saving")
            ai_texts_for_lxml = translations
            for idx, file_data in enumerate(trados_files_data, 1):
                with BytesIO(file_data['content']) as trados_file_bytes:
                    trados_doc = Document(trados_file_bytes)
                    original_filename = file_data['filename']
                    filename_base = os.path.splitext(os.path.basename(original_filename))[0]
                    if not filename_base:
                        filename_base = "未命名"
                    # 在process_translation保存文件前，确保目录存在
                    # 翻译结果保存到"翻译/"目录
                    translation_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '翻译')
                    os.makedirs(translation_dir, exist_ok=True)
                    translation_filename = get_unique_filepath(translation_dir, f"已翻译_{filename_base}.docx")
                    trados_doc.save(translation_filename)
                    # lxml后处理，安全符号替换（只用lxml写入目标cell）
                    trados_preserve_symbols_lxml(translation_filename, ai_texts_for_lxml)
                    update_progress(task_id, f'文件 {idx} 翻译完成，已保存到本地：翻译/{os.path.basename(translation_filename)}', 'saving')
                    download_links['translation'] = [f'已保存到本地：翻译/{os.path.basename(translation_filename)}']
            task = Task.query.get(task_id)
            if task:
                task.status = 'completed'
                task.download_links = download_links
                db.session.commit()
        except Exception as e:
            error_message = f"处理出错: {str(e)}"
            print(error_message)
            update_progress(task_id, error_message, "error")
            task = Task.query.get(task_id)
            if task:
                task.status = 'error'
                db.session.commit()
        finally:
            with active_tasks_lock:
                if task_id in active_tasks:
                    del active_tasks[task_id]

# 获取最近的进度记录
@app.route('/get_recent_progress')
def get_recent_progress():
    recent_progress = []
    with active_tasks_lock:
        for task_id, thread in active_tasks.items():
            # 尝试从线程的 do_run 属性获取状态
            status = 'in_progress'
            if hasattr(thread, 'do_run') and not thread.do_run:
                status = 'terminated'
            elif hasattr(thread, 'do_run') and not getattr(thread, 'do_run', True):
                status = 'completed'
            elif hasattr(thread, 'do_run') and getattr(thread, 'do_run', True):
                status = 'in_progress'
            # 错误信息
            if hasattr(thread, 'error_message'):
                status = 'error'
                recent_progress.append({
                    'task_id': task_id,
                    'message': thread.error_message,
                    'type': 'error',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            else:
                recent_progress.append({
                    'task_id': task_id,
                    'message': '任务进行中',
                    'type': 'info',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
    recent_progress.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(recent_progress[:3])

def split_text_with_context(texts, terminology, context, document_summary, max_tokens=MAX_TOKENS, safe_margin=SAFE_MARGIN):
    """拆分文本并为每个批次生成上下文"""
    split_texts = []
    current_tokens = 0
    current_batch = []
    context_batches = []

    for text in texts:
        text_tokens = len(encoding.encode(text))
        if current_tokens + text_tokens > max_tokens - safe_margin:
            if current_batch:
                split_texts.append(current_batch)
                # 动态生成上下文
                relevant_terms = get_relevant_terms(current_batch, terminology)
                current_context = add_dynamic_terminology_to_context(context, relevant_terms)
                if document_summary:
                    current_context += f"\n\n文档背景理解：\n{document_summary}"
                context_batches.append(current_context)
            current_batch = []
            current_tokens = 0

        current_batch.append(text)
        current_tokens += text_tokens

    if current_batch:
        split_texts.append(current_batch)
        # 最后一个批次的上下文
        relevant_terms = get_relevant_terms(current_batch, terminology)
        current_context = add_dynamic_terminology_to_context(context, relevant_terms)
        if document_summary:
            current_context += f"\n\n文档背景理解：\n{document_summary}"
        context_batches.append(current_context)

    return split_texts, context_batches





# 获取未完成的任务
@app.route('/check_unfinished_tasks', methods=['GET'])
def check_unfinished_tasks():
    # 查询数据库中是否存在状态为 'in_progress' 的任务
    unfinished_tasks = Task.query.filter_by(status='in_progress').all()
    if unfinished_tasks:
        return jsonify({'status': 'unfinished', 'task_id': unfinished_tasks[0].id})
    return jsonify({'status': 'finished'})

# 新增重启应用的接口
@app.route('/reset_application', methods=['POST'])
def reset_application():
    try:
        # 终止所有活动任务
        with active_tasks_lock:
            for task_id, thread in active_tasks.items():
                thread.do_run = False
                # 更新任务状态为终止
                task = Task.query.get(task_id)
                if task:
                    task.status = 'terminated'
            # 清空活动任务列表
            active_tasks.clear()
        return jsonify({'status': 'success', 'message': '应用已重置'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# 获取任务进度的接口
@app.route('/get_progress/<task_id>')
def get_progress(task_id):
    # 获取最新的50条进度记录
    progress_list = Progress.query.filter_by(task_id=task_id)\
        .order_by(Progress.timestamp.desc())\
        .limit(50)\
        .all()
    # 获取任务状态
    task = Task.query.get(task_id)
    task_status = task.status if task else 'unknown'
    return jsonify({
        'status': task_status,
        'progress': [{
            'message': p.message,
            'type': p.type,
            'timestamp': p.timestamp.strftime('%H:%M:%S')
        } for p in progress_list[::-1]]  # 反转列表使其按时间正序
    })

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

# 后端参数动态化
DEFAULT_API_URL = "https://api.deepseek.com/v1"
DEFAULT_API_KEY = "sk-a765b6c0dfae46829e8368352513ec5b"
DEFAULT_MODEL_NAME = "deepseek-chat"

@app.route("/translate", methods=["POST"])
def translate_file():
    try:
        api_url = request.form.get("api_url", DEFAULT_API_URL)
        api_key = request.form.get("api_key", DEFAULT_API_KEY)
        model_name = request.form.get("model_name", DEFAULT_MODEL_NAME)
        # 获取原文文件（如果有）
        original_files_data = []
        if 'original_file' in request.files:
            for original_file in request.files.getlist("original_file"):
                if original_file.filename:  # 确保文件被选择
                    file_content = original_file.read()
                    original_files_data.append(file_content)
        # 获取 Trados 文件
        trados_files_data = []
        for trados_file in request.files.getlist("trados_file"):
            file_content = trados_file.read()
            trados_files_data.append({
                'filename': trados_file.filename,
                'content': file_content
            })
        # 获取术语表（如果有）
        term_file_content = None
        if 'term_file' in request.files and request.files['term_file'].filename:
            term_file = request.files["term_file"]
            term_file_content = term_file.read()
        translation_requirements = request.form.get("translation_requirements", "").strip()
        task_id = str(int(time.time()))
        thread = threading.Thread(
            target=process_translation,
            args=(task_id, trados_files_data, term_file_content, translation_requirements, original_files_data, api_url, api_key, model_name)
        )
        with active_tasks_lock:
            active_tasks[task_id] = thread
        thread.start()
        return jsonify({"status": "success", "task_id": task_id})
    except Exception as e:
        error_message = f"处理出错: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message}), 500

@app.route("/analyze_terms", methods=["POST"])
def analyze_terms_route():
    try:
        api_url = request.form.get("api_url", DEFAULT_API_URL)
        api_key = request.form.get("api_key", DEFAULT_API_KEY)
        model_name = request.form.get("model_name", DEFAULT_MODEL_NAME)
        contract_files_data = []
        for contract_file in request.files.getlist("contract_files"):
            file_content = contract_file.read()
            contract_files_data.append({
                'filename': contract_file.filename,
                'content': file_content
            })
        term_types = request.form.get("term_types", "").strip().split('\n')
        task_id = str(int(time.time()))
        thread = threading.Thread(
            target=process_term_analysis,
            args=(task_id, contract_files_data, term_types, api_url, api_key, model_name)
        )
        with active_tasks_lock:
            active_tasks[task_id] = thread
        thread.start()
        return jsonify({"status": "success", "task_id": task_id})
    except Exception as e:
        error_message = f"处理出错: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message}), 500

@app.route("/terminate/<task_id>", methods=["POST"])
def terminate_task(task_id):
    with active_tasks_lock:
        if task_id in active_tasks:
            thread = active_tasks[task_id]
            thread.do_run = False
            # 更新任务状态为终止
            task = Task.query.get(task_id)
            if task:
                task.status = 'terminated'
                db.session.commit()
            return jsonify({'message': '任务已终止'})
    return jsonify({'message': '未找到任务'}), 404

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        print(f"尝试下载：{file_path}")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        error_message = f"下载文件时出错: {str(e)}"
        print(error_message)
        return error_message, 404

@app.route('/clear-downloads', methods=['POST'])
def clear_downloads():
    try:
        # 仅隐藏状态为 'completed' 的任务
        Task.query.filter_by(status='completed').update({Task.is_hidden: True})
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# HTML模板
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>翻译助手</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .api-param-row {
            display: flex;
            flex-wrap: wrap;
            gap: 18px;
            margin-bottom: 18px;
            align-items: flex-end;
        }
        .api-param-item {
            display: flex;
            align-items: center;
            min-width: 260px;
            margin-bottom: 0;
        }
        .api-param-item label {
            min-width: 70px;
            margin-right: 6px;
            color: #555;
        }
        .api-param-item select,
        .api-param-item input[type="text"] {
            flex: 1 1 120px;
            padding: 6px 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 6px;
        }
        .api-param-item .history-btn {
            background: #eee;
            color: #333;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 13px;
            cursor: pointer;
            margin-right: 0;
        }
        .api-param-item .history-btn:hover {
            background: #e0e0e0;
        }
        .history-dropdown {
            position: absolute;
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            z-index: 100;
            min-width: 180px;
            max-height: 180px;
            overflow-y: auto;
            margin-top: 2px;
        }
        .history-dropdown-item {
            display: flex;
            align-items: center;
            padding: 4px 10px;
            font-size: 14px;
            cursor: pointer;
        }
        .history-dropdown-item:hover {
            background: #f5f5f5;
        }
        .history-dropdown-item .delete-btn {
            background: #e74c3c;
            color: #fff;
            border: none;
            border-radius: 2px;
            padding: 2px 6px;
            font-size: 12px;
            margin-left: 8px;
            cursor: pointer;
        }
        .history-dropdown-item .delete-btn:hover {
            background: #c0392b;
        }
        @media (max-width: 800px) {
            .api-param-row { flex-direction: column; gap: 8px; }
            .api-param-item { min-width: 0; }
        }
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        h2 {
            color: #666;
            margin-top: 30px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        input[type="file"], textarea, input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        .button-row {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            margin-top: 20px;
        }
        #reset-button {
            background-color: #f39c12;
        }
        #reset-button:hover {
            background-color: #e67e22;
        }
        #progress-container {
            margin-top: 20px;
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        .task-links {
            background-color: #f9f9f9;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .task-links h4 {
            margin-top: 0;
            color: #333;
        }
        .tab-container {
            margin-top: 20px;
        }
        .tab {
            background-color: #f1f1f1;
            border: none;
            border-radius: 4px 4px 0 0;
            color: #555;
            cursor: pointer;
            padding: 10px 15px;
            margin-right: 2px;
        }
        .tab.active {
            background-color: white;
            color: #4CAF50;
            border: 1px solid #ddd;
            border-bottom: none;
        }
        .tab-content {
            display: none;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 4px 4px;
            background-color: white;
        }
        .tab-content.active {
            display: block;
        }
        #clear-downloads-button {
            background-color: #e74c3c;
            margin-top: 10px;
        }
        #clear-downloads-button:hover {
            background-color: #c0392b;
        }
        .history-list {
            list-style: none;
            padding: 0;
            margin: 0 0 5px 0;
        }
        .history-list li {
            display: flex;
            align-items: center;
            margin-bottom: 2px;
            font-size: 14px;
        }
        .history-list button {
            background: #e74c3c;
            color: #fff;
            border: none;
            border-radius: 2px;
            padding: 2px 6px;
            font-size: 12px;
            margin-left: 8px;
            cursor: pointer;
        }
        .history-list button:hover {
            background: #c0392b;
        }
    </style>
</head>
<body>
    <div style="width:100%;text-align:center;margin-top:32px;margin-bottom:24px;">
        <img src="/static/logo.jpg" alt="logo" style="max-width:180px;width:40vw;height:auto;box-shadow:0 2px 8px #eee;border-radius:12px;">
    </div>
    <h1>文档翻译与术语分析助手</h1>
    <div class="tab-container">
        <button class="tab active" onclick="openTab(event, 'translation-tab')">翻译文档</button>
        <button class="tab" onclick="openTab(event, 'terms-tab')">术语分析</button>
    </div>
    <div id="translation-tab" class="tab-content active">
        <div class="container">
            <h2>文档翻译</h2>
            <form id="translate-form">
                <div class="api-param-row">
                    <div class="api-param-item">
                        <label for="api_selector">API类型：</label>
                        <select id="api_selector">
                            <option value="https://yunwu.ai/v1">云雾API</option>
                            <option value="https://api.deepseek.com/v1">deepseekAPI</option>
                        </select>
                    </div>
                    <div class="api-param-item">
                        <label for="api_url">API URL：</label>
                        <input type="text" id="api_url" name="api_url" value="https://yunwu.ai/v1" />
                    </div>
                    <div class="api-param-item" style="position:relative;">
                        <label for="api_key">API Key：</label>
                        <input type="text" id="api_key" name="api_key" placeholder="请输入API Key" autocomplete="off" />
                        <button type="button" class="history-btn" onclick="showHistoryDropdown(event, 'api_key')">历史</button>
                        <div class="history-dropdown" id="api_key_history_dropdown" style="display:none;"></div>
                    </div>
                    <div class="api-param-item" style="position:relative;">
                        <label for="model_name">模型名称：</label>
                        <input type="text" id="model_name" name="model_name" placeholder="请输入模型名称" autocomplete="off" />
                        <button type="button" class="history-btn" onclick="showHistoryDropdown(event, 'model_name')">历史</button>
                        <div class="history-dropdown" id="model_name_history_dropdown" style="display:none;"></div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="original_file">原文文件（可选，帮助理解文档内容）:</label>
                    <input type="file" id="original_file" name="original_file" accept=".docx" multiple>
                </div>
                <div class="form-group">
                    <label for="trados_file">Trados 翻译文件（必选）:</label>
                    <input type="file" id="trados_file" name="trados_file" accept=".docx" multiple required>
                </div>
                <div class="form-group">
                    <label for="term_file">术语表（可选，Excel格式，第一列为原文术语，第二列为译文术语）:</label>
                    <input type="file" id="term_file" name="term_file" accept=".xlsx">
                </div>
                <div class="form-group">
                    <label for="translation_requirements">翻译要求:</label>
                    <textarea id="translation_requirements" name="translation_requirements" placeholder="请输入对翻译的特殊要求，例如风格、口吻、特定行业术语的处理方式等"></textarea>
                </div>
                <div class="button-row">
                    <button type="submit" id="translate-button">开始翻译</button>
                    <button type="button" id="reset-button">重启程序</button>
                    <button type="button" id="check-unfinished-tasks-button">查询未完成任务</button>
                </div>
            </form>
        </div>
    </div>
    <div id="terms-tab" class="tab-content">
        <div class="container">
            <h2>术语分析</h2>
            <form id="analyze-terms-form">
                <div class="api-param-row">
                    <div class="api-param-item">
                        <label for="api_selector_terms">API类型：</label>
                        <select id="api_selector_terms">
                            <option value="https://yunwu.ai/v1">云雾API</option>
                            <option value="https://api.deepseek.com/v1">deepseekAPI</option>
                        </select>
                    </div>
                    <div class="api-param-item">
                        <label for="api_url_terms">API URL：</label>
                        <input type="text" id="api_url_terms" name="api_url" value="https://yunwu.ai/v1" />
                    </div>
                    <div class="api-param-item" style="position:relative;">
                        <label for="api_key_terms">API Key：</label>
                        <input type="text" id="api_key_terms" name="api_key" placeholder="请输入API Key" autocomplete="off" />
                        <button type="button" class="history-btn" onclick="showHistoryDropdown(event, 'api_key_terms')">历史</button>
                        <div class="history-dropdown" id="api_key_history_dropdown_terms" style="display:none;"></div>
                    </div>
                    <div class="api-param-item" style="position:relative;">
                        <label for="model_name_terms">模型名称：</label>
                        <input type="text" id="model_name_terms" name="model_name" placeholder="请输入模型名称" autocomplete="off" />
                        <button type="button" class="history-btn" onclick="showHistoryDropdown(event, 'model_name_terms')">历史</button>
                        <div class="history-dropdown" id="model_name_history_dropdown_terms" style="display:none;"></div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="contract_files">需要分析的文档:</label>
                    <input type="file" id="contract_files" name="contract_files" accept=".docx" multiple required>
                </div>
                <div class="form-group">
                    <label for="term_types">术语类型（每行一个类型）:</label>
                    <textarea id="term_types" name="term_types" placeholder="例如:&#10;法律术语&#10;财务术语&#10;技术术语" required></textarea>
                </div>
                <div class="button-row">
                    <button type="submit" id="analyze-button">开始分析</button>
                    <button type="button" id="reset-button-terms" class="reset-button">重启程序</button>
                </div>
            </form>
        </div>
    </div>
    <div class="container">
        <h2>处理进度</h2>
        <div id="progress-container"></div>
    </div>
    <script>
        // ========== API参数历史管理 ========== //
        function saveHistory(key, value) {
            if (!value) return;
            let arr = JSON.parse(localStorage.getItem(key) || '[]');
            if (!arr.includes(value)) {
                arr.unshift(value);
                if (arr.length > 10) arr = arr.slice(0, 10);
                localStorage.setItem(key, JSON.stringify(arr));
            }
        }
        function loadHistory(key) {
            return JSON.parse(localStorage.getItem(key) || '[]');
        }
        function removeHistory(key, value) {
            let arr = loadHistory(key);
            arr = arr.filter(v => v !== value);
            localStorage.setItem(key, JSON.stringify(arr));
        }
        // ========== 弹出式历史菜单 ========== //
        function showHistoryDropdown(event, type) {
            event.stopPropagation();
            closeAllDropdowns();
            let inputId = type;
            let dropdownId = type + '_history_dropdown';
            let key = type + '_history';
            let input = document.getElementById(inputId);
            let dropdown = document.getElementById(dropdownId);
            let arr = loadHistory(key);
            dropdown.innerHTML = '';
            if (arr.length === 0) {
                let empty = document.createElement('div');
                empty.textContent = '暂无历史';
                empty.style.color = '#aaa';
                empty.style.padding = '8px 12px';
                dropdown.appendChild(empty);
            } else {
                arr.forEach(val => {
                    let item = document.createElement('div');
                    item.className = 'history-dropdown-item';
                    let span = document.createElement('span');
                    span.textContent = val;
                    span.style.flex = '1';
                    span.onclick = function(e) {
                        input.value = val;
                        saveHistory(key, val);
                        dropdown.style.display = 'none';
                        e.stopPropagation();
                    };
                    let del = document.createElement('button');
                    del.className = 'delete-btn';
                    del.textContent = '删除';
                    del.onclick = function(e) {
                        removeHistory(key, val);
                        showHistoryDropdown(event, type);
                        e.stopPropagation();
                    };
                    item.appendChild(span);
                    item.appendChild(del);
                    dropdown.appendChild(item);
                });
            }
            dropdown.style.display = 'block';
        }
        function closeAllDropdowns() {
            document.getElementById('api_key_history_dropdown').style.display = 'none';
            document.getElementById('model_name_history_dropdown').style.display = 'none';
            if(document.getElementById('api_key_history_dropdown_terms'))
                document.getElementById('api_key_history_dropdown_terms').style.display = 'none';
            if(document.getElementById('model_name_history_dropdown_terms'))
                document.getElementById('model_name_history_dropdown_terms').style.display = 'none';
        }
        document.addEventListener('click', closeAllDropdowns);
        // 输入失焦自动保存历史
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('api_key').addEventListener('blur', function() {
                saveHistory('api_key_history', this.value.trim());
            });
            document.getElementById('model_name').addEventListener('blur', function() {
                saveHistory('model_name_history', this.value.trim());
            });
            // 术语分析区
            if(document.getElementById('api_key_terms')) {
                document.getElementById('api_key_terms').addEventListener('blur', function() {
                    saveHistory('api_key_history_terms', this.value.trim());
                });
            }
            if(document.getElementById('model_name_terms')) {
                document.getElementById('model_name_terms').addEventListener('blur', function() {
                    saveHistory('model_name_history_terms', this.value.trim());
                });
            }
        });
        // ========== API参数区联动 ========== //
        function setupApiParamArea(prefix) {
            // 下拉选择自动填充API URL
            const selector = document.getElementById(prefix + 'api_selector');
            const urlInput = document.getElementById(prefix + 'api_url');
            if (selector && urlInput) {
                selector.addEventListener('change', function() {
                    urlInput.value = this.value;
                });
            }
            // 历史管理
            renderHistoryList(prefix + 'api_key_history', prefix + 'api_key_list', prefix + 'api_key_history', prefix + 'api_key');
            renderHistoryList(prefix + 'model_name_history', prefix + 'model_name_list', prefix + 'model_name_history', prefix + 'model_name');
            // 输入后保存历史
            const apiKeyInput = document.getElementById(prefix + 'api_key');
            if (apiKeyInput) {
                apiKeyInput.addEventListener('blur', function() {
                    saveHistory(prefix + 'api_key_history', this.value.trim());
                    renderHistoryList(prefix + 'api_key_history', prefix + 'api_key_list', prefix + 'api_key_history', prefix + 'api_key');
                });
            }
            const modelNameInput = document.getElementById(prefix + 'model_name');
            if (modelNameInput) {
                modelNameInput.addEventListener('blur', function() {
                    saveHistory(prefix + 'model_name_history', this.value.trim());
                    renderHistoryList(prefix + 'model_name_history', prefix + 'model_name_list', prefix + 'model_name_history', prefix + 'model_name');
                });
            }
        }
        document.addEventListener('DOMContentLoaded', function() {
            setupApiParamArea(''); // 文档翻译区
            setupApiParamArea('terms_'); // 术语分析区
        });
        // ========== 其余原有JS逻辑（进度、tab、表单等） ========== //
        // 全局变量
        let currentTaskId = null;
        let progressCheckInterval = null;
        // 获取历史进度，用于页面初始化或重新加载
        function getRecentProgress() {
            fetch('/get_recent_progress')
                .then(response => response.json())
                .then(data => {
                    const progressContainer = document.getElementById('progress-container');
                    progressContainer.innerHTML = '';
                    data.forEach(item => {
                        const messageElement = document.createElement('div');
                        messageElement.textContent = `[${item.timestamp}] ${item.message}`;
                        switch(item.type) {
                            case 'error':
                                messageElement.style.color = 'red';
                                break;
                            case 'translation':
                                messageElement.style.color = 'blue';
                                break;
                            case 'reading':
                                messageElement.style.color = 'green';
                                break;
                            case 'saving':
                                messageElement.style.color = 'purple';
                                break;
                            case 'terms':
                                messageElement.style.color = 'darkorange';
                                break;
                        }
                        progressContainer.appendChild(messageElement);
                    });
                    if (data.length > 0) {
                        progressContainer.scrollTop = progressContainer.scrollHeight;
                    }
                });
        }
        // 重置应用
        function resetApplication() {
            // 发送重置请求
            fetch('/reset_application', {
                method: 'POST'
            }).then(response => response.json()).then(data => {
                if (data.status === 'success') {
                    // 停止进度轮询
                    if (progressCheckInterval) {
                        clearInterval(progressCheckInterval);
                        progressCheckInterval = null;
                    }
                    // 重置当前任务ID
                    currentTaskId = null;
                    // 清空进度显示
                    const progressContainer = document.getElementById('progress-container');
                    progressContainer.innerHTML = '';
                    // 重新加载任务历史（这会清除之前的下载链接）
                    loadTaskHistory();
                    // 重置表单
                    document.getElementById('translate-form').reset();
                    document.getElementById('analyze-terms-form').reset();
                    // 显示成功消息
                    const messageElement = document.createElement('div');
                    messageElement.textContent = `[${new Date().toLocaleTimeString()}] 应用已重置，所有任务已终止`;
                    messageElement.style.color = 'blue';
                    progressContainer.appendChild(messageElement);
                    alert('程序已重置');
                } else {
                    alert('重置程序失败：' + data.message);
                }
            });
        }
        // 开始检查进度
        function startProgressChecking(taskId) {
            // 如果已经有进度检查在进行，先停止
            if (progressCheckInterval) {
                clearInterval(progressCheckInterval);
            }
            currentTaskId = taskId;
            const progressContainer = document.getElementById('progress-container');
            progressCheckInterval = setInterval(() => {
                fetch(`/get_progress/${taskId}`)
                    .then(response => response.json())
                    .then(data => {
                        // 更新进度显示
                        data.progress.forEach(item => {
                            // 检查是否已存在相同的消息
                            const messageId = `${item.timestamp}-${item.message}`;
                            if (!document.getElementById(messageId)) {
                                const messageElement = document.createElement('div');
                                messageElement.id = messageId;
                                messageElement.textContent = `[${item.timestamp}] ${item.message}`;
                                switch(item.type) {
                                    case 'error':
                                        messageElement.style.color = 'red';
                                        break;
                                    case 'translation':
                                        messageElement.style.color = 'blue';
                                        break;
                                    case 'reading':
                                        messageElement.style.color = 'green';
                                        break;
                                    case 'saving':
                                        messageElement.style.color = 'purple';
                                        break;
                                    case 'terms':
                                        messageElement.style.color = 'darkorange';
                                        break;
                                }
                                progressContainer.appendChild(messageElement);
                                progressContainer.scrollTop = progressContainer.scrollHeight;
                            }
                        });
                        // 如果任务完成，刷新下载链接并停止检查
                        if (data.status === 'completed' || data.status === 'error' || data.status === 'terminated') {
                            loadTaskHistory();
                            clearInterval(progressCheckInterval);
                            currentTaskId = null;
                        }
                    })
                    .catch(error => {
                        console.error('Error checking progress:', error);
                    });
            }, 2000);
        }
        // 切换标签页功能
        function openTab(evt, tabName) {
            var i, tabContent, tabButtons;
            // 隐藏所有标签内容
            tabContent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabContent.length; i++) {
                tabContent[i].classList.remove("active");
            }
            // 取消所有标签按钮的激活状态
            tabButtons = document.getElementsByClassName("tab");
            for (i = 0; i < tabButtons.length; i++) {
                tabButtons[i].classList.remove("active");
            }
            // 显示当前标签内容并激活按钮
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        // 页面的自适应
        document.addEventListener('DOMContentLoaded', function() {
            loadTaskHistory();
            getRecentProgress();
        });
        // 修改表单提交处理
        document.getElementById('translate-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            // 兼容性处理：如果api_key为空，自动用默认
            if (!formData.get('api_url')) formData.set('api_url', 'https://api.deepseek.com/v1');
            if (!formData.get('model_name')) formData.set('model_name', 'deepseek-chat');
            fetch('/translate', {
                method: 'POST',
                body: formData
            }).then(response => response.json()).then(data => {
                if (data.task_id) {
                    startProgressChecking(data.task_id);
                }
            });
        });
        // 修改术语分析表单提交处理
        document.getElementById('analyze-terms-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            if (!formData.get('api_url')) formData.set('api_url', 'https://api.deepseek.com/v1');
            if (!formData.get('model_name')) formData.set('model_name', 'deepseek-chat');
            fetch('/analyze_terms', {
                method: 'POST',
                body: formData
            }).then(response => response.json()).then(data => {
                if (data.task_id) {
                    startProgressChecking(data.task_id);
                }
            });
        });
        // 清除下载功能
        document.getElementById('clear-downloads-button').addEventListener('click', function() {
            fetch('/clear-downloads', {
                method: 'POST'
            }).then(response => response.json())
              .then(data => {
                  if (data.status === 'success') {
                      const downloadLinks = document.getElementById('download-links');
                      downloadLinks.innerHTML = '';
                  } else {
                      alert('清除下载链接失败：' + data.message);
                  }
              });
        });
        // 添加重启按钮事件处理
        document.getElementById('reset-button').addEventListener('click', resetApplication);
        document.getElementById('reset-button-terms').addEventListener('click', resetApplication);

        // 检查未完成任务的功能
        document.getElementById('check-unfinished-tasks-button').addEventListener('click', function() {
            fetch('/check_unfinished_tasks')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'unfinished' && data.task_id) {
                        alert('存在未完成的任务，开始检查任务进度');
                        startProgressChecking(data.task_id);
                    } else {
                        alert('没有未完成的任务');
                    }
                })
                .catch(error => {
                    console.error('查询未完成任务出错:', error);
                });
        });
        // WebSocket实时进度推送
        // 移除所有WebSocket相关代码，只保留数据库进度写入和前端接口轮询
        // update_progress只写数据库不推送WebSocket
        // 前端只用/get_progress接口轮询显示进度，不包含socket.io相关JS
    </script>
    <script>
    window.onload = function() {
        // 尝试全屏
        let el = document.documentElement;
        if (el.requestFullscreen) {
            el.requestFullscreen();
        } else if (el.webkitRequestFullScreen) {
            el.webkitRequestFullScreen();
        } else if (el.mozRequestFullScreen) {
            el.mozRequestFullScreen();
        } else if (el.msRequestFullscreen) {
            el.msRequestFullscreen();
        }
    };
    </script>
    <!-- 页面主体内容结束 -->
    <div style="width:100%;text-align:center;color:#888;font-size:13px;margin-top:48px;margin-bottom:18px;line-height:1.7;">
        本系统由开发者为广州译语言翻译服务有限责任公司专属定制开发。未经开发者与广州译语言翻译服务有限责任公司双方书面同意，开发者本人及公司均不得擅自转售、授权、复制、传播或用于其他商业用途。<br>
        开发者联系电话：16670034670
    </div>
</body>
</html>
'''

# 2. 初始化SocketIO（在app = Flask(__name__)后）
# 移除所有WebSocket相关代码，只保留数据库进度写入和前端接口轮询
# update_progress只写数据库不推送WebSocket
# 前端只用/get_progress接口轮询显示进度，不包含socket.io相关JS

def get_unique_filepath(directory, filename):
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}({i}){ext}"
        i += 1
    return os.path.join(directory, candidate)

if __name__ == '__main__':
    def start_flask():
        with app.app_context():
            db.create_all()
        app.run(host='0.0.0.0', port=5001, debug=False)

    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    time.sleep(1.5)  # 等待 Flask 启动

    import webview
    webview.create_window('译语言翻译系统', 'http://127.0.0.1:5001', width=1200, height=800, fullscreen=True)
    webview.start()
