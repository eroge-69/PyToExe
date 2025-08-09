import time
import datetime
import json
import os
import argparse

TASK_FILE = os.path.join(os.getcwd(), "tasks.json")

class TaskManager:
    def __init__(self, task_file=TASK_FILE):
        self.tasks = []
        self.completed_tasks = []
        self.pomodoro_sessions = 0
        self.task_file = task_file
        self.load_tasks()
        
    def load_tasks(self):
        if os.path.exists(self.task_file):
            try:
                with open(self.task_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.completed_tasks = data.get('completed_tasks', [])
                    self.pomodoro_sessions = data.get('pomodoro_sessions', 0)
            except Exception as e:
                print("تعذر تحميل ملف المهام:", e)
    
    def save_tasks(self):
        data = {
            'tasks': self.tasks,
            'completed_tasks': self.completed_tasks,
            'pomodoro_sessions': self.pomodoro_sessions
        }
        try:
            with open(self.task_file, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("تعذر حفظ ملف المهام:", e)
    
    def add_task(self, name, priority=1, estimated_pomodoros=1, due_date=None):
        max_id = max([t['id'] for t in self.tasks], default=0)
        task = {
            'id': max_id + 1,
            'name': name,
            'priority': priority,
            'estimated_pomodoros': estimated_pomodoros,
            'completed_pomodoros': 0,
            'due_date': due_date,
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'completed': False
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def complete_task(self, task_id):
        for task in list(self.tasks):
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.completed_tasks.append(task)
                self.tasks.remove(task)
                self.save_tasks()
                return True
        return False
    
    def complete_pomodoro(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed_pomodoros'] += 1
                self.pomodoro_sessions += 1
                self.save_tasks()
                
                if task['completed_pomodoros'] >= task['estimated_pomodoros']:
                    self.complete_task(task_id)
                return True
        return False
    
    def get_tasks_by_priority(self):
        return sorted(self.tasks, key=lambda x: (-x['priority'], x.get('due_date', '') or ''))
    
    def get_daily_stats(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        completed_today = [t for t in self.completed_tasks if t.get('completed_at', '').startswith(today)]
        return {
            'total_tasks': len(self.tasks),
            'completed_tasks': len(completed_today),
            'pomodoros_today': sum(t.get('completed_pomodoros', 0) for t in completed_today),
            'total_pomodoros': self.pomodoro_sessions
        }


class PomodoroTimer:
    def __init__(self, task_manager, work_minutes=25, break_minutes=5, long_break_minutes=15, fast=False):
        # if fast=True then the numbers are seconds for quick testing
        self.task_manager = task_manager
        self.fast = fast
        if fast:
            self.work_duration = work_minutes  # seconds
            self.break_duration = break_minutes
            self.long_break_duration = long_break_minutes
        else:
            self.work_duration = work_minutes * 60
            self.break_duration = break_minutes * 60
            self.long_break_duration = long_break_minutes * 60
        self.current_task_id = None
        self.is_running = False
        self.session_count = 0
    
    def start_work(self, task_id):
        self.current_task_id = task_id
        self.is_running = True
        self._print_banner(f"بدء جلسة العمل على المهمة: {self.get_task_name(task_id)}")
        self._run_timer(self.work_duration, "عمل")
        self.task_manager.complete_pomodoro(task_id)
        self.session_count += 1
        
        if self.session_count % 4 == 0:
            self.start_break(long=True)
        else:
            self.start_break()
    
    def start_break(self, long=False):
        duration = self.long_break_duration if long else self.break_duration
        break_type = "استراحة طويلة" if long else "استراحة قصيرة"
        self._print_banner(f"حان وقت {break_type}!")
        self._run_timer(duration, break_type)
    
    def _run_timer(self, duration, timer_type):
        start_time = time.time()
        try:
            while self.is_running and time.time() - start_time < duration:
                remaining = int(duration - (time.time() - start_time))
                mins, secs = divmod(remaining, 60)
                print(f"\r{timer_type} الوقت المتبقي: {mins:02d}:{secs:02d}", end="")
                time.sleep(1)
            if self.is_running:
                self._alert(f"انتهى وقت {timer_type}!")
                print()
        except KeyboardInterrupt:
            self.is_running = False
            print("\\nتم إيقاف المؤقت يدوياً.")
    
    def stop(self):
        self.is_running = False
    
    def _alert(self, message):
        print(f"\\nتنبيه: {message}")
    
    def get_task_name(self, task_id):
        for task in self.task_manager.tasks:
            if task['id'] == task_id:
                return task['name']
        return "مهمة غير معروفة"
    
    def _print_banner(self, text):
        print("\\n" + "="*50)
        print(text)
        print("="*50 + "\\n")


def show_welcome():
    print("\\n" + "="*50)
    print("مدير المهام التفاعلي مع تقنية بومودورو")
    print("="*50)
    print("\\nهذا البرنامج تفاعلي - ستختار المهام وتبدأ الجلسات بنفسك.")
    print("أوامر: (l)عرض المهام, (a)إضافة مهمة, (s)بدء مهمة, (t)إحصائيات, (q)خروج")
    print("\\nملحوظة: شغّل مع --fast لاختبار سريع (الأرقام هنا ثواني).\\n")


def initialize_sample_tasks(task_manager):
    if not task_manager.tasks:
        task_manager.add_task("قراءة كتاب جديد", priority=3, estimated_pomodoros=2)
        task_manager.add_task("إنهاء التقرير المطلوب", priority=5, estimated_pomodoros=1)
        task_manager.add_task("ممارسة الرياضة", priority=4, estimated_pomodoros=1)


def print_tasks(task_manager):
    tasks = task_manager.get_tasks_by_priority()
    if not tasks:
        print("\\nلا توجد مهام حالياً. أضف واحدة.")
        return
    print("\\nقائمة المهام:")
    print("-"*50)
    for t in tasks:
        print(f"ID: {t['id']} | {t['name']} | أولوية: {t['priority']} | تقديري بومودورو: {t['estimated_pomodoros']} | مكتمل: {t['completed']} | مكتمل بومودورو: {t.get('completed_pomodoros',0)}")
    print("-"*50)


def interactive_loop(task_manager, timer):
    show_welcome()
    initialize_sample_tasks(task_manager)
    while True:
        cmd = input("\\nأدخل أمر (l/a/s/t/q): ").strip().lower()
        if cmd == 'l':
            print_tasks(task_manager)
        elif cmd == 'a':
            name = input("اسم المهمة: ").strip()
            if not name:
                print("اسم غير صالح.")
                continue
            try:
                pr = int(input("أولوية (رقم أكبر = أعلى أولوية) [1]: ") or "1")
            except:
                pr = 1
            try:
                est = int(input("عدد جلسات بومودورو متوقعة [1]: ") or "1")
            except:
                est = 1
            task_manager.add_task(name, priority=pr, estimated_pomodoros=est)
            print("تمت الإضافة.")
        elif cmd == 's':
            print_tasks(task_manager)
            try:
                tid = int(input("أدخل ID المهمة التي تريد البدء عليها: ").strip())
            except:
                print("ID غير صالح.")
                continue
            if not any(t['id']==tid for t in task_manager.tasks):
                print("لا توجد مهمة بهذا الID.")
                continue
            timer.start_work(tid)
        elif cmd == 't':
            stats = task_manager.get_daily_stats()
            print("\\nالإحصائيات اليوم:")
            for k,v in stats.items():
                print(f"{k}: {v}")
        elif cmd == 'q':
            print("وداعاً! حفظ البيانات...")
            task_manager.save_tasks()
            break
        else:
            print("أمر غير معروف. استخدم l/a/s/t/q.")


def main():
    parser = argparse.ArgumentParser(description='مدير مهام بومودورو تفاعلي')
    parser.add_argument('--fast', action='store_true', help='وضع تجريبي سريع (يستخدم ثوانٍ بدلاً من دقائق)')
    parser.add_argument('--work', type=int, default=25, help='مدة العمل (دقائق) أو ثوانٍ لوضع --fast')
    parser.add_argument('--break', dest='brk', type=int, default=5, help='مدة الاستراحة (دقائق) أو ثوانٍ لوضع --fast')
    parser.add_argument('--long', dest='long_break', type=int, default=15, help='مدة الاستراحة الطويلة (دقائق) أو ثوانٍ لوضع --fast')
    args = parser.parse_args()
    
    tm = TaskManager()
    timer = PomodoroTimer(tm, work_minutes=args.work, break_minutes=args.brk, long_break_minutes=args.long_break, fast=args.fast)
    try:
        interactive_loop(tm, timer)
    except KeyboardInterrupt:
        print("\\nاكتشاف مقاطعة. حفظ الخروج...")
        tm.save_tasks()


if __name__ == '__main__':
    main()
