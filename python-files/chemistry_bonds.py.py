import pygame
import sys
import random
import math
from pygame.locals import *

# تهيئة pygame
pygame.init()
pygame.font.init()

# إعدادات الشاشة
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("لعبة الروابط الكيميائية - تعلم بمرح!")

# الألوان
BACKGROUND = (10, 20, 50)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 200, 100)
RED = (255, 80, 80)
YELLOW = (255, 220, 0)
PURPLE = (180, 80, 220)
ORANGE = (255, 150, 50)
CYAN = (0, 200, 200)
GRAY = (180, 180, 180)
LIGHT_BLUE = (100, 180, 255)
LIGHT_GREEN = (100, 230, 150)
DARK_BLUE = (0, 50, 100)

# الخطوط
title_font = pygame.font.SysFont("arial", 48, bold=True)
heading_font = pygame.font.SysFont("arial", 36, bold=True)
text_font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 24)
button_font = pygame.font.SysFont("arial", 26)

# حالة البرنامج
current_screen = "main_menu"
current_challenge = 0
score = 0
level = 1
challenge_answered = False
user_answer = ""

# بيانات الروابط الكيميائية
bond_types = [
    {
        "name": "الرابطة الأيونية",
        "color": BLUE,
        "description": "تحدث بين ذرة فلز (تفقد إلكترونات) وذرة لا فلز (تكتسب إلكترونات)",
        "examples": ["كلوريد الصوديوم (NaCl)", "بروميد البوتاسيوم (KBr)", "أكسيد المغنيسيوم (MgO)"],
        "mechanism": "تنتقل الإلكترونات من الذرة الأقل كهروسالبية إلى الذرة الأعلى كهروسالبية، مما يؤدي إلى تكوين أيونات متعاكسة الشحنة تتجاذب كهربائيًا."
    },
    {
        "name": "الرابطة التساهمية غير القطبية",
        "color": GREEN,
        "description": "تحدث بين ذرتين متشابهتين أو لهما فرق صغير في الكهروسالبية (أقل من 0.4)",
        "examples": ["غاز الهيدروجين (H₂)", "غاز الأكسجين (O₂)", "غاز النيتروجين (N₂)", "الميثان (CH₄)"],
        "mechanism": "تتشارك الذرتان زوجًا أو أكثر من الإلكترونات بالتساوي، حيث تكون الإلكترونات المزدوجة في منتصف المسافة بين النواتين."
    },
    {
        "name": "الرابطة التساهمية القطبية",
        "color": YELLOW,
        "description": "تحدث بين ذرتين مختلفتين في الكهروسالبية (فرق الكهروسالبية بين 0.4 و 1.7)",
        "examples": ["الماء (H₂O)", "فلوريد الهيدروجين (HF)", "الأمونيا (NH₃)", "كلوريد الهيدروجين (HCl)"],
        "mechanism": "تتشارك الذرتان زوجًا من الإلكترونات، لكن الإلكترونات تقضي وقتًا أطول بالقرب من الذرة الأعلى كهروسالبية، مما يخلق شحنة سالبة جزئية وأخرى موجبة جزئية."
    },
    {
        "name": "الرابطة الفلزية",
        "color": ORANGE,
        "description": "تحدث بين ذرات الفلزات في الشبكة البلورية",
        "examples": ["الحديد (Fe)", "النحاس (Cu)", "الذهب (Au)", "الألمنيوم (Al)"],
        "mechanism": "تتكون من أيونات فلزية موجبة محاطة ببحر من الإلكترونات الحرة المتحركة، مما يخلق قوى تجاذب قوية بين الأيونات الموجبة والإلكترونات السالبة."
    }
]

# التحديات
challenges = [
    {
        "question": "ما نوع الرابطة بين الصوديوم (فلز) والكلور (لا فلز)؟",
        "options": ["أيونية", "تساهمية غير قطبية", "تساهمية قطبية", "فلزية"],
        "answer": 0
    },
    {
        "question": "أي من المركبات التالية يحتوي على روابط تساهمية قطبية؟",
        "options": ["NaCl", "H₂O", "Fe", "O₂"],
        "answer": 1
    },
    {
        "question": "ما آلية تكوين الرابطة الفلزية؟",
        "options": [
            "تشارك الإلكترونات بالتساوي",
            "انتقال الإلكترونات من ذرة لأخرى",
            "بحر من الإلكترونات الحرة",
            "تساهمية مع قطبية عالية"
        ],
        "answer": 2
    },
    {
        "question": "أي زوج من العناصر سيكون بينهما رابطة تساهمية غير قطبية؟",
        "options": ["H و Cl", "O و O", "Na و Cl", "Mg و O"],
        "answer": 1
    },
    {
        "question": "ما الذي يحدد قطبية الرابطة التساهمية؟",
        "options": [
            "عدد الإلكترونات المتشاركة",
            "فرق الكهروسالبية بين الذرتين",
            "نوع العناصر (فلز أو لا فلز)",
            "درجة الحرارة"
        ],
        "answer": 1
    }
]

# ذرات لعرضها في المحاكاة
atoms = []

class Atom:
    def __init__(self, x, y, element, radius=30):
        self.x = x
        self.y = y
        self.element = element
        self.radius = radius
        self.color = self.get_color()
        self.electrons = self.get_electrons()
        self.electron_positions = []
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.calculate_electron_positions()
        
    def get_color(self):
        colors = {
            "H": (200, 200, 200),  # فضي
            "O": RED,              # أحمر
            "Na": PURPLE,          # بنفسجي
            "Cl": GREEN,           # أخضر
            "C": GRAY,            # رمادي
            "Fe": ORANGE,          # برتقالي
            "N": BLUE,             # أزرق
            "Mg": YELLOW           # أصفر
        }
        return colors.get(self.element, WHITE)
    
    def get_electrons(self):
        electrons = {
            "H": 1,
            "O": 8,
            "Na": 11,
            "Cl": 17,
            "C": 6,
            "Fe": 26,
            "N": 7,
            "Mg": 12
        }
        return electrons.get(self.element, 1)
    
    def calculate_electron_positions(self):
        self.electron_positions = []
        electron_count = min(self.electrons, 20)  # الحد الأقصى للإلكترونات المرئية
        
        for i in range(electron_count):
            angle = 2 * math.pi * i / electron_count
            distance = self.radius + 10
            ex = self.x + distance * math.cos(angle)
            ey = self.y + distance * math.sin(angle)
            self.electron_positions.append((ex, ey))
    
    def draw(self, surface):
        # رسم الذرة
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # رسم رمز العنصر
        symbol = small_font.render(self.element, True, WHITE)
        surface.blit(symbol, (self.x - symbol.get_width()//2, self.y - symbol.get_height()//2))
        
        # رسم الإلكترونات
        for ex, ey in self.electron_positions:
            pygame.draw.circle(surface, LIGHT_BLUE, (int(ex), int(ey)), 6)
            pygame.draw.circle(surface, CYAN, (int(ex), int(ey)), 6, 1)
    
    def update(self):
        # تحديث الموقع
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # ارتداد من حواف الشاشة
        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.velocity[0] *= -1
        if self.y < self.radius or self.y > HEIGHT - 150:
            self.velocity[1] *= -1
        
        # إعادة حساب مواقع الإلكترونات
        self.calculate_electron_positions()

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_surf = button_font.render(text, True, WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        surface.blit(self.text_surf, self.text_rect)
        
    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# إنشاء الأزرار
bond_buttons = []
for i, bond in enumerate(bond_types):
    button = Button(250, 200 + i*100, 500, 80, bond["name"], bond["color"], LIGHT_BLUE)
    bond_buttons.append(button)

# أزرار القائمة الرئيسية
main_menu_buttons = [
    Button(WIDTH//2 - 150, 250, 300, 70, "تعلم عن الروابط", GREEN, LIGHT_GREEN),
    Button(WIDTH//2 - 150, 350, 300, 70, "تمارين وتحديات", BLUE, LIGHT_BLUE),
    Button(WIDTH//2 - 150, 450, 300, 70, "محاكاة تفاعلية", PURPLE, (200, 150, 255))
]

# أزرار التحديات
challenge_buttons = []
for i in range(4):
    button = Button(200, 350 + i*80, 600, 60, "", DARK_BLUE, BLUE)
    challenge_buttons.append(button)

# أزرار التحكم
back_button = Button(50, HEIGHT - 80, 120, 50, "عودة", RED, (255, 150, 150))
next_button = Button(WIDTH - 170, HEIGHT - 80, 120, 50, "التالي", GREEN, LIGHT_GREEN)
reset_button = Button(WIDTH//2 - 60, HEIGHT - 80, 120, 50, "إعادة", ORANGE, (255, 200, 100))

# إنشاء ذرات للمحاكاة
def create_atoms():
    global atoms
    atoms = [
        Atom(200, 200, "Na"),
        Atom(400, 300, "Cl"),
        Atom(600, 200, "H"),
        Atom(800, 300, "O"),
        Atom(300, 500, "Fe"),
        Atom(700, 500, "C")
    ]

create_atoms()

# رسم القائمة الرئيسية
def draw_main_menu():
    # العنوان
    title = title_font.render("لعبة الروابط الكيميائية", True, YELLOW)
    subtitle = heading_font.render("تعلم أنواع الروابط بين الذرات بمرح!", True, CYAN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 150))
    
    # رسم الأزرار
    for button in main_menu_buttons:
        button.draw(screen)
    
    # رسم ذرات متحركة في الخلفية
    for atom in atoms:
        atom.draw(screen)
    
    # معلومات أسفل الشاشة
    footer = small_font.render("صمم لمساعدة الطلاب على فهم آلية تكوين الروابط الكيميائية", True, GRAY)
    screen.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 40))

# رسم شاشة اختيار نوع الرابطة
def draw_bond_selection():
    title = title_font.render("اختر نوع الرابطة لتعلم المزيد عنها", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    
    for button in bond_buttons:
        button.draw(screen)
    
    back_button.draw(screen)

# رسم شاشة التفاصيل
def draw_bond_details(index):
    bond = bond_types[index]
    
    # العنوان
    title = title_font.render(bond["name"], True, bond["color"])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    # الوصف
    desc = text_font.render(bond["description"], True, WHITE)
    screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 120))
    
    # آلية التكوين
    mech_title = heading_font.render("آلية التكوين:", True, YELLOW)
    screen.blit(mech_title, (100, 180))
    
    mechanism = text_font.render(bond["mechanism"], True, CYAN)
    screen.blit(mechanism, (100, 230))
    
    # الأمثلة
    examples_title = heading_font.render("أمثلة:", True, YELLOW)
    screen.blit(examples_title, (100, 300))
    
    for i, example in enumerate(bond["examples"]):
        ex_text = text_font.render(f"• {example}", True, GREEN)
        screen.blit(ex_text, (150, 350 + i*50))
    
    # رسم توضيحي
    pygame.draw.rect(screen, DARK_BLUE, (600, 180, 350, 350), border_radius=15)
    pygame.draw.rect(screen, bond["color"], (600, 180, 350, 350), 3, border_radius=15)
    
    # رسم ذرات
    if index == 0:  # أيونية
        pygame.draw.circle(screen, PURPLE, (700, 300), 40)
        pygame.draw.circle(screen, GREEN, (850, 300), 40)
        pygame.draw.line(screen, WHITE, (740, 300), (810, 300), 3)
        plus = heading_font.render("+", True, WHITE)
        minus = heading_font.render("-", True, WHITE)
        screen.blit(plus, (700 - plus.get_width()//2, 300 - plus.get_height()//2))
        screen.blit(minus, (850 - minus.get_width()//2, 300 - minus.get_height()//2))
        
    elif index == 1:  # تساهمية غير قطبية
        pygame.draw.circle(screen, GRAY, (700, 300), 40)
        pygame.draw.circle(screen, GRAY, (850, 300), 40)
        pygame.draw.line(screen, WHITE, (740, 300), (810, 300), 3)
        pygame.draw.circle(screen, CYAN, (775, 300), 10)
        
    elif index == 2:  # تساهمية قطبية
        pygame.draw.circle(screen, (200, 200, 200), (700, 300), 40)  # رمادي فاتح
        pygame.draw.circle(screen, RED, (850, 300), 40)
        pygame.draw.line(screen, WHITE, (740, 300), (810, 300), 3)
        pygame.draw.circle(screen, CYAN, (790, 290), 10)
        
    else:  # فلزية
        pygame.draw.circle(screen, ORANGE, (775, 300), 60)
        for i in range(8):
            angle = 2 * math.pi * i / 8
            x = 775 + 80 * math.cos(angle)
            y = 300 + 80 * math.sin(angle)
            pygame.draw.circle(screen, ORANGE, (int(x), int(y)), 20)
            pygame.draw.line(screen, YELLOW, (775, 300), (x, y), 2)
    
    # العودة
    back_button.draw(screen)

# رسم شاشة التحديات
def draw_challenges():
    global challenge_answered
    
    title = title_font.render(f"التحديات - المستوى {level}", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    score_text = heading_font.render(f"النقاط: {score}", True, GREEN)
    screen.blit(score_text, (WIDTH - 200, 50))
    
    if current_challenge < len(challenges):
        challenge = challenges[current_challenge]
        
        # السؤال
        question = text_font.render(challenge["question"], True, WHITE)
        screen.blit(question, (WIDTH//2 - question.get_width()//2, 150))
        
        # الخيارات
        for i, button in enumerate(challenge_buttons):
            button.text = challenge["options"][i]
            button.text_surf = text_font.render(button.text, True, WHITE)
            button.text_rect = button.text_surf.get_rect(center=button.rect.center)
            button.draw(screen)
            
            # إذا تم الإجابة
            if challenge_answered:
                if i == challenge["answer"]:
                    pygame.draw.rect(screen, GREEN, button.rect, 3, border_radius=10)
                else:
                    pygame.draw.rect(screen, RED, button.rect, 3, border_radius=10)
    
    else:
        # نهاية التحديات
        congrats = title_font.render("تهانينا! أكملت جميع التحديات", True, GREEN)
        screen.blit(congrats, (WIDTH//2 - congrats.get_width()//2, 250))
        
        final_score = heading_font.render(f"نقاطك النهائية: {score}", True, YELLOW)
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 350))
        
        restart = text_font.render("اضغط على 'إعادة' للبدء من جديد", True, CYAN)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 450))
    
    # أزرار التحكم
    back_button.draw(screen)
    reset_button.draw(screen)
    if current_challenge < len(challenges):
        next_button.draw(screen)

# رسم المحاكاة التفاعلية
def draw_simulation():
    title = title_font.render("المحاكاة التفاعلية للذرات", True, CYAN)
    subtitle = heading_font.render("شاهد كيف تتفاعل الذرات المختلفة لتكون الروابط", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 100))
    
    # رسم الذرات
    for atom in atoms:
        atom.draw(screen)
    
    # معلومات
    info = [
        "• الذرات الزرقاء: فلزات (مثل Na, Fe, Mg)",
        "• الذرات الخضراء: لا فلزات (مثل Cl, O)",
        "• الذرات الرمادية: أشباه فلزات (مثل C, Si)",
        "• حرك الذرات بالقرب من بعضها لتشاهد كيفية تكوين الروابط"
    ]
    
    for i, line in enumerate(info):
        text = small_font.render(line, True, WHITE)
        screen.blit(text, (50, HEIGHT - 180 + i*30))
    
    # أزرار التحكم
    back_button.draw(screen)
    reset_button.draw(screen)

# دورة اللعبة الرئيسية
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # معالجة الأحداث
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        # التحقق من النقر على الأزرار
        if current_screen == "main_menu":
            for i, button in enumerate(main_menu_buttons):
                if button.is_clicked(mouse_pos, event):
                    if i == 0:
                        current_screen = "bond_selection"
                    elif i == 1:
                        current_screen = "challenges"
                    else:
                        current_screen = "simulation"
        
        elif current_screen == "bond_selection":
            for i, button in enumerate(bond_buttons):
                if button.is_clicked(mouse_pos, event):
                    current_screen = "bond_details"
                    selected_bond = i
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"
        
        elif current_screen == "bond_details":
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "bond_selection"
        
        elif current_screen == "challenges":
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"
            
            if reset_button.is_clicked(mouse_pos, event):
                current_challenge = 0
                score = 0
                level = 1
                challenge_answered = False
            
            if next_button.is_clicked(mouse_pos, event) and challenge_answered:
                current_challenge += 1
                challenge_answered = False
                if current_challenge % 3 == 0:
                    level += 1
            
            if not challenge_answered and current_challenge < len(challenges):
                for i, button in enumerate(challenge_buttons):
                    if button.is_clicked(mouse_pos, event):
                        challenge_answered = True
                        if i == challenges[current_challenge]["answer"]:
                            score += level * 10
        
        elif current_screen == "simulation":
            if back_button.is_clicked(mouse_pos, event):
                current_screen = "main_menu"
            
            if reset_button.is_clicked(mouse_pos, event):
                create_atoms()
    
    # تحديث الذرات في المحاكاة
    if current_screen == "simulation" or current_screen == "main_menu":
        for atom in atoms:
            atom.update()
            
            # التحقق من التقارب بين الذرات
            for other in atoms:
                if atom != other:
                    distance = math.sqrt((atom.x - other.x)**2 + (atom.y - other.y)**2)
                    if distance < 100:
                        pygame.draw.line(screen, YELLOW, 
                                       (int(atom.x), int(atom.y)), 
                                       (int(other.x), int(other.y)), 2)
    
    # تعيين الخلفية
    screen.fill(BACKGROUND)
    
    # رسم شبكة في الخلفية
    for x in range(0, WIDTH, 30):
        pygame.draw.line(screen, (30, 40, 70), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 30):
        pygame.draw.line(screen, (30, 40, 70), (0, y), (WIDTH, y), 1)
    
    # رسم الشاشة الحالية
    if current_screen == "main_menu":
        draw_main_menu()
    
    elif current_screen == "bond_selection":
        draw_bond_selection()
    
    elif current_screen == "bond_details":
        draw_bond_details(selected_bond)
    
    elif current_screen == "challenges":
        draw_challenges()
    
    elif current_screen == "simulation":
        draw_simulation()
    
    # تحديث التحويم على الأزرار
    if current_screen == "bond_selection":
        for button in bond_buttons:
            button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
    
    elif current_screen == "bond_details":
        back_button.check_hover(mouse_pos)
    
    elif current_screen == "challenges":
        for button in challenge_buttons:
            button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
        next_button.check_hover(mouse_pos)
        reset_button.check_hover(mouse_pos)
    
    elif current_screen == "simulation":
        back_button.check_hover(mouse_pos)
        reset_button.check_hover(mouse_pos)
    
    elif current_screen == "main_menu":
        for button in main_menu_buttons:
            button.check_hover(mouse_pos)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()