import sqlite3
import random
import json
from datetime import datetime
from pylatex import Document, Section, Subsection, Command # type: ignore
from pylatex.utils import bold, NoEscape # type: ignore
import traceback

# ===== 題庫管理系統 =====
class QuestionBank:
    def __init__(self, db_path='question_bank.db'):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """建立數據庫連接"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Enable JSON extension for SQLite
            self.conn.execute('PRAGMA foreign_keys = ON')
        except sqlite3.Error as e:
            print(f"數據庫連接錯誤: {e}")
            raise
    
    def _create_tables(self):
        """創建數據庫表結構"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                q_type TEXT NOT NULL CHECK(q_type IN ('multiple_choice', 'fill_in_blank', 'essay')),
                options TEXT,          -- JSON格式: ["選項1", "選項2"]
                answer TEXT NOT NULL,
                knowledge_points TEXT, -- JSON格式: ["代數", "函數"]
                difficulty INTEGER CHECK(difficulty BETWEEN 1 AND 5),
                last_used DATE,
                usage_count INTEGER DEFAULT 0
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                config TEXT NOT NULL,   -- JSON格式的組卷配置
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"創建表錯誤: {e}")
            self.conn.rollback()
            raise
    
    def __del__(self):
        """析構函數，關閉數據庫連接"""
        if self.conn:
            self.conn.close()
    
    def add_question(self, content, q_type, answer, knowledge_points, difficulty, options=None):
        """添加題目到題庫"""
        try:
            if not content or not q_type or not answer:
                raise ValueError("內容、題型和答案不能為空")
            
            if difficulty not in range(1, 6):
                raise ValueError("難度必須在1-5之間")
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO questions (content, q_type, options, answer, knowledge_points, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                content.strip(),
                q_type.strip(),
                json.dumps(options, ensure_ascii=False) if options else None,
                answer.strip(),
                json.dumps([kp.strip() for kp in knowledge_points if kp.strip()], ensure_ascii=False),
                difficulty
            ))
            self.conn.commit()
            return cursor.lastrowid
        except (sqlite3.Error, json.JSONEncodeError) as e:
            print(f"添加題目錯誤: {e}")
            self.conn.rollback()
            raise
    
    def get_questions(self, filters=None):
        """根據條件篩選題目"""
        try:
            query = "SELECT * FROM questions WHERE 1=1"
            params = []
            
            if filters:
                if 'knowledge_points' in filters and filters['knowledge_points']:
                    query += " AND EXISTS (SELECT 1 FROM json_each(knowledge_points) WHERE value IN ({0}))".format
                    ','.join(['?']*len(filters['knowledge_points']))
                    params.extend([kp.strip() for kp in filters['knowledge_points'] if kp.strip()])
                    
                if 'difficulty_range' in filters:
                    min_diff, max_diff = filters['difficulty_range']
                    if min_diff > max_diff:
                        min_diff, max_diff = max_diff, min_diff
                    query += " AND difficulty BETWEEN ? AND ?"
                    params.extend([min_diff, max_diff])
                    
                if 'exclude_used' in filters and filters['exclude_used']:
                    query += " AND (last_used IS NULL OR last_used < date('now', '-6 months'))"
                
                if 'q_type' in filters and filters['q_type']:
                    query += " AND q_type = ?"
                    params.append(filters['q_type'])
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"查詢題目錯誤: {e}")
            raise

# ===== 智能組卷引擎 =====
class ExamGenerator:
    def __init__(self, question_bank):
        self.bank = question_bank
    
    def generate_exam(self, config):
        """
        根據配置生成試卷
        """
        if not config.get('sections'):
            raise ValueError("試卷配置必須包含題目部分")
    
        
        exam_questions = []
        used_ids = set()
        
        try:
            # 為每個部分生成題目
            for section in config['sections']:
                if not all(key in section for key in ['type', 'count', 'points_per']):
                    raise ValueError("每個題目部分必須包含type, count和points_per字段")
                
                filters = {
                    'q_type': section['type'],
                    'knowledge_points': section.get('knowledge_points', []),
                    'difficulty_range': section.get('difficulty_range', [1, 5]),
                    'exclude_used': section.get('exclude_used', True)
                }
                
                candidates = self.bank.get_questions(filters)
                candidates = [q for q in candidates if q[0] not in used_ids]
                
                if len(candidates) < section['count']:
                    # 嘗試放寬條件
                    filters['exclude_used'] = False
                    candidates = self.bank.get_questions(filters)
                    candidates = [q for q in candidates if q[0] not in used_ids]
                    
                    if len(candidates) < section['count']:
                        raise ValueError(f"題庫不足: 需要{section['count']}道{section['type']}題，僅找到{len(candidates)}道")
                
                selected = random.sample(candidates, section['count'])
                exam_questions.extend(selected)
                used_ids.update(q[0] for q in selected)
            
            return exam_questions
        except Exception as e:
            print(f"生成試卷錯誤: {e}")
            raise

# ===== PDF生成模塊 =====
class PDFGenerator:
    @staticmethod
    def escape_latex(text):
        """轉義LaTeX特殊字符"""
        if not text:
            return ""
        escape_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}'
        }
        return ''.join(escape_chars.get(c, c) for c in text)
    
    @staticmethod
    def create_exam_pdf(exam_title, questions, output_file="exam.pdf"):
        """生成PDF格式試卷"""
        try:
            doc = Document(documentclass="article", document_options=["a4paper"])
            
            # 添加試卷標頭
            doc.preamble.append(Command('title', PDFGenerator.escape_latex(exam_title)))
            doc.preamble.append(Command('date', NoEscape(r'\today')))
            doc.append(NoEscape(r'\maketitle'))
            
            # 添加題目
            with doc.create(Section("試題")):
                for i, q in enumerate(questions, 1):
                    q_content = PDFGenerator.escape_latex(q[1])  # 題目內容
                    q_type = q[2]
                    
                    with doc.create(Subsection(f"問題 {i}", numbering=False)):
                        doc.append(bold(f"({q_type}) ") + q_content)
                        
                        # 如果是選擇題，添加選項
                        if q_type == "multiple_choice" and q[3]:
                            try:
                                options = json.loads(q[3])
                                doc.append(NoEscape(r'\begin{itemize}'))
                                for opt in options:
                                    doc.append(NoEscape(rf'\item {PDFGenerator.escape_latex(opt)}'))
                                doc.append(NoEscape(r'\end{itemize}'))
                            except json.JSONDecodeError:
                                doc.append("\n[選項格式錯誤]")
            
            # 添加答案頁
            with doc.create(Section("參考答案", numbering=False)):
                doc.append(NoEscape(r'\begin{itemize}'))
                for i, q in enumerate(questions, 1):
                    doc.append(NoEscape(rf'\item[{i}.] {PDFGenerator.escape_latex(q[4])}'))
                doc.append(NoEscape(r'\end{itemize}'))
            
            # 生成PDF
            doc.generate_pdf(output_file.replace('.pdf', ''), clean_tex=True)
            return True
        except Exception as e:
            print(f"生成PDF錯誤: {e}")
            traceback.print_exc()
            return False

# ===== 導師操作界面 =====
def teacher_interface():
    try:
        bank = QuestionBank()
        generator = ExamGenerator(bank)
        
        # 初始化示例題目
        if not bank.get_questions():
            print("初始化題庫...")
            bank.add_question(
                "二次函數 $y=ax^2+bx+c$ 的頂點坐標公式是？",
                "fill_in_blank",
                r"$\left( -\frac{b}{2a}, \frac{4ac-b^2}{4a} \right)$",
                ["代數", "函數"],
                3
            )
            bank.add_question(
                "已知三角形ABC,∠A=30°,∠B=60°則∠C=?",
                "multiple_choice",
                "90°",
                ["幾何", "三角形"],
                2,
                ["30°", "60°", "90°", "120°"]
            )
        
        while True:
            print("\n===== 智能試卷生成系統 =====")
            print("1. 添加新題目")
            print("2. 生成新試卷")
            print("3. 使用模板生成試卷")
            print("4. 退出系統")
            
            choice = input("請選擇操作: ").strip()
            
            if choice == "1":
                try:
                    print("\n添加新題目:")
                    content = input("題目內容: ").strip()
                    while not content:
                        print("內容不能為空!")
                        content = input("題目內容: ").strip()
                    
                    q_type = input("題型 (multiple_choice/fill_in_blank/essay): ").strip().lower()
                    while q_type not in ['multiple_choice', 'fill_in_blank', 'essay']:
                        print("無效題型!")
                        q_type = input("題型 (multiple_choice/fill_in_blank/essay): ").strip().lower()
                    
                    answer = input("答案: ").strip()
                    while not answer:
                        print("答案不能為空!")
                        answer = input("答案: ").strip()
                    
                    knowledge = [kp.strip() for kp in input("知識點 (逗號分隔): ").split(",") if kp.strip()]
                    while not knowledge:
                        print("至少需要一個知識點!")
                        knowledge = [kp.strip() for kp in input("知識點 (逗號分隔): ").split(",") if kp.strip()]
                    
                    difficulty = input("難度 (1-5): ")
                    while not difficulty.isdigit() or int(difficulty) not in range(1, 6):
                        print("難度必須是1-5的數字!")
                        difficulty = input("難度 (1-5): ")
                    difficulty = int(difficulty)
                    
                    options = None
                    if q_type == "multiple_choice":
                        options = []
                        while True:
                            opt = input("輸入選項 (直接回車結束): ").strip()
                            if not opt:
                                if len(options) < 2:
                                    print("至少需要2個選項!")
                                    continue
                                break
                            options.append(opt)
                    
                    bank.add_question(content, q_type, answer, knowledge, difficulty, options)
                    print("題目添加成功!")
                except Exception as e:
                    print(f"操作失敗: {e}")
            
            elif choice == "2":
                try:
                    print("\n生成新試卷:")
                    title = input("試卷標題: ").strip()
                    while not title:
                        print("標題不能為空!")
                        title = input("試卷標題: ").strip()
                    
                    total_points = input("總分: ")
                    while not total_points.isdigit() or int(total_points) <= 0:
                        print("總分必須是正整數!")
                        total_points = input("總分: ")
                    total_points = int(total_points)
                    
                    sections = []
                    while True:
                        print("\n添加題目部分:")
                        s_type = input("題型 (multiple_choice/fill_in_blank/essay): ").strip().lower()
                        while s_type not in ['multiple_choice', 'fill_in_blank', 'essay']:
                            print("無效題型!")
                            s_type = input("題型 (multiple_choice/fill_in_blank/essay): ").strip().lower()
                        
                        s_count = input("題數: ")
                        while not s_count.isdigit() or int(s_count) <= 0:
                            print("題數必須是正整數!")
                            s_count = input("題數: ")
                        s_count = int(s_count)
                        
                        s_points = input("每題分數: ")
                        while not s_points.replace('.', '').isdigit() or float(s_points) <= 0:
                            print("分數必須是正數!")
                            s_points = input("每題分數: ")
                        s_points = float(s_points)
                        
                        s_knowledge = [kp.strip() for kp in input("知識點 (逗號分隔，留空為不限): ").split(",") if kp.strip()]
                        
                        s_diff_min = input("最低難度 (1-5): ")
                        while not s_diff_min.isdigit() or int(s_diff_min) not in range(1, 6):
                            print("難度必須是1-5的數字!")
                            s_diff_min = input("最低難度 (1-5): ")
                        s_diff_min = int(s_diff_min)
                        
                        s_diff_max = input("最高難度 (1-5): ")
                        while not s_diff_max.isdigit() or int(s_diff_max) not in range(1, 6):
                            print("難度必須是1-5的數字!")
                            s_diff_max = input("最高難度 (1-5): ")
                        s_diff_max = int(s_diff_max)
                        
                        sections.append({
                            "type": s_type,
                            "count": s_count,
                            "points_per": s_points,
                            "knowledge_points": s_knowledge,
                            "difficulty_range": [min(s_diff_min, s_diff_max), max(s_diff_min, s_diff_max)]
                        })
                        
                        if input("添加更多部分? (y/n): ").strip().lower() != 'y':
                            break
                    
                    config = {
                        "title": title,
                        "total_points": total_points,
                        "sections": sections
                    }
                    
                    questions = generator.generate_exam(config)
                    output_file = f"{title.replace(' ', '_')}.pdf"
                    if PDFGenerator.create_exam_pdf(title, questions, output_file):
                        print(f"試卷生成成功: {output_file}")
                        
                        if input("保存為模板? (y/n): ").strip().lower() == 'y':
                            template_id = generator.save_exam_template(config)
                            print(f"模板保存成功 (ID: {template_id})")
                    else:
                        print("試卷生成失敗")
                
                except Exception as e:
                    print(f"操作失敗: {e}")
            
            elif choice == "3":
                print("\n使用模板生成試卷:")
                # 實現從數據庫加載模板的功能
                try:
                    cursor = bank.conn.cursor()
                    cursor.execute("SELECT id, title FROM exams ORDER BY created_at DESC")
                    templates = cursor.fetchall()
                    
                    if not templates:
                        print("沒有找到任何模板")
                        continue
                    
                    print("\n可用模板:")
                    for t in templates:
                        print(f"{t[0]}. {t[1]}")
                    
                    template_id = input("請選擇模板ID: ").strip()
                    while not template_id.isdigit() or int(template_id) not in [t[0] for t in templates]:
                        print("無效的模板ID!")
                        template_id = input("請選擇模板ID: ").strip()
                    template_id = int(template_id)
                    
                    cursor.execute("SELECT config FROM exams WHERE id = ?", (template_id,))
                    config = json.loads(cursor.fetchone()[0])
                    
                    questions = generator.generate_exam(config)
                    output_file = f"{config['title'].replace(' ', '_')}_from_template.pdf"
                    if PDFGenerator.create_exam_pdf(config['title'], questions, output_file):
                        print(f"試卷生成成功: {output_file}")
                    else:
                        print("試卷生成失敗")
                
                except Exception as e:
                    print(f"操作失敗: {e}")
            
            elif choice == "4":
                print("系統退出")
                break
            
            else:
                print("無效選擇，請重新輸入!")
    
    except Exception as e:
        print(f"系統錯誤: {e}")
        traceback.print_exc()
    finally:
        if 'bank' in locals():
            del bank  # 觸發析構函數關閉數據庫連接