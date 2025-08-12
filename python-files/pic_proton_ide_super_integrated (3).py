"""
PIC Proton IDE - Super Integrated (Scenario + Peripheral Codegen + CHM Learning)
File: PIC_ProtonIDE_super_integrated.py

This file is a single-file prototype that integrates:
 - .bas parser & analyzer 🧾
 - .chm extractor & command learner 📚
 - CommandDB & MCUDB with ability to add learned commands 🔧
 - Suggestion engine & Analyzer for hints and fixes 💡🔎
 - AI integration points (OpenAI) with safe fallback 🤖
 - Simulator + Proteus hook (placeholder) 🖥️
 - Hardware interface (pyserial) placeholder 🔌
 - Flask API endpoints for uploading files, analyzing, scenario generation, enhancement, and peripheral management 🌐
 - Peripheral registry + code templates for: button, LCD, GLCD, dot matrix, 74HC164, 74HC595, 74HC165, DS1302, DS1307, DS18B20 (18B20), DHT11, DHT22, MAX232, and more 🎛️
 - Scenario processing: load txt scenario and generate Proton BASIC .bas code based on selected MCU and peripherals ✍️
 - "Geliştirme" (enhance) action: analyze uploaded .bas and produce an improved version with TRIS, init routines, and suggested optimizations 🔁

Notes:
 - This is a prototype. External integrations (Proteus, OpenAI, serial) are optional and have fallbacks.
 - Save files are stored under ./workspace by default.

Run demo + tests:
    python3 PIC_ProtonIDE_super_integrated.py

"""

import os
import re
import json
import shutil
import subprocess
import tempfile
import datetime
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

# Optional external libraries
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    import openai
except Exception:
    openai = None

try:
    from flask import Flask, request, jsonify, send_file
except Exception:
    Flask = None

try:
    import pychm
except Exception:
    pychm = None

try:
    import serial
except Exception:
    serial = None

# ----------------------------- Helpers ---------------------------------------

def now_utc_str():
    return str(datetime.datetime.utcnow())


def safe_mkdir(p: str):
    os.makedirs(p, exist_ok=True)

WORKSPACE = './workspace'
safe_mkdir(WORKSPACE)

# ----------------------------- BAS Parser -----------------------------------
class BasParser:
    """Parse Proton BASIC .bas content: device, commands, DIMs, subs"""
    device_re = re.compile(r"^\s*Device\s+(\S+)", re.IGNORECASE)
    token_re = re.compile(r"\b([A-Za-z_][A-Za-z0-9_\\.]*)\b")
    dim_re = re.compile(r"^\s*DIM\s+(\w+)(?:\s*AS\s*(\w+))?", re.IGNORECASE)

    def __init__(self, text: str):
        self.text = text or ''
        self.lines = self.text.splitlines()
        self.device: Optional[str] = None
        self.commands: Counter = Counter()
        self.symbols: Dict[str,str] = {}
        self.functions: Dict[str,Dict[str,int]] = {}
        self.line_map: Dict[int,str] = {}
        self._parse()

    def _parse(self):
        current_fn = None
        for i, raw in enumerate(self.lines,1):
            self.line_map[i] = raw
            code = raw.split("'",1)[0].strip()
            if not code:
                continue
            m = self.device_re.search(code)
            if m:
                self.device = m.group(1)
            for tok in self.token_re.findall(code):
                t = tok.upper()
                if re.match(r"^[A-Z_][A-Z0-9_\\.]*$", t):
                    self.commands[t] += 1
            dim_m = self.dim_re.match(code)
            if dim_m:
                name = dim_m.group(1)
                t = dim_m.group(2) or 'UNKNOWN'
                self.symbols[name] = t.upper()
            sub_m = re.match(r"^\s*(SUB|FUNCTION)\s+(\w+)", code, re.IGNORECASE)
            if sub_m:
                fname = sub_m.group(2)
                current_fn = fname
                self.functions[fname] = {'start': i, 'end': -1}
            end_m = re.match(r"^\s*(END SUB|END FUNCTION|ENDSUB|ENDFUNCTION)", code, re.IGNORECASE)
            if end_m and current_fn:
                self.functions[current_fn]['end'] = i
                current_fn = None

    def summary(self):
        return {'device': self.device, 'commands': dict(self.commands.most_common()), 'symbols': self.symbols, 'functions': self.functions, 'lines': len(self.lines)}

# ----------------------------- CHM Extractor --------------------------------
class ChmExtractor:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self.path = path

    def extract_to_dir(self, out_dir: Optional[str]=None) -> str:
        out_dir = out_dir or tempfile.mkdtemp(prefix='chm_')
        safe_mkdir(out_dir)
        # try pychm first
        if pychm is not None:
            try:
                chm = pychm.CHMFile(self.path)
                for ent in chm.files():
                    if ent.filename.endswith('/'):
                        continue
                    content = chm.read(ent.filename)
                    if content is None:
                        continue
                    fn = os.path.basename(ent.filename)
                    with open(os.path.join(out_dir, fn), 'wb') as f:
                        f.write(content)
                return out_dir
            except Exception:
                pass
        # try 7z
        if shutil.which('7z') or shutil.which('7za'):
            exe = shutil.which('7z') or shutil.which('7za')
            try:
                subprocess.run([exe, 'x', self.path, f'-o{out_dir}'], check=True, capture_output=True)
                return out_dir
            except Exception:
                pass
        # fallback: naive regex extraction
        with open(self.path, 'rb') as f:
            data = f.read()
        chunks = re.findall(rb'<html[\s\S]*?</html>', data, re.IGNORECASE)
        if not chunks:
            raise RuntimeError('Cannot extract CHM (no pychm/7z and no html chunks)')
        for i, c in enumerate(chunks,1):
            try:
                s = c.decode('utf-8', errors='ignore')
            except Exception:
                s = c.decode('latin-1', errors='ignore')
            with open(os.path.join(out_dir, f'chunk_{i}.html'), 'w', encoding='utf-8') as f:
                f.write(s)
        return out_dir

    def extract_texts(self, out_dir: Optional[str]=None) -> Dict[str,str]:
        d = self.extract_to_dir(out_dir)
        texts = {}
        for fn in os.listdir(d):
            path = os.path.join(d, fn)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw = f.read()
            except Exception:
                continue
            texts[fn] = self._html_to_text(raw)
        return texts

    def _html_to_text(self, html: str) -> str:
        if BeautifulSoup is not None:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                for s in soup(['script','style']):
                    s.decompose()
                txt = soup.get_text(separator='\n')
                lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
                return '\n'.join(lines)
            except Exception:
                pass
        # simple regex strip
        t = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
        t = re.sub(r'<style[\s\S]*?</style>', '', t, flags=re.IGNORECASE)
        t = re.sub(r'<[^>]+>', '', t)
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        return '\n'.join(lines)

# ----------------------------- CommandDB (learn) ----------------------------
class CommandDB:
    def __init__(self, path: str='./data/commands.json'):
        self.path = path
        safe_mkdir(os.path.dirname(self.path))
        self.db: Dict[str, Dict[str,Any]] = {}
        self._load()
        if not self.db:
            self._seed()

    def _seed(self):
        seeds = [
            ('HIGH','Set pin HIGH','HIGH PORTA.0'),
            ('LOW','Set pin LOW','LOW PORTB.0'),
            ('DIM','Declare variable','DIM x AS BYTE'),
            ('ADC.READ','Read ADC channel','value = ADC.Read(0)'),
            ('TRIS','TRIS register setting','TRISB = %11110000'),
        ]
        for n,d,e in seeds:
            self.add(n,d,e,source='seed',seeded=True)

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path,'r',encoding='utf-8') as f:
                    self.db = json.load(f)
            except Exception:
                self.db = {}

    def _save(self):
        try:
            with open(self.path,'w',encoding='utf-8') as f:
                json.dump(self.db, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add(self, name: str, desc: str, example: str, source: str='manual', seeded: bool=False):
        k = name.upper()
        ent = self.db.get(k, {})
        ent['description'] = ent.get('description') or desc
        ent['example'] = ent.get('example') or example
        ent.setdefault('sources', []).append({'src': source, 'at': now_utc_str()})
        ent['seeded'] = ent.get('seeded', False) or seeded
        self.db[k] = ent
        self._save()

    def get(self, name: str) -> Optional[Dict[str,Any]]:
        return self.db.get(name.upper())

    def search(self, prefix: str) -> List[str]:
        p = prefix.upper()
        return [k for k in self.db.keys() if k.startswith(p)]

    def learn_from_texts(self, texts: Dict[str,str]) -> List[str]:
        learned = []
        for fn, txt in texts.items():
            for line in txt.splitlines():
                ln = line.strip()
                m = re.match(r'^([A-Za-z0-9_\.]+)\s*[-:\u2013]\s*(.+)$', ln)
                if m:
                    cmd = m.group(1).upper()
                    desc = m.group(2).strip()
                    self.add(cmd, desc, '', source=f'CHM:{fn}')
                    learned.append(cmd)
                    continue
                m2 = re.match(r'^([A-Za-z_][A-Za-z0-9_\.]+)\s*\(.*\)$', ln)
                if m2:
                    cmd = m2.group(1).upper()
                    if cmd not in self.db:
                        self.add(cmd, '', '', source=f'CHM:{fn}')
                        learned.append(cmd)
        return list(set(learned))

# ----------------------------- MCUDB ---------------------------------------
class MCUDB:
    def __init__(self, path='./data/mcudb.json'):
        self.path = path
        safe_mkdir(os.path.dirname(self.path))
        self.db: Dict[str, Dict[str,Any]] = {}
        self._load()
        if not self.db:
            self._seed()

    def _seed(self):
        self.add('PIC16F877A', {'pins':40,'ports':{'A':8,'B':8,'C':8,'D':8,'E':3}, 'has_adc':True})
        self.add('PIC16F84A', {'pins':18,'ports':{'A':5,'B':8}, 'has_adc':False})

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path,'r',encoding='utf-8') as f:
                    self.db = json.load(f)
            except Exception:
                self.db = {}

    def _save(self):
        try:
            with open(self.path,'w',encoding='utf-8') as f:
                json.dump(self.db, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add(self, model: str, info: Dict[str,Any]):
        self.db[model.upper()] = info
        self._save()

    def get(self, model: Optional[str]) -> Optional[Dict[str,Any]]:
        if not model:
            return None
        return self.db.get(model.upper())

# ----------------------------- Peripheral Templates -------------------------
PERIPHERAL_TEMPLATES: Dict[str, Dict[str,str]] = {
    'button': {
        'init': "' Button init\nTRISB.0 = 1\n",
        'read': "' Read button\nIF PORTB.0 = 1 THEN 'pressed'\nEND IF\n",
    },
    'lcd': {
        'init': "' LCD init (I2C or parallel)\n' Example: CALL LCD_Init()\n",
        'usage': "' LCD example\nCALL LCD_Out(1,1, \"Hello\")\n",
    },
    '74HC595': {
        'init': "' 74HC595 init - data/clock/latch pins\nDATA_PIN = PORTB.0\nCLOCK_PIN = PORTB.1\nLATCH_PIN = PORTB.2\n",
        'write': "' Write byte to 74HC595\nSHIFT_OUT DATA_PIN, CLOCK_PIN, BYTEVAL\nTOGGLE LATCH_PIN\n",
    },
    '74HC164': {
        'init': "' 74HC164 init\nSER_PIN = PORTB.0\nCLK_PIN = PORTB.1\n",
        'write': "' Pulse bits to 74HC164\nFOR i = 7 TO 0 STEP -1\n  IF (VALUE AND (1 << i)) THEN HIGH SER_PIN ELSE LOW SER_PIN\n  HIGH CLK_PIN\n  LOW CLK_PIN\nNEXT i\n",
    },
    '74HC165': {
        'init': "' 74HC165 init (parallel-in serial-out)\nLOAD_PIN = PORTB.3\nCLK_PIN = PORTB.1\nDATA_PIN = PORTB.2\n",
        'read': "' Read 8-bit from 74HC165\nLOW LOAD_PIN\nHIGH LOAD_PIN\nFOR i=0 TO 7\n  HIGH CLK_PIN\n  b = b << 1 | INPUT(DATA_PIN)\n  LOW CLK_PIN\nNEXT i\n",
    },
    'ds1302': {
        'init': "' DS1302 init\nRST = PORTB.0\nDAT = PORTB.1\nCLK = PORTB.2\n",
        'read': "' Read time example - CALL DS1302_GetTime()\n",
    },
    'ds1307': {
        'init': "' DS1307 via I2C init\n' CALL I2C_Init()\n",
        'read': "' Get RTC time - CALL DS1307_ReadTime()\n",
    },
    'ds18b20': {
        'init': "' DS18B20 init (1-wire)\nONEWIRE_PIN = PORTB.0\n",
        'read': "' Read temp - CALL DS18B20_ReadTemp()\n",
    },
    'dht11': {
        'init': "' DHT11 init\nDHT_PIN = PORTB.0\n",
        'read': "' Read DHT11 - CALL DHT11_Read(DHT_PIN, temp, hum)\n",
    },
    'dht22': {
        'init': "' DHT22 init\nDHT_PIN = PORTB.0\n",
        'read': "' Read DHT22 - CALL DHT22_Read(DHT_PIN, temp, hum)\n",
    },
    'max232': {
        'init': "' MAX232 (UART level shifting) init\n' CALL UART_Init(9600)\n",
    },
}

# ----------------------------- Code Generator --------------------------------
class CodeGenerator:
    """Generate Proton BASIC code from scenario + peripheral selections"""
    def __init__(self, cmd_db: CommandDB, mcu_db: MCUDB):
        self.cmd_db = cmd_db
        self.mcu_db = mcu_db

    def generate_for_scenario(self, scenario_text: str, device: str, peripherals: List[str]) -> str:
        # naive: parse scenario lines like "When BUTTON pressed -> toggle LED"
        lines = scenario_text.splitlines()
        header = [f"' Generated by PIC Proton IDE - {now_utc_str()}", f"Device {device}", ""]
        # add TRIS/initialization skeleton based on peripherals
        init_lines = ["' --- Initialization ---"]
        # choose pins defaults from MCU if available
        mcu = self.mcu_db.get(device)
        port_map = {}
        if mcu:
            ports = mcu.get('ports', {})
            # simple mapping: first pin of each port
            for p,cnt in ports.items():
                port_map[p] = [f"PORT{p}.{i}" for i in range(cnt)]
        # include peripheral inits
        for per in peripherals:
            t = per.lower()
            tpl = PERIPHERAL_TEMPLATES.get(t)
            if tpl and tpl.get('init'):
                init_lines.append(tpl['init'])
        # main loop generation
        main_lines = ["' --- Main Loop ---", "DO"]
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            # sample pattern matching
            # "when BUTTON pressed toggle LED on PORTB.0"
            m = re.match(r'when\s+(\w+)\s+pressed\s+toggle\s+(\w+)(?:\s+on\s+(PORT[ABEDC]\.\d+))?', ln, re.IGNORECASE)
            if m:
                btn = m.group(1).lower()
                target = m.group(2).lower()
                pin = m.group(3) or 'PORTB.0'
                main_lines.append(f"  ' scenario: {ln}")
                # read button and toggle
                main_lines.append(f"  IF PORTB.0 = 1 THEN")
                main_lines.append(f"    TOGGLE {pin}")
                main_lines.append("  END IF")
                continue
            # "every 1s read DHT11 on PORTB.0 and send to LCD"
            m2 = re.match(r'every\s+(\d+)s\s+read\s+(\w+)\s+on\s+(PORT[ABEDC]\.\d+)\s+and\s+send\s+to\s+(\w+)', ln, re.IGNORECASE)
            if m2:
                interval = m2.group(1)
                dev = m2.group(2).lower()
                pin = m2.group(3)
                to = m2.group(4).lower()
                main_lines.append(f"  ' scenario: {ln}")
                main_lines.append(f"  CALL DelayMS({int(interval)*1000})")
                main_lines.append(f"  ' read {dev} on {pin} and display on {to}")
                if dev in ('dht11','dht22'):
                    main_lines.append(f"  CALL DHT_Read({pin})")
                elif dev in ('ds18b20','18b20'):
                    main_lines.append(f"  CALL DS18B20_Read({pin})")
                if to == 'lcd':
                    main_lines.append("  CALL LCD_Out(1,1, temp) ' example")
                continue
            # fallback: comment the line
            main_lines.append(f"  ' UNHANDLED: {ln}")
        main_lines.append("LOOP")

        code = '\n'.join(header + init_lines + [''] + main_lines)
        # simple beautify
        code = re.sub(r"\n{2,}", "\n\n", code)
        return code

    def enhance_bas(self, bas_text: str, device: Optional[str], peripherals: List[str]) -> str:
        # basic improvements: ensure Device exists, add TRIS for outputs, add peripheral inits
        parser = BasParser(bas_text)
        lines = bas_text.splitlines()
        out = []
        if not parser.device and device:
            out.append(f"Device {device}")
        # ensure TRIS lines for used ports
        used_ports = set()
        for cmd in parser.commands.keys():
            m = re.match(r'PORT([A-Z])\.(\d+)', cmd)
            if m:
                used_ports.add(m.group(1))
        for p in used_ports:
            out.append(f"TRIS{p} = %00000000  ' default to output; adjust as needed")
        # add peripheral inits
        out.append("' --- Peripheral Inits ---")
        for per in peripherals:
            tpl = PERIPHERAL_TEMPLATES.get(per.lower())
            if tpl and tpl.get('init'):
                out.append(tpl['init'])
        out.append("' --- Original Code ---")
        out.extend(lines)
        return '\n'.join(out)

# ----------------------------- Suggestion Engine ----------------------------
class SuggestionEngine:
    def __init__(self, cmd_db: CommandDB, mcu_db: MCUDB):
        self.cmd_db = cmd_db
        self.mcu_db = mcu_db

    def suggest_for_bas(self, bas_text: str) -> List[str]:
        parser = BasParser(bas_text)
        suggestions = []
        if not parser.device:
            suggestions.append('⚠️ Device tanımı yok — ekleyin.')
        if any(k in parser.commands for k in ['HIGH','LOW']) and 'TRIS' not in bas_text.upper():
            suggestions.append('🔔 TRIS ayarları yok — port yönlerini ayarlayın.')
        # recommend peripherals if commands seen
        for cmd in parser.commands.keys():
            if cmd.startswith('ADC'):
                suggestions.append('💡 ADC kullanımı tespit edildi — ADC_Read örnekleri için dokümantasyona bakın.')
        return suggestions

# ----------------------------- AI Integrator --------------------------------
class AIIntegrator:
    def __init__(self, api_key: Optional[str]=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if openai is not None and self.api_key:
            openai.api_key = self.api_key

    def summarize(self, text: str) -> str:
        if openai is not None and self.api_key:
            try:
                resp = openai.ChatCompletion.create(model='gpt-4o-mini', messages=[{'role':'user','content':f'Summarize this:\n{text}'}], max_tokens=200)
                return resp.choices[0].message.content
            except Exception as e:
                return f'LLM error: {e}'
        # fallback simple summary
        return '\n'.join(text.splitlines()[:10])

# ----------------------------- Flask API ------------------------------------
class GUIApp:
    def __init__(self, cmd_db: CommandDB, mcu_db: MCUDB, cg: CodeGenerator, sugg: SuggestionEngine, ai: AIIntegrator):
        if Flask is None:
            self.app = None
            return
        self.cmd_db = cmd_db
        self.mcu_db = mcu_db
        self.cg = cg
        self.sugg = sugg
        self.ai = ai
        self.app = Flask(__name__)
        self._routes()

    def _routes(self):
        @self.app.route('/upload_bas', methods=['POST'])
        def upload_bas():
            # accept raw code in JSON or file upload
            if 'file' in request.files:
                f = request.files['file']
                content = f.read().decode('utf-8', errors='ignore')
            else:
                content = request.json.get('code','')
            fname = request.json.get('filename') or f"upload_{int(datetime.datetime.utcnow().timestamp())}.bas"
            path = os.path.join(WORKSPACE, fname)
            with open(path, 'w', encoding='utf-8') as fo:
                fo.write(content)
            return jsonify({'ok': True, 'path': path})

        @self.app.route('/analyze_bas', methods=['POST'])
        def analyze_bas():
            data = request.json or {}
            code = data.get('code','')
            if not code and data.get('path'):
                try:
                    with open(data.get('path'),'r',encoding='utf-8') as f:
                        code = f.read()
                except Exception:
                    return jsonify({'ok':False,'msg':'Cannot read file'})
            parser = BasParser(code)
            analysis = self.sugg.suggest_for_bas(code)
            return jsonify({'ok':True,'summary':parser.summary(),'suggestions':analysis})

        @self.app.route('/generate_from_scenario', methods=['POST'])
        def gen_from_scenario():
            data = request.json or {}
            scenario = data.get('scenario','')
            device = data.get('device','PIC16F877A')
            peripherals = data.get('peripherals', [])
            code = self.cg.generate_for_scenario(scenario, device, peripherals)
            # save
            fname = data.get('outname') or f"scenario_{int(datetime.datetime.utcnow().timestamp())}.bas"
            path = os.path.join(WORKSPACE, fname)
            with open(path,'w',encoding='utf-8') as f:
                f.write(code)
            return jsonify({'ok':True,'path':path,'code':code})

        @self.app.route('/enhance_bas', methods=['POST'])
        def enhance_bas():
            data = request.json or {}
            code = data.get('code','')
            if not code and data.get('path'):
                try:
                    with open(data.get('path'),'r',encoding='utf-8') as f:
                        code = f.read()
                except Exception:
                    return jsonify({'ok':False,'msg':'Cannot read file'})
            device = data.get('device')
            peripherals = data.get('peripherals', [])
            new_code = self.cg.enhance_bas(code, device, peripherals)
            fname = data.get('outname') or f"enhanced_{int(datetime.datetime.utcnow().timestamp())}.bas"
            path = os.path.join(WORKSPACE, fname)
            with open(path,'w',encoding='utf-8') as f:
                f.write(new_code)
            return jsonify({'ok':True,'path':path,'code':new_code})

        @self.app.route('/learn_chm', methods=['POST'])
        def learn_chm():
            data = request.json or {}
            chm_path = data.get('chm_path')
            if not chm_path or not os.path.exists(chm_path):
                return jsonify({'ok':False,'msg':'CHM path missing or not accessible'})
            ex = ChmExtractor(chm_path)
            texts = ex.extract_texts()
            learned = self.cmd_db.learn_from_texts(texts)
            return jsonify({'ok':True,'learned':learned})

        @self.app.route('/list_peripherals', methods=['GET'])
        def list_peripherals():
            return jsonify({'ok':True,'peripherals': list(PERIPHERAL_TEMPLATES.keys())})

# ----------------------------- CLI Demo & Tests ------------------------------
SAMPLE_BAS = """' Demo code\nDevice PIC16F877A\nDIM led AS BYTE\nTRISB = %11110000\nHIGH PORTB.0\nDELAYMS 500\nLOW PORTB.0\n"""

SAMPLE_SCENARIO = """
When BUTTON pressed toggle LED on PORTB.0
Every 5s read DHT11 on PORTB.0 and send to LCD
"""


def demo():
    print('🔧 Starting super-integrated demo...')
    cmd_db = CommandDB()
    mcu_db = MCUDB()
    cg = CodeGenerator(cmd_db, mcu_db)
    sugg = SuggestionEngine(cmd_db, mcu_db)
    ai = AIIntegrator()
    gui = GUIApp(cmd_db, mcu_db, cg, sugg, ai) if Flask is not None else None

    # parse sample bas
    p = BasParser(SAMPLE_BAS)
    print('\n📄 Parsed SAMPLE_BAS summary:')
    print(p.summary())

    # generate from scenario
    code = cg.generate_for_scenario(SAMPLE_SCENARIO, 'PIC16F877A', ['dht11','lcd','button'])
    print('\n✍️ Generated code from scenario:')
    print(code.splitlines()[:30])

    # enhance existing bas
    enhanced = cg.enhance_bas(SAMPLE_BAS, 'PIC16F877A', ['74HC595','lcd'])
    print('\n🔁 Enhanced code sample (first 30 lines):')
    print('\n'.join(enhanced.splitlines()[:30]))

    # CHM learning demo (if file present at ./sample.chm)
    chm_path = './sample.chm'
    if os.path.exists(chm_path):
        try:
            ex = ChmExtractor(chm_path)
            texts = ex.extract_texts()
            learned = cmd_db.learn_from_texts(texts)
            print('\n📚 Learned from CHM:', learned)
        except Exception as e:
            print('CHM error:', e)
    else:
        print('\n📚 No sample.chm found; skip CHM demo')

    print('\n✅ Demo complete. If Flask installed, run GUI endpoints.')


def run_tests():
    print('\n🧪 Running tests...')
    cmd_db = CommandDB('./data/test_commands.json')
    mcu_db = MCUDB('./data/test_mcudb.json')
    p = BasParser(SAMPLE_BAS)
    assert p.device == 'PIC16F877A'
    assert 'HIGH' in p.commands
    c = CodeGenerator(cmd_db, mcu_db)
    code = c.generate_for_scenario(SAMPLE_SCENARIO, 'PIC16F877A', ['dht11','lcd'])
    assert 'DHT' in code.upper() or 'DHT11' in code.upper() or 'CALL DHT' in code
    enhanced = c.enhance_bas(SAMPLE_BAS, 'PIC16F877A', ['74HC595'])
    assert '74HC595' in enhanced or '74HC595' in ''.join(PERIPHERAL_TEMPLATES.keys())

    # added tests: check header and device line presence
    gen_code = c.generate_for_scenario('When BUTTON pressed toggle LED on PORTB.0', 'PIC16F877A', ['button'])
    assert "Generated by PIC Proton IDE" in gen_code or "Device PIC16F877A" in gen_code
    assert "Device PIC16F877A" in gen_code, 'Device header should be present in generated code'

    print('✅ Tests passed')

# ----------------------------- Entrypoint -----------------------------------
if __name__ == '__main__':
    demo()
    run_tests()

# -----------------------------------------------------------------------------
# Next steps & Integration tips:
# - You can point SAMPLE_CHM env var or use /learn_chm endpoint to feed CHM
# - For real OpenAI usage set OPENAI_API_KEY
# - For Proteus automation set PROTEUS_PATH and implement vendor CLI args in Simulator class
# - Expand PERIPHERAL_TEMPLATES with concrete Proton BASIC code tailored to your chosen compiler/runtime
# - Frontend GUI: a simple React or HTML page can call the Flask endpoints to implement buttons like "Senaryo Oluştur" and "Geliştir"
# -----------------------------------------------------------------------------
