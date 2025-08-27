# -*- coding: utf-8 -*-
"""
HBYS LCD + TTS Kombine Asistan v13 (Qt + pywebview)

- 2. değişimde konuşur ve ilk numara/saat değişmeden konuşmaz.
- RANDEVUSUZ: sadece numara okur → “76 Numara Lütfen Muayeneye Giriniz.”
- RANDEVULU: saat (HH:MM) okur → “10:30 randevulu hasta lütfen muayeneye giriniz.”
- Aynı anahtar (numara/saat) tekrar tekrar okutulmaz.
- QtWebEngine için autoplay serbest; TTS: tr-TR + Emel; web başlamazsa TR Windows TTS’e düşer.
"""

import os
# Sesin jest istememesini sağlar
os.environ.setdefault('PYWEBVIEW_GUI', 'qt')
os.environ.setdefault('QT_API', 'pyside6')
os.environ.setdefault('QTWEBENGINE_CHROMIUM_FLAGS', '--autoplay-policy=no-user-gesture-required')

import json, re, time, threading
from threading import Timer
import webview

# ========================= K O N F İG =========================
BASE_PREFIX = "http://hbys.aydinism.gov.tr/hbys-web/desktop/lib/lcd/indexSB.html"

HBYS_DEFAULT_URL = (
    "http://hbys.aydinism.gov.tr/hbys-web/desktop/lib/lcd/indexSB.html?data="
    "{%22data%22:{%22ustPanelArkaPlan%22:%22@FFCC99%22,%22altPanelGorulsun%22:1,"
    "%22doktorAdiSoyadi%22:%22Uzm.%20Dr.%20GAMZE%20T%C3%9CTEN%22,%22sabitYaziGorunsun%22:1,"
    "%22birimAdiPunto%22:25,%22mevcutHasta%22:{%22birimSevkId%22:5500044328422,%22randevu%22:0,"
    "%22adiSoyadi%22:%22DE****%20ER***%20HA***%22,%22siraNo%22:284},%22yaziTipi%22:%22Calibri%22,"
    "%22birimId%22:1404,%22hastaneAdiRenk%22:%22@FF0000%22,%22birimAdi%22:%22Nazilli%20DH%20Acil%20Servis%22,"
    "%22tema%22:3,%22siradakiHastaRenk%22:%22@CCFFFF%22,%22organizasyonAdi%22:%22Nazilli%20Devlet%20Hastanesi%22,"
    "%22hastaneAdiGorulsun%22:1,%22hastaSiraListInfo%22:[],%22kayanYazi%22:%22Nazilli%20DH%20Acil%20Servis%22,"
    "%22kayanYaziPunto%22:50,%22siradakiHastaArkaPlan%22:%22@993366%22,%22hastaListesiArkaPlan%22:%22@C0C0C0%22,"
    "%22doktorUzmanlik%22:%22Acil%20T%C4%B1p%22,%22sabitYazi%22:%22Nazilli%20DH%20Acil%20Servis%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%22,"
    "%22kayanYaziRenk%22:%22@FF0000%22}}"
)

TTS_URL = "https://www.text-to-speech.online/"
TTS_MODE = 'web+fallback'          # 'web' | 'fallback' | 'web+fallback'
TTS_BRIEFLY_SHOW_MS = 700

ENABLE_CHROME_MIRROR = True
CHROME_POLL_SEC = 0.8
MAX_SCAN_DEPTH = 6
DEBUG_CHROME_SCAN = False

AUTO_START = False
START_SPEAK_AFTER_CHANGES = 2       # İSTEK ÜZERİNE 2

CONTROL_W, CONTROL_H = 800, 480
HIDDEN_W, HIDDEN_H = 1, 1

SIRA_REGEX = re.compile(r"\b(\d{1,4})\b")
TIME_REGEX = re.compile(r"^\s*\d{1,2}:\d{2}\s*$", re.ASCII)   # HH:MM

FALLBACK_TR_PREFER_BY_NAME = ['emel', 'seda', 'elif', 'ahmet', 'tolga']
FALLBACK_TR_HINTS = ['tr-tr', 'turkish', 'türk', 'turk', 'turkce', 'türkçe']

# ========================= JS BLOKLARI =========================
OBSERVER_JS = r"""
(function(){
  function val(sel){ const el=document.querySelector(sel); return el?(el.textContent||'').trim():''; }
  function cell(r,c){
    try{ const row=document.querySelectorAll('#hastalar tbody tr')[r];
      if(!row) return '';
      const td=row.querySelectorAll('td')[c];
      return td?(td.textContent||'').trim():'';
    }catch(e){ return ''; }
  }
  function read(){ return {
    siraSpan: val('.sira_no'),
    isimSpan: val('.hasta_adi'),
    oncelikSpan: val('.hasta_oncelik'),
    saatCell: cell(0,0),
    siraCell: cell(0,1),
    isimCell: cell(0,2),
    oncCell:  cell(0,3)
  }; }
  let last='';
  function snapshot(force){
    const f=read(), sig=JSON.stringify(f);
    if(!force && sig===last) return; last=sig;
    const payload={href:location.href, ts:Date.now(), fields:f};
    try{ window.pywebview && window.pywebview.api && window.pywebview.api.on_lcd_change(payload); }catch(e){}
  }
  ['.sira_no','.hasta_adi','.hasta_oncelik','#hastalar tbody'].forEach(sel=>{
    (function attach(){
      const el=document.querySelector(sel);
      if(!el){ setTimeout(attach,500); return; }
      new MutationObserver(()=>snapshot(false)).observe(el,{childList:true,subtree:true,characterData:true});
    })();
  });
  snapshot(true);
  let href=location.href;
  setInterval(()=>{ if(location.href!==href){ href=location.href; snapshot(true);} },700);
})();
"""

CLOSE_ADS_JS = r"""
(function(){
  function hide(n){ if(!n||!n.style) return; n.style.setProperty('display','none','important'); n.style.setProperty('visibility','hidden','important'); n.style.setProperty('opacity','0','important'); }
  const sel=['[id*="ad"]','[class*="ad"]','[id*="ads"]','[class*="ads"]','[class*="overlay"]','[id*="overlay"]','[class*="modal"]','[id*="modal"]','[class*="popup"]','[id*="popup"]','[class*="banner"]','[id*="banner"]','iframe'];
  document.querySelectorAll(sel.join(',')).forEach(el=>{ try{ hide(el);}catch(e){} });
  const btns=[...document.querySelectorAll('button,[role="button"],.close,[class*="close"],[aria-label*="close"]')];
  const closeTexts=['×','x','✕','close','kapat','ok','skip','i agree','accept'];
  btns.forEach(b=>{ const t=(b.innerText||b.getAttribute('aria-label')||'').toLowerCase().trim(); if(closeTexts.some(c=>t.includes(c))){ try{ b.click(); }catch(e){} } });
  return 'overlay temiz';
})();
"""

AUDIO_HOOK_JS = r"""
(function(){
  if (window.__audioHookInstalled) return 'hook-ok';
  window.__audioHookInstalled = true;
  window.__audioStarted = 0;
  function mark(){ window.__audioStarted = Date.now(); }
  try{ document.addEventListener('play', mark, true); }catch(e){}
  try{
    const AC = window.AudioContext || window.webkitAudioContext;
    if(AC && AC.prototype){
      const p = AC.prototype, _old = p.createBufferSource;
      if(typeof _old==='function'){
        p.createBufferSource = function(){
          const node = _old.call(this);
          const _start = node.start;
          node.start = function(){ try{ mark(); }catch(e){}; return _start.apply(this, arguments); };
          return node;
        };
      }
    }
  }catch(e){}
  try{
    const HP = window.HTMLMediaElement && window.HTMLMediaElement.prototype;
    if(HP && typeof HP.play==='function'){
      const _p = HP.play;
      HP.play = function(){
        const r=_p.apply(this, arguments);
        try{ mark(); }catch(e){}
        if(r && typeof r.then==='function'){ r.then(()=>{try{mark()}catch(e){}}).catch(()=>{}); }
        return r;
      }
    }
  }catch(e){}
  return 'hook-installed';
})();
"""

CHECK_AUDIO_PLAYING_JS = r"""
(function(){
  try{
    if (typeof window.__audioStarted==='number' && (Date.now()-window.__audioStarted)<12000) return true;
    if (window.speechSynthesis && window.speechSynthesis.speaking) return true;
    try{
      const stopBtn = document.getElementById('stop') || document.querySelector('button#stop,[id*="stop"]');
      if (stopBtn){
        const cs = getComputedStyle(stopBtn);
        if (cs && cs.display!=='none' && !stopBtn.disabled) return true;
      }
    }catch(e){}
    const list = Array.from(document.querySelectorAll('audio'));
    for (const a of list){ if (a && !a.paused && !a.ended && a.currentTime>0) return true; }
  }catch(e){}
  return false;
})();
"""

STOP_AUDIO_JS = r"""
(function(){
  try{ if(window.speechSynthesis && window.speechSynthesis.cancel){ window.speechSynthesis.cancel(); } }catch(e){}
  try{ document.querySelectorAll('audio').forEach(a=>{ try{ a.pause(); a.currentTime=0; }catch(e){} }); }catch(e){}
  const ids=['stop','btn-stop','quick-stop'];
  for(const id of ids){ const b=document.getElementById(id); if(b){ try{ b.click(); }catch(e){} } }
  const labels=['stop','dur','durdur','bitir'];
  const cands=[...document.querySelectorAll('button,[role="button"],input[type=button],input[type=submit]')];
  for(const b of cands){
    const t=((b.innerText||b.value||'')+'').toLowerCase().trim();
    if(labels.some(x=>t.includes(x))){ try{ b.click(); }catch(e){} }
  }
  return 'stopped';
})();
"""

PRIME_AUDIO_JS = r"""
(async function(){
  try{
    const a = new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=');
    a.volume=0.0;
    await a.play();
    setTimeout(()=>{ try{ a.pause(); a.currentTime=0; }catch(e){} }, 250);
    return 'primed';
  }catch(e){ return 'err:'+e; }
})();
"""

SET_LOCALE_TR_JS = r"""
(function(){
  const sel=document.getElementById('locale')||document.querySelector('select#locale');
  if(!sel) return 'locale select yok';
  const wanted='tr-TR';
  const has=[...sel.options].some(o=>(o.value||'')===wanted);
  if(!has) return 'tr-TR yok';
  if(sel.value!==wanted){
    sel.value=wanted;
    sel.dispatchEvent(new Event('input',{bubbles:true}));
    sel.dispatchEvent(new Event('change',{bubbles:true}));
  }
  return 'tr-TR seçildi';
})();
"""

TRY_PICK_EMEL_STRICT_JS = r"""
(function(){
  const sel=document.getElementById('voice')||document.querySelector('select#voice');
  if(!sel) return 'VOICE_YOK';
  for(let i=0;i<sel.options.length;i++){
    const o=sel.options[i], val=(o.value||'').toLowerCase(), tx=(o.textContent||'').toLowerCase();
    if(val==='tr-tr-emelneural' || tx.includes('emel')){
      sel.selectedIndex=i;
      sel.dispatchEvent(new Event('input',{bubbles:true}));
      sel.dispatchEvent(new Event('change',{bubbles:true}));
      return 'OK_EMEL';
    }
  }
  return 'NOTYET';
})();
"""

PICK_AHMET_IF_ANY_JS = r"""
(function(){
  const sel=document.getElementById('voice')||document.querySelector('select#voice');
  if(!sel) return 'VOICE_YOK';
  for(let i=0;i<sel.options.length;i++){
    const o=sel.options[i], val=(o.value||'').toLowerCase(), tx=(o.textContent||'').toLowerCase();
    if(val==='tr-tr-ahmetneural' || tx.includes('ahmet')){
      sel.selectedIndex=i;
      sel.dispatchEvent(new Event('input',{bubbles:true}));
      sel.dispatchEvent(new Event('change',{bubbles:true}));
      return 'OK_AHMET';
    }
  }
  return 'AHMET_YOK';
})();
"""

SET_TEXT_JS_TMPL = r"""
(function(text){
  let target=null, maxA=-1;
  const cands=document.querySelectorAll('textarea,[contenteditable="true"]');
  cands.forEach(t=>{ const a=(t.offsetWidth||0)*(t.offsetHeight||0); if(a>maxA){maxA=a; target=t;} });
  if(!target) target=document.querySelector('textarea');
  if(!target) return 'textarea yok';
  if(target.isContentEditable){ target.focus(); target.innerText=text; }
  else { target.focus(); target.value=text; target.dispatchEvent(new Event('input',{bubbles:true})); target.dispatchEvent(new Event('change',{bubbles:true})); }
  return 'Metin yazıldı';
})(%s);
"""

CLICK_PLAY_JS = r"""
(function(){
  const texts=['play all','play','oyna','speak','listen','başlat'];
  const cands=[...document.querySelectorAll('button,[role="button"],input[type=button],input[type=submit]')];
  for(const b of cands){
    const t=((b.innerText||b.value||'')+'').toLowerCase().trim();
    if(texts.some(x=>t.includes(x))){ b.click(); return 'play-ok('+t+')'; }
  }
  return 'play-yok';
})();
"""

CONTROL_HTML = r"""
<!doctype html><html><head><meta charset="utf-8"/><title>HBYS + TTS Asistan</title>
<style>
 body{font-family:Segoe UI,Arial,sans-serif;margin:16px}
 .row{margin-bottom:12px} button{padding:9px 14px;margin-right:10px}
 #status{margin-top:6px;color:#034} #log{width:100%;height:230px;font-family:Consolas,monospace;font-size:12px}
 .footer{margin-top:10px;padding-top:8px;border-top:1px solid #ddd;text-align:center;font-weight:600}
 .sig{font-size:14px;color:#333}
 .sig strong{color:#111}
</style></head><body>
<h3 style="margin-top:0">HBYS LCD → TTS Asistan</h3>
<div class="row">
  <button id="btnStart">Başlat</button>
  <button id="btnStop">Kapat</button>
</div>
<div id="status">Durum: Hazır</div>
<textarea id="log" readonly></textarea>
<div class="footer"><div class="sig">Kodlayan <strong>Mustafa GÜNEŞDOĞDU</strong> — Nazilli Devlet Hastanesi Bilgi İşlem Birimi — 2025</div></div>
<script>
 const logEl=document.getElementById('log'), statusEl=document.getElementById('status');
 function appendLog(line){
   const n=new Date(), hh=String(n.getHours()).padStart(2,'0'), mm=String(n.getMinutes()).padStart(2,'0'), ss=String(n.getSeconds()).padStart(2,'0');
   logEl.value+=`[${hh}:${mm}:${ss}] `+line+"\n"; logEl.scrollTop=logEl.scrollHeight;
 }
 function setStatus(s){ statusEl.textContent="Durum: "+s; }
 document.getElementById('btnStart').addEventListener('click', async ()=>{
   try{ const r=await window.pywebview.api.start_all(); setStatus('Çalışıyor'); appendLog(r); }catch(e){ appendLog("[!] Hata: "+e); }
 });
 document.getElementById('btnStop').addEventListener('click', async ()=>{
   try{ const r=await window.pywebview.api.stop_all(); setStatus('Durduruldu'); appendLog(r); }catch(e){ appendLog("[!] Hata: "+e); }
 });
 window._log=appendLog; window._status=setStatus;
</script></body></html>
"""

# ========================= B R I D G E =========================
class Bridge:
    def __init__(self):
        self.ctrl = None
        self.lcd_win = None
        self.lcd_last_fields_sig = None

        self.chrome_thread = None
        self.chrome_stop = threading.Event()
        self._uia_ready = None

        self.tts_win = None
        self.tts_ready = False
        self.tts_voice_ready = False
        self.web_spoken_once = False

        self.changes_seen = 0
        self.speak_armed = False
        self.initial_number = None   # ilk token (numara veya saat)

        self.last_number = None      # son okunan token (numara veya saat)
        self.last_announce_ts = 0.0

        self._current_phrase = None
        self._current_attempts = 0
        self._phrase_retry_limit = 10
        self._phrase_started_ts = 0.0

        self._fallback_init_done = False
        self._fallback_ok = False
        self._fallback_tr_available = False
        self._tts_engine = None

        self._started_logged = False

    # ---------- LOG / STATUS ----------
    def _log(self, msg):
        try:
            if self.ctrl:
                self.ctrl.evaluate_js(f"window._log({json.dumps(msg)});")
        except:
            pass
    def _status(self, s):
        try:
            if self.ctrl:
                self.ctrl.evaluate_js(f"window._status({json.dumps(s)});")
        except:
            pass

    # ===================== LCD =====================
    def _ensure_lcd(self):
        if self.lcd_win: return
        self.lcd_win = webview.create_window(
            title='LCD Watcher (Hidden)',
            url='about:blank',
            width=HIDDEN_W, height=HIDDEN_H,
            hidden=True, frameless=True, confirm_close=False,
            js_api=self
        )
        def on_loaded():
            try:
                self.lcd_win.evaluate_js(OBSERVER_JS)
            except Exception as e:
                self._log(f"[!] LCD JS enjekte hata: {e}")
        self.lcd_win.events.loaded += on_loaded

    def start_lcd(self, url):
        self._ensure_lcd()
        try:
            self.lcd_win.load_url(url)
            self._log("[i] LCD izleme başladı.")
        except Exception as e:
            self._log(f"[!] LCD yüklenemedi: {e}")

    def stop_lcd(self):
        if self.lcd_win:
            try: self.lcd_win.load_url('about:blank')
            except: pass
        self.lcd_last_fields_sig = None
        self._log("[i] LCD izleme durdu.]")

    def on_lcd_change(self, payload):
        try:
            if isinstance(payload, str): payload = json.loads(payload)
        except: return True

        href = payload.get("href","")
        if not href.startswith(BASE_PREFIX): return True

        fields = payload.get("fields", {}) if isinstance(payload, dict) else {}
        fields_sig = json.dumps([
            fields.get("siraSpan",""), fields.get("isimSpan",""),
            fields.get("oncelikSpan",""), fields.get("saatCell",""),
            fields.get("siraCell",""), fields.get("isimCell",""),
            fields.get("oncCell","")
        ], ensure_ascii=False)

        if fields_sig == self.lcd_last_fields_sig:
            return True
        self.lcd_last_fields_sig = fields_sig

        # --- Randevulu mu? Saat mi? Numara mı? ---
        sira_text = (fields.get("siraSpan") or fields.get("siraCell") or "").strip()
        saat_text = (fields.get("saatCell") or "").strip()
        onc_text  = (fields.get("oncelikSpan") or fields.get("oncCell") or "").lower().strip()

        is_appt = False
        token = None

        # Saat görünüyorsa (HH:MM)
        if sira_text and TIME_REGEX.match(sira_text):
            is_appt = True
            token = sira_text
        elif saat_text and TIME_REGEX.match(saat_text):
            is_appt = True
            token = saat_text

        # Oncelik alanında "randevu" yazıyorsa sinyal say
        if ('randevu' in onc_text or 'mhrs' in onc_text):
            is_appt = True
            # saat yoksa yine de sira_text saat gibi gelmiş olabilir
            if not token and (saat_text and TIME_REGEX.match(saat_text)):
                token = saat_text

        # Randevusuz (sayı)
        if not is_appt:
            m = SIRA_REGEX.search(sira_text)
            if m:
                token = m.group(1)

        # Log
        if is_appt and token:
            self._log(f"LCD değişti → SAAT={token}")
        else:
            self._log(f"LCD değişti → NO={token or '?'}")

        # Sessiz başlatma sayacı
        self.changes_seen += 1
        if self.initial_number is None and token:
            self.initial_number = token

        if not self.speak_armed:
            remaining = START_SPEAK_AFTER_CHANGES - self.changes_seen
            if remaining > 0:
                self._log(f"[i] Sessiz mod: İlk {START_SPEAK_AFTER_CHANGES} değişiklik bekleniyor ({remaining} kaldı).")
                return True
            # İlk token ile aynıysa konuşma
            if not token or (self.initial_number is not None and token == self.initial_number):
                return True
            self.speak_armed = True
            self._log("[i] Konuşma ARM edildi.")

        if token:
            self._maybe_enqueue_number(token, is_appt)  # ses kısmına dokunmadan sadece cümle seçimi
        return True

    # ===================== Chrome Mirror =====================
    ADDRESS_NAMES = [
        'Address and search bar','Search or enter address','Address and Search bar',
        'Adres ve arama çubuğu','Arama yapın veya web adresini yazın',
        'Ara veya web adresini yazın','Adres çubuğu','Adres'
    ]
    EDIT_TYPES = {'EditControl','Edit','ComboBox','ComboBoxControl','DocumentControl','Text','Custom','Pane','ToolBar'}

    def _ensure_uia(self):
        if self._uia_ready is None:
            try:
                global auto
                import uiautomation as auto
                self._uia_ready = True
            except Exception:
                self._uia_ready = False
                self._log("[!] uiautomation yok (pip install uiautomation). Chrome aynası sınırlı kalır.")
        return self._uia_ready

    def chrome_watch_start(self):
        if not ENABLE_CHROME_MIRROR: return False
        if not self._ensure_uia(): return False
        if self.chrome_thread and self.chrome_thread.is_alive(): return True
        self.chrome_stop.clear()
        self.chrome_thread = threading.Thread(target=self._chrome_loop, daemon=True)
        self.chrome_thread.start()
        self._log("[i] Chrome izleme AKTİF.")
        return True

    def chrome_watch_stop(self):
        self.chrome_stop.set()
        self._log("[i] Chrome izleme PASİF.")
        return True

    def _get_chrome_lcd_url(self):
        try:
            root = auto.GetRootControl()
            for w in root.GetChildren():
                if 'Chrome_WidgetWin' not in w.ClassName: continue
                for nm in self.ADDRESS_NAMES:
                    try:
                        edit = w.EditControl(Name=nm, searchDepth=MAX_SCAN_DEPTH)
                        if edit and edit.Exists(0,0):
                            try: val = edit.GetValuePattern().Value
                            except Exception:
                                try: val = edit.GetLegacyIAccessiblePattern().Value
                                except Exception: val = ''
                            if val and (BASE_PREFIX in val or val.startswith(BASE_PREFIX)):
                                if DEBUG_CHROME_SCAN: self._log(f"[debug] Adres yakalandı ({nm}) → {val}")
                                return val
                    except: pass
                q=[(w,0)]
                while q:
                    node,d = q.pop(0)
                    if d>MAX_SCAN_DEPTH: continue
                    try:
                        ctype = getattr(node,'ControlTypeName','')
                        if ctype in self.EDIT_TYPES:
                            cand=''
                            try: cand=node.GetValuePattern().Value
                            except Exception:
                                try: cand=node.GetLegacyIAccessiblePattern().Value
                                except Exception:
                                    try: cand=node.Name or ''
                                    except Exception: cand=''
                            if cand and 'http' in cand:
                                url=cand.strip().replace('\r','').replace('\n','')
                                if BASE_PREFIX in url or url.startswith(BASE_PREFIX):
                                    if DEBUG_CHROME_SCAN: self._log(f"[debug] Derin tarama ({ctype}) → {url}")
                                    return url
                        for ch in node.GetChildren(): q.append((ch,d+1))
                    except: continue
        except: pass
        return None

    def _chrome_loop(self):
        last=None
        while not self.chrome_stop.is_set():
            url=self._get_chrome_lcd_url()
            if url and url!=last:
                last=url
                try:
                    if self.lcd_win: self.lcd_win.load_url(url)
                    self._log(f"[i] Chrome URL değişti → mirror edildi.")
                except Exception as e:
                    self._log(f"[!] LCD navigate hata: {e}")
            time.sleep(CHROME_POLL_SEC)

    # ===================== TTS =====================
    def _ensure_tts(self):
        if self.tts_win: return
        self.tts_win = webview.create_window(
            title='TTS Engine',
            url='about:blank',
            width=360, height=240,
            hidden=True, frameless=False, confirm_close=False
        )
        def on_loaded():
            try:
                self.tts_win.evaluate_js(AUDIO_HOOK_JS)
                def stop_burst():
                    for _ in range(8):
                        try:
                            self.tts_win.evaluate_js(CLOSE_ADS_JS)
                            self.tts_win.evaluate_js(STOP_AUDIO_JS)
                        except: pass
                        time.sleep(0.2)
                threading.Thread(target=stop_burst, daemon=True).start()
            except: pass

            threading.Thread(target=self._human_unlock_tts, daemon=True).start()

            def _late_voice():
                self.tts_voice_ready=False
                # Dil tr-TR
                for _ in range(15):
                    try:
                        r=self.tts_win.evaluate_js(SET_LOCALE_TR_JS)
                        if isinstance(r,str) and 'seçildi' in r.lower(): break
                    except: pass
                    time.sleep(0.2)
                # Emel (10 sn)
                ok=''; deadline=time.time()+10.0
                while time.time()<deadline:
                    try:
                        r=self.tts_win.evaluate_js(TRY_PICK_EMEL_STRICT_JS)
                        if r=='OK_EMEL': ok='OK Emel'; break
                    except: pass
                    time.sleep(0.25)
                # Ahmet fallback
                if not ok:
                    try:
                        rr=self.tts_win.evaluate_js(PICK_AHMET_IF_ANY_JS)
                        if rr=='OK_AHMET': ok='OK Ahmet'
                    except: pass

                # Sessiz prime
                try: self.tts_win.evaluate_js(PRIME_AUDIO_JS)
                except: pass

                self.tts_ready=True
                self.tts_voice_ready = bool(ok)
                self._log("[i] TTS hazır." + (f" ({ok})" if ok else " (ses seçilemedi)"))
                try: self.tts_win.evaluate_js(STOP_AUDIO_JS)
                except: pass

            threading.Thread(target=_late_voice, daemon=True).start()
        self.tts_win.events.loaded += on_loaded

    def _human_unlock_tts(self):
        try:
            self.tts_win.show(); time.sleep(TTS_BRIEFLY_SHOW_MS/1000.0); self.tts_win.hide()
        except: pass

    # ===================== KONUŞMA =====================
    def _maybe_enqueue_number(self, token, is_appt=False):
        """
        token: '76' veya '10:30'
        is_appt: True ise randevulu metni, değilse numara metni okunur.
        """
        now = time.time()
        if token == self.last_number and (now - self.last_announce_ts) < 10.0:
            return

        if is_appt:
            phrase = f"{token} randevulu hasta lütfen muayeneye giriniz."
        else:
            phrase = f"{token} Numara Lütfen Muayeneye Giriniz."

        self._log(f"TTS → {phrase}")
        self._play_phrase(phrase)
        self.last_number = token
        self.last_announce_ts = now

    def _play_phrase(self, phrase):
        self._current_phrase = phrase
        self._current_attempts = 0
        self._phrase_started_ts = time.time()

        if TTS_MODE in ('web','web+fallback'):
            if not (self.tts_ready and self.tts_voice_ready):
                Timer(0.5, lambda: self._play_phrase(phrase)).start()
                return
            try:
                try: self.tts_win.evaluate_js(STOP_AUDIO_JS)
                except: pass
                js = SET_TEXT_JS_TMPL % json.dumps(phrase, ensure_ascii=False)
                self.tts_win.evaluate_js(js)
                self.tts_win.evaluate_js(CLICK_PLAY_JS)
            except Exception as e:
                self._log(f"[!] Web TTS başlatma hata: {e}")
            self._watch_started()
            return

        self._fallback_say(phrase)

    def _watch_started(self):
        try:
            playing = self.tts_win.evaluate_js(CHECK_AUDIO_PLAYING_JS)
        except Exception:
            playing = False

        if playing:
            self.web_spoken_once = True
            return

        self._current_attempts += 1
        if self._current_attempts < self._phrase_retry_limit:
            try: self.tts_win.evaluate_js(CLICK_PLAY_JS)
            except: pass
            Timer(0.9, self._watch_started).start()
        else:
            self._log("[i] Web TTS henüz başlamadı, yeniden deneme bitti; fallback denenecek.")
            if TTS_MODE in ('web+fallback','fallback'):
                self._fallback_say(self._current_phrase)

    # ===================== FALLBACK (Windows TTS) =====================
    def _ensure_fallback(self):
        if self._fallback_init_done: return self._fallback_ok
        self._fallback_init_done = True
        try:
            import pyttsx3
            eng = pyttsx3.init()
            tr_id = None
            for v in eng.getProperty('voices'):
                name = (getattr(v,'name','') or '').lower()
                lang = ''
                try:
                    langb = getattr(v,'languages',[]) or []
                    if langb: lang = ''.join([str(x) for x in langb]).lower()
                except: pass
                if any(h in name for h in FALLBACK_TR_PREFER_BY_NAME) or any(h in lang for h in FALLBACK_TR_HINTS):
                    tr_id = v.id; break
            if tr_id is None:
                for v in eng.getProperty('voices'):
                    idl=(getattr(v,'id','') or '').lower(); nm=(getattr(v,'name','') or '').lower()
                    if 'tr' in idl or 'turk' in idl or 'tr-tr' in idl or 'türk' in nm: tr_id=v.id; break
            if tr_id:
                eng.setProperty('voice', tr_id)
                self._tts_engine = eng
                self._fallback_tr_available = True
                self._fallback_ok = True
                self._log("[i] Windows TTS hazır (Türkçe ses).")
            else:
                self._fallback_tr_available = False
                self._fallback_ok = False
                self._log("[i] Windows TTS hazır DEĞİL (TR sesi yok).")
        except Exception as e:
            self._fallback_ok = False
            self._log(f"[!] Windows TTS açılamadı: {e}")
        return self._fallback_ok

    def _fallback_say(self, phrase):
        if not self._ensure_fallback() or not self._fallback_tr_available:
            self._log("[i] Fallback atlandı (TR Windows sesi yok).")
            return
        try:
            self._log(f"[→] Windows TTS: {phrase}")
            self._tts_engine.say(phrase)
            self._tts_engine.runAndWait()
        except Exception as e:
            self._log(f"[!] Windows TTS hata: {e}")

    # ===================== KAMU API =====================
    def start_all(self):
        self.lcd_last_fields_sig = None
        self.changes_seen = 0
        self.speak_armed = False
        self.initial_number = None
        self.last_number = None
        self.last_announce_ts = 0.0
        self._current_phrase = None
        self._current_attempts = 0
        self.web_spoken_once = False

        self.start_lcd(HBYS_DEFAULT_URL)
        self.chrome_watch_start()
        self._ensure_tts()
        try:
            self.tts_win.load_url(TTS_URL)
            self._log("[i] TTS sayfası yüklendi.")
        except Exception as e:
            self._log(f"[!] TTS yüklenemedi: {e}")

        if not self._started_logged:
            self._log(f"LCD & TTS başlatıldı (sessiz mod; {START_SPEAK_AFTER_CHANGES}. değişimde ve ilk numara/saat değişince konuşur).")
            self._started_logged = True
        return "Başlatıldı"

    def stop_all(self):
        self.chrome_watch_stop()
        self.stop_lcd()
        if self.tts_win:
            try: self.tts_win.evaluate_js(STOP_AUDIO_JS)
            except: pass
        self._log("LCD & TTS durduruldu.")
        self._started_logged = False
        return "Durduruldu"

# ========================= U Y G U L A M A =========================
def main():
    bridge = Bridge()
    ctrl = webview.create_window(
        title='HBYS + TTS Asistan',
        html=CONTROL_HTML,
        width=CONTROL_W, height=CONTROL_H,
        resizable=False, confirm_close=True, frameless=False,
        js_api=bridge
    )
    bridge.ctrl = ctrl

    def on_ctrl_loaded():
        bridge._status("Hazır")
        if AUTO_START:
            try: bridge.start_all()
            except Exception as e: bridge._log(f"[!] Otomatik başlat hata: {e}")

    ctrl.events.loaded += on_ctrl_loaded
    webview.start()

if __name__ == '__main__':
    main()
