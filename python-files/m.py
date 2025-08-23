# -*- coding: utf-8 -*-
# save as: lan_portal_match.py
import os
import atexit
import shutil
import signal
import tempfile
import threading
import socket
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify, abort
from flask_socketio import SocketIO, emit
from base64 import b64decode

# -----------------------------
# تنظیمات
# -----------------------------
APP_TITLE = "پرتال داخلی LAN"
DEFAULT_PORT = 1717

temp_root = None
uploads_dir = None
templates_dir = None
static_dir = None

app = None
socketio = None

# داده‌های موقت
chat_history = []                 # لیست پیام‌ها (in-memory)
connected_users = {}              # sid -> username
waiting_queues = {"ttt": [], "chess": []}   # صف‌های مچ‌سازی
active_games = {}                 # room -> {"game":..., "players":[sid1,sid2]}

# -----------------------------
# HTML template (single-file)
# -----------------------------
INDEX_HTML = r"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<link rel="icon" href="{{ url_for('static_file', filename='logo.png') }}">
<style>
:root{--bg:#0b1020;--card:#0f162e;--muted:#9fb8d8;--border:#223456;--text:#e6f0ff;--accent:#6fa8ff;--accent2:#35d3ee}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(900px 400px at 10% -10%,rgba(53,211,238,.08),transparent 30%),var(--bg);color:var(--text);font-family:Tahoma,Arial,Roboto,system-ui}
.header{display:flex;align-items:center;gap:12px;padding:12px 20px;border-bottom:1px solid var(--border);background:rgba(0,0,0,.25);position:sticky;top:0;z-index:10}
.logo{width:36px;height:36px;border-radius:8px}
.container{max-width:1100px;margin:20px auto;padding:0 16px}
.card{background:linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.01));border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:14px}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.tabs{display:flex;gap:8px;flex-wrap:wrap}
.tab{padding:8px 12px;border-radius:10px;background:rgba(255,255,255,.02);cursor:pointer;border:1px solid var(--border)}
.tab.active{background:linear-gradient(180deg,var(--accent),var(--accent2));color:#001428;border-color:transparent}
.hide{display:none}
.input,textarea{background:rgba(255,255,255,.03);border:1px solid var(--border);padding:8px;border-radius:10px;color:var(--text)}
.btn{background:linear-gradient(180deg,var(--accent),var(--accent2));border:none;padding:8px 12px;border-radius:10px;color:#001428;cursor:pointer}
.muted{color:var(--muted);font-size:13px}
.chat-box{height:260px;overflow:auto;border-radius:10px;border:1px dashed var(--border);padding:8px;background:rgba(0,0,0,.12)}
.files li{display:flex;justify-content:space-between;align-items:center;padding:8px;border-bottom:1px dashed var(--border)}
.board-ttt{display:grid;grid-template-columns:repeat(3,90px);gap:8px;justify-content:center}
.cell-ttt{width:90px;height:90px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.03);border-radius:10px;font-size:42px;cursor:pointer}
.chess{display:grid;grid-template-columns:repeat(8,56px);grid-gap:4px;justify-content:center;user-select:none}
.sq{width:56px;height:56px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-size:28px;cursor:pointer}
.light{background:#20314a}
.dark{background:#122235}
.toast{position:fixed;left:50%;transform:translateX(-50%);bottom:18px;background:rgba(0,0,0,.6);padding:8px 12px;border-radius:10px;display:none;color:white}
.modal-back{position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:40}
.modal{background:rgba(6,12,24,.95);padding:18px;border-radius:12px;border:1px solid var(--border);width:92%;max-width:420px;animation:pop .35s}
@keyframes pop{from{transform:scale(.95);opacity:0}to{transform:scale(1);opacity:1}}
</style>
</head>
<body>
<div class="header">
  <img class="logo" src="{{ url_for('static_file', filename='logo.png') }}" alt="logo">
  <div>
    <div style="font-weight:700">{{ title }}</div>
    <div class="muted" id="who">کاربر: —</div>
  </div>
</div>

<div class="container">
  <div class="card">
    <div class="row" style="justify-content:space-between">
      <div>
        <strong>خوش آمدید 👋</strong>
        <div class="muted">این پرتال محلی روی شبکهٔ داخلی اجرا می‌شود.</div>
      </div>
      <div class="tabs">
        <div class="tab active" data-tab="chat" onclick="switchTab('chat')">چت</div>
        <div class="tab" data-tab="upload" onclick="switchTab('upload')">آپلود</div>
        <div class="tab" data-tab="files" onclick="switchTab('files')">فایل‌ها</div>
        <div class="tab" data-tab="games" onclick="switchTab('games')">بازی‌ها</div>
      </div>
    </div>
  </div>

  <!-- CHAT -->
  <section id="tab-chat" class="card">
    <h3>چت عمومی</h3>
    <div class="chat-box" id="chatBox"></div>
    <div class="row" style="margin-top:8px">
      <input id="msg" class="input" style="flex:1" placeholder="پیام... (Enter)">
      <button id="sendBtn" class="btn">ارسال</button>
    </div>
  </section>

  <!-- UPLOAD -->
  <section id="tab-upload" class="card hide">
    <h3>آپلود فایل</h3>
    <form id="uploadForm">
      <input type="file" id="fileInput" name="file">
      <button class="btn" type="submit">آپلود</button>
    </form>
    <div class="muted" style="margin-top:8px">فایل‌ها روی خود میزبان ذخیره می‌شوند.</div>
  </section>

  <!-- FILES -->
  <section id="tab-files" class="card hide">
    <h3>فایل‌های آپلود شده</h3>
    <ul id="fileList" class="files"></ul>
    <div class="row" style="margin-top:8px">
      <button id="refreshBtn" class="btn">بروزرسانی</button>
      <button id="clearBtn" class="btn">حذف همه</button>
    </div>
  </section>

  <!-- GAMES -->
  <section id="tab-games" class="card hide">
    <h3>بازی‌ها</h3>

    <div class="card">
      <div class="row">
        <button id="findTTT" class="btn">⭕ دوز (Find Player)</button>
        <button id="findChess" class="btn">♟ شطرنج (Find Player)</button>
        <button id="cancelFind" class="tab" style="display:none" onclick="leaveQueue()">انصراف</button>
      </div>
      <div class="muted" id="matchStatus">آمادهٔ جستجوی حریف…</div>
    </div>

    <div id="tttArea" class="card hide">
      <h4>دوز آنلاین</h4>
      <div class="board-ttt" id="boardTTT"></div>
      <div class="row" style="margin-top:8px">
        <div class="muted" id="tttTurn">نوبت: —</div>
        <button id="tttLeave" class="btn">خروج</button>
      </div>
    </div>

    <div id="chessArea" class="card hide">
      <h4>شطرنج آنلاین (ساده)</h4>
      <div class="chess" id="chessBoard"></div>
      <div class="row" style="margin-top:8px">
        <div class="muted" id="chessTurn">نوبت: —</div>
        <button id="chessLeave" class="btn">خروج</button>
      </div>
    </div>
  </section>

  <div class="muted" style="text-align:center;margin-top:14px">© {{ year }} · {{ title }}</div>
</div>

<div id="usernameModal" class="modal-back">
  <div class="modal">
    <h3>خوش آمدی 🎮</h3>
    <p class="muted">یک نام برای نمایش انتخاب کن:</p>
    <div class="row" style="margin-top:8px">
      <input id="nameInput" class="input" placeholder="مثلاً Ali">
      <button id="saveName" class="btn">ورود</button>
    </div>
  </div>
</div>

<div id="toast" class="toast"></div>

<!-- socket.io client served locally -->
<script src="{{ url_for('static_file', filename='socket.io.js') }}"></script>
<script>
/* کلی JS کلاینت — آفلاین، بدون CDN */
const $ = s=>document.querySelector(s);
const $$ = s=>document.querySelectorAll(s);
function toast(t){ const el=$("#toast"); el.textContent=t; el.style.display="block"; setTimeout(()=>el.style.display="none",2200); }

function switchTab(name){
  ["chat","upload","files","games"].forEach(id=> {
    const el = document.getElementById("tab-"+id);
    if(el) el.classList.toggle("hide", id!==name);
  });
  $$(".tab").forEach(x=>x.classList.remove("active"));
  $$(".tab").forEach(x=>{ if(x.dataset.tab===name) x.classList.add("active"); });
}

/* socket */
const socket = io(); // از سرور محلی بارگذاری میشه
let myRole = null, currentRoom=null, currentGame=null;

socket.on("connect", ()=> {
  const nm = localStorage.getItem("lan_name");
  if(nm){ socket.emit("join",{user:nm}); $("#who").textContent = "کاربر: "+nm; $("#usernameModal").style.display="none"; }
  socket.emit("history");
});

socket.on("history",(items)=>{ const box=$("#chatBox"); box.innerHTML=""; items.forEach(it=>addMsg(it.user,it.msg,it.t)); });
socket.on("msg", data=> addMsg(data.user,data.msg,data.t));

function addMsg(u,m,t){ const box=$("#chatBox"); const d=document.createElement("div"); d.className=""; d.innerHTML=`<div style="font-weight:700">${u}</div><div>${m}</div><div class="muted" style="font-size:12px">${new Date(t).toLocaleString()}</div>`; box.appendChild(d); box.scrollTop=box.scrollHeight; }

/* ثبت نام / پاپ‌آپ */
function showNameModal(){ $("#usernameModal").style.display="flex"; $("#nameInput").focus(); }
$("#saveName").addEventListener("click", ()=>{
  const v=$("#nameInput").value.trim();
  if(!v){ toast("نام خالی است"); return; }
  localStorage.setItem("lan_name", v);
  $("#who").textContent = "کاربر: "+v;
  $("#usernameModal").style.display="none";
  socket.emit("join",{user:v});
});

/* chat send */
$("#sendBtn").addEventListener("click", sendMsg);
$("#msg").addEventListener("keydown", e=>{ if(e.key==="Enter") sendMsg(); });
function sendMsg(){ const m=$("#msg").value.trim(); if(!m) return; const u=localStorage.getItem("lan_name")||"ناشناس"; socket.emit("msg",{user:u,msg:m}); $("#msg").value=""; }

/* آپلود/فایل */
function loadFiles(){
  fetch("/api/files").then(r=>r.json()).then(js=>{
    const ul=$("#fileList"); ul.innerHTML="";
    if(js.length===0){ ul.innerHTML="<li class='muted'>فایلی وجود ندارد.</li>"; return; }
    js.forEach(f=>{
      const li=document.createElement("li");
      const a=document.createElement("a"); a.textContent="دانلود"; a.href="/download/"+encodeURIComponent(f.name);
      a.className="btn"; a.setAttribute("download","");
      const del=document.createElement("button"); del.textContent="حذف"; del.className="tab";
      del.addEventListener("click", ()=>{ fetch("/api/delete/"+encodeURIComponent(f.name), {method:"POST"}).then(()=>loadFiles()); });
      li.innerHTML=`<div>${f.name} <span class="muted">(${f.size_h})</span></div>`;
      li.appendChild(a); li.appendChild(del);
      ul.appendChild(li);
    });
  });
}
$("#uploadForm").addEventListener("submit", e=>{ e.preventDefault(); const f=document.getElementById("fileInput").files[0]; if(!f){ toast("فایل انتخاب نشده"); return; } const fd=new FormData(); fd.append("file", f); fetch("/upload",{method:"POST", body:fd}).then(r=>{ if(r.ok){ toast("آپلود شد"); loadFiles(); } else toast("خطا"); }); });
$("#refreshBtn").addEventListener("click", loadFiles);
$("#clearBtn").addEventListener("click", ()=>{ fetch("/api/clear",{method:"POST"}).then(()=>loadFiles()); });

/* مچ‌سازی */
$("#findTTT").addEventListener("click", ()=>enterQueue("ttt"));
$("#findChess").addEventListener("click", ()=>enterQueue("chess"));
$("#cancelFind").addEventListener("click", ()=>leaveQueue());

function enterQueue(game){
  const nm = localStorage.getItem("lan_name");
  if(!nm){ showNameModal(); toast("ابتدا نام خود را وارد کنید"); return; }
  socket.emit("queue_enter",{game});
  $("#matchStatus").textContent = "⏳ در حال جستجو برای حریف...";
  $("#cancelFind").style.display="inline-block";
}
function leaveQueue(){
  socket.emit("queue_leave",{game:currentGame});
  $("#matchStatus").textContent = "آمادهٔ جستجو…";
  $("#cancelFind").style.display="none";
  currentGame=null; currentRoom=null; myRole=null;
}

socket.on("match_found", data=>{
  currentRoom = data.room; currentGame = data.game; myRole = data.role;
  $("#matchStatus").textContent = "✅ حریف پیدا شد — اتاق: "+currentRoom;
  $("#cancelFind").style.display="none";
  toast("شروع بازی — نقش شما: "+myRole);
  if(currentGame==="ttt"){ $("#tttArea").classList.remove("hide"); initTTT(); } 
  if(currentGame==="chess"){ $("#chessArea").classList.remove("hide"); initChess(); }
});

/* opponent left */
socket.on("opponent_left", d=>{
  toast("حریف خارج شد");
  if(currentGame==="ttt"){ $("#tttArea").classList.add("hide"); }
  if(currentGame==="chess"){ $("#chessArea").classList.add("hide"); }
  currentRoom=null; currentGame=null; myRole=null;
});

/* بازی TTT آنلاین (ساده) */
let tttState = Array(9).fill(null);
let tttTurn = "X";
function initTTT(){
  tttState = Array(9).fill(null);
  tttTurn = "X";
  renderTTT();
  $("#tttTurn").textContent = "نوبت: "+tttTurn;
}
function renderTTT(){
  const board=$("#boardTTT"); board.innerHTML="";
  for(let i=0;i<9;i++){
    const c=document.createElement("div"); c.className="cell-ttt"; c.textContent=tttState[i]||"";
    c.addEventListener("click", ()=> {
      if(!currentRoom) return;
      if(tttState[i]) return;
      if(tttTurn!==myRole){ toast("نوبت شما نیست"); return; }
      // انجام حرکت محلی و ارسال به سرور
      tttState[i]=myRole;
      socket.emit("game_move",{room:currentRoom, game:"ttt", move:{i, val:myRole}});
      tttTurn = (tttTurn==="X")?"O":"X";
      $("#tttTurn").textContent = "نوبت: "+tttTurn;
      renderTTT();
    });
    board.appendChild(c);
  }
}
socket.on("game_move", data=>{
  if(!currentRoom || data.room!==currentRoom) return;
  if(data.game==="ttt"){
    const m = data.move;
    // حریف حرکت زده — مقدار مخالفِ نقش ما خواهد بود
    tttState[m.i] = m.val;
    tttTurn = (tttTurn==="X")?"O":"X";
    renderTTT();
  }
});

/* شطرنج آنلاین (ساده) */
const U = {"P":"♙","R":"♖","N":"♘","B":"♗","Q":"♕","K":"♔","p":"♟","r":"♜","n":"♞","b":"♝","q":"♛","k":"♚"};
let chessBoard = [];
let chessTurn = "w";
let chessSel = null;
function initChess(){
  // شروع استاندارد
  const fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
  chessBoard = fenToBoard(fen);
  chessTurn = "w";
  chessSel = null;
  renderChess();
}
function fenToBoard(fen){
  const rows = fen.split("/");
  const b = [];
  for(let r=0;r<8;r++){
    const row=[]; let s=rows[r];
    for(const ch of s){
      if(/[1-8]/.test(ch)){ for(let k=0;k<parseInt(ch);k++) row.push("."); }
      else row.push(ch);
    }
    b.push(row);
  }
  return b;
}
function renderChess(){
  const el=$("#chessBoard"); el.innerHTML="";
  for(let r=0;r<8;r++){
    for(let c=0;c<8;c++){
      const sq=document.createElement("div"); sq.className="sq "+(((r+c)%2)?"dark":"light");
      const p = chessBoard[r][c]; if(p !== ".") sq.textContent = U[p];
      sq.addEventListener("click", ()=> {
        if(!currentRoom){ toast("در اتاق نیستید"); return; }
        const myColor = (myRole==="w")?"w":"b";
        if(chessTurn !== myColor){ toast("نوبت شما نیست"); return; }
        if(chessSel){
          const pr=chessSel.r, pc=chessSel.c;
          const tr=r, tc=c;
          // ساده: اجازه میدهیم هر حرکت را انجام بده و به سرور بفرستد (سرور هم به حریف خبر میده)
          const moving = chessBoard[pr][pc];
          if(moving==="." || (moving===moving.toUpperCase() && myColor==="b") || (moving===moving.toLowerCase() && myColor==="w")) {
            chessSel=null; renderChess(); return;
          }
          // ارسال حرکت به سرور (سرور آن را به حریف forward می‌کند)
          socket.emit("game_move",{room:currentRoom, game:"chess", move:{pr,pc,tr,tc}});
          // اعمال محلی موقت (سرور هم به حریف خواهد فرستاد و در اون‌سو اعمال می‌شود)
          chessBoard[tr][tc] = moving; chessBoard[pr][pc] = ".";
          chessTurn = (chessTurn==="w")?"b":"w";
          chessSel=null; renderChess();
        } else {
          // انتخاب مهره
          chessSel = {r,c}; renderChess();
        }
      });
      el.appendChild(sq);
    }
  }
  $("#chessTurn").textContent = "نوبت: "+(chessTurn==="w"?"سفید":"سیاه");
}
socket.on("game_move", data=>{
  if(!currentRoom || data.room!==currentRoom) return;
  if(data.game==="chess"){
    const {pr,pc,tr,tc} = data.move;
    const mv = chessBoard[pr][pc];
    chessBoard[pr][pc]=".";
    chessBoard[tr][tc]=mv;
    chessTurn = (chessTurn==="w")?"b":"w";
    renderChess();
  }
});

/* leave buttons */
$("#tttLeave").addEventListener("click", ()=> { socket.emit("leave_room",{room:currentRoom}); $("#tttArea").classList.add("hide"); currentRoom=null; myRole=null; currentGame=null; $("#matchStatus").textContent="آمادهٔ جستجو…"; });
$("#chessLeave").addEventListener("click", ()=> { socket.emit("leave_room",{room:currentRoom}); $("#chessArea").classList.add("hide"); currentRoom=null; myRole=null; currentGame=null; $("#matchStatus").textContent="آمادهٔ جستجو…"; });

/* server notifications for moves/resets forwarded above */
socket.on("game_reset", d=> {
  if(d.game==="ttt" && d.room===currentRoom) initTTT();
  if(d.game==="chess" && d.room===currentRoom) initChess();
});

/* وقتی صفحه لود شد */
window.addEventListener("load", ()=>{
  const nm = localStorage.getItem("lan_name");
  if(!nm) showNameModal(); else { $("#who").textContent = "کاربر: "+nm; $("#usernameModal").style.display="none"; }
  loadFiles();
});
</script>
</body>
</html>
"""

# لوگوی Base64 کوچک (سالم)
LOGO_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAZUlEQVR4nO3TsQkAMAwEwdr/"
    "6a1jDmgApIFBNVvM4wMAAAAAAAAAAADwH6Vtl14D4Yo77Di+HCDJgAwYIMmADBgAycCMGCDJ"
    "gAwYAMmADBgAycAMGCDJgAwYAMmADBgAyf4BqRYDeXlyUiIAAAAASUVORK5CYII="
)

# -----
# مهم: اینجا محتوای socket.io.min.js رو به Base64 بذار
# روش ساخت Base64:
#   1) فایل socket.io.min.js (مثلاً نسخه 4.6.x) را یکبار دانلود کن
#   2) با پایتون:  python -c "import base64,sys;print(base64.b64encode(open('socket.io.min.js','rb').read()).decode())" > sio.b64.txt
#   3) متن خروجی را کپی کن و داخل رشتهٔ زیر جایگزین کن:
# در حالت فعلی خالی است تا برنامه بالا بیاید و فقط هشدار چاپ کند.
SOCKET_IO_MIN_JS_BASE64 = "LyohDQogKiBTb2NrZXQuSU8gdjQuNi4xDQogKiAoYykgMjAxNC0yMDIzIEd1aWxsZXJtbyBSYXVjaA0KICogUmVsZWFzZWQgdW5kZXIgdGhlIE1JVCBMaWNlbnNlLg0KICovDQohZnVuY3Rpb24odCxlKXsib2JqZWN0Ij09dHlwZW9mIGV4cG9ydHMmJiJ1bmRlZmluZWQiIT10eXBlb2YgbW9kdWxlP21vZHVsZS5leHBvcnRzPWUoKToiZnVuY3Rpb24iPT10eXBlb2YgZGVmaW5lJiZkZWZpbmUuYW1kP2RlZmluZShlKToodD0idW5kZWZpbmVkIiE9dHlwZW9mIGdsb2JhbFRoaXM/Z2xvYmFsVGhpczp0fHxzZWxmKS5pbz1lKCl9KHRoaXMsKGZ1bmN0aW9uKCl7InVzZSBzdHJpY3QiO2Z1bmN0aW9uIHQoZSl7cmV0dXJuIHQ9ImZ1bmN0aW9uIj09dHlwZW9mIFN5bWJvbCYmInN5bWJvbCI9PXR5cGVvZiBTeW1ib2wuaXRlcmF0b3I/ZnVuY3Rpb24odCl7cmV0dXJuIHR5cGVvZiB0fTpmdW5jdGlvbih0KXtyZXR1cm4gdCYmImZ1bmN0aW9uIj09dHlwZW9mIFN5bWJvbCYmdC5jb25zdHJ1Y3Rvcj09PVN5bWJvbCYmdCE9PVN5bWJvbC5wcm90b3R5cGU/InN5bWJvbCI6dHlwZW9mIHR9LHQoZSl9ZnVuY3Rpb24gZSh0LGUpe2lmKCEodCBpbnN0YW5jZW9mIGUpKXRocm93IG5ldyBUeXBlRXJyb3IoIkNhbm5vdCBjYWxsIGEgY2xhc3MgYXMgYSBmdW5jdGlvbiIpfWZ1bmN0aW9uIG4odCxlKXtmb3IodmFyIG49MDtuPGUubGVuZ3RoO24rKyl7dmFyIHI9ZVtuXTtyLmVudW1lcmFibGU9ci5lbnVtZXJhYmxlfHwhMSxyLmNvbmZpZ3VyYWJsZT0hMCwidmFsdWUiaW4gciYmKHIud3JpdGFibGU9ITApLE9iamVjdC5kZWZpbmVQcm9wZXJ0eSh0LHIua2V5LHIpfX1mdW5jdGlvbiByKHQsZSxyKXtyZXR1cm4gZSYmbih0LnByb3RvdHlwZSxlKSxyJiZuKHQsciksT2JqZWN0LmRlZmluZVByb3BlcnR5KHQsInByb3RvdHlwZSIse3dyaXRhYmxlOiExfSksdH1mdW5jdGlvbiBpKCl7cmV0dXJuIGk9T2JqZWN0LmFzc2lnbj9PYmplY3QuYXNzaWduLmJpbmQoKTpmdW5jdGlvbih0KXtmb3IodmFyIGU9MTtlPGFyZ3VtZW50cy5sZW5ndGg7ZSsrKXt2YXIgbj1hcmd1bWVudHNbZV07Zm9yKHZhciByIGluIG4pT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKG4scikmJih0W3JdPW5bcl0pfXJldHVybiB0fSxpLmFwcGx5KHRoaXMsYXJndW1lbnRzKX1mdW5jdGlvbiBvKHQsZSl7aWYoImZ1bmN0aW9uIiE9dHlwZW9mIGUmJm51bGwhPT1lKXRocm93IG5ldyBUeXBlRXJyb3IoIlN1cGVyIGV4cHJlc3Npb24gbXVzdCBlaXRoZXIgYmUgbnVsbCBvciBhIGZ1bmN0aW9uIik7dC5wcm90b3R5cGU9T2JqZWN0LmNyZWF0ZShlJiZlLnByb3RvdHlwZSx7Y29uc3RydWN0b3I6e3ZhbHVlOnQsd3JpdGFibGU6ITAsY29uZmlndXJhYmxlOiEwfX0pLE9iamVjdC5kZWZpbmVQcm9wZXJ0eSh0LCJwcm90b3R5cGUiLHt3cml0YWJsZTohMX0pLGUmJmEodCxlKX1mdW5jdGlvbiBzKHQpe3JldHVybiBzPU9iamVjdC5zZXRQcm90b3R5cGVPZj9PYmplY3QuZ2V0UHJvdG90eXBlT2YuYmluZCgpOmZ1bmN0aW9uKHQpe3JldHVybiB0Ll9fcHJvdG9fX3x8T2JqZWN0LmdldFByb3RvdHlwZU9mKHQpfSxzKHQpfWZ1bmN0aW9uIGEodCxlKXtyZXR1cm4gYT1PYmplY3Quc2V0UHJvdG90eXBlT2Y/T2JqZWN0LnNldFByb3RvdHlwZU9mLmJpbmQoKTpmdW5jdGlvbih0LGUpe3JldHVybiB0Ll9fcHJvdG9fXz1lLHR9LGEodCxlKX1mdW5jdGlvbiBjKCl7aWYoInVuZGVmaW5lZCI9PXR5cGVvZiBSZWZsZWN0fHwhUmVmbGVjdC5jb25zdHJ1Y3QpcmV0dXJuITE7aWYoUmVmbGVjdC5jb25zdHJ1Y3Quc2hhbSlyZXR1cm4hMTtpZigiZnVuY3Rpb24iPT10eXBlb2YgUHJveHkpcmV0dXJuITA7dHJ5e3JldHVybiBCb29sZWFuLnByb3RvdHlwZS52YWx1ZU9mLmNhbGwoUmVmbGVjdC5jb25zdHJ1Y3QoQm9vbGVhbixbXSwoZnVuY3Rpb24oKXt9KSkpLCEwfWNhdGNoKHQpe3JldHVybiExfX1mdW5jdGlvbiB1KHQsZSxuKXtyZXR1cm4gdT1jKCk/UmVmbGVjdC5jb25zdHJ1Y3QuYmluZCgpOmZ1bmN0aW9uKHQsZSxuKXt2YXIgcj1bbnVsbF07ci5wdXNoLmFwcGx5KHIsZSk7dmFyIGk9bmV3KEZ1bmN0aW9uLmJpbmQuYXBwbHkodCxyKSk7cmV0dXJuIG4mJmEoaSxuLnByb3RvdHlwZSksaX0sdS5hcHBseShudWxsLGFyZ3VtZW50cyl9ZnVuY3Rpb24gaCh0KXt2YXIgZT0iZnVuY3Rpb24iPT10eXBlb2YgTWFwP25ldyBNYXA6dm9pZCAwO3JldHVybiBoPWZ1bmN0aW9uKHQpe2lmKG51bGw9PT10fHwobj10LC0xPT09RnVuY3Rpb24udG9TdHJpbmcuY2FsbChuKS5pbmRleE9mKCJbbmF0aXZlIGNvZGVdIikpKXJldHVybiB0O3ZhciBuO2lmKCJmdW5jdGlvbiIhPXR5cGVvZiB0KXRocm93IG5ldyBUeXBlRXJyb3IoIlN1cGVyIGV4cHJlc3Npb24gbXVzdCBlaXRoZXIgYmUgbnVsbCBvciBhIGZ1bmN0aW9uIik7aWYodm9pZCAwIT09ZSl7aWYoZS5oYXModCkpcmV0dXJuIGUuZ2V0KHQpO2Uuc2V0KHQscil9ZnVuY3Rpb24gcigpe3JldHVybiB1KHQsYXJndW1lbnRzLHModGhpcykuY29uc3RydWN0b3IpfXJldHVybiByLnByb3RvdHlwZT1PYmplY3QuY3JlYXRlKHQucHJvdG90eXBlLHtjb25zdHJ1Y3Rvcjp7dmFsdWU6cixlbnVtZXJhYmxlOiExLHdyaXRhYmxlOiEwLGNvbmZpZ3VyYWJsZTohMH19KSxhKHIsdCl9LGgodCl9ZnVuY3Rpb24gZih0KXtpZih2b2lkIDA9PT10KXRocm93IG5ldyBSZWZlcmVuY2VFcnJvcigidGhpcyBoYXNuJ3QgYmVlbiBpbml0aWFsaXNlZCAtIHN1cGVyKCkgaGFzbid0IGJlZW4gY2FsbGVkIik7cmV0dXJuIHR9ZnVuY3Rpb24gbCh0LGUpe2lmKGUmJigib2JqZWN0Ij09dHlwZW9mIGV8fCJmdW5jdGlvbiI9PXR5cGVvZiBlKSlyZXR1cm4gZTtpZih2b2lkIDAhPT1lKXRocm93IG5ldyBUeXBlRXJyb3IoIkRlcml2ZWQgY29uc3RydWN0b3JzIG1heSBvbmx5IHJldHVybiBvYmplY3Qgb3IgdW5kZWZpbmVkIik7cmV0dXJuIGYodCl9ZnVuY3Rpb24gcCh0KXt2YXIgZT1jKCk7cmV0dXJuIGZ1bmN0aW9uKCl7dmFyIG4scj1zKHQpO2lmKGUpe3ZhciBpPXModGhpcykuY29uc3RydWN0b3I7bj1SZWZsZWN0LmNvbnN0cnVjdChyLGFyZ3VtZW50cyxpKX1lbHNlIG49ci5hcHBseSh0aGlzLGFyZ3VtZW50cyk7cmV0dXJuIGwodGhpcyxuKX19ZnVuY3Rpb24gZCh0LGUpe2Zvcig7IU9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbCh0LGUpJiZudWxsIT09KHQ9cyh0KSk7KTtyZXR1cm4gdH1mdW5jdGlvbiB5KCl7cmV0dXJuIHk9InVuZGVmaW5lZCIhPXR5cGVvZiBSZWZsZWN0JiZSZWZsZWN0LmdldD9SZWZsZWN0LmdldC5iaW5kKCk6ZnVuY3Rpb24odCxlLG4pe3ZhciByPWQodCxlKTtpZihyKXt2YXIgaT1PYmplY3QuZ2V0T3duUHJvcGVydHlEZXNjcmlwdG9yKHIsZSk7cmV0dXJuIGkuZ2V0P2kuZ2V0LmNhbGwoYXJndW1lbnRzLmxlbmd0aDwzP3Q6bik6aS52YWx1ZX19LHkuYXBwbHkodGhpcyxhcmd1bWVudHMpfWZ1bmN0aW9uIHYodCxlKXsobnVsbD09ZXx8ZT50Lmxlbmd0aCkmJihlPXQubGVuZ3RoKTtmb3IodmFyIG49MCxyPW5ldyBBcnJheShlKTtuPGU7bisrKXJbbl09dFtuXTtyZXR1cm4gcn1mdW5jdGlvbiBnKHQsZSl7dmFyIG49InVuZGVmaW5lZCIhPXR5cGVvZiBTeW1ib2wmJnRbU3ltYm9sLml0ZXJhdG9yXXx8dFsiQEBpdGVyYXRvciJdO2lmKCFuKXtpZihBcnJheS5pc0FycmF5KHQpfHwobj1mdW5jdGlvbih0LGUpe2lmKHQpe2lmKCJzdHJpbmciPT10eXBlb2YgdClyZXR1cm4gdih0LGUpO3ZhciBuPU9iamVjdC5wcm90b3R5cGUudG9TdHJpbmcuY2FsbCh0KS5zbGljZSg4LC0xKTtyZXR1cm4iT2JqZWN0Ij09PW4mJnQuY29uc3RydWN0b3ImJihuPXQuY29uc3RydWN0b3IubmFtZSksIk1hcCI9PT1ufHwiU2V0Ij09PW4/QXJyYXkuZnJvbSh0KToiQXJndW1lbnRzIj09PW58fC9eKD86VWl8SSludCg/Ojh8MTZ8MzIpKD86Q2xhbXBlZCk/QXJyYXkkLy50ZXN0KG4pP3YodCxlKTp2b2lkIDB9fSh0KSl8fGUmJnQmJiJudW1iZXIiPT10eXBlb2YgdC5sZW5ndGgpe24mJih0PW4pO3ZhciByPTAsaT1mdW5jdGlvbigpe307cmV0dXJue3M6aSxuOmZ1bmN0aW9uKCl7cmV0dXJuIHI+PXQubGVuZ3RoP3tkb25lOiEwfTp7ZG9uZTohMSx2YWx1ZTp0W3IrK119fSxlOmZ1bmN0aW9uKHQpe3Rocm93IHR9LGY6aX19dGhyb3cgbmV3IFR5cGVFcnJvcigiSW52YWxpZCBhdHRlbXB0IHRvIGl0ZXJhdGUgbm9uLWl0ZXJhYmxlIGluc3RhbmNlLlxuSW4gb3JkZXIgdG8gYmUgaXRlcmFibGUsIG5vbi1hcnJheSBvYmplY3RzIG11c3QgaGF2ZSBhIFtTeW1ib2wuaXRlcmF0b3JdKCkgbWV0aG9kLiIpfXZhciBvLHM9ITAsYT0hMTtyZXR1cm57czpmdW5jdGlvbigpe249bi5jYWxsKHQpfSxuOmZ1bmN0aW9uKCl7dmFyIHQ9bi5uZXh0KCk7cmV0dXJuIHM9dC5kb25lLHR9LGU6ZnVuY3Rpb24odCl7YT0hMCxvPXR9LGY6ZnVuY3Rpb24oKXt0cnl7c3x8bnVsbD09bi5yZXR1cm58fG4ucmV0dXJuKCl9ZmluYWxseXtpZihhKXRocm93IG99fX19dmFyIG09T2JqZWN0LmNyZWF0ZShudWxsKTttLm9wZW49IjAiLG0uY2xvc2U9IjEiLG0ucGluZz0iMiIsbS5wb25nPSIzIixtLm1lc3NhZ2U9IjQiLG0udXBncmFkZT0iNSIsbS5ub29wPSI2Ijt2YXIgaz1PYmplY3QuY3JlYXRlKG51bGwpO09iamVjdC5rZXlzKG0pLmZvckVhY2goKGZ1bmN0aW9uKHQpe2tbbVt0XV09dH0pKTtmb3IodmFyIGI9e3R5cGU6ImVycm9yIixkYXRhOiJwYXJzZXIgZXJyb3IifSx3PSJmdW5jdGlvbiI9PXR5cGVvZiBCbG9ifHwidW5kZWZpbmVkIiE9dHlwZW9mIEJsb2ImJiJbb2JqZWN0IEJsb2JDb25zdHJ1Y3Rvcl0iPT09T2JqZWN0LnByb3RvdHlwZS50b1N0cmluZy5jYWxsKEJsb2IpLF89ImZ1bmN0aW9uIj09dHlwZW9mIEFycmF5QnVmZmVyLEU9ZnVuY3Rpb24odCxlLG4pe3ZhciByLGk9dC50eXBlLG89dC5kYXRhO3JldHVybiB3JiZvIGluc3RhbmNlb2YgQmxvYj9lP24obyk6TyhvLG4pOl8mJihvIGluc3RhbmNlb2YgQXJyYXlCdWZmZXJ8fChyPW8sImZ1bmN0aW9uIj09dHlwZW9mIEFycmF5QnVmZmVyLmlzVmlldz9BcnJheUJ1ZmZlci5pc1ZpZXcocik6ciYmci5idWZmZXIgaW5zdGFuY2VvZiBBcnJheUJ1ZmZlcikpP2U/bihvKTpPKG5ldyBCbG9iKFtvXSksbik6bihtW2ldKyhvfHwiIikpfSxPPWZ1bmN0aW9uKHQsZSl7dmFyIG49bmV3IEZpbGVSZWFkZXI7cmV0dXJuIG4ub25sb2FkPWZ1bmN0aW9uKCl7dmFyIHQ9bi5yZXN1bHQuc3BsaXQoIiwiKVsxXTtlKCJiIit0KX0sbi5yZWFkQXNEYXRhVVJMKHQpfSxBPSJBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWmFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1Njc4OSsvIixSPSJ1bmRlZmluZWQiPT10eXBlb2YgVWludDhBcnJheT9bXTpuZXcgVWludDhBcnJheSgyNTYpLFQ9MDtUPEEubGVuZ3RoO1QrKylSW0EuY2hhckNvZGVBdChUKV09VDt2YXIgQz0iZnVuY3Rpb24iPT10eXBlb2YgQXJyYXlCdWZmZXIsQj1mdW5jdGlvbih0LGUpe2lmKCJzdHJpbmciIT10eXBlb2YgdClyZXR1cm57dHlwZToibWVzc2FnZSIsZGF0YTpOKHQsZSl9O3ZhciBuPXQuY2hhckF0KDApO3JldHVybiJiIj09PW4/e3R5cGU6Im1lc3NhZ2UiLGRhdGE6Uyh0LnN1YnN0cmluZygxKSxlKX06a1tuXT90Lmxlbmd0aD4xP3t0eXBlOmtbbl0sZGF0YTp0LnN1YnN0cmluZygxKX06e3R5cGU6a1tuXX06Yn0sUz1mdW5jdGlvbih0LGUpe2lmKEMpe3ZhciBuPWZ1bmN0aW9uKHQpe3ZhciBlLG4scixpLG8scz0uNzUqdC5sZW5ndGgsYT10Lmxlbmd0aCxjPTA7Ij0iPT09dFt0Lmxlbmd0aC0xXSYmKHMtLSwiPSI9PT10W3QubGVuZ3RoLTJdJiZzLS0pO3ZhciB1PW5ldyBBcnJheUJ1ZmZlcihzKSxoPW5ldyBVaW50OEFycmF5KHUpO2ZvcihlPTA7ZTxhO2UrPTQpbj1SW3QuY2hhckNvZGVBdChlKV0scj1SW3QuY2hhckNvZGVBdChlKzEpXSxpPVJbdC5jaGFyQ29kZUF0KGUrMildLG89Ult0LmNoYXJDb2RlQXQoZSszKV0saFtjKytdPW48PDJ8cj4+NCxoW2MrK109KDE1JnIpPDw0fGk+PjIsaFtjKytdPSgzJmkpPDw2fDYzJm87cmV0dXJuIHV9KHQpO3JldHVybiBOKG4sZSl9cmV0dXJue2Jhc2U2NDohMCxkYXRhOnR9fSxOPWZ1bmN0aW9uKHQsZSl7cmV0dXJuImJsb2IiPT09ZSYmdCBpbnN0YW5jZW9mIEFycmF5QnVmZmVyP25ldyBCbG9iKFt0XSk6dH0seD1TdHJpbmcuZnJvbUNoYXJDb2RlKDMwKTtmdW5jdGlvbiBMKHQpe2lmKHQpcmV0dXJuIGZ1bmN0aW9uKHQpe2Zvcih2YXIgZSBpbiBMLnByb3RvdHlwZSl0W2VdPUwucHJvdG90eXBlW2VdO3JldHVybiB0fSh0KX1MLnByb3RvdHlwZS5vbj1MLnByb3RvdHlwZS5hZGRFdmVudExpc3RlbmVyPWZ1bmN0aW9uKHQsZSl7cmV0dXJuIHRoaXMuX2NhbGxiYWNrcz10aGlzLl9jYWxsYmFja3N8fHt9LCh0aGlzLl9jYWxsYmFja3NbIiQiK3RdPXRoaXMuX2NhbGxiYWNrc1siJCIrdF18fFtdKS5wdXNoKGUpLHRoaXN9LEwucHJvdG90eXBlLm9uY2U9ZnVuY3Rpb24odCxlKXtmdW5jdGlvbiBuKCl7dGhpcy5vZmYodCxuKSxlLmFwcGx5KHRoaXMsYXJndW1lbnRzKX1yZXR1cm4gbi5mbj1lLHRoaXMub24odCxuKSx0aGlzfSxMLnByb3RvdHlwZS5vZmY9TC5wcm90b3R5cGUucmVtb3ZlTGlzdGVuZXI9TC5wcm90b3R5cGUucmVtb3ZlQWxsTGlzdGVuZXJzPUwucHJvdG90eXBlLnJlbW92ZUV2ZW50TGlzdGVuZXI9ZnVuY3Rpb24odCxlKXtpZih0aGlzLl9jYWxsYmFja3M9dGhpcy5fY2FsbGJhY2tzfHx7fSwwPT1hcmd1bWVudHMubGVuZ3RoKXJldHVybiB0aGlzLl9jYWxsYmFja3M9e30sdGhpczt2YXIgbixyPXRoaXMuX2NhbGxiYWNrc1siJCIrdF07aWYoIXIpcmV0dXJuIHRoaXM7aWYoMT09YXJndW1lbnRzLmxlbmd0aClyZXR1cm4gZGVsZXRlIHRoaXMuX2NhbGxiYWNrc1siJCIrdF0sdGhpcztmb3IodmFyIGk9MDtpPHIubGVuZ3RoO2krKylpZigobj1yW2ldKT09PWV8fG4uZm49PT1lKXtyLnNwbGljZShpLDEpO2JyZWFrfXJldHVybiAwPT09ci5sZW5ndGgmJmRlbGV0ZSB0aGlzLl9jYWxsYmFja3NbIiQiK3RdLHRoaXN9LEwucHJvdG90eXBlLmVtaXQ9ZnVuY3Rpb24odCl7dGhpcy5fY2FsbGJhY2tzPXRoaXMuX2NhbGxiYWNrc3x8e307Zm9yKHZhciBlPW5ldyBBcnJheShhcmd1bWVudHMubGVuZ3RoLTEpLG49dGhpcy5fY2FsbGJhY2tzWyIkIit0XSxyPTE7cjxhcmd1bWVudHMubGVuZ3RoO3IrKyllW3ItMV09YXJndW1lbnRzW3JdO2lmKG4pe3I9MDtmb3IodmFyIGk9KG49bi5zbGljZSgwKSkubGVuZ3RoO3I8aTsrK3IpbltyXS5hcHBseSh0aGlzLGUpfXJldHVybiB0aGlzfSxMLnByb3RvdHlwZS5lbWl0UmVzZXJ2ZWQ9TC5wcm90b3R5cGUuZW1pdCxMLnByb3RvdHlwZS5saXN0ZW5lcnM9ZnVuY3Rpb24odCl7cmV0dXJuIHRoaXMuX2NhbGxiYWNrcz10aGlzLl9jYWxsYmFja3N8fHt9LHRoaXMuX2NhbGxiYWNrc1siJCIrdF18fFtdfSxMLnByb3RvdHlwZS5oYXNMaXN0ZW5lcnM9ZnVuY3Rpb24odCl7cmV0dXJuISF0aGlzLmxpc3RlbmVycyh0KS5sZW5ndGh9O3ZhciBQPSJ1bmRlZmluZWQiIT10eXBlb2Ygc2VsZj9zZWxmOiJ1bmRlZmluZWQiIT10eXBlb2Ygd2luZG93P3dpbmRvdzpGdW5jdGlvbigicmV0dXJuIHRoaXMiKSgpO2Z1bmN0aW9uIGoodCl7Zm9yKHZhciBlPWFyZ3VtZW50cy5sZW5ndGgsbj1uZXcgQXJyYXkoZT4xP2UtMTowKSxyPTE7cjxlO3IrKyluW3ItMV09YXJndW1lbnRzW3JdO3JldHVybiBuLnJlZHVjZSgoZnVuY3Rpb24oZSxuKXtyZXR1cm4gdC5oYXNPd25Qcm9wZXJ0eShuKSYmKGVbbl09dFtuXSksZX0pLHt9KX12YXIgcT1QLnNldFRpbWVvdXQsST1QLmNsZWFyVGltZW91dDtmdW5jdGlvbiBEKHQsZSl7ZS51c2VOYXRpdmVUaW1lcnM/KHQuc2V0VGltZW91dEZuPXEuYmluZChQKSx0LmNsZWFyVGltZW91dEZuPUkuYmluZChQKSk6KHQuc2V0VGltZW91dEZuPVAuc2V0VGltZW91dC5iaW5kKFApLHQuY2xlYXJUaW1lb3V0Rm49UC5jbGVhclRpbWVvdXQuYmluZChQKSl9dmFyIEYsTT1mdW5jdGlvbih0KXtvKGksdCk7dmFyIG49cChpKTtmdW5jdGlvbiBpKHQscixvKXt2YXIgcztyZXR1cm4gZSh0aGlzLGkpLChzPW4uY2FsbCh0aGlzLHQpKS5kZXNjcmlwdGlvbj1yLHMuY29udGV4dD1vLHMudHlwZT0iVHJhbnNwb3J0RXJyb3IiLHN9cmV0dXJuIHIoaSl9KGgoRXJyb3IpKSxVPWZ1bmN0aW9uKHQpe28oaSx0KTt2YXIgbj1wKGkpO2Z1bmN0aW9uIGkodCl7dmFyIHI7cmV0dXJuIGUodGhpcyxpKSwocj1uLmNhbGwodGhpcykpLndyaXRhYmxlPSExLEQoZihyKSx0KSxyLm9wdHM9dCxyLnF1ZXJ5PXQucXVlcnksci5zb2NrZXQ9dC5zb2NrZXQscn1yZXR1cm4gcihpLFt7a2V5OiJvbkVycm9yIix2YWx1ZTpmdW5jdGlvbih0LGUsbil7cmV0dXJuIHkocyhpLnByb3RvdHlwZSksImVtaXRSZXNlcnZlZCIsdGhpcykuY2FsbCh0aGlzLCJlcnJvciIsbmV3IE0odCxlLG4pKSx0aGlzfX0se2tleToib3BlbiIsdmFsdWU6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5yZWFkeVN0YXRlPSJvcGVuaW5nIix0aGlzLmRvT3BlbigpLHRoaXN9fSx7a2V5OiJjbG9zZSIsdmFsdWU6ZnVuY3Rpb24oKXtyZXR1cm4ib3BlbmluZyIhPT10aGlzLnJlYWR5U3RhdGUmJiJvcGVuIiE9PXRoaXMucmVhZHlTdGF0ZXx8KHRoaXMuZG9DbG9zZSgpLHRoaXMub25DbG9zZSgpKSx0aGlzfX0se2tleToic2VuZCIsdmFsdWU6ZnVuY3Rpb24odCl7Im9wZW4iPT09dGhpcy5yZWFkeVN0YXRlJiZ0aGlzLndyaXRlKHQpfX0se2tleToib25PcGVuIix2YWx1ZTpmdW5jdGlvbigpe3RoaXMucmVhZHlTdGF0ZT0ib3BlbiIsdGhpcy53cml0YWJsZT0hMCx5KHMoaS5wcm90b3R5cGUpLCJlbWl0UmVzZXJ2ZWQiLHRoaXMpLmNhbGwodGhpcywib3BlbiIpfX0se2tleToib25EYXRhIix2YWx1ZTpmdW5jdGlvbih0KXt2YXIgZT1CKHQsdGhpcy5zb2NrZXQuYmluYXJ5VHlwZSk7dGhpcy5vblBhY2tldChlKX19LHtrZXk6Im9uUGFja2V0Iix2YWx1ZTpmdW5jdGlvbih0KXt5KHMoaS5wcm90b3R5cGUpLCJlbWl0UmVzZXJ2ZWQiLHRoaXMpLmNhbGwodGhpcywicGFja2V0Iix0KX19LHtrZXk6Im9uQ2xvc2UiLHZhbHVlOmZ1bmN0aW9uKHQpe3RoaXMucmVhZHlTdGF0ZT0iY2xvc2VkIix5KHMoaS5wcm90b3R5cGUpLCJlbWl0UmVzZXJ2ZWQiLHRoaXMpLmNhbGwodGhpcywiY2xvc2UiLHQpfX0se2tleToicGF1c2UiLHZhbHVlOmZ1bmN0aW9uKHQpe319XSksaX0oTCksVj0iMDEyMzQ1Njc4OUFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXotXyIuc3BsaXQoIiIpLEg9e30sSz0wLFk9MDtmdW5jdGlvbiB6KHQpe3ZhciBlPSIiO2Rve2U9Vlt0JTY0XStlLHQ9TWF0aC5mbG9vcih0LzY0KX13aGlsZSh0PjApO3JldHVybiBlfWZ1bmN0aW9uIFcoKXt2YXIgdD16KCtuZXcgRGF0ZSk7cmV0dXJuIHQhPT1GPyhLPTAsRj10KTp0KyIuIit6KEsrKyl9Zm9yKDtZPDY0O1krKylIW1ZbWV1dPVk7ZnVuY3Rpb24gJCh0KXt2YXIgZT0iIjtmb3IodmFyIG4gaW4gdCl0Lmhhc093blByb3BlcnR5KG4pJiYoZS5sZW5ndGgmJihlKz0iJiIpLGUrPWVuY29kZVVSSUNvbXBvbmVudChuKSsiPSIrZW5jb2RlVVJJQ29tcG9uZW50KHRbbl0pKTtyZXR1cm4gZX1mdW5jdGlvbiBKKHQpe2Zvcih2YXIgZT17fSxuPXQuc3BsaXQoIiYiKSxyPTAsaT1uLmxlbmd0aDtyPGk7cisrKXt2YXIgbz1uW3JdLnNwbGl0KCI9Iik7ZVtkZWNvZGVVUklDb21wb25lbnQob1swXSldPWRlY29kZVVSSUNvbXBvbmVudChvWzFdKX1yZXR1cm4gZX12YXIgUT0hMTt0cnl7UT0idW5kZWZpbmVkIiE9dHlwZW9mIFhNTEh0dHBSZXF1ZXN0JiYid2l0aENyZWRlbnRpYWxzImluIG5ldyBYTUxIdHRwUmVxdWVzdH1jYXRjaCh0KXt9dmFyIFg9UTtmdW5jdGlvbiBHKHQpe3ZhciBlPXQueGRvbWFpbjt0cnl7aWYoInVuZGVmaW5lZCIhPXR5cGVvZiBYTUxIdHRwUmVxdWVzdCYmKCFlfHxYKSlyZXR1cm4gbmV3IFhNTEh0dHBSZXF1ZXN0fWNhdGNoKHQpe31pZighZSl0cnl7cmV0dXJuIG5ldyhQW1siQWN0aXZlIl0uY29uY2F0KCJPYmplY3QiKS5qb2luKCJYIildKSgiTWljcm9zb2Z0LlhNTEhUVFAiKX1jYXRjaCh0KXt9fWZ1bmN0aW9uIFooKXt9dmFyIHR0PW51bGwhPW5ldyBHKHt4ZG9tYWluOiExfSkucmVzcG9uc2VUeXBlLGV0PWZ1bmN0aW9uKHQpe28ocyx0KTt2YXIgbj1wKHMpO2Z1bmN0aW9uIHModCl7dmFyIHI7aWYoZSh0aGlzLHMpLChyPW4uY2FsbCh0aGlzLHQpKS5wb2xsaW5nPSExLCJ1bmRlZmluZWQiIT10eXBlb2YgbG9jYXRpb24pe3ZhciBpPSJodHRwczoiPT09bG9jYXRpb24ucHJvdG9jb2wsbz1sb2NhdGlvbi5wb3J0O298fChvPWk/IjQ0MyI6IjgwIiksci54ZD0idW5kZWZpbmVkIiE9dHlwZW9mIGxvY2F0aW9uJiZ0Lmhvc3RuYW1lIT09bG9jYXRpb24uaG9zdG5hbWV8fG8hPT10LnBvcnQsci54cz10LnNlY3VyZSE9PWl9dmFyIGE9dCYmdC5mb3JjZUJhc2U2NDtyZXR1cm4gci5zdXBwb3J0c0JpbmFyeT10dCYmIWEscn1yZXR1cm4gcihzLFt7a2V5OiJuYW1lIixnZXQ6ZnVuY3Rpb24oKXtyZXR1cm4icG9sbGluZyJ9fSx7a2V5OiJkb09wZW4iLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5wb2xsKCl9fSx7a2V5OiJwYXVzZSIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9dGhpczt0aGlzLnJlYWR5U3RhdGU9InBhdXNpbmciO3ZhciBuPWZ1bmN0aW9uKCl7ZS5yZWFkeVN0YXRlPSJwYXVzZWQiLHQoKX07aWYodGhpcy5wb2xsaW5nfHwhdGhpcy53cml0YWJsZSl7dmFyIHI9MDt0aGlzLnBvbGxpbmcmJihyKyssdGhpcy5vbmNlKCJwb2xsQ29tcGxldGUiLChmdW5jdGlvbigpey0tcnx8bigpfSkpKSx0aGlzLndyaXRhYmxlfHwocisrLHRoaXMub25jZSgiZHJhaW4iLChmdW5jdGlvbigpey0tcnx8bigpfSkpKX1lbHNlIG4oKX19LHtrZXk6InBvbGwiLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5wb2xsaW5nPSEwLHRoaXMuZG9Qb2xsKCksdGhpcy5lbWl0UmVzZXJ2ZWQoInBvbGwiKX19LHtrZXk6Im9uRGF0YSIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9dGhpczsoZnVuY3Rpb24odCxlKXtmb3IodmFyIG49dC5zcGxpdCh4KSxyPVtdLGk9MDtpPG4ubGVuZ3RoO2krKyl7dmFyIG89QihuW2ldLGUpO2lmKHIucHVzaChvKSwiZXJyb3IiPT09by50eXBlKWJyZWFrfXJldHVybiByfSkodCx0aGlzLnNvY2tldC5iaW5hcnlUeXBlKS5mb3JFYWNoKChmdW5jdGlvbih0KXtpZigib3BlbmluZyI9PT1lLnJlYWR5U3RhdGUmJiJvcGVuIj09PXQudHlwZSYmZS5vbk9wZW4oKSwiY2xvc2UiPT09dC50eXBlKXJldHVybiBlLm9uQ2xvc2Uoe2Rlc2NyaXB0aW9uOiJ0cmFuc3BvcnQgY2xvc2VkIGJ5IHRoZSBzZXJ2ZXIifSksITE7ZS5vblBhY2tldCh0KX0pKSwiY2xvc2VkIiE9PXRoaXMucmVhZHlTdGF0ZSYmKHRoaXMucG9sbGluZz0hMSx0aGlzLmVtaXRSZXNlcnZlZCgicG9sbENvbXBsZXRlIiksIm9wZW4iPT09dGhpcy5yZWFkeVN0YXRlJiZ0aGlzLnBvbGwoKSl9fSx7a2V5OiJkb0Nsb3NlIix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PXRoaXMsZT1mdW5jdGlvbigpe3Qud3JpdGUoW3t0eXBlOiJjbG9zZSJ9XSl9OyJvcGVuIj09PXRoaXMucmVhZHlTdGF0ZT9lKCk6dGhpcy5vbmNlKCJvcGVuIixlKX19LHtrZXk6IndyaXRlIix2YWx1ZTpmdW5jdGlvbih0KXt2YXIgZT10aGlzO3RoaXMud3JpdGFibGU9ITEsZnVuY3Rpb24odCxlKXt2YXIgbj10Lmxlbmd0aCxyPW5ldyBBcnJheShuKSxpPTA7dC5mb3JFYWNoKChmdW5jdGlvbih0LG8pe0UodCwhMSwoZnVuY3Rpb24odCl7cltvXT10LCsraT09PW4mJmUoci5qb2luKHgpKX0pKX0pKX0odCwoZnVuY3Rpb24odCl7ZS5kb1dyaXRlKHQsKGZ1bmN0aW9uKCl7ZS53cml0YWJsZT0hMCxlLmVtaXRSZXNlcnZlZCgiZHJhaW4iKX0pKX0pKX19LHtrZXk6InVyaSIsdmFsdWU6ZnVuY3Rpb24oKXt2YXIgdD10aGlzLnF1ZXJ5fHx7fSxlPXRoaXMub3B0cy5zZWN1cmU/Imh0dHBzIjoiaHR0cCIsbj0iIjshMSE9PXRoaXMub3B0cy50aW1lc3RhbXBSZXF1ZXN0cyYmKHRbdGhpcy5vcHRzLnRpbWVzdGFtcFBhcmFtXT1XKCkpLHRoaXMuc3VwcG9ydHNCaW5hcnl8fHQuc2lkfHwodC5iNjQ9MSksdGhpcy5vcHRzLnBvcnQmJigiaHR0cHMiPT09ZSYmNDQzIT09TnVtYmVyKHRoaXMub3B0cy5wb3J0KXx8Imh0dHAiPT09ZSYmODAhPT1OdW1iZXIodGhpcy5vcHRzLnBvcnQpKSYmKG49IjoiK3RoaXMub3B0cy5wb3J0KTt2YXIgcj0kKHQpO3JldHVybiBlKyI6Ly8iKygtMSE9PXRoaXMub3B0cy5ob3N0bmFtZS5pbmRleE9mKCI6Iik/IlsiK3RoaXMub3B0cy5ob3N0bmFtZSsiXSI6dGhpcy5vcHRzLmhvc3RuYW1lKStuK3RoaXMub3B0cy5wYXRoKyhyLmxlbmd0aD8iPyIrcjoiIil9fSx7a2V5OiJyZXF1ZXN0Iix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PWFyZ3VtZW50cy5sZW5ndGg+MCYmdm9pZCAwIT09YXJndW1lbnRzWzBdP2FyZ3VtZW50c1swXTp7fTtyZXR1cm4gaSh0LHt4ZDp0aGlzLnhkLHhzOnRoaXMueHN9LHRoaXMub3B0cyksbmV3IG50KHRoaXMudXJpKCksdCl9fSx7a2V5OiJkb1dyaXRlIix2YWx1ZTpmdW5jdGlvbih0LGUpe3ZhciBuPXRoaXMscj10aGlzLnJlcXVlc3Qoe21ldGhvZDoiUE9TVCIsZGF0YTp0fSk7ci5vbigic3VjY2VzcyIsZSksci5vbigiZXJyb3IiLChmdW5jdGlvbih0LGUpe24ub25FcnJvcigieGhyIHBvc3QgZXJyb3IiLHQsZSl9KSl9fSx7a2V5OiJkb1BvbGwiLHZhbHVlOmZ1bmN0aW9uKCl7dmFyIHQ9dGhpcyxlPXRoaXMucmVxdWVzdCgpO2Uub24oImRhdGEiLHRoaXMub25EYXRhLmJpbmQodGhpcykpLGUub24oImVycm9yIiwoZnVuY3Rpb24oZSxuKXt0Lm9uRXJyb3IoInhociBwb2xsIGVycm9yIixlLG4pfSkpLHRoaXMucG9sbFhocj1lfX1dKSxzfShVKSxudD1mdW5jdGlvbih0KXtvKGksdCk7dmFyIG49cChpKTtmdW5jdGlvbiBpKHQscil7dmFyIG87cmV0dXJuIGUodGhpcyxpKSxEKGYobz1uLmNhbGwodGhpcykpLHIpLG8ub3B0cz1yLG8ubWV0aG9kPXIubWV0aG9kfHwiR0VUIixvLnVyaT10LG8uYXN5bmM9ITEhPT1yLmFzeW5jLG8uZGF0YT12b2lkIDAhPT1yLmRhdGE/ci5kYXRhOm51bGwsby5jcmVhdGUoKSxvfXJldHVybiByKGksW3trZXk6ImNyZWF0ZSIsdmFsdWU6ZnVuY3Rpb24oKXt2YXIgdD10aGlzLGU9aih0aGlzLm9wdHMsImFnZW50IiwicGZ4Iiwia2V5IiwicGFzc3BocmFzZSIsImNlcnQiLCJjYSIsImNpcGhlcnMiLCJyZWplY3RVbmF1dGhvcml6ZWQiLCJhdXRvVW5yZWYiKTtlLnhkb21haW49ISF0aGlzLm9wdHMueGQsZS54c2NoZW1lPSEhdGhpcy5vcHRzLnhzO3ZhciBuPXRoaXMueGhyPW5ldyBHKGUpO3RyeXtuLm9wZW4odGhpcy5tZXRob2QsdGhpcy51cmksdGhpcy5hc3luYyk7dHJ5e2lmKHRoaXMub3B0cy5leHRyYUhlYWRlcnMpZm9yKHZhciByIGluIG4uc2V0RGlzYWJsZUhlYWRlckNoZWNrJiZuLnNldERpc2FibGVIZWFkZXJDaGVjayghMCksdGhpcy5vcHRzLmV4dHJhSGVhZGVycyl0aGlzLm9wdHMuZXh0cmFIZWFkZXJzLmhhc093blByb3BlcnR5KHIpJiZuLnNldFJlcXVlc3RIZWFkZXIocix0aGlzLm9wdHMuZXh0cmFIZWFkZXJzW3JdKX1jYXRjaCh0KXt9aWYoIlBPU1QiPT09dGhpcy5tZXRob2QpdHJ5e24uc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwidGV4dC9wbGFpbjtjaGFyc2V0PVVURi04Iil9Y2F0Y2godCl7fXRyeXtuLnNldFJlcXVlc3RIZWFkZXIoIkFjY2VwdCIsIiovKiIpfWNhdGNoKHQpe30id2l0aENyZWRlbnRpYWxzImluIG4mJihuLndpdGhDcmVkZW50aWFscz10aGlzLm9wdHMud2l0aENyZWRlbnRpYWxzKSx0aGlzLm9wdHMucmVxdWVzdFRpbWVvdXQmJihuLnRpbWVvdXQ9dGhpcy5vcHRzLnJlcXVlc3RUaW1lb3V0KSxuLm9ucmVhZHlzdGF0ZWNoYW5nZT1mdW5jdGlvbigpezQ9PT1uLnJlYWR5U3RhdGUmJigyMDA9PT1uLnN0YXR1c3x8MTIyMz09PW4uc3RhdHVzP3Qub25Mb2FkKCk6dC5zZXRUaW1lb3V0Rm4oKGZ1bmN0aW9uKCl7dC5vbkVycm9yKCJudW1iZXIiPT10eXBlb2Ygbi5zdGF0dXM/bi5zdGF0dXM6MCl9KSwwKSl9LG4uc2VuZCh0aGlzLmRhdGEpfWNhdGNoKGUpe3JldHVybiB2b2lkIHRoaXMuc2V0VGltZW91dEZuKChmdW5jdGlvbigpe3Qub25FcnJvcihlKX0pLDApfSJ1bmRlZmluZWQiIT10eXBlb2YgZG9jdW1lbnQmJih0aGlzLmluZGV4PWkucmVxdWVzdHNDb3VudCsrLGkucmVxdWVzdHNbdGhpcy5pbmRleF09dGhpcyl9fSx7a2V5OiJvbkVycm9yIix2YWx1ZTpmdW5jdGlvbih0KXt0aGlzLmVtaXRSZXNlcnZlZCgiZXJyb3IiLHQsdGhpcy54aHIpLHRoaXMuY2xlYW51cCghMCl9fSx7a2V5OiJjbGVhbnVwIix2YWx1ZTpmdW5jdGlvbih0KXtpZih2b2lkIDAhPT10aGlzLnhociYmbnVsbCE9PXRoaXMueGhyKXtpZih0aGlzLnhoci5vbnJlYWR5c3RhdGVjaGFuZ2U9Wix0KXRyeXt0aGlzLnhoci5hYm9ydCgpfWNhdGNoKHQpe30idW5kZWZpbmVkIiE9dHlwZW9mIGRvY3VtZW50JiZkZWxldGUgaS5yZXF1ZXN0c1t0aGlzLmluZGV4XSx0aGlzLnhocj1udWxsfX19LHtrZXk6Im9uTG9hZCIsdmFsdWU6ZnVuY3Rpb24oKXt2YXIgdD10aGlzLnhoci5yZXNwb25zZVRleHQ7bnVsbCE9PXQmJih0aGlzLmVtaXRSZXNlcnZlZCgiZGF0YSIsdCksdGhpcy5lbWl0UmVzZXJ2ZWQoInN1Y2Nlc3MiKSx0aGlzLmNsZWFudXAoKSl9fSx7a2V5OiJhYm9ydCIsdmFsdWU6ZnVuY3Rpb24oKXt0aGlzLmNsZWFudXAoKX19XSksaX0oTCk7aWYobnQucmVxdWVzdHNDb3VudD0wLG50LnJlcXVlc3RzPXt9LCJ1bmRlZmluZWQiIT10eXBlb2YgZG9jdW1lbnQpaWYoImZ1bmN0aW9uIj09dHlwZW9mIGF0dGFjaEV2ZW50KWF0dGFjaEV2ZW50KCJvbnVubG9hZCIscnQpO2Vsc2UgaWYoImZ1bmN0aW9uIj09dHlwZW9mIGFkZEV2ZW50TGlzdGVuZXIpe2FkZEV2ZW50TGlzdGVuZXIoIm9ucGFnZWhpZGUiaW4gUD8icGFnZWhpZGUiOiJ1bmxvYWQiLHJ0LCExKX1mdW5jdGlvbiBydCgpe2Zvcih2YXIgdCBpbiBudC5yZXF1ZXN0cyludC5yZXF1ZXN0cy5oYXNPd25Qcm9wZXJ0eSh0KSYmbnQucmVxdWVzdHNbdF0uYWJvcnQoKX12YXIgaXQ9ImZ1bmN0aW9uIj09dHlwZW9mIFByb21pc2UmJiJmdW5jdGlvbiI9PXR5cGVvZiBQcm9taXNlLnJlc29sdmU/ZnVuY3Rpb24odCl7cmV0dXJuIFByb21pc2UucmVzb2x2ZSgpLnRoZW4odCl9OmZ1bmN0aW9uKHQsZSl7cmV0dXJuIGUodCwwKX0sb3Q9UC5XZWJTb2NrZXR8fFAuTW96V2ViU29ja2V0LHN0PSJ1bmRlZmluZWQiIT10eXBlb2YgbmF2aWdhdG9yJiYic3RyaW5nIj09dHlwZW9mIG5hdmlnYXRvci5wcm9kdWN0JiYicmVhY3RuYXRpdmUiPT09bmF2aWdhdG9yLnByb2R1Y3QudG9Mb3dlckNhc2UoKSxhdD1mdW5jdGlvbih0KXtvKGksdCk7dmFyIG49cChpKTtmdW5jdGlvbiBpKHQpe3ZhciByO3JldHVybiBlKHRoaXMsaSksKHI9bi5jYWxsKHRoaXMsdCkpLnN1cHBvcnRzQmluYXJ5PSF0LmZvcmNlQmFzZTY0LHJ9cmV0dXJuIHIoaSxbe2tleToibmFtZSIsZ2V0OmZ1bmN0aW9uKCl7cmV0dXJuIndlYnNvY2tldCJ9fSx7a2V5OiJkb09wZW4iLHZhbHVlOmZ1bmN0aW9uKCl7aWYodGhpcy5jaGVjaygpKXt2YXIgdD10aGlzLnVyaSgpLGU9dGhpcy5vcHRzLnByb3RvY29scyxuPXN0P3t9OmoodGhpcy5vcHRzLCJhZ2VudCIsInBlck1lc3NhZ2VEZWZsYXRlIiwicGZ4Iiwia2V5IiwicGFzc3BocmFzZSIsImNlcnQiLCJjYSIsImNpcGhlcnMiLCJyZWplY3RVbmF1dGhvcml6ZWQiLCJsb2NhbEFkZHJlc3MiLCJwcm90b2NvbFZlcnNpb24iLCJvcmlnaW4iLCJtYXhQYXlsb2FkIiwiZmFtaWx5IiwiY2hlY2tTZXJ2ZXJJZGVudGl0eSIpO3RoaXMub3B0cy5leHRyYUhlYWRlcnMmJihuLmhlYWRlcnM9dGhpcy5vcHRzLmV4dHJhSGVhZGVycyk7dHJ5e3RoaXMud3M9c3Q/bmV3IG90KHQsZSxuKTplP25ldyBvdCh0LGUpOm5ldyBvdCh0KX1jYXRjaCh0KXtyZXR1cm4gdGhpcy5lbWl0UmVzZXJ2ZWQoImVycm9yIix0KX10aGlzLndzLmJpbmFyeVR5cGU9dGhpcy5zb2NrZXQuYmluYXJ5VHlwZXx8ImFycmF5YnVmZmVyIix0aGlzLmFkZEV2ZW50TGlzdGVuZXJzKCl9fX0se2tleToiYWRkRXZlbnRMaXN0ZW5lcnMiLHZhbHVlOmZ1bmN0aW9uKCl7dmFyIHQ9dGhpczt0aGlzLndzLm9ub3Blbj1mdW5jdGlvbigpe3Qub3B0cy5hdXRvVW5yZWYmJnQud3MuX3NvY2tldC51bnJlZigpLHQub25PcGVuKCl9LHRoaXMud3Mub25jbG9zZT1mdW5jdGlvbihlKXtyZXR1cm4gdC5vbkNsb3NlKHtkZXNjcmlwdGlvbjoid2Vic29ja2V0IGNvbm5lY3Rpb24gY2xvc2VkIixjb250ZXh0OmV9KX0sdGhpcy53cy5vbm1lc3NhZ2U9ZnVuY3Rpb24oZSl7cmV0dXJuIHQub25EYXRhKGUuZGF0YSl9LHRoaXMud3Mub25lcnJvcj1mdW5jdGlvbihlKXtyZXR1cm4gdC5vbkVycm9yKCJ3ZWJzb2NrZXQgZXJyb3IiLGUpfX19LHtrZXk6IndyaXRlIix2YWx1ZTpmdW5jdGlvbih0KXt2YXIgZT10aGlzO3RoaXMud3JpdGFibGU9ITE7Zm9yKHZhciBuPWZ1bmN0aW9uKG4pe3ZhciByPXRbbl0saT1uPT09dC5sZW5ndGgtMTtFKHIsZS5zdXBwb3J0c0JpbmFyeSwoZnVuY3Rpb24odCl7dHJ5e2Uud3Muc2VuZCh0KX1jYXRjaCh0KXt9aSYmaXQoKGZ1bmN0aW9uKCl7ZS53cml0YWJsZT0hMCxlLmVtaXRSZXNlcnZlZCgiZHJhaW4iKX0pLGUuc2V0VGltZW91dEZuKX0pKX0scj0wO3I8dC5sZW5ndGg7cisrKW4ocil9fSx7a2V5OiJkb0Nsb3NlIix2YWx1ZTpmdW5jdGlvbigpe3ZvaWQgMCE9PXRoaXMud3MmJih0aGlzLndzLmNsb3NlKCksdGhpcy53cz1udWxsKX19LHtrZXk6InVyaSIsdmFsdWU6ZnVuY3Rpb24oKXt2YXIgdD10aGlzLnF1ZXJ5fHx7fSxlPXRoaXMub3B0cy5zZWN1cmU/IndzcyI6IndzIixuPSIiO3RoaXMub3B0cy5wb3J0JiYoIndzcyI9PT1lJiY0NDMhPT1OdW1iZXIodGhpcy5vcHRzLnBvcnQpfHwid3MiPT09ZSYmODAhPT1OdW1iZXIodGhpcy5vcHRzLnBvcnQpKSYmKG49IjoiK3RoaXMub3B0cy5wb3J0KSx0aGlzLm9wdHMudGltZXN0YW1wUmVxdWVzdHMmJih0W3RoaXMub3B0cy50aW1lc3RhbXBQYXJhbV09VygpKSx0aGlzLnN1cHBvcnRzQmluYXJ5fHwodC5iNjQ9MSk7dmFyIHI9JCh0KTtyZXR1cm4gZSsiOi8vIisoLTEhPT10aGlzLm9wdHMuaG9zdG5hbWUuaW5kZXhPZigiOiIpPyJbIit0aGlzLm9wdHMuaG9zdG5hbWUrIl0iOnRoaXMub3B0cy5ob3N0bmFtZSkrbit0aGlzLm9wdHMucGF0aCsoci5sZW5ndGg/Ij8iK3I6IiIpfX0se2tleToiY2hlY2siLHZhbHVlOmZ1bmN0aW9uKCl7cmV0dXJuISFvdH19XSksaX0oVSksY3Q9e3dlYnNvY2tldDphdCxwb2xsaW5nOmV0fSx1dD0vXig/Oig/IVteOkBcLz8jXSs6W146QFwvXSpAKShodHRwfGh0dHBzfHdzfHdzcyk6XC9cLyk/KCg/OigoW146QFwvPyNdKikoPzo6KFteOkBcLz8jXSopKT8pP0ApPygoPzpbYS1mMC05XXswLDR9Oil7Miw3fVthLWYwLTldezAsNH18W146XC8/I10qKSg/OjooXGQqKSk/KSgoKFwvKD86W14/I10oPyFbXj8jXC9dKlwuW14/I1wvLl0rKD86Wz8jXXwkKSkpKlwvPyk/KFtePyNcL10qKSkoPzpcPyhbXiNdKikpPyg/OiMoLiopKT8pLyxodD1bInNvdXJjZSIsInByb3RvY29sIiwiYXV0aG9yaXR5IiwidXNlckluZm8iLCJ1c2VyIiwicGFzc3dvcmQiLCJob3N0IiwicG9ydCIsInJlbGF0aXZlIiwicGF0aCIsImRpcmVjdG9yeSIsImZpbGUiLCJxdWVyeSIsImFuY2hvciJdO2Z1bmN0aW9uIGZ0KHQpe3ZhciBlPXQsbj10LmluZGV4T2YoIlsiKSxyPXQuaW5kZXhPZigiXSIpOy0xIT1uJiYtMSE9ciYmKHQ9dC5zdWJzdHJpbmcoMCxuKSt0LnN1YnN0cmluZyhuLHIpLnJlcGxhY2UoLzovZywiOyIpK3Quc3Vic3RyaW5nKHIsdC5sZW5ndGgpKTtmb3IodmFyIGksbyxzPXV0LmV4ZWModHx8IiIpLGE9e30sYz0xNDtjLS07KWFbaHRbY11dPXNbY118fCIiO3JldHVybi0xIT1uJiYtMSE9ciYmKGEuc291cmNlPWUsYS5ob3N0PWEuaG9zdC5zdWJzdHJpbmcoMSxhLmhvc3QubGVuZ3RoLTEpLnJlcGxhY2UoLzsvZywiOiIpLGEuYXV0aG9yaXR5PWEuYXV0aG9yaXR5LnJlcGxhY2UoIlsiLCIiKS5yZXBsYWNlKCJdIiwiIikucmVwbGFjZSgvOy9nLCI6IiksYS5pcHY2dXJpPSEwKSxhLnBhdGhOYW1lcz1mdW5jdGlvbih0LGUpe3ZhciBuPS9cL3syLDl9L2cscj1lLnJlcGxhY2UobiwiLyIpLnNwbGl0KCIvIik7Ii8iIT1lLnNsaWNlKDAsMSkmJjAhPT1lLmxlbmd0aHx8ci5zcGxpY2UoMCwxKTsiLyI9PWUuc2xpY2UoLTEpJiZyLnNwbGljZShyLmxlbmd0aC0xLDEpO3JldHVybiByfSgwLGEucGF0aCksYS5xdWVyeUtleT0oaT1hLnF1ZXJ5LG89e30saS5yZXBsYWNlKC8oPzpefCYpKFteJj1dKik9PyhbXiZdKikvZywoZnVuY3Rpb24odCxlLG4pe2UmJihvW2VdPW4pfSkpLG8pLGF9dmFyIGx0PWZ1bmN0aW9uKG4pe28oYSxuKTt2YXIgcz1wKGEpO2Z1bmN0aW9uIGEobil7dmFyIHIsbz1hcmd1bWVudHMubGVuZ3RoPjEmJnZvaWQgMCE9PWFyZ3VtZW50c1sxXT9hcmd1bWVudHNbMV06e307cmV0dXJuIGUodGhpcyxhKSwocj1zLmNhbGwodGhpcykpLndyaXRlQnVmZmVyPVtdLG4mJiJvYmplY3QiPT09dChuKSYmKG89bixuPW51bGwpLG4/KG49ZnQobiksby5ob3N0bmFtZT1uLmhvc3Qsby5zZWN1cmU9Imh0dHBzIj09PW4ucHJvdG9jb2x8fCJ3c3MiPT09bi5wcm90b2NvbCxvLnBvcnQ9bi5wb3J0LG4ucXVlcnkmJihvLnF1ZXJ5PW4ucXVlcnkpKTpvLmhvc3QmJihvLmhvc3RuYW1lPWZ0KG8uaG9zdCkuaG9zdCksRChmKHIpLG8pLHIuc2VjdXJlPW51bGwhPW8uc2VjdXJlP28uc2VjdXJlOiJ1bmRlZmluZWQiIT10eXBlb2YgbG9jYXRpb24mJiJodHRwczoiPT09bG9jYXRpb24ucHJvdG9jb2wsby5ob3N0bmFtZSYmIW8ucG9ydCYmKG8ucG9ydD1yLnNlY3VyZT8iNDQzIjoiODAiKSxyLmhvc3RuYW1lPW8uaG9zdG5hbWV8fCgidW5kZWZpbmVkIiE9dHlwZW9mIGxvY2F0aW9uP2xvY2F0aW9uLmhvc3RuYW1lOiJsb2NhbGhvc3QiKSxyLnBvcnQ9by5wb3J0fHwoInVuZGVmaW5lZCIhPXR5cGVvZiBsb2NhdGlvbiYmbG9jYXRpb24ucG9ydD9sb2NhdGlvbi5wb3J0OnIuc2VjdXJlPyI0NDMiOiI4MCIpLHIudHJhbnNwb3J0cz1vLnRyYW5zcG9ydHN8fFsicG9sbGluZyIsIndlYnNvY2tldCJdLHIud3JpdGVCdWZmZXI9W10sci5wcmV2QnVmZmVyTGVuPTAsci5vcHRzPWkoe3BhdGg6Ii9lbmdpbmUuaW8iLGFnZW50OiExLHdpdGhDcmVkZW50aWFsczohMSx1cGdyYWRlOiEwLHRpbWVzdGFtcFBhcmFtOiJ0IixyZW1lbWJlclVwZ3JhZGU6ITEsYWRkVHJhaWxpbmdTbGFzaDohMCxyZWplY3RVbmF1dGhvcml6ZWQ6ITAscGVyTWVzc2FnZURlZmxhdGU6e3RocmVzaG9sZDoxMDI0fSx0cmFuc3BvcnRPcHRpb25zOnt9LGNsb3NlT25CZWZvcmV1bmxvYWQ6ITB9LG8pLHIub3B0cy5wYXRoPXIub3B0cy5wYXRoLnJlcGxhY2UoL1wvJC8sIiIpKyhyLm9wdHMuYWRkVHJhaWxpbmdTbGFzaD8iLyI6IiIpLCJzdHJpbmciPT10eXBlb2Ygci5vcHRzLnF1ZXJ5JiYoci5vcHRzLnF1ZXJ5PUooci5vcHRzLnF1ZXJ5KSksci5pZD1udWxsLHIudXBncmFkZXM9bnVsbCxyLnBpbmdJbnRlcnZhbD1udWxsLHIucGluZ1RpbWVvdXQ9bnVsbCxyLnBpbmdUaW1lb3V0VGltZXI9bnVsbCwiZnVuY3Rpb24iPT10eXBlb2YgYWRkRXZlbnRMaXN0ZW5lciYmKHIub3B0cy5jbG9zZU9uQmVmb3JldW5sb2FkJiYoci5iZWZvcmV1bmxvYWRFdmVudExpc3RlbmVyPWZ1bmN0aW9uKCl7ci50cmFuc3BvcnQmJihyLnRyYW5zcG9ydC5yZW1vdmVBbGxMaXN0ZW5lcnMoKSxyLnRyYW5zcG9ydC5jbG9zZSgpKX0sYWRkRXZlbnRMaXN0ZW5lcigiYmVmb3JldW5sb2FkIixyLmJlZm9yZXVubG9hZEV2ZW50TGlzdGVuZXIsITEpKSwibG9jYWxob3N0IiE9PXIuaG9zdG5hbWUmJihyLm9mZmxpbmVFdmVudExpc3RlbmVyPWZ1bmN0aW9uKCl7ci5vbkNsb3NlKCJ0cmFuc3BvcnQgY2xvc2UiLHtkZXNjcmlwdGlvbjoibmV0d29yayBjb25uZWN0aW9uIGxvc3QifSl9LGFkZEV2ZW50TGlzdGVuZXIoIm9mZmxpbmUiLHIub2ZmbGluZUV2ZW50TGlzdGVuZXIsITEpKSksci5vcGVuKCkscn1yZXR1cm4gcihhLFt7a2V5OiJjcmVhdGVUcmFuc3BvcnQiLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlPWkoe30sdGhpcy5vcHRzLnF1ZXJ5KTtlLkVJTz00LGUudHJhbnNwb3J0PXQsdGhpcy5pZCYmKGUuc2lkPXRoaXMuaWQpO3ZhciBuPWkoe30sdGhpcy5vcHRzLnRyYW5zcG9ydE9wdGlvbnNbdF0sdGhpcy5vcHRzLHtxdWVyeTplLHNvY2tldDp0aGlzLGhvc3RuYW1lOnRoaXMuaG9zdG5hbWUsc2VjdXJlOnRoaXMuc2VjdXJlLHBvcnQ6dGhpcy5wb3J0fSk7cmV0dXJuIG5ldyBjdFt0XShuKX19LHtrZXk6Im9wZW4iLHZhbHVlOmZ1bmN0aW9uKCl7dmFyIHQsZT10aGlzO2lmKHRoaXMub3B0cy5yZW1lbWJlclVwZ3JhZGUmJmEucHJpb3JXZWJzb2NrZXRTdWNjZXNzJiYtMSE9PXRoaXMudHJhbnNwb3J0cy5pbmRleE9mKCJ3ZWJzb2NrZXQiKSl0PSJ3ZWJzb2NrZXQiO2Vsc2V7aWYoMD09PXRoaXMudHJhbnNwb3J0cy5sZW5ndGgpcmV0dXJuIHZvaWQgdGhpcy5zZXRUaW1lb3V0Rm4oKGZ1bmN0aW9uKCl7ZS5lbWl0UmVzZXJ2ZWQoImVycm9yIiwiTm8gdHJhbnNwb3J0cyBhdmFpbGFibGUiKX0pLDApO3Q9dGhpcy50cmFuc3BvcnRzWzBdfXRoaXMucmVhZHlTdGF0ZT0ib3BlbmluZyI7dHJ5e3Q9dGhpcy5jcmVhdGVUcmFuc3BvcnQodCl9Y2F0Y2godCl7cmV0dXJuIHRoaXMudHJhbnNwb3J0cy5zaGlmdCgpLHZvaWQgdGhpcy5vcGVuKCl9dC5vcGVuKCksdGhpcy5zZXRUcmFuc3BvcnQodCl9fSx7a2V5OiJzZXRUcmFuc3BvcnQiLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlPXRoaXM7dGhpcy50cmFuc3BvcnQmJnRoaXMudHJhbnNwb3J0LnJlbW92ZUFsbExpc3RlbmVycygpLHRoaXMudHJhbnNwb3J0PXQsdC5vbigiZHJhaW4iLHRoaXMub25EcmFpbi5iaW5kKHRoaXMpKS5vbigicGFja2V0Iix0aGlzLm9uUGFja2V0LmJpbmQodGhpcykpLm9uKCJlcnJvciIsdGhpcy5vbkVycm9yLmJpbmQodGhpcykpLm9uKCJjbG9zZSIsKGZ1bmN0aW9uKHQpe3JldHVybiBlLm9uQ2xvc2UoInRyYW5zcG9ydCBjbG9zZSIsdCl9KSl9fSx7a2V5OiJwcm9iZSIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9dGhpcyxuPXRoaXMuY3JlYXRlVHJhbnNwb3J0KHQpLHI9ITE7YS5wcmlvcldlYnNvY2tldFN1Y2Nlc3M9ITE7dmFyIGk9ZnVuY3Rpb24oKXtyfHwobi5zZW5kKFt7dHlwZToicGluZyIsZGF0YToicHJvYmUifV0pLG4ub25jZSgicGFja2V0IiwoZnVuY3Rpb24odCl7aWYoIXIpaWYoInBvbmciPT09dC50eXBlJiYicHJvYmUiPT09dC5kYXRhKXtpZihlLnVwZ3JhZGluZz0hMCxlLmVtaXRSZXNlcnZlZCgidXBncmFkaW5nIixuKSwhbilyZXR1cm47YS5wcmlvcldlYnNvY2tldFN1Y2Nlc3M9IndlYnNvY2tldCI9PT1uLm5hbWUsZS50cmFuc3BvcnQucGF1c2UoKGZ1bmN0aW9uKCl7cnx8ImNsb3NlZCIhPT1lLnJlYWR5U3RhdGUmJihmKCksZS5zZXRUcmFuc3BvcnQobiksbi5zZW5kKFt7dHlwZToidXBncmFkZSJ9XSksZS5lbWl0UmVzZXJ2ZWQoInVwZ3JhZGUiLG4pLG49bnVsbCxlLnVwZ3JhZGluZz0hMSxlLmZsdXNoKCkpfSkpfWVsc2V7dmFyIGk9bmV3IEVycm9yKCJwcm9iZSBlcnJvciIpO2kudHJhbnNwb3J0PW4ubmFtZSxlLmVtaXRSZXNlcnZlZCgidXBncmFkZUVycm9yIixpKX19KSkpfTtmdW5jdGlvbiBvKCl7cnx8KHI9ITAsZigpLG4uY2xvc2UoKSxuPW51bGwpfXZhciBzPWZ1bmN0aW9uKHQpe3ZhciByPW5ldyBFcnJvcigicHJvYmUgZXJyb3I6ICIrdCk7ci50cmFuc3BvcnQ9bi5uYW1lLG8oKSxlLmVtaXRSZXNlcnZlZCgidXBncmFkZUVycm9yIixyKX07ZnVuY3Rpb24gYygpe3MoInRyYW5zcG9ydCBjbG9zZWQiKX1mdW5jdGlvbiB1KCl7cygic29ja2V0IGNsb3NlZCIpfWZ1bmN0aW9uIGgodCl7biYmdC5uYW1lIT09bi5uYW1lJiZvKCl9dmFyIGY9ZnVuY3Rpb24oKXtuLnJlbW92ZUxpc3RlbmVyKCJvcGVuIixpKSxuLnJlbW92ZUxpc3RlbmVyKCJlcnJvciIscyksbi5yZW1vdmVMaXN0ZW5lcigiY2xvc2UiLGMpLGUub2ZmKCJjbG9zZSIsdSksZS5vZmYoInVwZ3JhZGluZyIsaCl9O24ub25jZSgib3BlbiIsaSksbi5vbmNlKCJlcnJvciIscyksbi5vbmNlKCJjbG9zZSIsYyksdGhpcy5vbmNlKCJjbG9zZSIsdSksdGhpcy5vbmNlKCJ1cGdyYWRpbmciLGgpLG4ub3BlbigpfX0se2tleToib25PcGVuIix2YWx1ZTpmdW5jdGlvbigpe2lmKHRoaXMucmVhZHlTdGF0ZT0ib3BlbiIsYS5wcmlvcldlYnNvY2tldFN1Y2Nlc3M9IndlYnNvY2tldCI9PT10aGlzLnRyYW5zcG9ydC5uYW1lLHRoaXMuZW1pdFJlc2VydmVkKCJvcGVuIiksdGhpcy5mbHVzaCgpLCJvcGVuIj09PXRoaXMucmVhZHlTdGF0ZSYmdGhpcy5vcHRzLnVwZ3JhZGUpZm9yKHZhciB0PTAsZT10aGlzLnVwZ3JhZGVzLmxlbmd0aDt0PGU7dCsrKXRoaXMucHJvYmUodGhpcy51cGdyYWRlc1t0XSl9fSx7a2V5OiJvblBhY2tldCIsdmFsdWU6ZnVuY3Rpb24odCl7aWYoIm9wZW5pbmciPT09dGhpcy5yZWFkeVN0YXRlfHwib3BlbiI9PT10aGlzLnJlYWR5U3RhdGV8fCJjbG9zaW5nIj09PXRoaXMucmVhZHlTdGF0ZSlzd2l0Y2godGhpcy5lbWl0UmVzZXJ2ZWQoInBhY2tldCIsdCksdGhpcy5lbWl0UmVzZXJ2ZWQoImhlYXJ0YmVhdCIpLHQudHlwZSl7Y2FzZSJvcGVuIjp0aGlzLm9uSGFuZHNoYWtlKEpTT04ucGFyc2UodC5kYXRhKSk7YnJlYWs7Y2FzZSJwaW5nIjp0aGlzLnJlc2V0UGluZ1RpbWVvdXQoKSx0aGlzLnNlbmRQYWNrZXQoInBvbmciKSx0aGlzLmVtaXRSZXNlcnZlZCgicGluZyIpLHRoaXMuZW1pdFJlc2VydmVkKCJwb25nIik7YnJlYWs7Y2FzZSJlcnJvciI6dmFyIGU9bmV3IEVycm9yKCJzZXJ2ZXIgZXJyb3IiKTtlLmNvZGU9dC5kYXRhLHRoaXMub25FcnJvcihlKTticmVhaztjYXNlIm1lc3NhZ2UiOnRoaXMuZW1pdFJlc2VydmVkKCJkYXRhIix0LmRhdGEpLHRoaXMuZW1pdFJlc2VydmVkKCJtZXNzYWdlIix0LmRhdGEpfX19LHtrZXk6Im9uSGFuZHNoYWtlIix2YWx1ZTpmdW5jdGlvbih0KXt0aGlzLmVtaXRSZXNlcnZlZCgiaGFuZHNoYWtlIix0KSx0aGlzLmlkPXQuc2lkLHRoaXMudHJhbnNwb3J0LnF1ZXJ5LnNpZD10LnNpZCx0aGlzLnVwZ3JhZGVzPXRoaXMuZmlsdGVyVXBncmFkZXModC51cGdyYWRlcyksdGhpcy5waW5nSW50ZXJ2YWw9dC5waW5nSW50ZXJ2YWwsdGhpcy5waW5nVGltZW91dD10LnBpbmdUaW1lb3V0LHRoaXMubWF4UGF5bG9hZD10Lm1heFBheWxvYWQsdGhpcy5vbk9wZW4oKSwiY2xvc2VkIiE9PXRoaXMucmVhZHlTdGF0ZSYmdGhpcy5yZXNldFBpbmdUaW1lb3V0KCl9fSx7a2V5OiJyZXNldFBpbmdUaW1lb3V0Iix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PXRoaXM7dGhpcy5jbGVhclRpbWVvdXRGbih0aGlzLnBpbmdUaW1lb3V0VGltZXIpLHRoaXMucGluZ1RpbWVvdXRUaW1lcj10aGlzLnNldFRpbWVvdXRGbigoZnVuY3Rpb24oKXt0Lm9uQ2xvc2UoInBpbmcgdGltZW91dCIpfSksdGhpcy5waW5nSW50ZXJ2YWwrdGhpcy5waW5nVGltZW91dCksdGhpcy5vcHRzLmF1dG9VbnJlZiYmdGhpcy5waW5nVGltZW91dFRpbWVyLnVucmVmKCl9fSx7a2V5OiJvbkRyYWluIix2YWx1ZTpmdW5jdGlvbigpe3RoaXMud3JpdGVCdWZmZXIuc3BsaWNlKDAsdGhpcy5wcmV2QnVmZmVyTGVuKSx0aGlzLnByZXZCdWZmZXJMZW49MCwwPT09dGhpcy53cml0ZUJ1ZmZlci5sZW5ndGg/dGhpcy5lbWl0UmVzZXJ2ZWQoImRyYWluIik6dGhpcy5mbHVzaCgpfX0se2tleToiZmx1c2giLHZhbHVlOmZ1bmN0aW9uKCl7aWYoImNsb3NlZCIhPT10aGlzLnJlYWR5U3RhdGUmJnRoaXMudHJhbnNwb3J0LndyaXRhYmxlJiYhdGhpcy51cGdyYWRpbmcmJnRoaXMud3JpdGVCdWZmZXIubGVuZ3RoKXt2YXIgdD10aGlzLmdldFdyaXRhYmxlUGFja2V0cygpO3RoaXMudHJhbnNwb3J0LnNlbmQodCksdGhpcy5wcmV2QnVmZmVyTGVuPXQubGVuZ3RoLHRoaXMuZW1pdFJlc2VydmVkKCJmbHVzaCIpfX19LHtrZXk6ImdldFdyaXRhYmxlUGFja2V0cyIsdmFsdWU6ZnVuY3Rpb24oKXtpZighKHRoaXMubWF4UGF5bG9hZCYmInBvbGxpbmciPT09dGhpcy50cmFuc3BvcnQubmFtZSYmdGhpcy53cml0ZUJ1ZmZlci5sZW5ndGg+MSkpcmV0dXJuIHRoaXMud3JpdGVCdWZmZXI7Zm9yKHZhciB0LGU9MSxuPTA7bjx0aGlzLndyaXRlQnVmZmVyLmxlbmd0aDtuKyspe3ZhciByPXRoaXMud3JpdGVCdWZmZXJbbl0uZGF0YTtpZihyJiYoZSs9InN0cmluZyI9PXR5cGVvZih0PXIpP2Z1bmN0aW9uKHQpe2Zvcih2YXIgZT0wLG49MCxyPTAsaT10Lmxlbmd0aDtyPGk7cisrKShlPXQuY2hhckNvZGVBdChyKSk8MTI4P24rPTE6ZTwyMDQ4P24rPTI6ZTw1NTI5Nnx8ZT49NTczNDQ/bis9MzoocisrLG4rPTQpO3JldHVybiBufSh0KTpNYXRoLmNlaWwoMS4zMyoodC5ieXRlTGVuZ3RofHx0LnNpemUpKSksbj4wJiZlPnRoaXMubWF4UGF5bG9hZClyZXR1cm4gdGhpcy53cml0ZUJ1ZmZlci5zbGljZSgwLG4pO2UrPTJ9cmV0dXJuIHRoaXMud3JpdGVCdWZmZXJ9fSx7a2V5OiJ3cml0ZSIsdmFsdWU6ZnVuY3Rpb24odCxlLG4pe3JldHVybiB0aGlzLnNlbmRQYWNrZXQoIm1lc3NhZ2UiLHQsZSxuKSx0aGlzfX0se2tleToic2VuZCIsdmFsdWU6ZnVuY3Rpb24odCxlLG4pe3JldHVybiB0aGlzLnNlbmRQYWNrZXQoIm1lc3NhZ2UiLHQsZSxuKSx0aGlzfX0se2tleToic2VuZFBhY2tldCIsdmFsdWU6ZnVuY3Rpb24odCxlLG4scil7aWYoImZ1bmN0aW9uIj09dHlwZW9mIGUmJihyPWUsZT12b2lkIDApLCJmdW5jdGlvbiI9PXR5cGVvZiBuJiYocj1uLG49bnVsbCksImNsb3NpbmciIT09dGhpcy5yZWFkeVN0YXRlJiYiY2xvc2VkIiE9PXRoaXMucmVhZHlTdGF0ZSl7KG49bnx8e30pLmNvbXByZXNzPSExIT09bi5jb21wcmVzczt2YXIgaT17dHlwZTp0LGRhdGE6ZSxvcHRpb25zOm59O3RoaXMuZW1pdFJlc2VydmVkKCJwYWNrZXRDcmVhdGUiLGkpLHRoaXMud3JpdGVCdWZmZXIucHVzaChpKSxyJiZ0aGlzLm9uY2UoImZsdXNoIixyKSx0aGlzLmZsdXNoKCl9fX0se2tleToiY2xvc2UiLHZhbHVlOmZ1bmN0aW9uKCl7dmFyIHQ9dGhpcyxlPWZ1bmN0aW9uKCl7dC5vbkNsb3NlKCJmb3JjZWQgY2xvc2UiKSx0LnRyYW5zcG9ydC5jbG9zZSgpfSxuPWZ1bmN0aW9uIG4oKXt0Lm9mZigidXBncmFkZSIsbiksdC5vZmYoInVwZ3JhZGVFcnJvciIsbiksZSgpfSxyPWZ1bmN0aW9uKCl7dC5vbmNlKCJ1cGdyYWRlIixuKSx0Lm9uY2UoInVwZ3JhZGVFcnJvciIsbil9O3JldHVybiJvcGVuaW5nIiE9PXRoaXMucmVhZHlTdGF0ZSYmIm9wZW4iIT09dGhpcy5yZWFkeVN0YXRlfHwodGhpcy5yZWFkeVN0YXRlPSJjbG9zaW5nIix0aGlzLndyaXRlQnVmZmVyLmxlbmd0aD90aGlzLm9uY2UoImRyYWluIiwoZnVuY3Rpb24oKXt0LnVwZ3JhZGluZz9yKCk6ZSgpfSkpOnRoaXMudXBncmFkaW5nP3IoKTplKCkpLHRoaXN9fSx7a2V5OiJvbkVycm9yIix2YWx1ZTpmdW5jdGlvbih0KXthLnByaW9yV2Vic29ja2V0U3VjY2Vzcz0hMSx0aGlzLmVtaXRSZXNlcnZlZCgiZXJyb3IiLHQpLHRoaXMub25DbG9zZSgidHJhbnNwb3J0IGVycm9yIix0KX19LHtrZXk6Im9uQ2xvc2UiLHZhbHVlOmZ1bmN0aW9uKHQsZSl7Im9wZW5pbmciIT09dGhpcy5yZWFkeVN0YXRlJiYib3BlbiIhPT10aGlzLnJlYWR5U3RhdGUmJiJjbG9zaW5nIiE9PXRoaXMucmVhZHlTdGF0ZXx8KHRoaXMuY2xlYXJUaW1lb3V0Rm4odGhpcy5waW5nVGltZW91dFRpbWVyKSx0aGlzLnRyYW5zcG9ydC5yZW1vdmVBbGxMaXN0ZW5lcnMoImNsb3NlIiksdGhpcy50cmFuc3BvcnQuY2xvc2UoKSx0aGlzLnRyYW5zcG9ydC5yZW1vdmVBbGxMaXN0ZW5lcnMoKSwiZnVuY3Rpb24iPT10eXBlb2YgcmVtb3ZlRXZlbnRMaXN0ZW5lciYmKHJlbW92ZUV2ZW50TGlzdGVuZXIoImJlZm9yZXVubG9hZCIsdGhpcy5iZWZvcmV1bmxvYWRFdmVudExpc3RlbmVyLCExKSxyZW1vdmVFdmVudExpc3RlbmVyKCJvZmZsaW5lIix0aGlzLm9mZmxpbmVFdmVudExpc3RlbmVyLCExKSksdGhpcy5yZWFkeVN0YXRlPSJjbG9zZWQiLHRoaXMuaWQ9bnVsbCx0aGlzLmVtaXRSZXNlcnZlZCgiY2xvc2UiLHQsZSksdGhpcy53cml0ZUJ1ZmZlcj1bXSx0aGlzLnByZXZCdWZmZXJMZW49MCl9fSx7a2V5OiJmaWx0ZXJVcGdyYWRlcyIsdmFsdWU6ZnVuY3Rpb24odCl7Zm9yKHZhciBlPVtdLG49MCxyPXQubGVuZ3RoO248cjtuKyspfnRoaXMudHJhbnNwb3J0cy5pbmRleE9mKHRbbl0pJiZlLnB1c2godFtuXSk7cmV0dXJuIGV9fV0pLGF9KEwpO2x0LnByb3RvY29sPTQsbHQucHJvdG9jb2w7dmFyIHB0PSJmdW5jdGlvbiI9PXR5cGVvZiBBcnJheUJ1ZmZlcixkdD1PYmplY3QucHJvdG90eXBlLnRvU3RyaW5nLHl0PSJmdW5jdGlvbiI9PXR5cGVvZiBCbG9ifHwidW5kZWZpbmVkIiE9dHlwZW9mIEJsb2ImJiJbb2JqZWN0IEJsb2JDb25zdHJ1Y3Rvcl0iPT09ZHQuY2FsbChCbG9iKSx2dD0iZnVuY3Rpb24iPT10eXBlb2YgRmlsZXx8InVuZGVmaW5lZCIhPXR5cGVvZiBGaWxlJiYiW29iamVjdCBGaWxlQ29uc3RydWN0b3JdIj09PWR0LmNhbGwoRmlsZSk7ZnVuY3Rpb24gZ3QodCl7cmV0dXJuIHB0JiYodCBpbnN0YW5jZW9mIEFycmF5QnVmZmVyfHxmdW5jdGlvbih0KXtyZXR1cm4iZnVuY3Rpb24iPT10eXBlb2YgQXJyYXlCdWZmZXIuaXNWaWV3P0FycmF5QnVmZmVyLmlzVmlldyh0KTp0LmJ1ZmZlciBpbnN0YW5jZW9mIEFycmF5QnVmZmVyfSh0KSl8fHl0JiZ0IGluc3RhbmNlb2YgQmxvYnx8dnQmJnQgaW5zdGFuY2VvZiBGaWxlfWZ1bmN0aW9uIG10KGUsbil7aWYoIWV8fCJvYmplY3QiIT09dChlKSlyZXR1cm4hMTtpZihBcnJheS5pc0FycmF5KGUpKXtmb3IodmFyIHI9MCxpPWUubGVuZ3RoO3I8aTtyKyspaWYobXQoZVtyXSkpcmV0dXJuITA7cmV0dXJuITF9aWYoZ3QoZSkpcmV0dXJuITA7aWYoZS50b0pTT04mJiJmdW5jdGlvbiI9PXR5cGVvZiBlLnRvSlNPTiYmMT09PWFyZ3VtZW50cy5sZW5ndGgpcmV0dXJuIG10KGUudG9KU09OKCksITApO2Zvcih2YXIgbyBpbiBlKWlmKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChlLG8pJiZtdChlW29dKSlyZXR1cm4hMDtyZXR1cm4hMX1mdW5jdGlvbiBrdCh0KXt2YXIgZT1bXSxuPXQuZGF0YSxyPXQ7cmV0dXJuIHIuZGF0YT1idChuLGUpLHIuYXR0YWNobWVudHM9ZS5sZW5ndGgse3BhY2tldDpyLGJ1ZmZlcnM6ZX19ZnVuY3Rpb24gYnQoZSxuKXtpZighZSlyZXR1cm4gZTtpZihndChlKSl7dmFyIHI9e19wbGFjZWhvbGRlcjohMCxudW06bi5sZW5ndGh9O3JldHVybiBuLnB1c2goZSkscn1pZihBcnJheS5pc0FycmF5KGUpKXtmb3IodmFyIGk9bmV3IEFycmF5KGUubGVuZ3RoKSxvPTA7bzxlLmxlbmd0aDtvKyspaVtvXT1idChlW29dLG4pO3JldHVybiBpfWlmKCJvYmplY3QiPT09dChlKSYmIShlIGluc3RhbmNlb2YgRGF0ZSkpe3ZhciBzPXt9O2Zvcih2YXIgYSBpbiBlKU9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChlLGEpJiYoc1thXT1idChlW2FdLG4pKTtyZXR1cm4gc31yZXR1cm4gZX1mdW5jdGlvbiB3dCh0LGUpe3JldHVybiB0LmRhdGE9X3QodC5kYXRhLGUpLGRlbGV0ZSB0LmF0dGFjaG1lbnRzLHR9ZnVuY3Rpb24gX3QoZSxuKXtpZighZSlyZXR1cm4gZTtpZihlJiYhMD09PWUuX3BsYWNlaG9sZGVyKXtpZigibnVtYmVyIj09dHlwZW9mIGUubnVtJiZlLm51bT49MCYmZS5udW08bi5sZW5ndGgpcmV0dXJuIG5bZS5udW1dO3Rocm93IG5ldyBFcnJvcigiaWxsZWdhbCBhdHRhY2htZW50cyIpfWlmKEFycmF5LmlzQXJyYXkoZSkpZm9yKHZhciByPTA7cjxlLmxlbmd0aDtyKyspZVtyXT1fdChlW3JdLG4pO2Vsc2UgaWYoIm9iamVjdCI9PT10KGUpKWZvcih2YXIgaSBpbiBlKU9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChlLGkpJiYoZVtpXT1fdChlW2ldLG4pKTtyZXR1cm4gZX12YXIgRXQ7IWZ1bmN0aW9uKHQpe3RbdC5DT05ORUNUPTBdPSJDT05ORUNUIix0W3QuRElTQ09OTkVDVD0xXT0iRElTQ09OTkVDVCIsdFt0LkVWRU5UPTJdPSJFVkVOVCIsdFt0LkFDSz0zXT0iQUNLIix0W3QuQ09OTkVDVF9FUlJPUj00XT0iQ09OTkVDVF9FUlJPUiIsdFt0LkJJTkFSWV9FVkVOVD01XT0iQklOQVJZX0VWRU5UIix0W3QuQklOQVJZX0FDSz02XT0iQklOQVJZX0FDSyJ9KEV0fHwoRXQ9e30pKTt2YXIgT3Q9ZnVuY3Rpb24oKXtmdW5jdGlvbiB0KG4pe2UodGhpcyx0KSx0aGlzLnJlcGxhY2VyPW59cmV0dXJuIHIodCxbe2tleToiZW5jb2RlIix2YWx1ZTpmdW5jdGlvbih0KXtyZXR1cm4gdC50eXBlIT09RXQuRVZFTlQmJnQudHlwZSE9PUV0LkFDS3x8IW10KHQpP1t0aGlzLmVuY29kZUFzU3RyaW5nKHQpXTp0aGlzLmVuY29kZUFzQmluYXJ5KHt0eXBlOnQudHlwZT09PUV0LkVWRU5UP0V0LkJJTkFSWV9FVkVOVDpFdC5CSU5BUllfQUNLLG5zcDp0Lm5zcCxkYXRhOnQuZGF0YSxpZDp0LmlkfSl9fSx7a2V5OiJlbmNvZGVBc1N0cmluZyIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9IiIrdC50eXBlO3JldHVybiB0LnR5cGUhPT1FdC5CSU5BUllfRVZFTlQmJnQudHlwZSE9PUV0LkJJTkFSWV9BQ0t8fChlKz10LmF0dGFjaG1lbnRzKyItIiksdC5uc3AmJiIvIiE9PXQubnNwJiYoZSs9dC5uc3ArIiwiKSxudWxsIT10LmlkJiYoZSs9dC5pZCksbnVsbCE9dC5kYXRhJiYoZSs9SlNPTi5zdHJpbmdpZnkodC5kYXRhLHRoaXMucmVwbGFjZXIpKSxlfX0se2tleToiZW5jb2RlQXNCaW5hcnkiLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlPWt0KHQpLG49dGhpcy5lbmNvZGVBc1N0cmluZyhlLnBhY2tldCkscj1lLmJ1ZmZlcnM7cmV0dXJuIHIudW5zaGlmdChuKSxyfX1dKSx0fSgpLEF0PWZ1bmN0aW9uKG4pe28oYSxuKTt2YXIgaT1wKGEpO2Z1bmN0aW9uIGEodCl7dmFyIG47cmV0dXJuIGUodGhpcyxhKSwobj1pLmNhbGwodGhpcykpLnJldml2ZXI9dCxufXJldHVybiByKGEsW3trZXk6ImFkZCIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU7aWYoInN0cmluZyI9PXR5cGVvZiB0KXtpZih0aGlzLnJlY29uc3RydWN0b3IpdGhyb3cgbmV3IEVycm9yKCJnb3QgcGxhaW50ZXh0IGRhdGEgd2hlbiByZWNvbnN0cnVjdGluZyBhIHBhY2tldCIpO3ZhciBuPShlPXRoaXMuZGVjb2RlU3RyaW5nKHQpKS50eXBlPT09RXQuQklOQVJZX0VWRU5UO258fGUudHlwZT09PUV0LkJJTkFSWV9BQ0s/KGUudHlwZT1uP0V0LkVWRU5UOkV0LkFDSyx0aGlzLnJlY29uc3RydWN0b3I9bmV3IFJ0KGUpLDA9PT1lLmF0dGFjaG1lbnRzJiZ5KHMoYS5wcm90b3R5cGUpLCJlbWl0UmVzZXJ2ZWQiLHRoaXMpLmNhbGwodGhpcywiZGVjb2RlZCIsZSkpOnkocyhhLnByb3RvdHlwZSksImVtaXRSZXNlcnZlZCIsdGhpcykuY2FsbCh0aGlzLCJkZWNvZGVkIixlKX1lbHNle2lmKCFndCh0KSYmIXQuYmFzZTY0KXRocm93IG5ldyBFcnJvcigiVW5rbm93biB0eXBlOiAiK3QpO2lmKCF0aGlzLnJlY29uc3RydWN0b3IpdGhyb3cgbmV3IEVycm9yKCJnb3QgYmluYXJ5IGRhdGEgd2hlbiBub3QgcmVjb25zdHJ1Y3RpbmcgYSBwYWNrZXQiKTsoZT10aGlzLnJlY29uc3RydWN0b3IudGFrZUJpbmFyeURhdGEodCkpJiYodGhpcy5yZWNvbnN0cnVjdG9yPW51bGwseShzKGEucHJvdG90eXBlKSwiZW1pdFJlc2VydmVkIix0aGlzKS5jYWxsKHRoaXMsImRlY29kZWQiLGUpKX19fSx7a2V5OiJkZWNvZGVTdHJpbmciLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlPTAsbj17dHlwZTpOdW1iZXIodC5jaGFyQXQoMCkpfTtpZih2b2lkIDA9PT1FdFtuLnR5cGVdKXRocm93IG5ldyBFcnJvcigidW5rbm93biBwYWNrZXQgdHlwZSAiK24udHlwZSk7aWYobi50eXBlPT09RXQuQklOQVJZX0VWRU5UfHxuLnR5cGU9PT1FdC5CSU5BUllfQUNLKXtmb3IodmFyIHI9ZSsxOyItIiE9PXQuY2hhckF0KCsrZSkmJmUhPXQubGVuZ3RoOyk7dmFyIGk9dC5zdWJzdHJpbmcocixlKTtpZihpIT1OdW1iZXIoaSl8fCItIiE9PXQuY2hhckF0KGUpKXRocm93IG5ldyBFcnJvcigiSWxsZWdhbCBhdHRhY2htZW50cyIpO24uYXR0YWNobWVudHM9TnVtYmVyKGkpfWlmKCIvIj09PXQuY2hhckF0KGUrMSkpe2Zvcih2YXIgbz1lKzE7KytlOyl7aWYoIiwiPT09dC5jaGFyQXQoZSkpYnJlYWs7aWYoZT09PXQubGVuZ3RoKWJyZWFrfW4ubnNwPXQuc3Vic3RyaW5nKG8sZSl9ZWxzZSBuLm5zcD0iLyI7dmFyIHM9dC5jaGFyQXQoZSsxKTtpZigiIiE9PXMmJk51bWJlcihzKT09cyl7Zm9yKHZhciBjPWUrMTsrK2U7KXt2YXIgdT10LmNoYXJBdChlKTtpZihudWxsPT11fHxOdW1iZXIodSkhPXUpey0tZTticmVha31pZihlPT09dC5sZW5ndGgpYnJlYWt9bi5pZD1OdW1iZXIodC5zdWJzdHJpbmcoYyxlKzEpKX1pZih0LmNoYXJBdCgrK2UpKXt2YXIgaD10aGlzLnRyeVBhcnNlKHQuc3Vic3RyKGUpKTtpZighYS5pc1BheWxvYWRWYWxpZChuLnR5cGUsaCkpdGhyb3cgbmV3IEVycm9yKCJpbnZhbGlkIHBheWxvYWQiKTtuLmRhdGE9aH1yZXR1cm4gbn19LHtrZXk6InRyeVBhcnNlIix2YWx1ZTpmdW5jdGlvbih0KXt0cnl7cmV0dXJuIEpTT04ucGFyc2UodCx0aGlzLnJldml2ZXIpfWNhdGNoKHQpe3JldHVybiExfX19LHtrZXk6ImRlc3Ryb3kiLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5yZWNvbnN0cnVjdG9yJiYodGhpcy5yZWNvbnN0cnVjdG9yLmZpbmlzaGVkUmVjb25zdHJ1Y3Rpb24oKSx0aGlzLnJlY29uc3RydWN0b3I9bnVsbCl9fV0sW3trZXk6ImlzUGF5bG9hZFZhbGlkIix2YWx1ZTpmdW5jdGlvbihlLG4pe3N3aXRjaChlKXtjYXNlIEV0LkNPTk5FQ1Q6cmV0dXJuIm9iamVjdCI9PT10KG4pO2Nhc2UgRXQuRElTQ09OTkVDVDpyZXR1cm4gdm9pZCAwPT09bjtjYXNlIEV0LkNPTk5FQ1RfRVJST1I6cmV0dXJuInN0cmluZyI9PXR5cGVvZiBufHwib2JqZWN0Ij09PXQobik7Y2FzZSBFdC5FVkVOVDpjYXNlIEV0LkJJTkFSWV9FVkVOVDpyZXR1cm4gQXJyYXkuaXNBcnJheShuKSYmbi5sZW5ndGg+MDtjYXNlIEV0LkFDSzpjYXNlIEV0LkJJTkFSWV9BQ0s6cmV0dXJuIEFycmF5LmlzQXJyYXkobil9fX1dKSxhfShMKSxSdD1mdW5jdGlvbigpe2Z1bmN0aW9uIHQobil7ZSh0aGlzLHQpLHRoaXMucGFja2V0PW4sdGhpcy5idWZmZXJzPVtdLHRoaXMucmVjb25QYWNrPW59cmV0dXJuIHIodCxbe2tleToidGFrZUJpbmFyeURhdGEiLHZhbHVlOmZ1bmN0aW9uKHQpe2lmKHRoaXMuYnVmZmVycy5wdXNoKHQpLHRoaXMuYnVmZmVycy5sZW5ndGg9PT10aGlzLnJlY29uUGFjay5hdHRhY2htZW50cyl7dmFyIGU9d3QodGhpcy5yZWNvblBhY2ssdGhpcy5idWZmZXJzKTtyZXR1cm4gdGhpcy5maW5pc2hlZFJlY29uc3RydWN0aW9uKCksZX1yZXR1cm4gbnVsbH19LHtrZXk6ImZpbmlzaGVkUmVjb25zdHJ1Y3Rpb24iLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5yZWNvblBhY2s9bnVsbCx0aGlzLmJ1ZmZlcnM9W119fV0pLHR9KCksVHQ9T2JqZWN0LmZyZWV6ZSh7X19wcm90b19fOm51bGwscHJvdG9jb2w6NSxnZXQgUGFja2V0VHlwZSgpe3JldHVybiBFdH0sRW5jb2RlcjpPdCxEZWNvZGVyOkF0fSk7ZnVuY3Rpb24gQ3QodCxlLG4pe3JldHVybiB0Lm9uKGUsbiksZnVuY3Rpb24oKXt0Lm9mZihlLG4pfX12YXIgQnQ9T2JqZWN0LmZyZWV6ZSh7Y29ubmVjdDoxLGNvbm5lY3RfZXJyb3I6MSxkaXNjb25uZWN0OjEsZGlzY29ubmVjdGluZzoxLG5ld0xpc3RlbmVyOjEscmVtb3ZlTGlzdGVuZXI6MX0pLFN0PWZ1bmN0aW9uKHQpe28oYSx0KTt2YXIgbj1wKGEpO2Z1bmN0aW9uIGEodCxyLG8pe3ZhciBzO3JldHVybiBlKHRoaXMsYSksKHM9bi5jYWxsKHRoaXMpKS5jb25uZWN0ZWQ9ITEscy5yZWNvdmVyZWQ9ITEscy5yZWNlaXZlQnVmZmVyPVtdLHMuc2VuZEJ1ZmZlcj1bXSxzLl9xdWV1ZT1bXSxzLl9xdWV1ZVNlcT0wLHMuaWRzPTAscy5hY2tzPXt9LHMuZmxhZ3M9e30scy5pbz10LHMubnNwPXIsbyYmby5hdXRoJiYocy5hdXRoPW8uYXV0aCkscy5fb3B0cz1pKHt9LG8pLHMuaW8uX2F1dG9Db25uZWN0JiZzLm9wZW4oKSxzfXJldHVybiByKGEsW3trZXk6ImRpc2Nvbm5lY3RlZCIsZ2V0OmZ1bmN0aW9uKCl7cmV0dXJuIXRoaXMuY29ubmVjdGVkfX0se2tleToic3ViRXZlbnRzIix2YWx1ZTpmdW5jdGlvbigpe2lmKCF0aGlzLnN1YnMpe3ZhciB0PXRoaXMuaW87dGhpcy5zdWJzPVtDdCh0LCJvcGVuIix0aGlzLm9ub3Blbi5iaW5kKHRoaXMpKSxDdCh0LCJwYWNrZXQiLHRoaXMub25wYWNrZXQuYmluZCh0aGlzKSksQ3QodCwiZXJyb3IiLHRoaXMub25lcnJvci5iaW5kKHRoaXMpKSxDdCh0LCJjbG9zZSIsdGhpcy5vbmNsb3NlLmJpbmQodGhpcykpXX19fSx7a2V5OiJhY3RpdmUiLGdldDpmdW5jdGlvbigpe3JldHVybiEhdGhpcy5zdWJzfX0se2tleToiY29ubmVjdCIsdmFsdWU6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5jb25uZWN0ZWR8fCh0aGlzLnN1YkV2ZW50cygpLHRoaXMuaW8uX3JlY29ubmVjdGluZ3x8dGhpcy5pby5vcGVuKCksIm9wZW4iPT09dGhpcy5pby5fcmVhZHlTdGF0ZSYmdGhpcy5vbm9wZW4oKSksdGhpc319LHtrZXk6Im9wZW4iLHZhbHVlOmZ1bmN0aW9uKCl7cmV0dXJuIHRoaXMuY29ubmVjdCgpfX0se2tleToic2VuZCIsdmFsdWU6ZnVuY3Rpb24oKXtmb3IodmFyIHQ9YXJndW1lbnRzLmxlbmd0aCxlPW5ldyBBcnJheSh0KSxuPTA7bjx0O24rKyllW25dPWFyZ3VtZW50c1tuXTtyZXR1cm4gZS51bnNoaWZ0KCJtZXNzYWdlIiksdGhpcy5lbWl0LmFwcGx5KHRoaXMsZSksdGhpc319LHtrZXk6ImVtaXQiLHZhbHVlOmZ1bmN0aW9uKHQpe2lmKEJ0Lmhhc093blByb3BlcnR5KHQpKXRocm93IG5ldyBFcnJvcignIicrdC50b1N0cmluZygpKyciIGlzIGEgcmVzZXJ2ZWQgZXZlbnQgbmFtZScpO2Zvcih2YXIgZT1hcmd1bWVudHMubGVuZ3RoLG49bmV3IEFycmF5KGU+MT9lLTE6MCkscj0xO3I8ZTtyKyspbltyLTFdPWFyZ3VtZW50c1tyXTtpZihuLnVuc2hpZnQodCksdGhpcy5fb3B0cy5yZXRyaWVzJiYhdGhpcy5mbGFncy5mcm9tUXVldWUmJiF0aGlzLmZsYWdzLnZvbGF0aWxlKXJldHVybiB0aGlzLl9hZGRUb1F1ZXVlKG4pLHRoaXM7dmFyIGk9e3R5cGU6RXQuRVZFTlQsZGF0YTpuLG9wdGlvbnM6e319O2lmKGkub3B0aW9ucy5jb21wcmVzcz0hMSE9PXRoaXMuZmxhZ3MuY29tcHJlc3MsImZ1bmN0aW9uIj09dHlwZW9mIG5bbi5sZW5ndGgtMV0pe3ZhciBvPXRoaXMuaWRzKysscz1uLnBvcCgpO3RoaXMuX3JlZ2lzdGVyQWNrQ2FsbGJhY2sobyxzKSxpLmlkPW99dmFyIGE9dGhpcy5pby5lbmdpbmUmJnRoaXMuaW8uZW5naW5lLnRyYW5zcG9ydCYmdGhpcy5pby5lbmdpbmUudHJhbnNwb3J0LndyaXRhYmxlLGM9dGhpcy5mbGFncy52b2xhdGlsZSYmKCFhfHwhdGhpcy5jb25uZWN0ZWQpO3JldHVybiBjfHwodGhpcy5jb25uZWN0ZWQ/KHRoaXMubm90aWZ5T3V0Z29pbmdMaXN0ZW5lcnMoaSksdGhpcy5wYWNrZXQoaSkpOnRoaXMuc2VuZEJ1ZmZlci5wdXNoKGkpKSx0aGlzLmZsYWdzPXt9LHRoaXN9fSx7a2V5OiJfcmVnaXN0ZXJBY2tDYWxsYmFjayIsdmFsdWU6ZnVuY3Rpb24odCxlKXt2YXIgbixyPXRoaXMsaT1udWxsIT09KG49dGhpcy5mbGFncy50aW1lb3V0KSYmdm9pZCAwIT09bj9uOnRoaXMuX29wdHMuYWNrVGltZW91dDtpZih2b2lkIDAhPT1pKXt2YXIgbz10aGlzLmlvLnNldFRpbWVvdXRGbigoZnVuY3Rpb24oKXtkZWxldGUgci5hY2tzW3RdO2Zvcih2YXIgbj0wO248ci5zZW5kQnVmZmVyLmxlbmd0aDtuKyspci5zZW5kQnVmZmVyW25dLmlkPT09dCYmci5zZW5kQnVmZmVyLnNwbGljZShuLDEpO2UuY2FsbChyLG5ldyBFcnJvcigib3BlcmF0aW9uIGhhcyB0aW1lZCBvdXQiKSl9KSxpKTt0aGlzLmFja3NbdF09ZnVuY3Rpb24oKXtyLmlvLmNsZWFyVGltZW91dEZuKG8pO2Zvcih2YXIgdD1hcmd1bWVudHMubGVuZ3RoLG49bmV3IEFycmF5KHQpLGk9MDtpPHQ7aSsrKW5baV09YXJndW1lbnRzW2ldO2UuYXBwbHkocixbbnVsbF0uY29uY2F0KG4pKX19ZWxzZSB0aGlzLmFja3NbdF09ZX19LHtrZXk6ImVtaXRXaXRoQWNrIix2YWx1ZTpmdW5jdGlvbih0KXtmb3IodmFyIGU9dGhpcyxuPWFyZ3VtZW50cy5sZW5ndGgscj1uZXcgQXJyYXkobj4xP24tMTowKSxpPTE7aTxuO2krKylyW2ktMV09YXJndW1lbnRzW2ldO3ZhciBvPXZvaWQgMCE9PXRoaXMuZmxhZ3MudGltZW91dHx8dm9pZCAwIT09dGhpcy5fb3B0cy5hY2tUaW1lb3V0O3JldHVybiBuZXcgUHJvbWlzZSgoZnVuY3Rpb24obixpKXtyLnB1c2goKGZ1bmN0aW9uKHQsZSl7cmV0dXJuIG8/dD9pKHQpOm4oZSk6bih0KX0pKSxlLmVtaXQuYXBwbHkoZSxbdF0uY29uY2F0KHIpKX0pKX19LHtrZXk6Il9hZGRUb1F1ZXVlIix2YWx1ZTpmdW5jdGlvbih0KXt2YXIgZSxuPXRoaXM7ImZ1bmN0aW9uIj09dHlwZW9mIHRbdC5sZW5ndGgtMV0mJihlPXQucG9wKCkpO3ZhciByPXtpZDp0aGlzLl9xdWV1ZVNlcSsrLHRyeUNvdW50OjAscGVuZGluZzohMSxhcmdzOnQsZmxhZ3M6aSh7ZnJvbVF1ZXVlOiEwfSx0aGlzLmZsYWdzKX07dC5wdXNoKChmdW5jdGlvbih0KXtpZihyPT09bi5fcXVldWVbMF0pe3ZhciBpPW51bGwhPT10O2lmKGkpci50cnlDb3VudD5uLl9vcHRzLnJldHJpZXMmJihuLl9xdWV1ZS5zaGlmdCgpLGUmJmUodCkpO2Vsc2UgaWYobi5fcXVldWUuc2hpZnQoKSxlKXtmb3IodmFyIG89YXJndW1lbnRzLmxlbmd0aCxzPW5ldyBBcnJheShvPjE/by0xOjApLGE9MTthPG87YSsrKXNbYS0xXT1hcmd1bWVudHNbYV07ZS5hcHBseSh2b2lkIDAsW251bGxdLmNvbmNhdChzKSl9cmV0dXJuIHIucGVuZGluZz0hMSxuLl9kcmFpblF1ZXVlKCl9fSkpLHRoaXMuX3F1ZXVlLnB1c2gociksdGhpcy5fZHJhaW5RdWV1ZSgpfX0se2tleToiX2RyYWluUXVldWUiLHZhbHVlOmZ1bmN0aW9uKCl7dmFyIHQ9YXJndW1lbnRzLmxlbmd0aD4wJiZ2b2lkIDAhPT1hcmd1bWVudHNbMF0mJmFyZ3VtZW50c1swXTtpZih0aGlzLmNvbm5lY3RlZCYmMCE9PXRoaXMuX3F1ZXVlLmxlbmd0aCl7dmFyIGU9dGhpcy5fcXVldWVbMF07ZS5wZW5kaW5nJiYhdHx8KGUucGVuZGluZz0hMCxlLnRyeUNvdW50KyssdGhpcy5mbGFncz1lLmZsYWdzLHRoaXMuZW1pdC5hcHBseSh0aGlzLGUuYXJncykpfX19LHtrZXk6InBhY2tldCIsdmFsdWU6ZnVuY3Rpb24odCl7dC5uc3A9dGhpcy5uc3AsdGhpcy5pby5fcGFja2V0KHQpfX0se2tleToib25vcGVuIix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PXRoaXM7ImZ1bmN0aW9uIj09dHlwZW9mIHRoaXMuYXV0aD90aGlzLmF1dGgoKGZ1bmN0aW9uKGUpe3QuX3NlbmRDb25uZWN0UGFja2V0KGUpfSkpOnRoaXMuX3NlbmRDb25uZWN0UGFja2V0KHRoaXMuYXV0aCl9fSx7a2V5OiJfc2VuZENvbm5lY3RQYWNrZXQiLHZhbHVlOmZ1bmN0aW9uKHQpe3RoaXMucGFja2V0KHt0eXBlOkV0LkNPTk5FQ1QsZGF0YTp0aGlzLl9waWQ/aSh7cGlkOnRoaXMuX3BpZCxvZmZzZXQ6dGhpcy5fbGFzdE9mZnNldH0sdCk6dH0pfX0se2tleToib25lcnJvciIsdmFsdWU6ZnVuY3Rpb24odCl7dGhpcy5jb25uZWN0ZWR8fHRoaXMuZW1pdFJlc2VydmVkKCJjb25uZWN0X2Vycm9yIix0KX19LHtrZXk6Im9uY2xvc2UiLHZhbHVlOmZ1bmN0aW9uKHQsZSl7dGhpcy5jb25uZWN0ZWQ9ITEsZGVsZXRlIHRoaXMuaWQsdGhpcy5lbWl0UmVzZXJ2ZWQoImRpc2Nvbm5lY3QiLHQsZSl9fSx7a2V5OiJvbnBhY2tldCIsdmFsdWU6ZnVuY3Rpb24odCl7aWYodC5uc3A9PT10aGlzLm5zcClzd2l0Y2godC50eXBlKXtjYXNlIEV0LkNPTk5FQ1Q6dC5kYXRhJiZ0LmRhdGEuc2lkP3RoaXMub25jb25uZWN0KHQuZGF0YS5zaWQsdC5kYXRhLnBpZCk6dGhpcy5lbWl0UmVzZXJ2ZWQoImNvbm5lY3RfZXJyb3IiLG5ldyBFcnJvcigiSXQgc2VlbXMgeW91IGFyZSB0cnlpbmcgdG8gcmVhY2ggYSBTb2NrZXQuSU8gc2VydmVyIGluIHYyLnggd2l0aCBhIHYzLnggY2xpZW50LCBidXQgdGhleSBhcmUgbm90IGNvbXBhdGlibGUgKG1vcmUgaW5mb3JtYXRpb24gaGVyZTogaHR0cHM6Ly9zb2NrZXQuaW8vZG9jcy92My9taWdyYXRpbmctZnJvbS0yLXgtdG8tMy0wLykiKSk7YnJlYWs7Y2FzZSBFdC5FVkVOVDpjYXNlIEV0LkJJTkFSWV9FVkVOVDp0aGlzLm9uZXZlbnQodCk7YnJlYWs7Y2FzZSBFdC5BQ0s6Y2FzZSBFdC5CSU5BUllfQUNLOnRoaXMub25hY2sodCk7YnJlYWs7Y2FzZSBFdC5ESVNDT05ORUNUOnRoaXMub25kaXNjb25uZWN0KCk7YnJlYWs7Y2FzZSBFdC5DT05ORUNUX0VSUk9SOnRoaXMuZGVzdHJveSgpO3ZhciBlPW5ldyBFcnJvcih0LmRhdGEubWVzc2FnZSk7ZS5kYXRhPXQuZGF0YS5kYXRhLHRoaXMuZW1pdFJlc2VydmVkKCJjb25uZWN0X2Vycm9yIixlKX19fSx7a2V5OiJvbmV2ZW50Iix2YWx1ZTpmdW5jdGlvbih0KXt2YXIgZT10LmRhdGF8fFtdO251bGwhPXQuaWQmJmUucHVzaCh0aGlzLmFjayh0LmlkKSksdGhpcy5jb25uZWN0ZWQ/dGhpcy5lbWl0RXZlbnQoZSk6dGhpcy5yZWNlaXZlQnVmZmVyLnB1c2goT2JqZWN0LmZyZWV6ZShlKSl9fSx7a2V5OiJlbWl0RXZlbnQiLHZhbHVlOmZ1bmN0aW9uKHQpe2lmKHRoaXMuX2FueUxpc3RlbmVycyYmdGhpcy5fYW55TGlzdGVuZXJzLmxlbmd0aCl7dmFyIGUsbj1nKHRoaXMuX2FueUxpc3RlbmVycy5zbGljZSgpKTt0cnl7Zm9yKG4ucygpOyEoZT1uLm4oKSkuZG9uZTspe2UudmFsdWUuYXBwbHkodGhpcyx0KX19Y2F0Y2godCl7bi5lKHQpfWZpbmFsbHl7bi5mKCl9fXkocyhhLnByb3RvdHlwZSksImVtaXQiLHRoaXMpLmFwcGx5KHRoaXMsdCksdGhpcy5fcGlkJiZ0Lmxlbmd0aCYmInN0cmluZyI9PXR5cGVvZiB0W3QubGVuZ3RoLTFdJiYodGhpcy5fbGFzdE9mZnNldD10W3QubGVuZ3RoLTFdKX19LHtrZXk6ImFjayIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9dGhpcyxuPSExO3JldHVybiBmdW5jdGlvbigpe2lmKCFuKXtuPSEwO2Zvcih2YXIgcj1hcmd1bWVudHMubGVuZ3RoLGk9bmV3IEFycmF5KHIpLG89MDtvPHI7bysrKWlbb109YXJndW1lbnRzW29dO2UucGFja2V0KHt0eXBlOkV0LkFDSyxpZDp0LGRhdGE6aX0pfX19fSx7a2V5OiJvbmFjayIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9dGhpcy5hY2tzW3QuaWRdOyJmdW5jdGlvbiI9PXR5cGVvZiBlJiYoZS5hcHBseSh0aGlzLHQuZGF0YSksZGVsZXRlIHRoaXMuYWNrc1t0LmlkXSl9fSx7a2V5OiJvbmNvbm5lY3QiLHZhbHVlOmZ1bmN0aW9uKHQsZSl7dGhpcy5pZD10LHRoaXMucmVjb3ZlcmVkPWUmJnRoaXMuX3BpZD09PWUsdGhpcy5fcGlkPWUsdGhpcy5jb25uZWN0ZWQ9ITAsdGhpcy5lbWl0QnVmZmVyZWQoKSx0aGlzLmVtaXRSZXNlcnZlZCgiY29ubmVjdCIpLHRoaXMuX2RyYWluUXVldWUoITApfX0se2tleToiZW1pdEJ1ZmZlcmVkIix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PXRoaXM7dGhpcy5yZWNlaXZlQnVmZmVyLmZvckVhY2goKGZ1bmN0aW9uKGUpe3JldHVybiB0LmVtaXRFdmVudChlKX0pKSx0aGlzLnJlY2VpdmVCdWZmZXI9W10sdGhpcy5zZW5kQnVmZmVyLmZvckVhY2goKGZ1bmN0aW9uKGUpe3Qubm90aWZ5T3V0Z29pbmdMaXN0ZW5lcnMoZSksdC5wYWNrZXQoZSl9KSksdGhpcy5zZW5kQnVmZmVyPVtdfX0se2tleToib25kaXNjb25uZWN0Iix2YWx1ZTpmdW5jdGlvbigpe3RoaXMuZGVzdHJveSgpLHRoaXMub25jbG9zZSgiaW8gc2VydmVyIGRpc2Nvbm5lY3QiKX19LHtrZXk6ImRlc3Ryb3kiLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5zdWJzJiYodGhpcy5zdWJzLmZvckVhY2goKGZ1bmN0aW9uKHQpe3JldHVybiB0KCl9KSksdGhpcy5zdWJzPXZvaWQgMCksdGhpcy5pby5fZGVzdHJveSh0aGlzKX19LHtrZXk6ImRpc2Nvbm5lY3QiLHZhbHVlOmZ1bmN0aW9uKCl7cmV0dXJuIHRoaXMuY29ubmVjdGVkJiZ0aGlzLnBhY2tldCh7dHlwZTpFdC5ESVNDT05ORUNUfSksdGhpcy5kZXN0cm95KCksdGhpcy5jb25uZWN0ZWQmJnRoaXMub25jbG9zZSgiaW8gY2xpZW50IGRpc2Nvbm5lY3QiKSx0aGlzfX0se2tleToiY2xvc2UiLHZhbHVlOmZ1bmN0aW9uKCl7cmV0dXJuIHRoaXMuZGlzY29ubmVjdCgpfX0se2tleToiY29tcHJlc3MiLHZhbHVlOmZ1bmN0aW9uKHQpe3JldHVybiB0aGlzLmZsYWdzLmNvbXByZXNzPXQsdGhpc319LHtrZXk6InZvbGF0aWxlIixnZXQ6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5mbGFncy52b2xhdGlsZT0hMCx0aGlzfX0se2tleToidGltZW91dCIsdmFsdWU6ZnVuY3Rpb24odCl7cmV0dXJuIHRoaXMuZmxhZ3MudGltZW91dD10LHRoaXN9fSx7a2V5OiJvbkFueSIsdmFsdWU6ZnVuY3Rpb24odCl7cmV0dXJuIHRoaXMuX2FueUxpc3RlbmVycz10aGlzLl9hbnlMaXN0ZW5lcnN8fFtdLHRoaXMuX2FueUxpc3RlbmVycy5wdXNoKHQpLHRoaXN9fSx7a2V5OiJwcmVwZW5kQW55Iix2YWx1ZTpmdW5jdGlvbih0KXtyZXR1cm4gdGhpcy5fYW55TGlzdGVuZXJzPXRoaXMuX2FueUxpc3RlbmVyc3x8W10sdGhpcy5fYW55TGlzdGVuZXJzLnVuc2hpZnQodCksdGhpc319LHtrZXk6Im9mZkFueSIsdmFsdWU6ZnVuY3Rpb24odCl7aWYoIXRoaXMuX2FueUxpc3RlbmVycylyZXR1cm4gdGhpcztpZih0KXtmb3IodmFyIGU9dGhpcy5fYW55TGlzdGVuZXJzLG49MDtuPGUubGVuZ3RoO24rKylpZih0PT09ZVtuXSlyZXR1cm4gZS5zcGxpY2UobiwxKSx0aGlzfWVsc2UgdGhpcy5fYW55TGlzdGVuZXJzPVtdO3JldHVybiB0aGlzfX0se2tleToibGlzdGVuZXJzQW55Iix2YWx1ZTpmdW5jdGlvbigpe3JldHVybiB0aGlzLl9hbnlMaXN0ZW5lcnN8fFtdfX0se2tleToib25BbnlPdXRnb2luZyIsdmFsdWU6ZnVuY3Rpb24odCl7cmV0dXJuIHRoaXMuX2FueU91dGdvaW5nTGlzdGVuZXJzPXRoaXMuX2FueU91dGdvaW5nTGlzdGVuZXJzfHxbXSx0aGlzLl9hbnlPdXRnb2luZ0xpc3RlbmVycy5wdXNoKHQpLHRoaXN9fSx7a2V5OiJwcmVwZW5kQW55T3V0Z29pbmciLHZhbHVlOmZ1bmN0aW9uKHQpe3JldHVybiB0aGlzLl9hbnlPdXRnb2luZ0xpc3RlbmVycz10aGlzLl9hbnlPdXRnb2luZ0xpc3RlbmVyc3x8W10sdGhpcy5fYW55T3V0Z29pbmdMaXN0ZW5lcnMudW5zaGlmdCh0KSx0aGlzfX0se2tleToib2ZmQW55T3V0Z29pbmciLHZhbHVlOmZ1bmN0aW9uKHQpe2lmKCF0aGlzLl9hbnlPdXRnb2luZ0xpc3RlbmVycylyZXR1cm4gdGhpcztpZih0KXtmb3IodmFyIGU9dGhpcy5fYW55T3V0Z29pbmdMaXN0ZW5lcnMsbj0wO248ZS5sZW5ndGg7bisrKWlmKHQ9PT1lW25dKXJldHVybiBlLnNwbGljZShuLDEpLHRoaXN9ZWxzZSB0aGlzLl9hbnlPdXRnb2luZ0xpc3RlbmVycz1bXTtyZXR1cm4gdGhpc319LHtrZXk6Imxpc3RlbmVyc0FueU91dGdvaW5nIix2YWx1ZTpmdW5jdGlvbigpe3JldHVybiB0aGlzLl9hbnlPdXRnb2luZ0xpc3RlbmVyc3x8W119fSx7a2V5OiJub3RpZnlPdXRnb2luZ0xpc3RlbmVycyIsdmFsdWU6ZnVuY3Rpb24odCl7aWYodGhpcy5fYW55T3V0Z29pbmdMaXN0ZW5lcnMmJnRoaXMuX2FueU91dGdvaW5nTGlzdGVuZXJzLmxlbmd0aCl7dmFyIGUsbj1nKHRoaXMuX2FueU91dGdvaW5nTGlzdGVuZXJzLnNsaWNlKCkpO3RyeXtmb3Iobi5zKCk7IShlPW4ubigpKS5kb25lOyl7ZS52YWx1ZS5hcHBseSh0aGlzLHQuZGF0YSl9fWNhdGNoKHQpe24uZSh0KX1maW5hbGx5e24uZigpfX19fV0pLGF9KEwpO2Z1bmN0aW9uIE50KHQpe3Q9dHx8e30sdGhpcy5tcz10Lm1pbnx8MTAwLHRoaXMubWF4PXQubWF4fHwxZTQsdGhpcy5mYWN0b3I9dC5mYWN0b3J8fDIsdGhpcy5qaXR0ZXI9dC5qaXR0ZXI+MCYmdC5qaXR0ZXI8PTE/dC5qaXR0ZXI6MCx0aGlzLmF0dGVtcHRzPTB9TnQucHJvdG90eXBlLmR1cmF0aW9uPWZ1bmN0aW9uKCl7dmFyIHQ9dGhpcy5tcypNYXRoLnBvdyh0aGlzLmZhY3Rvcix0aGlzLmF0dGVtcHRzKyspO2lmKHRoaXMuaml0dGVyKXt2YXIgZT1NYXRoLnJhbmRvbSgpLG49TWF0aC5mbG9vcihlKnRoaXMuaml0dGVyKnQpO3Q9MD09KDEmTWF0aC5mbG9vcigxMCplKSk/dC1uOnQrbn1yZXR1cm4gMHxNYXRoLm1pbih0LHRoaXMubWF4KX0sTnQucHJvdG90eXBlLnJlc2V0PWZ1bmN0aW9uKCl7dGhpcy5hdHRlbXB0cz0wfSxOdC5wcm90b3R5cGUuc2V0TWluPWZ1bmN0aW9uKHQpe3RoaXMubXM9dH0sTnQucHJvdG90eXBlLnNldE1heD1mdW5jdGlvbih0KXt0aGlzLm1heD10fSxOdC5wcm90b3R5cGUuc2V0Sml0dGVyPWZ1bmN0aW9uKHQpe3RoaXMuaml0dGVyPXR9O3ZhciB4dD1mdW5jdGlvbihuKXtvKHMsbik7dmFyIGk9cChzKTtmdW5jdGlvbiBzKG4scil7dmFyIG8sYTtlKHRoaXMscyksKG89aS5jYWxsKHRoaXMpKS5uc3BzPXt9LG8uc3Vicz1bXSxuJiYib2JqZWN0Ij09PXQobikmJihyPW4sbj12b2lkIDApLChyPXJ8fHt9KS5wYXRoPXIucGF0aHx8Ii9zb2NrZXQuaW8iLG8ub3B0cz1yLEQoZihvKSxyKSxvLnJlY29ubmVjdGlvbighMSE9PXIucmVjb25uZWN0aW9uKSxvLnJlY29ubmVjdGlvbkF0dGVtcHRzKHIucmVjb25uZWN0aW9uQXR0ZW1wdHN8fDEvMCksby5yZWNvbm5lY3Rpb25EZWxheShyLnJlY29ubmVjdGlvbkRlbGF5fHwxZTMpLG8ucmVjb25uZWN0aW9uRGVsYXlNYXgoci5yZWNvbm5lY3Rpb25EZWxheU1heHx8NWUzKSxvLnJhbmRvbWl6YXRpb25GYWN0b3IobnVsbCE9PShhPXIucmFuZG9taXphdGlvbkZhY3RvcikmJnZvaWQgMCE9PWE/YTouNSksby5iYWNrb2ZmPW5ldyBOdCh7bWluOm8ucmVjb25uZWN0aW9uRGVsYXkoKSxtYXg6by5yZWNvbm5lY3Rpb25EZWxheU1heCgpLGppdHRlcjpvLnJhbmRvbWl6YXRpb25GYWN0b3IoKX0pLG8udGltZW91dChudWxsPT1yLnRpbWVvdXQ/MmU0OnIudGltZW91dCksby5fcmVhZHlTdGF0ZT0iY2xvc2VkIixvLnVyaT1uO3ZhciBjPXIucGFyc2VyfHxUdDtyZXR1cm4gby5lbmNvZGVyPW5ldyBjLkVuY29kZXIsby5kZWNvZGVyPW5ldyBjLkRlY29kZXIsby5fYXV0b0Nvbm5lY3Q9ITEhPT1yLmF1dG9Db25uZWN0LG8uX2F1dG9Db25uZWN0JiZvLm9wZW4oKSxvfXJldHVybiByKHMsW3trZXk6InJlY29ubmVjdGlvbiIsdmFsdWU6ZnVuY3Rpb24odCl7cmV0dXJuIGFyZ3VtZW50cy5sZW5ndGg/KHRoaXMuX3JlY29ubmVjdGlvbj0hIXQsdGhpcyk6dGhpcy5fcmVjb25uZWN0aW9ufX0se2tleToicmVjb25uZWN0aW9uQXR0ZW1wdHMiLHZhbHVlOmZ1bmN0aW9uKHQpe3JldHVybiB2b2lkIDA9PT10P3RoaXMuX3JlY29ubmVjdGlvbkF0dGVtcHRzOih0aGlzLl9yZWNvbm5lY3Rpb25BdHRlbXB0cz10LHRoaXMpfX0se2tleToicmVjb25uZWN0aW9uRGVsYXkiLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlO3JldHVybiB2b2lkIDA9PT10P3RoaXMuX3JlY29ubmVjdGlvbkRlbGF5Oih0aGlzLl9yZWNvbm5lY3Rpb25EZWxheT10LG51bGw9PT0oZT10aGlzLmJhY2tvZmYpfHx2b2lkIDA9PT1lfHxlLnNldE1pbih0KSx0aGlzKX19LHtrZXk6InJhbmRvbWl6YXRpb25GYWN0b3IiLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlO3JldHVybiB2b2lkIDA9PT10P3RoaXMuX3JhbmRvbWl6YXRpb25GYWN0b3I6KHRoaXMuX3JhbmRvbWl6YXRpb25GYWN0b3I9dCxudWxsPT09KGU9dGhpcy5iYWNrb2ZmKXx8dm9pZCAwPT09ZXx8ZS5zZXRKaXR0ZXIodCksdGhpcyl9fSx7a2V5OiJyZWNvbm5lY3Rpb25EZWxheU1heCIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU7cmV0dXJuIHZvaWQgMD09PXQ/dGhpcy5fcmVjb25uZWN0aW9uRGVsYXlNYXg6KHRoaXMuX3JlY29ubmVjdGlvbkRlbGF5TWF4PXQsbnVsbD09PShlPXRoaXMuYmFja29mZil8fHZvaWQgMD09PWV8fGUuc2V0TWF4KHQpLHRoaXMpfX0se2tleToidGltZW91dCIsdmFsdWU6ZnVuY3Rpb24odCl7cmV0dXJuIGFyZ3VtZW50cy5sZW5ndGg/KHRoaXMuX3RpbWVvdXQ9dCx0aGlzKTp0aGlzLl90aW1lb3V0fX0se2tleToibWF5YmVSZWNvbm5lY3RPbk9wZW4iLHZhbHVlOmZ1bmN0aW9uKCl7IXRoaXMuX3JlY29ubmVjdGluZyYmdGhpcy5fcmVjb25uZWN0aW9uJiYwPT09dGhpcy5iYWNrb2ZmLmF0dGVtcHRzJiZ0aGlzLnJlY29ubmVjdCgpfX0se2tleToib3BlbiIsdmFsdWU6ZnVuY3Rpb24odCl7dmFyIGU9dGhpcztpZih+dGhpcy5fcmVhZHlTdGF0ZS5pbmRleE9mKCJvcGVuIikpcmV0dXJuIHRoaXM7dGhpcy5lbmdpbmU9bmV3IGx0KHRoaXMudXJpLHRoaXMub3B0cyk7dmFyIG49dGhpcy5lbmdpbmUscj10aGlzO3RoaXMuX3JlYWR5U3RhdGU9Im9wZW5pbmciLHRoaXMuc2tpcFJlY29ubmVjdD0hMTt2YXIgaT1DdChuLCJvcGVuIiwoZnVuY3Rpb24oKXtyLm9ub3BlbigpLHQmJnQoKX0pKSxvPUN0KG4sImVycm9yIiwoZnVuY3Rpb24obil7ci5jbGVhbnVwKCksci5fcmVhZHlTdGF0ZT0iY2xvc2VkIixlLmVtaXRSZXNlcnZlZCgiZXJyb3IiLG4pLHQ/dChuKTpyLm1heWJlUmVjb25uZWN0T25PcGVuKCl9KSk7aWYoITEhPT10aGlzLl90aW1lb3V0KXt2YXIgcz10aGlzLl90aW1lb3V0OzA9PT1zJiZpKCk7dmFyIGE9dGhpcy5zZXRUaW1lb3V0Rm4oKGZ1bmN0aW9uKCl7aSgpLG4uY2xvc2UoKSxuLmVtaXQoImVycm9yIixuZXcgRXJyb3IoInRpbWVvdXQiKSl9KSxzKTt0aGlzLm9wdHMuYXV0b1VucmVmJiZhLnVucmVmKCksdGhpcy5zdWJzLnB1c2goKGZ1bmN0aW9uKCl7Y2xlYXJUaW1lb3V0KGEpfSkpfXJldHVybiB0aGlzLnN1YnMucHVzaChpKSx0aGlzLnN1YnMucHVzaChvKSx0aGlzfX0se2tleToiY29ubmVjdCIsdmFsdWU6ZnVuY3Rpb24odCl7cmV0dXJuIHRoaXMub3Blbih0KX19LHtrZXk6Im9ub3BlbiIsdmFsdWU6ZnVuY3Rpb24oKXt0aGlzLmNsZWFudXAoKSx0aGlzLl9yZWFkeVN0YXRlPSJvcGVuIix0aGlzLmVtaXRSZXNlcnZlZCgib3BlbiIpO3ZhciB0PXRoaXMuZW5naW5lO3RoaXMuc3Vicy5wdXNoKEN0KHQsInBpbmciLHRoaXMub25waW5nLmJpbmQodGhpcykpLEN0KHQsImRhdGEiLHRoaXMub25kYXRhLmJpbmQodGhpcykpLEN0KHQsImVycm9yIix0aGlzLm9uZXJyb3IuYmluZCh0aGlzKSksQ3QodCwiY2xvc2UiLHRoaXMub25jbG9zZS5iaW5kKHRoaXMpKSxDdCh0aGlzLmRlY29kZXIsImRlY29kZWQiLHRoaXMub25kZWNvZGVkLmJpbmQodGhpcykpKX19LHtrZXk6Im9ucGluZyIsdmFsdWU6ZnVuY3Rpb24oKXt0aGlzLmVtaXRSZXNlcnZlZCgicGluZyIpfX0se2tleToib25kYXRhIix2YWx1ZTpmdW5jdGlvbih0KXt0cnl7dGhpcy5kZWNvZGVyLmFkZCh0KX1jYXRjaCh0KXt0aGlzLm9uY2xvc2UoInBhcnNlIGVycm9yIix0KX19fSx7a2V5OiJvbmRlY29kZWQiLHZhbHVlOmZ1bmN0aW9uKHQpe3ZhciBlPXRoaXM7aXQoKGZ1bmN0aW9uKCl7ZS5lbWl0UmVzZXJ2ZWQoInBhY2tldCIsdCl9KSx0aGlzLnNldFRpbWVvdXRGbil9fSx7a2V5OiJvbmVycm9yIix2YWx1ZTpmdW5jdGlvbih0KXt0aGlzLmVtaXRSZXNlcnZlZCgiZXJyb3IiLHQpfX0se2tleToic29ja2V0Iix2YWx1ZTpmdW5jdGlvbih0LGUpe3ZhciBuPXRoaXMubnNwc1t0XTtyZXR1cm4gbj90aGlzLl9hdXRvQ29ubmVjdCYmIW4uYWN0aXZlJiZuLmNvbm5lY3QoKToobj1uZXcgU3QodGhpcyx0LGUpLHRoaXMubnNwc1t0XT1uKSxufX0se2tleToiX2Rlc3Ryb3kiLHZhbHVlOmZ1bmN0aW9uKHQpe2Zvcih2YXIgZT0wLG49T2JqZWN0LmtleXModGhpcy5uc3BzKTtlPG4ubGVuZ3RoO2UrKyl7dmFyIHI9bltlXTtpZih0aGlzLm5zcHNbcl0uYWN0aXZlKXJldHVybn10aGlzLl9jbG9zZSgpfX0se2tleToiX3BhY2tldCIsdmFsdWU6ZnVuY3Rpb24odCl7Zm9yKHZhciBlPXRoaXMuZW5jb2Rlci5lbmNvZGUodCksbj0wO248ZS5sZW5ndGg7bisrKXRoaXMuZW5naW5lLndyaXRlKGVbbl0sdC5vcHRpb25zKX19LHtrZXk6ImNsZWFudXAiLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5zdWJzLmZvckVhY2goKGZ1bmN0aW9uKHQpe3JldHVybiB0KCl9KSksdGhpcy5zdWJzLmxlbmd0aD0wLHRoaXMuZGVjb2Rlci5kZXN0cm95KCl9fSx7a2V5OiJfY2xvc2UiLHZhbHVlOmZ1bmN0aW9uKCl7dGhpcy5za2lwUmVjb25uZWN0PSEwLHRoaXMuX3JlY29ubmVjdGluZz0hMSx0aGlzLm9uY2xvc2UoImZvcmNlZCBjbG9zZSIpLHRoaXMuZW5naW5lJiZ0aGlzLmVuZ2luZS5jbG9zZSgpfX0se2tleToiZGlzY29ubmVjdCIsdmFsdWU6ZnVuY3Rpb24oKXtyZXR1cm4gdGhpcy5fY2xvc2UoKX19LHtrZXk6Im9uY2xvc2UiLHZhbHVlOmZ1bmN0aW9uKHQsZSl7dGhpcy5jbGVhbnVwKCksdGhpcy5iYWNrb2ZmLnJlc2V0KCksdGhpcy5fcmVhZHlTdGF0ZT0iY2xvc2VkIix0aGlzLmVtaXRSZXNlcnZlZCgiY2xvc2UiLHQsZSksdGhpcy5fcmVjb25uZWN0aW9uJiYhdGhpcy5za2lwUmVjb25uZWN0JiZ0aGlzLnJlY29ubmVjdCgpfX0se2tleToicmVjb25uZWN0Iix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PXRoaXM7aWYodGhpcy5fcmVjb25uZWN0aW5nfHx0aGlzLnNraXBSZWNvbm5lY3QpcmV0dXJuIHRoaXM7dmFyIGU9dGhpcztpZih0aGlzLmJhY2tvZmYuYXR0ZW1wdHM+PXRoaXMuX3JlY29ubmVjdGlvbkF0dGVtcHRzKXRoaXMuYmFja29mZi5yZXNldCgpLHRoaXMuZW1pdFJlc2VydmVkKCJyZWNvbm5lY3RfZmFpbGVkIiksdGhpcy5fcmVjb25uZWN0aW5nPSExO2Vsc2V7dmFyIG49dGhpcy5iYWNrb2ZmLmR1cmF0aW9uKCk7dGhpcy5fcmVjb25uZWN0aW5nPSEwO3ZhciByPXRoaXMuc2V0VGltZW91dEZuKChmdW5jdGlvbigpe2Uuc2tpcFJlY29ubmVjdHx8KHQuZW1pdFJlc2VydmVkKCJyZWNvbm5lY3RfYXR0ZW1wdCIsZS5iYWNrb2ZmLmF0dGVtcHRzKSxlLnNraXBSZWNvbm5lY3R8fGUub3BlbigoZnVuY3Rpb24obil7bj8oZS5fcmVjb25uZWN0aW5nPSExLGUucmVjb25uZWN0KCksdC5lbWl0UmVzZXJ2ZWQoInJlY29ubmVjdF9lcnJvciIsbikpOmUub25yZWNvbm5lY3QoKX0pKSl9KSxuKTt0aGlzLm9wdHMuYXV0b1VucmVmJiZyLnVucmVmKCksdGhpcy5zdWJzLnB1c2goKGZ1bmN0aW9uKCl7Y2xlYXJUaW1lb3V0KHIpfSkpfX19LHtrZXk6Im9ucmVjb25uZWN0Iix2YWx1ZTpmdW5jdGlvbigpe3ZhciB0PXRoaXMuYmFja29mZi5hdHRlbXB0czt0aGlzLl9yZWNvbm5lY3Rpbmc9ITEsdGhpcy5iYWNrb2ZmLnJlc2V0KCksdGhpcy5lbWl0UmVzZXJ2ZWQoInJlY29ubmVjdCIsdCl9fV0pLHN9KEwpLEx0PXt9O2Z1bmN0aW9uIFB0KGUsbil7Im9iamVjdCI9PT10KGUpJiYobj1lLGU9dm9pZCAwKTt2YXIgcixpPWZ1bmN0aW9uKHQpe3ZhciBlPWFyZ3VtZW50cy5sZW5ndGg+MSYmdm9pZCAwIT09YXJndW1lbnRzWzFdP2FyZ3VtZW50c1sxXToiIixuPWFyZ3VtZW50cy5sZW5ndGg+Mj9hcmd1bWVudHNbMl06dm9pZCAwLHI9dDtuPW58fCJ1bmRlZmluZWQiIT10eXBlb2YgbG9jYXRpb24mJmxvY2F0aW9uLG51bGw9PXQmJih0PW4ucHJvdG9jb2wrIi8vIituLmhvc3QpLCJzdHJpbmciPT10eXBlb2YgdCYmKCIvIj09PXQuY2hhckF0KDApJiYodD0iLyI9PT10LmNoYXJBdCgxKT9uLnByb3RvY29sK3Q6bi5ob3N0K3QpLC9eKGh0dHBzP3x3c3M/KTpcL1wvLy50ZXN0KHQpfHwodD12b2lkIDAhPT1uP24ucHJvdG9jb2wrIi8vIit0OiJodHRwczovLyIrdCkscj1mdCh0KSksci5wb3J0fHwoL14oaHR0cHx3cykkLy50ZXN0KHIucHJvdG9jb2wpP3IucG9ydD0iODAiOi9eKGh0dHB8d3MpcyQvLnRlc3Qoci5wcm90b2NvbCkmJihyLnBvcnQ9IjQ0MyIpKSxyLnBhdGg9ci5wYXRofHwiLyI7dmFyIGk9LTEhPT1yLmhvc3QuaW5kZXhPZigiOiIpPyJbIityLmhvc3QrIl0iOnIuaG9zdDtyZXR1cm4gci5pZD1yLnByb3RvY29sKyI6Ly8iK2krIjoiK3IucG9ydCtlLHIuaHJlZj1yLnByb3RvY29sKyI6Ly8iK2krKG4mJm4ucG9ydD09PXIucG9ydD8iIjoiOiIrci5wb3J0KSxyfShlLChuPW58fHt9KS5wYXRofHwiL3NvY2tldC5pbyIpLG89aS5zb3VyY2Uscz1pLmlkLGE9aS5wYXRoLGM9THRbc10mJmEgaW4gTHRbc10ubnNwcztyZXR1cm4gbi5mb3JjZU5ld3x8blsiZm9yY2UgbmV3IGNvbm5lY3Rpb24iXXx8ITE9PT1uLm11bHRpcGxleHx8Yz9yPW5ldyB4dChvLG4pOihMdFtzXXx8KEx0W3NdPW5ldyB4dChvLG4pKSxyPUx0W3NdKSxpLnF1ZXJ5JiYhbi5xdWVyeSYmKG4ucXVlcnk9aS5xdWVyeUtleSksci5zb2NrZXQoaS5wYXRoLG4pfXJldHVybiBpKFB0LHtNYW5hZ2VyOnh0LFNvY2tldDpTdCxpbzpQdCxjb25uZWN0OlB0fSksUHR9KSk7DQovLyMgc291cmNlTWFwcGluZ1VSTD1zb2NrZXQuaW8ubWluLmpzLm1hcA=="  

def write_assets():
    global temp_root, uploads_dir, templates_dir, static_dir
    temp_root = Path(tempfile.mkdtemp(prefix="lan_portal_"))
    uploads_dir = temp_root / "uploads"
    templates_dir = temp_root / "templates"
    static_dir = temp_root / "static"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)

    (templates_dir / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    with open(static_dir / "logo.png", "wb") as f:
        f.write(b64decode(LOGO_PNG_BASE64))

    # socket.io client (offline)
    sio_path = static_dir / "socket.io.js"
    if SOCKET_IO_MIN_JS_BASE64:
        try:
            sio_bytes = b64decode(SOCKET_IO_MIN_JS_BASE64)
            with open(sio_path, "wb") as f:
                f.write(sio_bytes)
        except Exception as e:
            print("[warn] نتونستم socket.io.js رو بنویسم:", e)
            (static_dir / "socket.io.js").write_text("// socket.io.js missing (Base64 decoding failed)", encoding="utf-8")
    else:
        print("[warn] فایل socket.io.js فعلاً خالی است. برای کار آفلاین real-time، Base64 را پر کن.")
        (static_dir / "socket.io.js").write_text("// socket.io.js missing — please embed Base64", encoding="utf-8")

def cleanup():
    if temp_root and temp_root.exists():
        try:
            shutil.rmtree(temp_root, ignore_errors=True)
        except Exception:
            pass

def human_size(n):
    f = float(n)
    for unit in ["B","KB","MB","GB","TB"]:
        if f < 1024:
            return f"{f:.0f} {unit}"
        f /= 1024.0
    return f"{f:.0f} PB"

# -----------------------------
# Flask + Socket.IO (server-side logic)
# -----------------------------
def make_app():
    global app, socketio
    app = Flask(__name__, static_folder=str(static_dir), template_folder=str(templates_dir))
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1GB
    socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

    @app.route("/")
    def index():
        return render_template("index.html", title=APP_TITLE, year=datetime.now().year)

    @app.route("/static/<path:filename>")
    def static_file(filename):
        return send_from_directory(static_dir, filename)

    @app.route("/upload", methods=["POST"])
    def upload():
        f = request.files.get("file")
        if not f or f.filename == "":
            return "no file", 400
        safe_name = os.path.basename(f.filename)
        dest = uploads_dir / safe_name
        f.save(dest)
        return "ok", 200

    @app.route("/download/<path:name>")
    def download(name):
        name = os.path.basename(name)
        p = uploads_dir / name
        if not p.exists():
            abort(404)
        return send_from_directory(uploads_dir, name, as_attachment=True)

    @app.route("/api/files")
    def api_files():
        items = []
        for p in sorted(uploads_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if p.is_file():
                st = p.stat()
                items.append({"name": p.name, "size": st.st_size, "size_h": human_size(st.st_size)})
        return jsonify(items)

    @app.route("/api/delete/<path:name>", methods=["POST"])
    def api_delete(name):
        name = os.path.basename(name)
        p = uploads_dir / name
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass
        return "ok"

    @app.route("/api/clear", methods=["POST"])
    def api_clear():
        for p in uploads_dir.iterdir():
            if p.is_file():
                try:
                    p.unlink()
                except Exception:
                    pass
        return "ok"

    # --- socket events ---
    @socketio.on("join")
    def on_join(data):
        username = (data or {}).get("user", "کاربر")
        connected_users[request.sid] = username
        emit("msg", {"user":"سیستم","msg":f"{username} متصل شد.", "t": datetime.utcnow().isoformat()}, broadcast=True)

    @socketio.on("history")
    def on_history():
        emit("history", chat_history[-200:])

    @socketio.on("msg")
    def on_msg(data):
        user = (data or {}).get("user", "ناشناس")
        msg = (data or {}).get("msg", "")
        if not msg:
            return
        item = {"t": datetime.utcnow().isoformat(), "user": user, "msg": msg}
        chat_history.append(item)
        if len(chat_history) > 1000:
            del chat_history[:200]
        emit("msg", item, broadcast=True)

    @socketio.on("disconnect")
    def on_disconnect():
        sid = request.sid
        # حذف از صف‌ها
        for g in waiting_queues:
            waiting_queues[g] = [x for x in waiting_queues[g] if x != sid]
        # اطلاع به حریف‌ها و پاک‌سازی اتاق‌ها شامل sid
        rooms_to_remove = []
        for room, info in list(active_games.items()):
            if sid in info.get("players", []):
                # پیدا کردن حریف
                opp = [s for s in info["players"] if s != sid]
                for o in opp:
                    try:
                        emit("opponent_left", {"room": room, "game": info["game"]}, to=o)
                    except Exception:
                        pass
                rooms_to_remove.append(room)
        for r in rooms_to_remove:
            active_games.pop(r, None)
        connected_users.pop(sid, None)

    # Queue enter/leave and matchmaking
    @socketio.on("queue_enter")
    def queue_enter(data):
        game = (data or {}).get("game")
        sid = request.sid
        if game not in waiting_queues:
            return
        if sid not in waiting_queues[game]:
            waiting_queues[game].append(sid)
        # اگر دو نفر در صف باشند، جفت کن
        if len(waiting_queues[game]) >= 2:
            s1 = waiting_queues[game].pop(0)
            s2 = waiting_queues[game].pop(0)
            room = uuid.uuid4().hex[:8]
            active_games[room] = {"game": game, "players": [s1, s2]}
            # ارسال اطلاعات مچ به هر دو طرف
            if game == "ttt":
                try:
                    emit("match_found", {"room": room, "game": game, "role": "X"}, to=s1)
                    emit("match_found", {"room": room, "game": game, "role": "O"}, to=s2)
                except Exception:
                    pass
            else:  # chess
                try:
                    emit("match_found", {"room": room, "game": game, "role": "w"}, to=s1)
                    emit("match_found", {"room": room, "game": game, "role": "b"}, to=s2)
                except Exception:
                    pass

    @socketio.on("queue_leave")
    def queue_leave(data):
        game = (data or {}).get("game")
        sid = request.sid
        if game in waiting_queues:
            waiting_queues[game] = [x for x in waiting_queues[game] if x != sid]

    @socketio.on("leave_room")
    def leave_room_event(data):
        room = (data or {}).get("room")
        sid = request.sid
        if not room:
            return
        info = active_games.get(room)
        if not info:
            return
        # notify opponent
        for s in info.get("players", []):
            if s != sid:
                emit("opponent_left", {"room": room, "game": info["game"]}, to=s)
        active_games.pop(room, None)

    @socketio.on("game_move")
    def on_game_move(data):
        room = (data or {}).get("room")
        game = (data or {}).get("game")
        move = (data or {}).get("move")
        if not room or room not in active_games:
            return
        players = active_games[room]["players"]
        # forward move to the other player(s)
        for s in players:
            if s != request.sid:
                try:
                    emit("game_move", {"room": room, "game": game, "move": move}, to=s)
                except Exception:
                    pass

    @socketio.on("game_reset")
    def on_game_reset(data):
        room = (data or {}).get("room")
        game = (data or {}).get("game")
        if not room or room not in active_games:
            return
        players = active_games[room]["players"]
        for s in players:
            if s != request.sid:
                try:
                    emit("game_reset", {"room": room, "game": game}, to=s)
                except Exception:
                    pass

    return app, socketio

def open_browser(port):
    try:
        import webbrowser
        webbrowser.open_new(f"http://localhost:{port}")
    except Exception:
        pass

def handle_signals():
    def _handler(signum, frame):
        cleanup()
        os._exit(0)
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, _handler)
        except Exception:
            pass

def run_server():
    write_assets()
    handle_signals()
    atexit.register(cleanup)
    app, sio = make_app()

    port = DEFAULT_PORT
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                break
            except OSError:
                port += 1
                if port > DEFAULT_PORT + 50:
                    raise RuntimeError("پورت مناسب پیدا نشد")

    ips = []
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
    except Exception:
        pass
    print("="*50)
    print(f"{APP_TITLE}")
    print(f"شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"لوکال: http://localhost:{port}")
    for ip in ips:
        if ip and not ip.startswith("127."):
            print(f"LAN:    http://{ip}:{port}")
    print("="*50)

    threading.Timer(0.6, lambda: open_browser(port)).start()
    sio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run_server()
