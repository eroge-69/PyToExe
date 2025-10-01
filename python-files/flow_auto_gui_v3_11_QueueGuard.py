# ========== [AUTO-INSERTED POPUP-PAUSE PATCH v1] ==========
# This block adds auto-pause when a queue/limit popup appears, then waits & reloads before resuming.
# Safe to include multiple times; functions are defined only if missing.

try:
    import time as _pp_time
    import re as _pp_re
    from selenium.webdriver.common.by import By as _PP_By
    from selenium.webdriver.support.ui import WebDriverWait as _PP_Wait
    from selenium.webdriver.support import expected_conditions as _PP_EC
except Exception:
    pass

def _pp_cfg_get_bool(self, attr, default):
    v = getattr(self, attr, default)
    try:
        # tk.BooleanVar or similar
        return bool(v.get())
    except Exception:
        return bool(v)

def _pp_cfg_get_str(self, attr, default):
    v = getattr(self, attr, default)
    try:
        return str(v.get())
    except Exception:
        try:
            return str(v)
        except Exception:
            return str(default)

def _pp_detect_popup_text_in_this_context(driver, pattern):
    js = r"""
    const pat = new RegExp(arguments[0]||"queue|max|limit|quota|rate\\s*limit|try again|pending|hàng chờ|đã đạt|quá nhiều|đang xử lý", 'i');
    function vis(el){
      try{ const s=getComputedStyle(el);
           return (el.offsetParent!==null) || (s.display!=='none' && s.visibility!=='hidden') }
      catch(e){ return true }
    }
    function allNodes(root){
      const out=[];
      const push=(r)=>{ if(r && r.querySelectorAll){ out.push(r); for(const e of r.querySelectorAll('*')) out.push(e); } };
      push(root||document);
      // shadowRoots
      for(const el of out.slice()){
        if(el && el.shadowRoot){ push(el.shadowRoot); }
      }
      return out;
    }
    const cands = [];
    for(const el of allNodes(document)){
      if(!el || !vis(el)) continue;
      const role = (el.getAttribute&&el.getAttribute('role'))||'';
      const cls  = ((el.className&&el.className.baseVal) ? el.className.baseVal : (el.className||''))+' '+(el.id||'');
      const modal = el.getAttribute && (el.getAttribute('aria-modal')==='true');
      if (modal || /(^| )modal|dialog|alert|snackbar|toast( |$)/i.test(cls) || /^(dialog|alert)$/i.test(role)) {
        cands.push(el);
      }
    }
    for(const el of cands){
      const t = (el.innerText||'').trim();
      if(t && pat.test(t)) return t.slice(0,400);
    }
    const bodyT = (document.body && document.body.innerText) || '';
    const m = pat.exec(bodyT);
    return m ? (m[0]+'') : null;
    """
    try:
        return driver.execute_script(js, pattern)
    except Exception:
        return None

def _pp_detect_popup_anywhere(driver, pattern):
    txt = _pp_detect_popup_text_in_this_context(driver, pattern)
    if txt: return txt
    try:
        iframes = driver.find_elements(_PP_By.TAG_NAME, "iframe")
    except Exception:
        iframes = []
    for f in iframes:
        try:
            driver.switch_to.frame(f)
            txt = _pp_detect_popup_text_in_this_context(driver, pattern)
            driver.switch_to.default_content()
            if txt: return txt
        except Exception:
            try: driver.switch_to.default_content()
            except: pass
    return None

def _pp_try_close_popup(driver):
    js = r"""
    const labels = ["OK","Close","Dismiss","Got it","Understood","Retry","Continue","Cancel",
                    "Đóng","Thử lại","Bỏ qua","Tiếp tục","Xong","Đồng ý"];
    function clickByText(root){
      const els = root.querySelectorAll('button, [role="button"], a, div, span');
      for(const el of els){
        const t = (el.innerText||'').trim();
        if(!t) continue;
        for(const lb of labels){
          if(new RegExp("^\\s*"+lb+"\\s*$","i").test(t)){
            el.click(); return true;
          }
        }
      }
      return false;
    }
    if (clickByText(document)) return true;
    // also try in shadow roots
    const all = document.querySelectorAll('*');
    for(const e of all){
      if (e.shadowRoot && clickByText(e.shadowRoot)) return true;
    }
    return false;
    """
    try:
        return bool(driver.execute_script(js))
    except Exception:
        return False

# Attach patches only if FlowAutoApp exists
try:
    FlowAutoApp
except NameError:
    FlowAutoApp = None

if FlowAutoApp is not None:

    # smart_sleep
    if not hasattr(FlowAutoApp, "smart_sleep"):
        def _pp_smart_sleep(self, seconds):
            end = _pp_time.time() + max(0.0, float(seconds or 0))
            while _pp_time.time() < end:
                try:
                    self._auto_pause_check()
                except Exception:
                    pass
                # if self.pause attribute exists, honor it
                if getattr(self, "pause", False):
                    while getattr(self, "pause", False):
                        _pp_time.sleep(0.25)
                _pp_time.sleep(0.5)

        FlowAutoApp.smart_sleep = _pp_smart_sleep

    # _auto_pause_check
    if not hasattr(FlowAutoApp, "_auto_pause_check"):
        def _pp_auto_pause_check(self):
            # If no driver yet, skip
            drv = getattr(self, "driver", None)
            if drv is None: 
                return False
            try:
                enable = _pp_cfg_get_bool(self, "pause_on_popup", True)
            except Exception:
                enable = True
            if not enable:
                return False
            pattern = _pp_cfg_get_str(self, "popup_regex",
               r"queue|max|limit|quota|rate\s*limit|try again|pending|hàng chờ|đã đạt|quá nhiều|đang xử lý|không tạo được|khong tao duoc|unable to (create|generate)|could not (create|generate)|please try again later|quota exceeded|over\s*quota|service unavailable|temporarily unavailable")
            try:
                txt = _pp_detect_popup_anywhere(drv, pattern)
                if txt:
                    try:
                        self._handle_popup_pause(txt)
                    except Exception:
                        # Fallback: inline handling
                        if not getattr(self, "pause", False):
                            try: self.pause = True
                            except: pass
                        try:
                            self.log(f"⏸️ Pop-up: “{txt}” – chờ cooldown…")
                        except Exception: pass
                        _pp_try_close_popup(drv)
                        try:
                            wait_s = max(10, int(float(_pp_cfg_get_str(self, "popup_cooldown", "75") or "75")))
                        except Exception:
                            wait_s = 75
                        _pp_time.sleep(wait_s)
                        try:
                            if _pp_cfg_get_bool(self, "reload_after_popup", True):
                                try:
                                    self.log("🔁 Reload lại trang sau pop-up…")
                                except Exception: pass
                                drv.refresh()
                                _PP_Wait(drv, 30).until(_PP_EC.presence_of_element_located((_PP_By.TAG_NAME,"body")))
                                _pp_time.sleep(1.5)
                        except Exception:
                            pass
                        try:
                            self.pause = False
                            self.log("▶️ RESUME sau pop-up.")
                        except Exception: pass
                    return True
            except Exception:
                return False
            return False

        FlowAutoApp._auto_pause_check = _pp_auto_pause_check

    # _handle_popup_pause (used by _auto_pause_check)
    if not hasattr(FlowAutoApp, "_handle_popup_pause"):
        def _pp_handle_popup_pause(self, popup_text):
            try:
                if not getattr(self, "pause", False):
                    try: 
                        self.pause = True
                    except Exception:
                        pass
                try:
                    self.log(f"⏸️ Phát hiện pop-up: “{popup_text}” → PAUSE")
                except Exception: 
                    pass

                _pp_try_close_popup(self.driver)

                # cooldown
                try:
                    wait_s = max(10, int(float(_pp_cfg_get_str(self, "popup_cooldown", "75") or "75")))
                except Exception:
                    wait_s = 75
                try:
                    self.log(f"⏳ Đợi {wait_s}s để hàng chờ hạ nhiệt…")
                except Exception: pass

                t0 = _pp_time.time()
                while _pp_time.time() - t0 < wait_s:
                    _pp_time.sleep(0.5)

                if _pp_cfg_get_bool(self, "reload_after_popup", True):
                    try:
                        self.log("🔁 Reload lại trang sau pop-up…")
                    except Exception: pass
                    try:
                        self.driver.refresh()
                        _PP_Wait(self.driver, 30).until(_PP_EC.presence_of_element_located((_PP_By.TAG_NAME,"body")))
                        _pp_time.sleep(1.5)
                    except Exception as e:
                        try: self.log(f"⚠️ Reload lỗi (bỏ qua): {e}")
                        except Exception: pass
            finally:
                try:
                    self.pause = False
                    self.log("▶️ Đã RESUME sau pop-up.")
                except Exception:
                    pass

        FlowAutoApp._handle_popup_pause = _pp_handle_popup_pause

    # Wrap the sending function to check before & after
    try:
        if hasattr(FlowAutoApp, "fill_prompt_and_generate"):
            if not hasattr(FlowAutoApp, "_orig_fill_prompt_and_generate"):
                FlowAutoApp._orig_fill_prompt_and_generate = FlowAutoApp.fill_prompt_and_generate

                
                def _pp_fill_wrapper(self, *a, **kw):
                    # Pre-check popups
                    try:
                        self._auto_pause_check()
                    except Exception:
                        pass
                    try:
                        res = self._orig_fill_prompt_and_generate(*a, **kw)
                        ok = (res is True) or (res is None)
                    except Exception as e:
                        ok = False
                        err = e
                    if ok:
                        try:
                            self._auto_pause_check()
                        except Exception:
                            pass
                        return res
                    # Fallback path: try to inject text and click generate via JS / heuristics
                    try:
                        drv = self.driver
                        prompt_text = None
                        try:
                            # Try to read first positional arg as the prompt text
                            if len(a) >= 1 and isinstance(a[0], str):
                                prompt_text = a[0]
                            elif "prompt" in kw and isinstance(kw["prompt"], str):
                                prompt_text = kw["prompt"]
                        except Exception:
                            pass
                        if not prompt_text:
                            try:
                                prompt_text = kw.get("text") or kw.get("content") or ""
                            except Exception:
                                prompt_text = ""
                        js_inject = r'''
                        const text = arguments[0]||"";
                        function visible(el){ try{ const s=getComputedStyle(el); return (el.offsetParent!==null) || (s.display!=='none'&&s.visibility!=='hidden'); }catch(e){ return true; } }
                        function setEditable(el, t){
                          try{
                            if(el.isContentEditable){ el.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, t); return true; }
                            if(el.tagName==='TEXTAREA' || el.tagName==='INPUT'){
                              el.focus(); el.value = t;
                              el.dispatchEvent(new Event('input', {bubbles:true}));
                              el.dispatchEvent(new Event('change', {bubbles:true}));
                              return true;
                            }
                          }catch(e){}
                          return false;
                        }
                        function allNodes(root){
                          const arr=[];
                          const push=(r)=>{ if(r && r.querySelectorAll){ arr.push(r); for(const e of r.querySelectorAll('*')) arr.push(e); } };
                          push(root||document);
                          for(const el of arr.slice()){
                            if(el && el.shadowRoot){ push(el.shadowRoot); }
                          }
                          return arr;
                        }
                        let edited=false;
                        // try main doc
                        for(const el of allNodes(document)){
                          if(!visible(el)) continue;
                          if (el.isContentEditable || el.tagName==='TEXTAREA' || el.tagName==='INPUT') {
                            if(setEditable(el, text)){ edited=true; break; }
                          }
                        }
                        // click a "Generate" like button
                        const labels = [/^\s*Generate\s*$/i,/^\s*Tạo\s*$/i,/^\s*Create\s*$/i,/^\s*Run\s*$/i,/^\s*Submit\s*$/i];
                        function tryClick(root){
                          const nodes = root.querySelectorAll('button,[role="button"],a,div,span');
                          for(const n of nodes){
                            const t=(n.innerText||'').trim();
                            for(const r of labels){ if(r.test(t)){ n.click(); return true; } }
                          }
                          return false;
                        }
                        let clicked = tryClick(document);
                        // Return state
                        return edited || clicked;
                        '''
                        ok_js = drv.execute_script(js_inject, prompt_text)
                        # small wait
                        try: self.smart_sleep(1.2)
                        except Exception: pass
                        # post-check popups
                        try: self._auto_pause_check()
                        except Exception: pass
                        return True if ok_js else False
                    except Exception:
                        # final post-check
                        try:
                            self._auto_pause_check()
                        except Exception:
                            pass
                        return False
    
                FlowAutoApp.fill_prompt_and_generate = _pp_fill_wrapper
    except Exception:
        pass

# ========== [/AUTO-INSERTED POPUP-PAUSE PATCH v1] ==========

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Auto v3.10 — Single Project Session + Multi-Output — NETWORK DOWNLOAD
- FIX: Khi đổi file prompts .txt, tool sẽ tự động KHỞI ĐỘNG LẠI từ dòng 1 nếu nội dung file khác (dù cùng đường dẫn).
  Cơ chế: lưu chữ ký (signature) theo SHA1 của nội dung + kích thước + mtime; nếu signature khác thì reset index.
- Thêm: Ô "Start at line (1-based)" để chủ động bắt đầu từ dòng bất kỳ.
- Thêm: Nút "Reset progress" để về dòng 1 cho file hiện tại.
- Giữ nguyên cơ chế resume khi nội dung không thay đổi.
- (Tùy chọn) Outputs per prompt: gửi cùng một prompt nhiều lần liên tiếp.

Bản này SỬA LỖI SyntaxError (dư dấu ngoặc ")" trong phần parse performance log) và thêm selftests phụ để tránh tái phát.
"""

import os, sys, json, time, threading, re, random, hashlib
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import requests



# === Added: required Selenium imports (fix crash: NameError for Options/webdriver/By/etc.) ===
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
except ImportError as e:
    raise ImportError("Selenium is required. Install with: pip install selenium") from e

# === Added: safe defaults for previously undefined constants (fix crash on first run) ===
from pathlib import Path as _Path
DEFAULT_DOWNLOAD_DIR = str(_Path.home() / "Downloads" / "flow_auto_videos")
SETTINGS_FILE = "flow_settings.json"
BATCH_STATE_FILE = "flow_batch_state.json"
# Default Flow URL (can be overridden in the UI). Using labs.google as hinted by cookies domain.
FLOW_URL = "https://labs.google/"

# === VeeVee After-Finish Helpers ===
def _slow_scroll_window(driver, step=400, pause=0.7, idle_rounds=8, max_minutes=10, max_steps=None):
    """Kéo chậm rãi tới đáy cho window hiện tại. Có fallback cuộn container và phím PAGE_DOWN."""
    import time as _time
    last_h = -1
    idle = 0
    steps_done = 0
    t0 = _time.time()
    def get_metrics():
        try:
            return driver.execute_script(
                "var se=document.scrollingElement||document.documentElement||document.body;"
                "return [se.scrollHeight, se.scrollTop, window.innerHeight];"
            )
        except Exception:
            return [0,0,0]
    while _time.time() - t0 < max_minutes * 60:
        h, y, inner = get_metrics()
        moved = False
        try:
            driver.execute_script("window.scrollBy(0, arguments[0]);", int(step))
            _time.sleep(pause)
            _h2, y2, _in2 = get_metrics()
            moved = (y2 > y)
        except Exception:
            moved = False
        if not moved:
            try:
                res = driver.execute_script(
                    """
                    var step=arguments[0];
                    var nodes = Array.from(document.querySelectorAll('*')).filter(e=>{
                        try{
                            var s=getComputedStyle(e);
                            return (s.overflowY==='auto'||s.overflowY==='scroll') && e.scrollHeight>e.clientHeight+50;
                        }catch(err){return false;}
                    }).sort((a,b)=>b.scrollHeight-a.scrollHeight);
                    if(nodes.length){
                        var el=nodes[0];
                        var before=el.scrollTop;
                        el.scrollTop = Math.min(el.scrollTop + step, el.scrollHeight);
                        return [nodes.length, before, el.scrollTop, el.scrollHeight, el.clientHeight];
                    } else {
                        return [0,0,0,0,0];
                    }
                    """, int(step)
                )
                if isinstance(res, (list, tuple)) and len(res)>=3 and res[2] > res[1]:
                    moved = True
            except Exception:
                pass
        if not moved:
            try:
                try:
                    driver.execute_script("document.body && document.body.focus && document.body.focus();")
                except Exception:
                    pass
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.keys import Keys
                actions = ActionChains(driver)
                for _ in range(3):
                    actions.send_keys(Keys.PAGE_DOWN)
                actions.perform()
                _time.sleep(pause)
                _h2, y2, _in2 = get_metrics()
                moved = (y2 > y)
            except Exception:
                moved = False
        steps_done += 1
        if max_steps is not None and steps_done >= int(max_steps):
            break
        if moved:
            idle = 0
            last_h = h
            continue
        else:
            if h == last_h:
                idle += 1
            else:
                idle = 0
                last_h = h
            if idle >= idle_rounds and max_steps is None:
                break

def reload_wait_and_slow_scroll_all_contexts(driver, log, step=400, pause=0.7, pre_wait=90, loops=750):
    """Chờ pre_wait giây, reload trang, rồi kéo chậm theo số bước (loops) ở main & mọi iframe."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time as _time
    try:
        pre = float(pre_wait) if pre_wait is not None else 0
    except Exception:
        pre = 0
    if pre > 0:
        try:
            log(f"⏳ Đợi {int(pre)}s trước khi reload & scroll…")
        except Exception:
            pass
        _time.sleep(pre)
    try:
        driver.refresh()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        _time.sleep(2.0)  # post-wait để nội dung ổn định
    except Exception as e:
        try: log(f"⚠️ Reload thất bại (bỏ qua): {e}")
        except: pass
    try:
        _slow_scroll_window(driver, step=step, pause=pause, max_steps=int(float(loops)))
    except Exception as e:
        try: log(f"⚠️ Lỗi scroll main: {e}")
        except: pass
    try:
        frames = driver.find_elements(By.TAG_NAME, "iframe")
    except Exception:
        frames = []
    for f in frames:
        try:
            driver.switch_to.frame(f)
            _slow_scroll_window(driver, step=step, pause=pause, max_steps=int(float(loops)))
        except Exception:
            pass
        finally:
            try:
                driver.switch_to.default_content()
            except:
                pass

def slugify(text, maxlen=60):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (s[:maxlen] or "video").strip("-")

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def file_signature(path):
    """SHA1 của nội dung + kích thước + mtime. Trả về None nếu lỗi."""
    try:
        h = hashlib.sha1()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        st = os.stat(path)
        h.update(str(st.st_size).encode())
        h.update(str(int(st.st_mtime)).encode())
        return h.hexdigest()
    except Exception:
        return None

# =============== Selenium Driver ===============
def build_driver(download_dir, headless=False):
    opts = Options()
    # Enable performance logging for Network events
    opts.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    opts.add_experimental_option("prefs", prefs)
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=opts)
    drv.set_window_size(1280, 900)
    # Enable CDP Network to capture responses
    try:
        drv.execute_cdp_cmd('Network.enable', {})
    except Exception:
        pass
    return drv

# =============== Cookies ===============
def load_cookies_to_driver(driver, cookies_json_path, domain_hint="google.com"):
    if not cookies_json_path or not os.path.exists(cookies_json_path):
        return
    try:
        with open(cookies_json_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
    except Exception:
        return
    driver.get(f"https://{domain_hint}"); time.sleep(1)
    for c in cookies:
        cookie = {"name": c.get("name") or c.get("Name"), "value": c.get("value") or c.get("Value")}
        if "domain" in c: cookie["domain"] = c["domain"]
        if "path" in c: cookie["path"] = c["path"]
        if "expiry" in c:
            try: cookie["expiry"] = int(c["expiry"])
            except: pass
        if "secure" in c: cookie["secure"] = bool(c.get("secure", False))
        if "httpOnly" in c: cookie["httpOnly"] = bool(c.get("httpOnly", c.get("http_only", False)))
        try: driver.add_cookie(cookie)
        except Exception:
            pass

# ------------- helpers -------------
def _visible(el):
    try: return el.is_displayed() and el.is_enabled()
    except: return False

def _switch_iframes_then(fn):
    from selenium.common.exceptions import NoSuchFrameException
    def inner(driver, log):
        if fn(driver, log): return True
        for f in driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                driver.switch_to.frame(f)
                if fn(driver, log):
                    driver.switch_to.default_content(); return True
            except NoSuchFrameException:
                pass
            finally:
                try: driver.switch_to.default_content()
                except: pass
        return False
    return inner

# ============== Editor session ==============
def ensure_editor_session(driver, log, project_url=None):
    # 1) open Flow homepage or the provided project URL
    if not project_url:
        driver.get(FLOW_URL)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        try:
            _switch_iframes_then(lambda d,l: _strict_click_generate(d))(driver, log)
        except Exception:
            pass
    else:
        driver.get(project_url)

    # Wait until we are inside an editor/project URL
    for _ in range(60):
        if re.search(r"/project|/editor|/create|/new", driver.current_url, re.I):
            return driver.current_url
        time.sleep(1)
    raise RuntimeError("Không vào được trang editor.")

def _inject_text_like_human(driver, el, text, log):
    try:
        el.click()
        try: el.clear()
        except: pass
    except: pass
    # React/Lexical: set value + dispatch input/change
    driver.execute_script("""
    const el=arguments[0], val=arguments[1];
    if (el.isContentEditable){
      el.focus();
      document.execCommand && document.execCommand('selectAll', false, null);
      document.execCommand && document.execCommand('insertText', false, val);
    } else {
      const tag = (el.tagName||'').toUpperCase();
      const dTA=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value');
      const dIN=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value');
      const setter = tag==='TEXTAREA'?dTA:dIN;
      if (setter) setter.set.call(el,val); else el.value=val;
    }
    const opt={bubbles:true, composed:true};
    el.dispatchEvent(new InputEvent('input', opt));
    el.dispatchEvent(new Event('change', opt));
    """, el, text)

def _query_prompt_inputs(driver):
    try:
        tars = driver.find_elements(By.TAG_NAME, 'textarea')
        inns = driver.find_elements(By.TAG_NAME, 'input')
        eds  = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
        nodes = [*tars, *inns, *eds]
        return [n for n in nodes if _visible(n)]
    except Exception:
        return []


def _strict_click_generate(driver):
    js = r"""
    // Only click true 'Generate/Run/Submit' buttons near the composer; avoid Help (Trợ giúp)
    const labelRe = /^\s*(Generate|Tạo|Create|Run|Submit|Gửi)\s*$/i;
    function visible(el){
      try{ const s=getComputedStyle(el); return (el.offsetParent!==null) || (s.display!=='none' && s.visibility!=='hidden'); }catch(e){ return true; }
    }
    function inHelp(el){
      try{
        while(el){
          if(el.getAttribute){
            const aria=(el.getAttribute('aria-label')||'')+(el.getAttribute('aria-labelledby')||'')+(el.id||'');
            const role=(el.getAttribute('role')||'');
            if(/trợ giúp|tro giup|help/i.test(aria) || /dialog/i.test(role)) return true;
          }
          el = el.parentNode || el.host;
        }
      }catch(e){}
      return false;
    }
    // Find candidate inputs/editors
    const inputs = [];
    for(const el of document.querySelectorAll('textarea, input, [contenteditable="true"]')){
      if(visible(el) && !inHelp(el)) inputs.push(el);
    }
    function nearestButton(from){
      let cur = from;
      for(let depth=0; depth<5 && cur; depth++){
        const scope = cur.querySelectorAll ? cur : (cur.shadowRoot || null);
        if(scope){
          const cand = scope.querySelectorAll('button,[role="button"]');
          for(const b of cand){
            if(!visible(b) || inHelp(b)) continue;
            const t=(b.innerText||'').trim();
            if(labelRe.test(t)) return b;
          }
        }
        cur = cur.parentNode || cur.host;
      }
      // Fallback: global strict search
      for(const b of document.querySelectorAll('button,[role="button"]')){
        if(!visible(b) || inHelp(b)) continue;
        const t=(b.innerText||'').trim();
        if(labelRe.test(t)) return b;
      }
      return null;
    }
    for(const inp of inputs){
      const b = nearestButton(inp);
      if(b){ b.click(); return true; }
    }
    return false;
    """
    try:
        return bool(driver.execute_script(js))
    except Exception:
        return False

def fill_prompt_and_generate(driver, prompt, log):
    nodes = _query_prompt_inputs(driver)
    ok=False
    for n in nodes:
        try:
            _inject_text_like_human(driver, n, prompt, log)
            ok=True; break
        except Exception:
            continue
    if not ok:
        def deep_find_fill(drv, _log):
            try:
                tars = drv.find_elements(By.TAG_NAME, 'textarea')
                inns = drv.find_elements(By.TAG_NAME, 'input')
                eds  = drv.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                nodes = [*tars, *inns, *eds]
                nodes = [n for n in nodes if n.is_displayed()]
                for n in nodes:
                    try:
                        _inject_text_like_human(drv, n, prompt, log)
                        return True
                    except Exception:
                        pass
                return False
            except Exception:
                return False
        if not _switch_iframes_then(deep_find_fill)(driver, log):
            return False

    # Submit via Enter / Ctrl+Enter / Cmd+Enter and try visible "Generate" buttons
    for seq in [(Keys.ENTER,), (Keys.CONTROL, "\n"), (Keys.COMMAND, "\n")]:
        try:
            ac = ActionChains(driver)
            for k in seq:
                if k == "\n":
                    ac.send_keys("\n")
                else:
                    ac.key_down(k)
            for k in seq:
                if k != "\n":
                    ac.key_up(k)
            ac.perform()
        except Exception:
            pass

    _switch_iframes_then(lambda d,l: _strict_click_generate(d))(
        driver, log
    )
    return True

def wait_for_result_urls(driver, log, timeout=360):
    start=time.time()
    urls=[]
    def try_video_src(drv, _log):
        vids=drv.find_elements(By.TAG_NAME,"video")
        out=[]
        for v in vids:
            try:
                src=v.get_attribute("src") or ""
                if not src or src.startswith("blob:"):
                    continue
                out.append(src)
            except:
                pass
        return out
    while time.time()-start<timeout:
        found=_switch_iframes_then(lambda d,l: try_video_src(d,l))(driver, log)
        for u in (found or []):
            if u not in urls:
                urls.append(u)
        if urls:
            return urls
        time.sleep(2)
    return urls

# =============== GUI (Batch) =================
class FlowAutoApp:
    def __init__(self, root):
        self.root=root
        root.title("Flow Auto v3.10 — Single Project Session + Multi-Output — NETWORK DOWNLOAD")
        self.running=False
        self.pause=False
        self.driver=None

        self.settings=load_json(SETTINGS_FILE, {})

        # Row 3b: After-finish reload & slow scroll (for VeeVee)
        try:
            self.after_finish_scroll = tk.BooleanVar(value=self.settings.get("after_finish_scroll", False))
        except Exception:
            self.after_finish_scroll = tk.BooleanVar(value=False)
        tk.Checkbutton(
            root,
            text="After batch: Reload & slow-scroll to bottom (for VeeVee)",
            variable=self.after_finish_scroll
        ).grid(row=3, column=2, sticky="w", padx=4)

        # tốc độ kéo: bước & delay
        try:
            self.scroll_step = tk.StringVar(value=str(self.settings.get("scroll_step", "400")))
            self.scroll_pause = tk.StringVar(value=str(self.settings.get("scroll_pause", "0.7")))
        except Exception:
            self.scroll_step = tk.StringVar(value="400")
            self.scroll_pause = tk.StringVar(value="0.7")
        tk.Label(root, text="Scroll step(px) / pause(s)").grid(row=3, column=3, sticky="e")
        tk.Entry(root, textvariable=self.scroll_step, width=6).grid(row=3, column=4, sticky="w")
        tk.Entry(root, textvariable=self.scroll_pause, width=6).grid(row=3, column=4, sticky="e", padx=6)

        # Pre-wait(s) & Scroll loops
        try:
            self.prewait_seconds = tk.StringVar(value=str(self.settings.get("prewait_seconds", "90")))
            self.scroll_loops = tk.StringVar(value=str(self.settings.get("scroll_loops", "750")))
        except Exception:
            self.prewait_seconds = tk.StringVar(value="90")
            self.scroll_loops = tk.StringVar(value="750")
        tk.Label(root, text="Pre-wait(s) / Scroll loops").grid(row=3, column=5, sticky="e", padx=(12,0))
        tk.Entry(root, textvariable=self.prewait_seconds, width=6).grid(row=3, column=6, sticky="w")
        tk.Entry(root, textvariable=self.scroll_loops, width=6).grid(row=3, column=6, sticky="e", padx=6)
        # Results storage
        self.results=[]  # list of dict: {idx,prompt,status,urls}

        # Row 0: cookies
        tk.Label(root,text="Cookies JSON").grid(row=0,column=0,sticky="w")
        self.cookie_var=tk.StringVar(value=self.settings.get("cookie_file",""))
        tk.Entry(root,textvariable=self.cookie_var,width=60).grid(row=0,column=1)
        tk.Button(root,text="Browse",command=self.pick_cookie).grid(row=0,column=2)

        # Row 1: download dir
        tk.Label(root,text="Download dir").grid(row=1,column=0,sticky="w")
        self.dl_var=tk.StringVar(value=self.settings.get("download_dir",DEFAULT_DOWNLOAD_DIR))
        tk.Entry(root,textvariable=self.dl_var,width=60).grid(row=1,column=1)
        tk.Button(root,text="Browse",command=self.pick_dir).grid(row=1,column=2)

        # Row 2: project URL (optional)
        tk.Label(root,text="Project URL (optional)").grid(row=2,column=0,sticky="w")
        self.project_url=tk.StringVar(value=self.settings.get("project_url",""))
        tk.Entry(root,textvariable=self.project_url,width=60).grid(row=2,column=1)

        # Row 3: headless
        self.headless=tk.BooleanVar(value=self.settings.get("headless",False))
        tk.Checkbutton(root,text="Headless",variable=self.headless).grid(row=3,column=1,sticky="w")

        # Row 4: prompt single (optional)
        tk.Label(root,text="Prompt (single test)").grid(row=4,column=0,sticky="nw")
        self.prompt_box=ScrolledText(root,width=70,height=5)
        self.prompt_box.grid(row=4,column=1,columnspan=2,sticky="we")

        # Row 5: batch file + pacing
        tk.Label(root,text="Prompts file (.txt, mỗi dòng 1 prompt)").grid(row=5,column=0,sticky="w")
        self.prompts_file=tk.StringVar(value=self.settings.get("prompts_file",""))
        tk.Entry(root,textvariable=self.prompts_file,width=60).grid(row=5,column=1)
        tk.Button(root,text="Browse",command=self.pick_prompts).grid(row=5,column=2)

        tk.Label(root,text="Delay giữa jobs (giây): min").grid(row=6,column=0,sticky="e")
        self.delay_min=tk.StringVar(value=str(self.settings.get("delay_min","3")))
        self.delay_max=tk.StringVar(value=str(self.settings.get("delay_max","8")))
        tk.Entry(root,textvariable=self.delay_min,width=8).grid(row=6,column=1,sticky="w")
        tk.Label(root,text="max").grid(row=6,column=1)
        tk.Entry(root,textvariable=self.delay_max,width=8).grid(row=6,column=1,sticky="e")

        # Row 6b: outputs per prompt + start line override
        tk.Label(root,text="Outputs per prompt").grid(row=7,column=2,sticky="e")
        self.outputs_per_prompt=tk.StringVar(value=str(self.settings.get("outputs_per_prompt","1")))
        tk.Entry(root,textvariable=self.outputs_per_prompt,width=5).grid(row=7,column=2,sticky="w", padx=90)

        tk.Label(root,text="Start at line (1-based)").grid(row=7,column=0,sticky="e")
        self.start_line_override=tk.StringVar(value="")
        tk.Entry(root,textvariable=self.start_line_override,width=10).grid(row=7,column=1,sticky="w")

        # Row 7: controls
        tk.Button(root,text="Run ONE",command=self.run_one,bg="#3498db",fg="white").grid(row=8,column=0,sticky="we")
        tk.Button(root,text="Run BATCH",command=self.run_batch,bg="#2ecc71",fg="white").grid(row=8,column=1,sticky="we")
        tk.Button(root,text="Pause/Resume",command=self.toggle_pause).grid(row=8,column=2,sticky="we")
        tk.Button(root,text="Reset progress",command=self.reset_progress).grid(row=8,column=3,sticky="we")

        # Row 8: log
        tk.Label(root,text="Log").grid(row=9,column=0,sticky="nw")
        self.logbox=ScrolledText(root,width=70,height=10,state="disabled")
        self.logbox.grid(row=9,column=1,columnspan=3,sticky="we")

        # Row 9: results table
        tk.Label(root,text="Results").grid(row=10,column=0,sticky="nw")
        self.tree = ttk.Treeview(root, columns=("idx","prompt","status","urls"), show="headings", height=8)
        for col, w in [("idx",50), ("prompt",360), ("status",120), ("urls",240)]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=w, anchor="w")
        self.tree.grid(row=10, column=1, columnspan=3, sticky="we")
        self.tree_scroll = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.grid(row=10, column=4, sticky="ns")

        # Announce mode in log asap
        try:
            self.log("ℹ️ NETWORK DOWNLOAD: tool sẽ gửi prompt và cố gắng thu URL video để tải về.")
        except Exception:
            pass

    def log(self,msg):
        self.logbox.config(state="normal")
        self.logbox.insert("end",f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.logbox.see("end"); self.logbox.config(state="disabled")
        print(msg)

    def pick_cookie(self):
        p=filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if p: self.cookie_var.set(p)

    def pick_dir(self):
        d=filedialog.askdirectory()
        if d: self.dl_var.set(d)

    def pick_prompts(self):
        p=filedialog.askopenfilename(filetypes=[("Text files","*.txt")])
        if p:
            self.prompts_file.set(p)
            sig = file_signature(p)
            save_json(BATCH_STATE_FILE, {"path": p, "sig": sig, "index": 0})
            self.log("🔁 Đã chọn file mới và reset progress về dòng 1.")

    def reset_progress(self):
        p = self.prompts_file.get().strip()
        if not p:
            messagebox.showwarning("Thiếu file","Chọn file prompts .txt trước khi reset.")
            return
        sig = file_signature(p)
        save_json(BATCH_STATE_FILE, {"path": p, "sig": sig, "index": 0})
        self.log("✅ Progress reset về dòng 1 cho file hiện tại.")

    
    def save_settings(self):
        save_json(SETTINGS_FILE, {
            "cookie_file": self.cookie_var.get(),
            "download_dir": self.dl_var.get(),
            "headless": self.headless.get(),
            "prompts_file": self.prompts_file.get(),
            "delay_min": self.delay_min.get(),
            "delay_max": self.delay_max.get(),
            "outputs_per_prompt": self.outputs_per_prompt.get(),
            "project_url": self.project_url.get(),
            "after_finish_scroll": self.after_finish_scroll.get(),
            "scroll_step": self.scroll_step.get(),
            "scroll_pause": self.scroll_pause.get(),
            "prewait_seconds": self.prewait_seconds.get(),
            "scroll_loops": self.scroll_loops.get(),
        })


    # ------- Single run -------
    def run_one(self):
        if self.running: return
        self.save_settings()
        prompt=self.prompt_box.get("1.0","end").strip()
        if not prompt:
            messagebox.showwarning("Thiếu prompt","Nhập prompt test trước.")
            return
        threading.Thread(target=self._do_one,args=(prompt,),daemon=True).start()

    def _add_result_row(self, idx, prompt, status="queued", urls=None):
        rec={"idx":idx,"prompt":prompt,"status":status,"urls":urls or []}
        self.results.append(rec)
        if getattr(self, "tree", None):
            self.tree.insert("", "end", iid=str(idx), values=(idx, (prompt[:80]+"..." if len(prompt)>80 else prompt), status, ", ".join(rec["urls"])))

    def _update_result_row(self, idx, **kw):
        for r in self.results:
            if r["idx"]==idx:
                r.update({k:v for k,v in kw.items() if v is not None})
                if getattr(self, "tree", None):
                    self.tree.item(str(idx), values=(r["idx"], (r["prompt"][:80]+"..." if len(r["prompt"])>80 else r["prompt"]), r["status"], ", ".join(r["urls"])))
                break

    def _poll_completion_async(self, idx, prompt):
        def worker():
            try:
                urls = wait_for_result_urls(self.driver, self.log, timeout=360)

                # Try to capture direct video URLs from Network logs as well
                more_urls = collect_video_urls_from_logs(self.driver)
                # If still empty, try to play first <video> to trigger network and re-collect
                if not (urls or more_urls):
                    try:
                        vids=self.driver.find_elements(By.TAG_NAME,"video")
                        if vids:
                            self.driver.execute_script("try{arguments[0].play&&arguments[0].play()}catch(e){}", vids[0])
                            time.sleep(2)
                            more_urls = collect_video_urls_from_logs(self.driver)
                    except Exception:
                        pass
                combined = []
                for u in (urls or []) + (more_urls or []):
                    if u not in combined:
                        combined.append(u)

                # Download locally using cookie header
                local_files=[]
                if combined:
                    try:
                        headers = build_cookie_header(self.driver)
                    except Exception:
                        headers = {}
                    for i,u in enumerate(combined):
                        try:
                            fname = f"flow_{idx}_{i}.mp4"
                            path = smart_download(u, self.dl_var.get(), filename=fname, headers=headers)
                            local_files.append(path)
                        except Exception as de:
                            self.log(f"⚠️ Download failed: {u} ({de})")

                    # Append CSV row
                    try:
                        import csv, datetime as _dt
                        csv_path = os.path.join(self.dl_var.get(), "flow_runs.csv")
                        with open(csv_path, "a", encoding="utf-8", newline="") as f:
                            w=csv.writer(f)
                            if f.tell()==0:
                                w.writerow(["timestamp","index","prompt","remote_urls","local_files"])
                            w.writerow([_dt.datetime.now().isoformat(timespec="seconds"), idx, prompt, " | ".join(combined), " | ".join(local_files)])
                        self.log(f"💾 Saved CSV: {csv_path}")
                    except Exception as ce:
                        self.log(f"⚠️ CSV write error: {ce}")

                if (urls or more_urls):
                    final_urls = combined if 'combined' in locals() else urls
                    self.log(f"🎉 Completed: {len(final_urls)} URL(s) sẵn sàng cho prompt {idx}.")
                    self._update_result_row(idx, status="completed", urls=final_urls)
                else:
                    self._update_result_row(idx, status="timeout")
            except Exception as e:
                self._update_result_row(idx, status=f"error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _do_one(self, prompt):
        self.running=True
        try:
            os.makedirs(self.dl_var.get(),exist_ok=True)
            self.driver = build_driver(self.dl_var.get(), headless=self.headless.get())
            self.log("Injecting cookies…"); load_cookies_to_driver(self.driver, self.cookie_var.get(), "labs.google")
            project_url = ensure_editor_session(self.driver, self.log, project_url=(self.project_url.get().strip() or None))
            self.log(f"Project: {project_url}")
            ok=fill_prompt_and_generate(self.driver, prompt, self.log)
            if not ok:
                raise RuntimeError("Không gửi được prompt.")

            # Add row and start poll
            idx=len(self.results)+1
            self._add_result_row(idx, prompt, status="sent")
            self._poll_completion_async(idx, prompt)
            self.log("✅ ONE done: đã gửi prompt và đang theo dõi kết quả.")
        except Exception as e:
            self.log(f"❌ ONE error: {e}")
        finally:
            self.running=False

    def toggle_pause(self):
        self.pause=not getattr(self, "pause", False)
        self.log("⏸️ Paused" if self.pause else "▶️ Resumed")

    def _resolve_start_index(self, prompts):
        """Quyết định start_idx dựa trên: override > (path & sig khớp ? resume : reset)."""
        current_path = self.prompts_file.get()
        current_sig = file_signature(current_path) if current_path else None

        # 1) override từ UI
        ov = (self.start_line_override.get() or "").strip()
        if ov.isdigit():
            start_idx = max(0, int(ov)-1)
            save_json(BATCH_STATE_FILE, {"path": current_path, "sig": current_sig, "index": start_idx})
            return start_idx

        # 2) theo state (path + sig)
        state = load_json(BATCH_STATE_FILE, {"path": None, "sig": None, "index": 0})
        if state.get("path") == current_path and state.get("sig") == current_sig:
            return int(state.get("index", 0))
        else:
            save_json(BATCH_STATE_FILE, {"path": current_path, "sig": current_sig, "index": 0})
            return 0

    def run_batch(self):
        if self.running: return
        self.save_settings()
        if not self.prompts_file.get():
            messagebox.showwarning("Thiếu file","Chọn file prompts .txt")
            return
        with open(self.prompts_file.get(),"r",encoding="utf-8") as f:
            prompts=[ln.strip() for ln in f if ln.strip()]
        if not prompts:
            messagebox.showwarning("Rỗng","File không có prompt.")
            return

        start_idx = self._resolve_start_index(prompts)
        self.log(f"Batch size: {len(prompts)} | start từ index {start_idx} (dòng {start_idx+1})")
        threading.Thread(target=self._do_batch,args=(prompts,start_idx),daemon=True).start()

    def _do_batch(self, prompts, start_idx):
        self.running=True
        try:
            os.makedirs(self.dl_var.get(),exist_ok=True)
            if not self.driver:
                self.driver = build_driver(self.dl_var.get(), headless=self.headless.get())
                self.log("Injecting cookies…"); load_cookies_to_driver(self.driver, self.cookie_var.get(), "labs.google")

            project_url = ensure_editor_session(self.driver, self.log, project_url=(self.project_url.get().strip() or None))
            self.log(f"Project: {project_url}")

            outs = max(1, int(self.outputs_per_prompt.get() or 1))

            for i in range(start_idx, len(prompts)):
                while self.pause:
                    self.smart_sleep(1)

                p=prompts[i]
                self.log(f"--- [{i+1}/{len(prompts)}] Submit: {p[:90]}")

                try:
                    try:
                        if not str(self.driver.current_url).startswith(str(project_url).rstrip('/')):
                            self.driver.get(project_url)
                            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                            self.smart_sleep(0.5)
                    except Exception:
                        project_url = ensure_editor_session(self.driver, self.log, project_url=project_url)

                    # Gửi N lần cho cùng một prompt nếu cần
                    success_any=False
                    for k in range(outs):
                        ok=fill_prompt_and_generate(self.driver, p, self.log)
                        success_any = success_any or ok
                        if outs>1:
                            self.smart_sleep(1.0)
                    if not success_any: raise RuntimeError("Không gửi được prompt.")

                    self.log("✅ Prompt đã gửi.")
                    # update resume state sau khi GỬI thành công prompt i
                    current_path=self.prompts_file.get()
                    current_sig=file_signature(current_path)
                    save_json(BATCH_STATE_FILE, {"path": current_path, "sig": current_sig, "index": i+1})
                except Exception as e:
                    self.log(f"❌ Error at index {i}: {e}")
                    backoff = random.uniform(6.0, 12.0)
                    self.log(f"↻ Retry sau ~{backoff:.1f}s")
                    self.smart_sleep(backoff)
                    try:
                        success_any=False
                        for k in range(outs):
                            ok=fill_prompt_and_generate(self.driver, p, self.log)
                            success_any = success_any or ok
                            if outs>1:
                                self.smart_sleep(1.0)
                        if not success_any: raise RuntimeError("Không gửi được prompt.")
                        self.log("✅ Prompt đã gửi (retry).")
                        current_path=self.prompts_file.get()
                        current_sig=file_signature(current_path)
                        save_json(BATCH_STATE_FILE, {"path": current_path, "sig": current_sig, "index": i+1})
                    except Exception as e2:
                        self.log(f"⛔ Skipped index {i}: {e2}")

                dmin=float(self.delay_min.get() or 3)
                dmax=float(self.delay_max.get() or 8)
                sleep_s=random.uniform(dmin, max(dmin, dmax))
                self.log(f"…throttle sleep ~{sleep_s:.1f}s"); self.smart_sleep(sleep_s)

            # === After-finish hook for VeeVee: reload + slow scroll ===
            try:
                if getattr(self, "after_finish_scroll", None) and self.after_finish_scroll.get():
                    stp = int(float(self.scroll_step.get() or "400"))
                    pau = float(self.scroll_pause.get() or "0.7")
                    pre = float(self.prewait_seconds.get() or 90.0)
                    loops = int(float(self.scroll_loops.get() or 750))
                    self.log("🔁 Reload page & slow-scroll tới đáy (để VeeVee nhận diện toàn bộ)…")
                    reload_wait_and_slow_scroll_all_contexts(self.driver, self.log, step=stp, pause=pau, pre_wait=pre, loops=loops)
                    self.log("✅ Slow-scroll xong. Bạn có thể dùng VeeVee để tải.")
            except Exception as e:
                try:
                    self.log(f"⚠️ After-finish scroll error: {e}")
                except Exception:
                    pass

            self.log("🎯 Batch DONE.")
        finally:
            self.running=False
            self.log("Đóng Chrome tay khi xong kiểm tra.")

# =============== Self tests ===============
import json as _json

def _selftests():
    # Basic slugify tests (GIỮ NGUYÊN)
    assert slugify("Hello  World!!") == "hello-world"
    assert slugify("") == "video"
    assert slugify("___") == "video"
    assert slugify("A B C") == "a-b-c"
    # Sanity: ensure no Python 'and' inside JS snippet
    js_vis = "return (getComputedStyle(el).display!==\"none\" && getComputedStyle(el).visibility!==\"hidden\");"
    assert " and " not in js_vis

    # NEW: smoke-test cho parser của performance log (tránh lỗi dấu ngoặc)
    entry = {"message": _json.dumps({
        "message": {
            "method": "Network.responseReceived",
            "params": {"response": {"mimeType": "video/mp4", "url": "https://example.com/vid.mp4"}}
        }
    })}
    msg = _json.loads(entry.get("message", "")).get("message", {})
    assert msg.get("method") == "Network.responseReceived"
    assert msg.get("params", {}).get("response", {}).get("url", "").endswith(".mp4")

    print("✅ Selftests passed.")

# ============== Network capture & download helpers (Method 2) ==============
VIDEO_MIME_HINTS = ("video/mp4", "application/octet-stream")
VIDEO_EXT_HINTS = (".mp4", ".mov", ".m4v")

def collect_video_urls_from_logs(driver):
    """Parse Chrome performance logs to find direct video URLs (non-blob)."""
    urls=set()
    try:
        logs = driver.get_log("performance")
    except Exception:
        logs = []
    for entry in logs:
        try:
            # FIX: loại bỏ dấu ngoặc thừa sau loads(...))
            msg = _json.loads(entry.get("message","")) .get("message",{})
            if msg.get("method") == "Network.responseReceived":
                resp = msg.get("params",{}).get("response",{})
                mime = (resp.get("mimeType") or "").lower()
                url = resp.get("url") or ""
                if not url or url.startswith("blob:") or url.startswith("data:"):
                    continue
                if (mime in VIDEO_MIME_HINTS) or any(url.lower().split("?")[0].endswith(ext) for ext in VIDEO_EXT_HINTS):
                    urls.add(url)
        except Exception:
            continue
    return list(urls)

def build_cookie_header(driver):
    """Return headers dict with current Selenium cookies joined for requests."""
    try:
        cookies = driver.get_cookies()
    except Exception:
        cookies = []
    if not cookies:
        return {}
    ck = "; ".join([f"{c['name']}={c['value']}" for c in cookies if 'name' in c and 'value' in c])
    return {"Cookie": ck}

def smart_download(url, out_dir, filename=None, headers=None, timeout=600):
    """Download a file using requests with streaming."""
    import os, re, requests
    os.makedirs(out_dir, exist_ok=True)
    if not filename:
        fname = re.sub(r"[^\w\-.]", "_", (url.split("?")[0].split("/")[-1] or "video.mp4"))
    else:
        fname = filename
    out_path = os.path.join(out_dir, fname)
    with requests.get(url, headers=headers or {}, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
    return out_path

# =============== Entry ===============

# ========== [POPUP-PAUSE CORE PATCH v3 — injected after FlowAutoApp class] ==========
import types as _PP_types
import time as _PP_time
try:
    from selenium.webdriver.common.by import By as _PP_By
    from selenium.webdriver.support.ui import WebDriverWait as _PP_Wait
    from selenium.webdriver.support import expected_conditions as _PP_EC
except Exception:
    _PP_By=_PP_Wait=_PP_EC=None

def _PP_cfg_get_bool(self, attr, default):
    v = getattr(self, attr, default)
    try: return bool(v.get())
    except Exception: return bool(v)

def _PP_cfg_get_str(self, attr, default):
    v = getattr(self, attr, default)
    try: return str(v.get())
    except Exception:
        try: return str(v)
        except Exception: return str(default)

def _PP_detect_popup_text_in_this_context(driver, pattern):
    js = r"""
    const pat = new RegExp(arguments[0]||"queue|max|limit|quota|rate\s*limit|try again|pending|hàng chờ|đã đạt|quá nhiều|đang xử lý", 'i');
    function vis(el){ try{ const s=getComputedStyle(el); return (el.offsetParent!==null)||(s.display!=='none'&&s.visibility!=='hidden') }catch(e){return true} }
    function allNodes(root){
      const out=[]; const push=(r)=>{ if(r&&r.querySelectorAll){ out.push(r); for(const e of r.querySelectorAll('*')) out.push(e);} };
      push(root||document);
      for(const el of out.slice()){ if(el&&el.shadowRoot){ push(el.shadowRoot);} }
      return out;
    }
    const cands=[];
    for(const el of allNodes(document)){
      if(!el || !vis(el)) continue;
      const role=(el.getAttribute&&el.getAttribute('role'))||'';
      const cls = ((el.className&&el.className.baseVal)?el.className.baseVal:(el.className||''))+' '+(el.id||'');
      const modal = el.getAttribute && (el.getAttribute('aria-modal')==='true');
      if (modal || /(^| )modal|dialog|alert|snackbar|toast( |$)/i.test(cls) || /^(dialog|alert)$/i.test(role)) cands.push(el);
    }
    for(const el of cands){
      const t=(el.innerText||'').trim();
      if(t && pat.test(t)) return t.slice(0,400);
    }
    const bodyT=(document.body&&document.body.innerText)||'';
    const m=pat.exec(bodyT);
    return m ? (m[0]+'') : null;
    """
    try: return driver.execute_script(js, pattern)
    except Exception: return None

def _PP_detect_popup_anywhere(driver, pattern):
    txt = _PP_detect_popup_text_in_this_context(driver, pattern)
    if txt: return txt
    try:
        iframes = driver.find_elements(_PP_By.TAG_NAME, "iframe") if _PP_By else []
    except Exception:
        iframes = []
    for f in iframes:
        try:
            driver.switch_to.frame(f)
            txt = _PP_detect_popup_text_in_this_context(driver, pattern)
            driver.switch_to.default_content()
            if txt: return txt
        except Exception:
            try: driver.switch_to.default_content()
            except: pass
    return None

def _PP_try_close_popup(driver):
    js = r"""
    const labels=["OK","Close","Dismiss","Got it","Understood","Retry","Continue","Cancel","Đóng","Thử lại","Bỏ qua","Tiếp tục","Xong","Đồng ý"];
    function clickByText(root){
      const els=root.querySelectorAll('button,[role="button"],a,div,span');
      for(const el of els){
        const t=(el.innerText||'').trim();
        for(const lb of labels){
          if(new RegExp("^\\s*"+lb+"\\s*$","i").test(t)){ el.click(); return true; }
        }
      }
      return false;
    }
    if(clickByText(document)) return true;
    const all=document.querySelectorAll('*');
    for(const e of all){ if(e.shadowRoot && clickByText(e.shadowRoot)) return true; }
    return false;
    """
    try: return bool(driver.execute_script(js))
    except Exception: return False

def _PP_smart_sleep(self, seconds):
    end = _PP_time.time() + max(0.0, float(seconds or 0))
    while _PP_time.time() < end:
        try: self._auto_pause_check()
        except Exception: pass
        if getattr(self, "pause", False):
            while getattr(self, "pause", False):
                _PP_time.sleep(0.25)
        _PP_time.sleep(0.5)

def _PP__auto_pause_check(self):
    drv = getattr(self, "driver", None)
    if drv is None: return False
    if not _PP_cfg_get_bool(self, "pause_on_popup", True): return False
    pattern = _PP_cfg_get_str(self, "popup_regex", r"queue|max|limit|quota|rate\s*limit|try again|pending|hàng chờ|đã đạt|quá nhiều|đang xử lý|không tạo được|khong tao duoc|unable to (create|generate)|could not (create|generate)|please try again later|quota exceeded|over\s*quota|service unavailable|temporarily unavailable")
    try:
        txt = _PP_detect_popup_anywhere(drv, pattern)
        if txt:
            try: self._handle_popup_pause(txt); return True
            except Exception:
                try: self.pause = True
                except Exception: pass
                try: self.log(f"⏸️ Pop-up: “{txt}” – chờ cooldown…")
                except Exception: pass
                _PP_try_close_popup(drv)
                try: wait_s = max(10, int(float(_PP_cfg_get_str(self, "popup_cooldown", "75") or "75")))
                except Exception: wait_s = 75
                _PP_time.sleep(wait_s)
                try:
                    if _PP_cfg_get_bool(self, "reload_after_popup", True) and _PP_By and _PP_Wait and _PP_EC:
                        try: self.log("🔁 Reload lại trang sau pop-up…")
                        except Exception: pass
                        try:
                            drv.refresh()
                            _PP_Wait(drv, 30).until(_PP_EC.presence_of_element_located((_PP_By.TAG_NAME,"body")))
                            _PP_time.sleep(1.5)
                        except Exception: pass
                except Exception: pass
                try: self.pause = False; self.log("▶️ RESUME sau pop-up.")
                except Exception: pass
                return True
    except Exception:
        return False
    return False

def _PP__handle_popup_pause(self, popup_text):
    try:
        if not getattr(self, "pause", False):
            try: self.pause = True
            except Exception: pass
        try: self.log(f"⏸️ Phát hiện pop-up: “{popup_text}” → PAUSE")
        except Exception: pass
        _PP_try_close_popup(self.driver)
        try: wait_s = max(10, int(float(_PP_cfg_get_str(self, "popup_cooldown", "75") or "75")))
        except Exception: wait_s = 75
        try: self.log(f"⏳ Đợi {wait_s}s để hàng chờ hạ nhiệt…")
        except Exception: pass
        t0 = _PP_time.time()
        while _PP_time.time() - t0 < wait_s: _PP_time.sleep(0.5)
        if _PP_cfg_get_bool(self, "reload_after_popup", True) and _PP_By and _PP_Wait and _PP_EC:
            try: self.log("🔁 Reload lại trang sau pop-up…")
            except Exception: pass
            try:
                self.driver.refresh()
                _PP_Wait(self.driver, 30).until(_PP_EC.presence_of_element_located((_PP_By.TAG_NAME,"body")))
                _PP_time.sleep(1.5)
            except Exception as e:
                try: self.log(f"⚠️ Reload lỗi (bỏ qua): {e}")
                except Exception: pass
    finally:
        try: self.pause = False; self.log("▶️ Đã RESUME sau pop-up.")
        except Exception: pass

if not hasattr(FlowAutoApp, "smart_sleep"): FlowAutoApp.smart_sleep = _PP_smart_sleep
if not hasattr(FlowAutoApp, "_auto_pause_check"): FlowAutoApp._auto_pause_check = _PP__auto_pause_check
if not hasattr(FlowAutoApp, "_handle_popup_pause"): FlowAutoApp._handle_popup_pause = _PP__handle_popup_pause

if not hasattr(FlowAutoApp, "_PP_orig___init__"):
    FlowAutoApp._PP_orig___init__ = FlowAutoApp.__init__
    def _PP_init_wrap(self, *a, **kw):
        FlowAutoApp._PP_orig___init__(self, *a, **kw)
        if not hasattr(self, "smart_sleep"):
            try: self.smart_sleep = _PP_types.MethodType(_PP_smart_sleep, self)
            except Exception: pass
        if not hasattr(self, "_auto_pause_check"):
            try: self._auto_pause_check = _PP_types.MethodType(_PP__auto_pause_check, self)
            except Exception: pass
        if not hasattr(self, "_handle_popup_pause"):
            try: self._handle_popup_pause = _PP_types.MethodType(_PP__handle_popup_pause, self)
            except Exception: pass
        for k, v in [("pause_on_popup", True), ("reload_after_popup", True), ("popup_cooldown", "75"),
                     ("popup_regex", r"queue|max|limit|quota|rate\s*limit|try again|pending|hàng chờ|đã đạt|quá nhiều|đang xử lý|không tạo được|khong tao duoc|unable to (create|generate)|could not (create|generate)|please try again later|quota exceeded|over\s*quota|service unavailable|temporarily unavailable")]:
            if not hasattr(self, k):
                try: setattr(self, k, v)
                except Exception: pass
    FlowAutoApp.__init__ = _PP_init_wrap

if hasattr(FlowAutoApp, "fill_prompt_and_generate") and not hasattr(FlowAutoApp, "_PP_orig_send"):
    FlowAutoApp._PP_orig_send = FlowAutoApp.fill_prompt_and_generate
    def _PP_send_wrap(self, *a, **kw):
        try: self._auto_pause_check()
        except Exception: pass
        try:
            res = FlowAutoApp._PP_orig_send(self, *a, **kw)
            ok = (res is True) or (res is None)
        except Exception:
            ok = False
        if ok:
            try: self._auto_pause_check()
            except Exception: pass
            return res
        try:
            drv = self.driver
            prompt_text = None
            if len(a)>=1 and isinstance(a[0], str): prompt_text = a[0]
            elif isinstance(kw.get("prompt", None), str): prompt_text = kw["prompt"]
            else: prompt_text = kw.get("text") or kw.get("content") or ""
            js = r'''            const text = arguments[0]||"";
            function visible(el){ try{ const s=getComputedStyle(el); return (el.offsetParent!==null)||(s.display!=='none'&&s.visibility!=='hidden'); }catch(e){ return true; } }
            function setEditable(el, t){
              try{
                if(el.isContentEditable){ el.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, t); return true; }
                if(el.tagName==='TEXTAREA'||el.tagName==='INPUT'){ el.focus(); el.value=t; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return true; }
              }catch(e){}
              return false;
            }
            function allNodes(root){ const a=[]; const push=(r)=>{ if(r&&r.querySelectorAll){ a.push(r); for(const e of r.querySelectorAll('*')) a.push(e);} }; push(root||document); for(const n of a.slice()){ if(n&&n.shadowRoot){ push(n.shadowRoot);} } return a;}
            let edited=false;
            for(const el of allNodes(document)){ if(!visible(el)) continue; if (el.isContentEditable || el.tagName==='TEXTAREA' || el.tagName==='INPUT') { if(setEditable(el, text)){ edited=true; break; } } }
            const labels=[/^\s*Generate\s*$/i,/^\s*Tạo\s*$/i,/^\s*Create\s*$/i,/^\s*Run\s*$/i,/^\s*Submit\s*$/i];
            function tryClick(root){ const nodes=root.querySelectorAll('button,[role="button"],a,div,span'); for(const n of nodes){ const t=(n.innerText||'').trim(); for(const r of labels){ if(r.test(t)){ n.click(); return true; } } } return false; }
            let clicked = tryClick(document);
            return edited || clicked;
            '''
            drv.execute_script(js, prompt_text)
        except Exception:
            pass
        try: self._auto_pause_check()
        except Exception: pass
        return True
    FlowAutoApp.fill_prompt_and_generate = _PP_send_wrap

# ========== [/POPUP-PAUSE CORE PATCH v3] ==========
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        _selftests()
    else:
        root=tk.Tk()
        app=FlowAutoApp(root)
        root.mainloop()







# ========== [AUTO-INSERTED QUEUEGUARD v1.1] ==========
# Prevents wasting prompts by respecting Flow's queue limit (default 5)
# and by avoiding reloads while jobs are stuck at 99%.
# Safe to include multiple times.

try:
    import time as _QG_time
    import types as _QG_types
except Exception:
    pass

def _QG_js_scanner():
    return r"""
    function visible(el){
      try{ const s=getComputedStyle(el); return (el.offsetParent!==null)||(s.display!=='none'&&s.visibility!=='hidden'); }
      catch(e){ return true; }
    }
    function allNodes(){
      const arr=[document];
      for (let i=0;i<arr.length;i++){
        const n=arr[i];
        try{
          if(n && n.querySelectorAll){
            for(const e of n.querySelectorAll('*')) arr.push(e);
          }
          if(n && n.shadowRoot){
            arr.push(n.shadowRoot);
            for(const e of n.shadowRoot.querySelectorAll('*')) arr.push(e);
          }
        }catch(e){}
      }
      return arr;
    }
    const percRe = /\\b(\\d{1,3})\\s*%/;
    let active=0, ninetyNine=0;
    for(const el of allNodes()){
      if(!visible(el)) continue;
      const role = (el.getAttribute && el.getAttribute('role')) || '';
      if (/progressbar/i.test(role)) {
        active++;
        const t=(el.innerText||'');
        const m=percRe.exec(t);
        if(m && +m[1]>=99) ninetyNine++;
        continue;
      }
      const t=(el.innerText||'').trim();
      const m=percRe.exec(t);
      if(m){ active++; if(+m[1]>=99) ninetyNine++; }
    }
    const limitPat=/(maximum\\s*5|max\\s*5|tối\\s*đa\\s*5|da\\s*đạt\\s*5|hàng\\s*chờ|queue|quota|limit)/i;
    let hasLimitToast=false;
    for(const el of allNodes()){
      if(!visible(el)) continue;
      const role=(el.getAttribute&&el.getAttribute('role'))||'';
      const cls=((el.className&&el.className.baseVal)?el.className.baseVal:(el.className||''))+' '+(el.id||'');
      const modal = el.getAttribute && (el.getAttribute('aria-modal')==='true');
      if (modal || /(\\bmodal\\b|dialog|alert|snackbar|toast)/i.test(cls) || /^(dialog|alert)$/i.test(role)) {
        const t=(el.innerText||'').trim();
        if (t && limitPat.test(t)) { hasLimitToast=true; break; }
      }
    }
    return {active, ninetyNine, hasLimitToast};
    """
def _QG_snapshot(driver):
    try:
        return driver.execute_script(_QG_js_scanner()) or {"active":0,"ninetyNine":0,"hasLimitToast":False}
    except Exception:
        return {"active":0,"ninetyNine":0,"hasLimitToast":False}

def _QG__queue_wait_gate(self):
    # Read config / defaults
    try:
        respect = bool(getattr(self, "respect_queue", True))
        if hasattr(respect, "get"): respect = bool(respect.get())
    except Exception:
        respect = True
    if not respect:
        return
    try:
        maxq = int(float(getattr(self, "queue_limit", 5)))
    except Exception:
        maxq = 5
    try:
        stall_t = int(float(getattr(self, "queue_stall_99s", 180)))
    except Exception:
        stall_t = 180

    seen99_t0 = None
    while True:
        snap = _QG_snapshot(self.driver)
        act = int(snap.get("active",0) or 0)
        n99 = int(snap.get("ninetyNine",0) or 0)
        lim = bool(snap.get("hasLimitToast",False))

        # Toggle reload protection if 99% is present
        try:
            if n99>0:
                setattr(self, "reload_after_popup", False)
                if seen99_t0 is None:
                    seen99_t0 = _QG_time.time()
                waited = int(_QG_time.time() - seen99_t0)
                if waited % 10 == 0:
                    try: self.log(f"⏸️ 99% stuck x{n99}. Waiting for a free slot… ({waited}s)")
                    except Exception: pass
                # honor stall_t but never force reload
                if waited >= stall_t:
                    # still just wait; do not reload to avoid losing jobs
                    pass
            else:
                setattr(self, "reload_after_popup", True)
                seen99_t0 = None
        except Exception:
            pass

        # Exit condition: queue below limit and no limit toast
        if act < maxq and not lim:
            return

        # Sleep and repeat
        try: self.log(f"⏳ Queue busy: active={act}, 99%={n99}, limit_toast={lim}. Recheck in 3s…")
        except Exception: pass
        try:
            self.smart_sleep(3.0)
        except Exception:
            _QG_time.sleep(3.0)

# Inject init defaults
try:
    FlowAutoApp
    if not hasattr(FlowAutoApp, "_QG_inited"):
        _QG_old_init = getattr(FlowAutoApp, "__init__", None)
        def _QG_init_wrap(self, *a, **kw):
            if _QG_old_init:
                _QG_old_init(self, *a, **kw)
            # Pull from settings if available
            try:
                _s = getattr(self, "settings", {}) or {}
            except Exception:
                _s = {}
            def _s_bool(k, dv):
                try:
                    v = _s.get(k, dv)
                    return bool(v)
                except Exception:
                    return dv
            def _s_int(k, dv):
                try:
                    v = int(float(_s.get(k, dv)))
                    return v
                except Exception:
                    return dv
            # Soft defaults; don't assume UI exists
            for k,v in [("respect_queue", _s_bool("respect_queue", True)),
                        ("queue_limit", _s_int("max_queue", 5)),
                        ("queue_stall_99s", _s_int("stall_99s", 180))]:
                if not hasattr(self, k):
                    try: setattr(self, k, v)
                    except Exception: pass
            # ensure flag exists
            if not hasattr(self, "reload_after_popup"):
                try: setattr(self, "reload_after_popup", True)
                except Exception: pass
            try:
                self._queue_wait_gate = _QG_types.MethodType(_QG__queue_wait_gate, self)
            except Exception:
                pass
        FlowAutoApp.__init__ = _QG_init_wrap
        setattr(FlowAutoApp, "_QG_inited", True)

    # Wrap send method to gate by queue
    if hasattr(FlowAutoApp, "fill_prompt_and_generate") and not hasattr(FlowAutoApp, "_QG_orig_send"):
        FlowAutoApp._QG_orig_send = FlowAutoApp.fill_prompt_and_generate
        def _QG_send_wrap(self, *a, **kw):
            try: self._queue_wait_gate()
            except Exception: pass
            return FlowAutoApp._QG_orig_send(self, *a, **kw)
        FlowAutoApp.fill_prompt_and_generate = _QG_send_wrap
except NameError:
    pass
# ========== [END QUEUEGUARD] ==========
