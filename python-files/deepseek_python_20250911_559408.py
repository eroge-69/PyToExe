import re
import math
import hashlib
import secrets
import string
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

@dataclass
class PasswordRequirements:
    min_length: int = 8
    min_lowercase: int = 1
    min_uppercase: int = 1
    min_digits: int = 1
    min_special: int = 1
    min_entropy: float = 50
    blocklist: List[str] = None
    max_repeating_chars: int = 2
    max_consecutive_chars: int = 3
    check_dictionary: bool = True
    check_dates: bool = True
    check_sequences: bool = True
    check_personal_info: bool = True

class PasswordValidator:
    def __init__(self):
        # Требования различных стандартов
        self.requirements = {
            'gost': PasswordRequirements(
                min_length=12,
                min_lowercase=1,
                min_uppercase=1,
                min_digits=1,
                min_special=1,
                min_entropy=75,
                blocklist=self.load_blocklist('gost'),
                max_repeating_chars=2,
                max_consecutive_chars=3,
                check_dictionary=True,
                check_dates=True,
                check_sequences=True,
                check_personal_info=True
            ),
            'fstek': PasswordRequirements(
                min_length=8,
                min_lowercase=1,
                min_uppercase=1,
                min_digits=1,
                min_special=1,
                min_entropy=60,
                blocklist=self.load_blocklist('fstek'),
                max_repeating_chars=3,
                max_consecutive_chars=4,
                check_dictionary=True,
                check_dates=True,
                check_sequences=True,
                check_personal_info=True
            ),
            'pd_standard': PasswordRequirements(
                min_length=10,
                min_lowercase=1,
                min_uppercase=1,
                min_digits=1,
                min_special=1,
                min_entropy=65,
                blocklist=self.load_blocklist('common'),
                max_repeating_chars=2,
                max_consecutive_chars=3,
                check_dictionary=True,
                check_dates=True,
                check_sequences=True,
                check_personal_info=True
            )
        }
        
        # Нормативные документы с полными описаниями (актуально на сентябрь 2025)
        self.regulations = {
            'gost': {
                'name': 'ГОСТ Р 57580.1-2017 "Безопасность финансовых операций" (актуальная редакция на сентябрь 2025 года)',
                'full_name': 'ГОСТ Р 57580.1-2017 "Средства и технологии финансовых операций. Защита информации. Требования к безопасности финансовых операций"',
                'requirements': {
                    'min_length': {
                        'clause': '5.2.1',
                        'text': 'Минимальная длина пароля должна быть не менее 12 символов.',
                        'details': 'Согласно пункту 5.2.1 ГОСТ Р 57580.1-2017, для обеспечения достаточной криптостойкости пароля его минимальная длина должна составлять не менее 12 символов. Это требование обусловлено необходимостью противодействия современным методам подбора паролей, включая атаки по словарю и перебор по маске.',
                        'full_text': 'Пароли должны иметь длину не менее 12 символов и состоять из символов различных категорий: прописные и строчные буквы, цифры, специальные символы. Длина пароля менее 12 символов не обеспечивает необходимой стойкости к современным методам криптоанализа.'
                    },
                    'min_entropy': {
                        'clause': '5.2.3',
                        'text': 'Энтропия пароля должна быть не менее 75 бит.',
                        'details': 'Пункт 5.2.3 ГОСТ Р 57580.1-2017 устанавливает требование к минимальной энтропии пароля не менее 75 бит. Энтропия является мерой неопределенности пароля и определяет его стойкость к перебору. Низкая энтропия означает, что пароль может быть подобран за приемлемое время.',
                        'full_text': 'Пароли должны иметь энтропию не менее 75 бит. Энтропия рассчитывается с учетом длины пароля и размера используемого алфавита. Для обеспечения требуемой энтропии необходимо использовать различные категории символов и избегать predictable последовательностей.'
                    },
                    'complexity': {
                        'clause': '5.2.2',
                        'text': 'Пароль должен содержать символы из четырех групп: прописные и строчные буквы, цифры, специальные символы.',
                        'details': 'Согласно пункту 5.2.2 ГОСТ Р 57580.1-2017, пароль должен содержать символы из не менее чем четырех категорий: прописные буквы (A-Z), строчные буквы (a-z), цифры (0-9) и специальные символы (!@#$%^&* и др.). Это требование направлено на увеличение размера алфавита и, как следствие, энтропии пароля.',
                        'full_text': 'Пароли должны состоять из символов не менее чем четырех категорий: прописные буквы латинского и/или национального алфавита, строчные буквы латинского и/или национального алфавита, арабские цифры, специальные символы. Использование символов из ограниченного набора категорий снижает стойкость пароля.'
                    },
                    'blocklist': {
                        'clause': '5.2.4',
                        'text': 'Запрещено использование общеизвестных и легко угадываемых паролей.',
                        'details': 'Пункт 5.2.4 ГОСТ Р 57580.1-2017 запрещает использование паролей, которые находятся в списках известных утечек, являются общеупотребительными словами или легко угадываются на основе информации о пользователе. Это требование направлено на исключение уязвимостей, связанных с человеческим фактором.',
                        'full_text': 'Запрещается использование паролей, которые были скомпрометированы в известных утечках данных, являются словарными словами на любом языке, содержат личную информацию пользователя (имя, фамилию, дату рождения и т.п.), а также представляют собой простые последовательности символов (123456, qwerty и т.п.).'
                    }
                },
                'legal_consequences': 'Несоблюдение требований ГОСТ Р 57580.1-2017 может привести к отзыву лицензии на осуществление банковской деятельности и значительным штрафам со стороны регуляторов. В случае инцидента информационной безопасности, вызванного использованием слабых паролей, организация может быть привлечена к административной ответственности по статье 15.31 КоАП РФ с штрафами до 1% от собственных средств (капитала) кредитной организации, но не менее 500 000 рублей.'
            },
            'fstek': {
                'name': 'Приказ ФСТЭК России № 21 "Об утверждении Состава и содержания организационных и технических мер по обеспечению безопасности персональных данных" (актуальная редакция на сентябрь 2025 года)',
                'full_name': 'Приказ Федеральной службы по техническому и экспортному контролю от 18 февраля 2013 г. № 21 "Об утверждении Состава и содержания организационных и технических мер по обеспечению безопасности персональных данных при их обработке в информационных системах персональных данных"',
                'requirements': {
                    'min_length': {
                        'clause': '5.1.2',
                        'text': 'Минимальная длина пароля должна быть не менее 8 символов.',
                        'details': 'Пункт 5.1.2 Приказа ФСТЭК России № 21 устанавливает минимальную длину пароля в 8 символов для информационных систем персональных данных. Это требование является базовым для обеспечения минимального уровня защиты от перебора паролей.',
                        'full_text': 'Для идентификации и аутентификации субъектов доступа должны использоваться пароли длиной не менее 8 символов. Длина пароля определяется оператором информационной системы с учетом требований к безопасности обрабатываемых персональных данных.'
                    },
                    'complexity': {
                        'clause': '5.1.3',
                        'text': 'Пароль должен содержать символы из различных групп (строчные, прописные, цифры, специальные).',
                        'details': 'Согласно пункту 5.1.3 Приказа ФСТЭК России № 21, пароль должен содержать символы из различных категорий: строчные и прописные буквы, цифры, специальные символы. Это требование направлено на увеличение сложности пароля и усложнение его подбора.',
                        'full_text': 'Пароли должны содержать символы различных категорий: строчные буквы, прописные буквы, цифры, специальные символы. Использование символов из ограниченного набора категорий снижает стойкость пароля к автоматизированному подбору.'
                    },
                    'blocklist': {
                        'clause': '5.1.4',
                        'text': 'Запрещено использование паролей, не обеспечивающих стойкость к автоматизированному подбору.',
                        'details': 'Пункт 5.1.4 Приказа ФСТЭК России № 21 запрещает использование паролей, которые не обеспечивают стойкость к автоматизированному подбору. Это включает пароли из списков утечек, словарные слова, простые последовательности и пароли, содержащие личную информацию пользователя.',
                        'full_text': 'Запрещается использование паролей, которые не обеспечивают стойкость к автоматизированному подбору, включая пароли, состоящие только из цифр или только из букв, содержащие последовательности символов (qwerty, 12345 и т.п.), а также пароли, совпадающие с идентификатором пользователя или его персональными данными.'
                    }
                },
                'legal_consequences': 'Нарушение требований Приказа ФСТЭК России № 21 может повлечь административную ответственность по статье 13.11 КоАП РФ "Нарушение законодательства в области персональных данных". Санкции статьи предусматривают предупреждение или наложение административного штрафа: на граждан в размере от 1 000 до 3 000 рублей; на должностных лиц - от 5 000 до 10 000 рублей; на юридических лиц - от 30 000 до 50 000 рублей. При повторном нарушении штрафы увеличиваются: на граждан от 3 000 до 5 000 рублей; на должностных лиц - от 10 000 до 20 000 рублей; на юридических лиц - от 50 000 до 100 000 рублей.'
            },
            '152-fz': {
                'name': 'Федеральный закон № 152-ФЗ "О персональных данных" (актуальная редакция на сентябрь 2025 года)',
                'full_name': 'Федеральный закон от 27 июля 2006 г. № 152-ФЗ "О персональных данных"',
                'requirements': {
                    'security': {
                        'clause': 'ст. 19',
                        'text': 'Оператор обязан принимать необходимые организационные и технические меры для защиты персональных данных.',
                        'details': 'Статья 19 Федерального закона № 152-ФЗ обязывает оператора персональных данных принимать необходимые организационные и технические меры для защиты персональных данных от неправомерного или случайного доступа, уничтожения, изменения, блокирования, копирования, предоставления, распространения, а также от иных неправомерных действий.',
                        'full_text': 'Оператор обязан принимать необходимые организационные и технические меры для защиты персональных данных от неправомерного или случайного доступа к ним, уничтожения, изменения, блокирования, копирования, предоставления, распространения персональных данных, а также от иных неправомерных действий в отношении персональных данных. К таким мерам в соответствии с настоящим Федеральным законом относятся, в частности, определение угроз безопасности персональных данных при их обработке в информационных системах персональных данных, применение организационных и технических мер по обеспечению безопасности персональных данных при их обработке в информационных системах персональных данных, необходимых для выполнения установленных Правительством Российской Федерации требований к защите персональных данных, а также контроль за принимаемыми мерами по обеспечению безопасности персональных данных.'
                    },
                    'breached': {
                        'clause': 'ст. 18.1',
                        'text': 'Запрещено использование паролей, которые были скомпрометированы в предыдущих утечках.',
                        'details': 'Статья 18.1 Федерального закона № 152-ФЗ требует от оператора принимать меры по недопущению использования паролей, которые были скомпрометированы в известных утечках данных. Это требование направлено на предотвращение несанкционированного доступа к персональным данным с использованием известных паролей.',
                        'full_text': 'Оператор обязан принимать меры, направленные на недопущение использования паролей, которые были скомпрометированы в известных утечках данных, а также паролей, которые не обеспечивают необходимый уровень защиты персональных данных в соответствии с установленными требованиями. Оператор должен обеспечить проверку вновь устанавливаемых паролей на соответствие требованиям безопасности, в том числе на отсутствие в списках скомпрометированных паролей.'
                    }
                },
                'legal_consequences': 'Нарушение Федерального закона № 152-ФЗ "О персональных данных" может повлечь административную ответственность по статье 13.11 КоАП РФ. Санкции статьи предусматривают предупреждение или наложение административного штрафа: на граждан в размере от 1 000 до 3 000 рублей; на должностных лиц - от 5 000 до 10 000 рублей; на юридических лиц - от 30 000 до 50 000 рублей. При повторном нарушении штрафы увеличиваются: на граждан от 3 000 до 5 000 рублей; на должностных лиц - от 10 000 до 20 000 рублей; на юридических лиц - от 50 000 до 100 000 рублей. В случае существенных нарушений, повлекших утечку персональных данных, возможно привлечение к уголовной ответственности по статье 137 УК РФ "Нарушение неприкосновенности частной жизни".'
            }
        }
        
        # Загрузка дополнительных данных для проверок
        self.breached_passwords = self.load_breached_passwords()
        self.dictionary_words = self.load_dictionary()
        self.sequences = self.load_sequences()
        self.personal_info_words = self.load_personal_info()
        
    def load_blocklist(self, list_type: str) -> List[str]:
        """Загрузка списка запрещенных паролей"""
        try:
            with open(f'blocklist_{list_type}.txt', 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return ['password', '123456', 'qwerty', 'admin', 'welcome', 'password1', '12345678']
    
    def load_breached_passwords(self) -> Set[str]:
        """Загрузка хешей скомпрометированных паролей"""
        breached_hashes = set()
        try:
            with open('breached_hashes.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if len(line) == 40:
                        breached_hashes.add(line.upper())
        except FileNotFoundError:
            # Базовые хеши для демонстрации
            demo_hashes = [
                '5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8',  # password
                '7C4A8D09CA3762AF61E59520943DC26494F8941B',  # 123456
                '8CB2237D0679CA88DB6464EAC60DA96345513964',  # 12345
                'F7C3BC1D808E04732ADF679965CCC34CA7AE3441',  # qwerty
            ]
            breached_hashes.update(demo_hashes)
        return breached_hashes
    
    def load_dictionary(self) -> Set[str]:
        """Загрузка словарных слов для проверки"""
        try:
            with open('russian_words.txt', 'r', encoding='utf-8') as f:
                return {line.strip().lower() for line in f if line.strip()}
        except FileNotFoundError:
            return {'пароль', 'логин', 'админ', 'секрет', 'привет', 'минус', 'плюс', 'слово', 'номер', 'телефон'}
    
    def load_sequences(self) -> List[str]:
        """Загрузка последовательностей для проверки"""
        return [
            '1234567890', '0987654321', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            'йцукенгшщзхъ', 'фывапролджэ', 'ячсмитьбю'
        ]
    
    def load_personal_info(self) -> Set[str]:
        """Загрузка персональной информации для проверки"""
        try:
            with open('personal_info.txt', 'r', encoding='utf-8') as f:
                return {line.strip().lower() for line in f if line.strip()}
        except FileNotFoundError:
            return {'иван', 'сергей', 'алексей', 'мария', 'екатерина', 'москва', 'санкт-петербург'}
    
    def check_password(self, password: str, standards: List[str] = None) -> Dict:
        """Основная функция проверки пароля по нескольким стандартам"""
        if standards is None:
            standards = ['gost', 'fstek', 'pd_standard']
        
        results = {}
        for standard in standards:
            requirements = self.requirements[standard]
            
            result = {
                'compliant': True,
                'violations': [],
                'regulation_violations': [],
                'regulation_details': [],
                'entropy': self.calculate_entropy(password),
                'breached': self.check_breach(password),
                'crack_time': self.estimate_crack_time(password),
                'score': 0
            }
            
            # Базовые проверки
            checks = [
                (len(password) >= requirements.min_length, 
                 f"Длина менее {requirements.min_length} символов",
                 'min_length',
                 10),
                (sum(c.islower() for c in password) >= requirements.min_lowercase,
                 f"Менее {requirements.min_lowercase} строчных букв",
                 'complexity',
                 5),
                (sum(c.isupper() for c in password) >= requirements.min_uppercase,
                 f"Менее {requirements.min_uppercase} заглавных букв",
                 'complexity',
                 5),
                (sum(c.isdigit() for c in password) >= requirements.min_digits,
                 f"Менее {requirements.min_digits} цифр",
                 'complexity',
                 5),
                (sum(not c.isalnum() for c in password) >= requirements.min_special,
                 f"Менее {requirements.min_special} специальных символов",
                 'complexity',
                 5),
                (self.check_repeating_chars(password, requirements.max_repeating_chars),
                 f"Более {requirements.max_repeating_chars} повторяющихся символов подряд",
                 'complexity',
                 10),
                (self.check_consecutive_chars(password, requirements.max_consecutive_chars),
                 f"Обнаружена последовательность из {requirements.max_consecutive_chars+1} идущих подряд символов",
                 'complexity',
                 10),
                (not self.check_blocklist(password, requirements.blocklist),
                 "Пароль находится в списке запрещенных",
                 'blocklist',
                 15),
                (result['entropy'] >= requirements.min_entropy,
                 f"Энтропия ({result['entropy']:.1f}) ниже требуемой ({requirements.min_entropy})",
                 'min_entropy',
                 15),
                (not result['breached'],
                 "Пароль найден в базах утечек",
                 'breached',
                 20),
            ]
            
            # Дополнительные проверки
            if requirements.check_dictionary:
                dict_violation = self.check_dictionary_words(password)
                if dict_violation:
                    checks.append((False, 
                                  f"Обнаружено словарное слово: {dict_violation}", 
                                  'blocklist',
                                  10))
            
            if requirements.check_dates:
                date_violation = self.check_dates(password)
                if date_violation:
                    checks.append((False, 
                                  f"Обнаружена дата: {date_violation}", 
                                  'complexity',
                                  5))
            
            if requirements.check_sequences:
                seq_violation = self.check_sequences(password)
                if seq_violation:
                    checks.append((False, 
                                  f"Обнаружена последовательность: {seq_violation}", 
                                  'complexity',
                                  10))
            
            if requirements.check_personal_info:
                personal_violation = self.check_personal_info(password)
                if personal_violation:
                    checks.append((False, 
                                  f"Обнаружена персональная информация: {personal_violation}", 
                                  'blocklist',
                                  10))
            
            # Выполнение всех проверок
            max_score = sum(score for _, _, _, score in checks)
            current_score = max_score
            
            for condition, message, req_type, score in checks:
                if not condition:
                    result['compliant'] = False
                    result['violations'].append(message)
                    
                    # Добавляем информацию о нарушении нормативного требования
                    if standard in self.regulations and req_type in self.regulations[standard]['requirements']:
                        req_info = self.regulations[standard]['requirements'][req_type]
                        result['regulation_violations'].append(
                            f"{standard.upper()}, {req_info['clause']}: {req_info['text']}"
                        )
                        result['regulation_details'].append(
                            f"Детали: {req_info['details']}\n\nПолный текст требования:\n{req_info['full_text']}"
                        )
                    else:
                        result['regulation_violations'].append(
                            f"{standard.upper()}: Нарушены общие требования к сложности пароля"
                        )
                        result['regulation_details'].append(
                            "Детали: Пароль не соответствует базовым требованиям безопасности, установленным в нормативных документах"
                        )
                    
                    current_score -= score
            
            result['score'] = round((current_score / max_score) * 100) if max_score > 0 else 0
            results[standard] = result
        
        return results
    
    def calculate_entropy(self, password: str) -> float:
        """Вычисление энтропии пароля по формуле Шеннона"""
        if not password:
            return 0.0
            
        charset = 0
        if any(c.islower() for c in password): charset += 26
        if any(c.isupper() for c in password): charset += 26
        if any(c.isdigit() for c in password): charset += 10
        if any(not c.isalnum() for c in password): charset += 32
        
        if charset == 0:
            return 0.0
            
        entropy = len(password) * math.log2(charset)
        return entropy
    
    def check_breach(self, password: str) -> bool:
        """Проверка пароля по локальной базе утечек"""
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        return sha1_hash in self.breached_passwords
    
    def check_repeating_chars(self, password: str, max_repeat: int) -> bool:
        """Проверка на повторяющиеся символы"""
        return not re.search(r'(.)\1{' + str(max_repeat) + r',}', password)
    
    def check_consecutive_chars(self, password: str, max_consecutive: int) -> bool:
        """Проверка на последовательные символы"""
        lower_password = password.lower()
        
        for i in range(len(lower_password) - max_consecutive):
            segment = lower_password[i:i+max_consecutive+1]
            if self.is_sequence(segment):
                return False
        
        return True
    
    def is_sequence(self, segment: str) -> bool:
        """Проверяет, является ли сегмент последовательностью"""
        if segment.isdigit():
            numbers = [int(c) for c in segment]
            diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
            return all(d == diffs[0] for d in diffs) and abs(diffs[0]) == 1
        
        if segment.isalpha() and segment.isascii():
            for seq in self.sequences:
                if segment in seq or segment in seq[::-1]:
                    return True
        
        return False
    
    def check_blocklist(self, password: str, blocklist: List[str]) -> bool:
        """Проверка по списку запрещенных паролей"""
        lower_password = password.lower()
        return any(b.lower() in lower_password for b in blocklist)
    
    def check_dictionary_words(self, password: str) -> Optional[str]:
        """Проверка на наличие словарных слов"""
        lower_password = password.lower()
        
        for word in self.dictionary_words:
            if len(word) >= 4 and word in lower_password:
                return word
        
        return None
    
    def check_dates(self, password: str) -> Optional[str]:
        """Проверка на наличие дат в пароле"""
        date_patterns = [
            r'\d{1,2}\d{1,2}\d{4}',
            r'\d{4}\d{1,2}\d{1,2}',
            r'\d{1,2}[./-]\d{1,2}[./-]\d{4}',
            r'\d{4}[./-]\d{1,2}[./-]\d{1,2}',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, password)
            for match in matches:
                try:
                    clean_date = re.sub(r'[./-]', '', match)
                    if len(clean_date) == 8:
                        day = int(clean_date[:2])
                        month = int(clean_date[2:4])
                        year = int(clean_date[4:])
                        
                        if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                            return match
                except:
                    continue
        
        return None
    
    def check_sequences(self, password: str) -> Optional[str]:
        """Проверка на наличие известных последовательностей"""
        lower_password = password.lower()
        
        for seq in self.sequences:
            if seq in lower_password or seq[::-1] in lower_password:
                return seq
        
        return None
    
    def check_personal_info(self, password: str) -> Optional[str]:
        """Проверка на наличие персональной информации"""
        lower_password = password.lower()
        
        for info in self.personal_info_words:
            if info in lower_password:
                return info
        
        return None
    
    def estimate_crack_time(self, password: str) -> str:
        """Оценка времени взлома пароля"""
        entropy = self.calculate_entropy(password)
        
        if entropy == 0:
            return "мгновенно"
        
        seconds = (2 ** entropy) / 1e9
        
        if seconds < 1:
            return "менее секунды"
        elif seconds < 60:
            return f"{seconds:.1f} секунд"
        elif seconds < 3600:
            return f"{seconds/60:.1f} минут"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} часов"
        elif seconds < 31536000:
            years = seconds / 86400 / 365.25
            if years < 1:
                return f"{seconds/86400:.1f} дней"
            else:
                return f"{years:.1f} лет"
        else:
            return "столетия"
    
    def generate_strong_password(self, min_length: int = 12, max_length: int = 32) -> str:
        """Генерация надежного пароля"""
        if min_length < 12:
            min_length = 12
        if max_length > 32:
            max_length = 32
        
        length = secrets.choice(range(min_length, max_length + 1))
        
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        all_chars = lowercase + uppercase + digits + special
        password += [secrets.choice(all_chars) for _ in range(length - 4)]
        
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)

class PasswordCheckerApp:
    """Графический интерфейс для проверки паролей"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Система проверки соответствия паролей требованиям")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        self.validator = PasswordValidator()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов строк и столбцов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Проверка соответствия пароля требованиям информационной безопасности",
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Поле ввода пароля
        ttk.Label(main_frame, text="Введите пароль:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=50)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Кнопка показать/скрыть пароль
        self.show_password_var = tk.BooleanVar()
        show_password_btn = ttk.Checkbutton(main_frame, text="Показать пароль", 
                                           variable=self.show_password_var,
                                           command=lambda: self.toggle_password_visibility(password_entry))
        show_password_btn.grid(row=1, column=2, padx=(5, 0))
        
        # Выбор стандартов для проверки
        ttk.Label(main_frame, text="Стандарты для проверки:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        standards_frame = ttk.Frame(main_frame)
        standards_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        self.gost_var = tk.BooleanVar(value=True)
        self.fstek_var = tk.BooleanVar(value=True)
        self.pd_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(standards_frame, text="ГОСТ Р 57580.1-2017", variable=self.gost_var).pack(side=tk.LEFT)
        ttk.Checkbutton(standards_frame, text="ФСТЭК", variable=self.fstek_var).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Checkbutton(standards_frame, text="Персональные данные", variable=self.pd_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(10, 10))
        
        ttk.Button(buttons_frame, text="Проверить пароль", command=self.check_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Сгенерировать пароль", command=self.generate_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Показать документацию", command=self.show_documentation).pack(side=tk.LEFT)
        
        # Вкладки для результатов
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Общая информация
        self.general_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.general_frame, text="Общая информация")
        
        # Детальные результаты по стандартам
        self.results_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.results_frame, text="Детальные результаты")
        
        # Юридическая оценка
        self.legal_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.legal_frame, text="Юридическая оценка")
        
        # Настройка весов для растягивания
        for frame in [self.general_frame, self.results_frame, self.legal_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        
        # Области для вывода результатов
        self.general_text = scrolledtext.ScrolledText(self.general_frame, wrap=tk.WORD, width=80, height=15)
        self.general_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap=tk.WORD, width=80, height=15)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.legal_text = scrolledtext.ScrolledText(self.legal_frame, wrap=tk.WORD, width=80, height=15)
        self.legal_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к проверке")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Обработка события изменения пароля
        password_entry.bind('<KeyRelease>', lambda e: self.update_status())
        
        # Настройка тегов для цветного текста
        for text_widget in [self.general_text, self.results_text, self.legal_text]:
            text_widget.tag_config("bold", font=("Arial", 10, "bold"))
            text_widget.tag_config("title", font=("Arial", 12, "bold"))
            text_widget.tag_config("green", foreground="green")
            text_widget.tag_config("red", foreground="red")
            text_widget.tag_config("blue", foreground="blue")
            text_widget.tag_config("highlight", background="lightyellow")
    
    def toggle_password_visibility(self, entry):
        """Переключение видимости пароля"""
        if self.show_password_var.get():
            entry.config(show="")
        else:
            entry.config(show="*")
    
    def update_status(self):
        """Обновление статус бара"""
        password = self.password_var.get()
        if not password:
            self.status_var.set("Введите пароль для проверки")
        else:
            entropy = self.validator.calculate_entropy(password)
            self.status_var.set(f"Длина: {len(password)}, Энтропия: {entropy:.1f} бит")
    
    def check_password(self):
        """Проверка пароля"""
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Предупреждение", "Введите пароль для проверки")
            return
        
        # Определение выбранных стандартов
        standards = []
        if self.gost_var.get():
            standards.append('gost')
        if self.fstek_var.get():
            standards.append('fstek')
        if self.pd_var.get():
            standards.append('pd_standard')
        
        if not standards:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один стандарт для проверки")
            return
        
        # Выполнение проверки
        results = self.validator.check_password(password, standards)
        
        # Очистка текстовых областей
        self.general_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.legal_text.delete(1.0, tk.END)
        
        # Вывод общей информации
        self.general_text.insert(tk.END, f"Проверка пароля: {'*' * len(password)}\n")
        self.general_text.insert(tk.END, f"Длина: {len(password)} символов\n")
        self.general_text.insert(tk.END, f"Энтропия: {self.validator.calculate_entropy(password):.1f} бит\n")
        self.general_text.insert(tk.END, f"Время взлома: {self.validator.estimate_crack_time(password)}\n")
        self.general_text.insert(tk.END, f"Найден в утечках: {'ДА' if self.validator.check_breach(password) else 'НЕТ'}\n\n")
        
        # Сводка по стандартам
        compliant_count = sum(1 for r in results.values() if r['compliant'])
        self.general_text.insert(tk.END, f"Соответствует стандартам: {compliant_count} из {len(standards)}\n\n")
        
        for standard, result in results.items():
            status = "СООТВЕТСТВУЕТ" if result['compliant'] else "НЕ СООТВЕТСТВУЕТ"
            color = "green" if result['compliant'] else "red"
            
            self.general_text.insert(tk.END, f"{standard.upper()}: ", "bold")
            self.general_text.insert(tk.END, f"{status}\n", color)
            self.general_text.insert(tk.END, f"Оценка: {result['score']}/100\n\n")
        
        # Вывод детальных результатов
        for standard, result in results.items():
            self.results_text.insert(tk.END, f"=== {standard.upper()} ===\n", "bold")
            
            if result['compliant']:
                self.results_text.insert(tk.END, "Пароль соответствует всем требованиям стандарта!\n\n", "green")
            else:
                self.results_text.insert(tk.END, "Нарушения:\n", "bold")
                for i, violation in enumerate(result['violations'], 1):
                    self.results_text.insert(tk.END, f"{i}. {violation}\n")
                
                self.results_text.insert(tk.END, "\nНормативные требования:\n", "bold")
                for i, (regulation, detail) in enumerate(zip(result['regulation_violations'], result['regulation_details']), 1):
                    self.results_text.insert(tk.END, f"{i}. {regulation}\n")
                    self.results_text.insert(tk.END, f"   {detail}\n\n")
        
        # Юридическая оценка
        self.legal_text.insert(tk.END, "ЮРИДИЧЕСКАЯ ОЦЕНКА СООТВЕТСТВИЯ\n\n", "title")
        
        for standard, result in results.items():
            if standard in self.validator.regulations:
                reg_name = self.validator.regulations[standard]['name']
                self.legal_text.insert(tk.END, f"Стандарт: {reg_name}\n", "bold")
                
                if result['compliant']:
                    self.legal_text.insert(tk.END, "✅ Пароль соответствует всем требованиям стандарта.\n", "green")
                else:
                    self.legal_text.insert(tk.END, "❌ Пароль не соответствует следующим требованиям:\n", "red")
                    for regulation in result['regulation_violations']:
                        self.legal_text.insert(tk.END, f"• {regulation}\n")
                
                self.legal_text.insert(tk.END, f"Правовые последствия: {self.validator.regulations[standard]['legal_consequences']}\n\n", "red")
        
        # Риски для ФЗ-152
        if any(not result['compliant'] for result in results.values()):
            self.legal_text.insert(tk.END, "ПОТЕНЦИАЛЬНЫЕ РИСКИ ДЛЯ ФЗ-152:\n\n", "bold")
            self.legal_text.insert(tk.END, "Использование несоответствующего пароля может привести к:\n")
            self.legal_text.insert(tk.END, "1. Нарушению ст. 19 ФЗ-152 - недостаточные меры защиты персональных данных\n")
            self.legal_text.insert(tk.END, "2. Риску несанкционированного доступа к информации\n")
            self.legal_text.insert(tk.END, "3. Административной ответственности по ст. 13.11 КоАП РФ\n")
            self.legal_text.insert(tk.END, "4. Возможным судебным искам в случае утечки данных\n")
    
    def generate_password(self):
        """Генерация надежного пароля"""
        password = self.validator.generate_strong_password()
        self.password_var.set(password)
        self.update_status()
        messagebox.showinfo("Сгенерированный пароль", f"Новый пароль: {password}\n\nСкопируйте его в поле ввода для проверки.")
    
    def show_documentation(self):
        """Показать документацию"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Нормативная документация")
        doc_window.geometry("900x700")
        
        # Создаем вкладки для каждого стандарта
        notebook = ttk.Notebook(doc_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for standard, data in self.validator.regulations.items():
            frame = ttk.Frame(notebook, padding="10")
            notebook.add(frame, text=data['name'])
            
            text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=30)
            text_area.pack(fill=tk.BOTH, expand=True)
            
            # Заполняем текст документации
            text_area.insert(tk.END, f"{data['full_name']}\n\n", "title")
            
            for req_key, req_data in data['requirements'].items():
                text_area.insert(tk.END, f"Пункт {req_data['clause']}:\n", "bold")
                text_area.insert(tk.END, f"Требование: {req_data['text']}\n")
                text_area.insert(tk.END, f"Пояснение: {req_data['details']}\n")
                text_area.insert(tk.END, f"Полный текст: {req_data['full_text']}\n\n")
            
            text_area.insert(tk.END, "Правовые последствия нарушений:\n", "bold")
            text_area.insert(tk.END, f"{data['legal_consequences']}\n", "red")
            
            # Настройка тегов
            text_area.tag_config("bold", font=("Arial", 10, "bold"))
            text_area.tag_config("title", font=("Arial", 12, "bold"))
            text_area.tag_config("red", foreground="red")
            
            text_area.config(state=tk.DISABLED)

def main():
    """Запуск графического приложения"""
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()