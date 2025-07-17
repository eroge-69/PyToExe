from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import nest_asyncio
import yt_dlp

app = FastAPI()
nest_asyncio.apply()

# Reproductor con drag & drop, duración, modo oscuro, click para reproducir
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Reprotube</title>
  <style>
    body { font-family: Tahoma; background: #d4d0c8; padding: 10px; font-size: 13px; }
    .container { display: flex; gap: 15px; }
    .left-column { flex: 0 0 350px; }
    .right-column { flex: 1; }
    .panel { background: #fff; border: 2px inset #aaa; padding: 10px; margin-bottom: 10px; }
    .title { background: #666; color: white; padding: 5px; margin-bottom: 5px; font-weight: bold; }
    .playlist { max-height: 250px; overflow-y: auto; border: 1px solid #999; padding-left: 0; background: #000; }
    .track {
      padding: 5px; border-bottom: 1px solid #333; cursor: grab; user-select: none; display: flex; align-items: center; justify-content: space-between; color: white;
    }
    .track.playing { background: #800000; font-weight: bold; color: white; }
    .track.next { background: #004000; font-weight: bold; color: white; }
    .track.queued { background: #333; color: white; }
    .controls button {
      font-size: 20px; padding: 12px 20px; margin: 0 5px; cursor: pointer;
      background: #eee; border: 2px solid #aaa; border-radius: 6px;
      min-width: 60px; height: 50px;
    }
    .controls button:hover { background: #ddd; }
    .move-btn {
      font-size: 14px; padding: 3px 6px; margin: 0 2px; cursor: pointer;
      background: #eee; border: 1px solid #aaa; border-radius: 3px;
    }
    .move-btn:hover { background: #ddd; }
    .track-title {
      flex-grow: 1;
      margin-right: 10px;
    }
    textarea { width: 100%; height: 120px; resize: vertical; font-family: monospace; font-size: 13px; }
    .info { margin-top: 5px; }
    .total-time { font-weight: bold; padding: 5px; background: #eee; text-align: right; }
    .add-button { 
      font-size: 16px; padding: 8px 16px; margin-top: 10px; cursor: pointer;
      background: #4CAF50; color: white; border: 1px solid #45a049; border-radius: 4px;
      width: 100%;
    }
    .add-button:hover { background: #45a049; }
  </style>
</head>
<body>
  <div class="container">
    <div class="left-column">
      <div class="panel">
        <div class="title">Pegar enlaces de YouTube</div>
        <textarea id="url" placeholder="Pega acá varios links o texto con links de YouTube..."></textarea>
        <button class="add-button" onclick="add()">Agregar todos</button>
      </div>
    </div>

    <div class="right-column">
      <div class="panel">
        <div class="title">Pista actual</div>
        <div id="current">Ninguna pista</div>
        <div class="info">
          <b>Duración:</b> <span id="dur">--:--</span> |
          <b>Restante:</b> <span id="left">--:--</span> |
          <b>Volumen:</b> <input type="range" id="vol" min="0" max="100" value="100" oninput="setVolume(this.value)" />
          <label><input type="checkbox" id="auto" checked> Reproducir lista completa</label>
        </div>
      </div>

      <div class="panel">
        <div class="title">Pista siguiente</div>
        <div id="nexttrack">Ninguna pista seleccionada</div>
      </div>

      <div class="panel">
        <div class="title">Lista de reproducción</div>
        <ul id="sortable" class="playlist"></ul>
        <div class="total-time" id="totaltime">Duración total: --:--</div>
      </div>

      <div class="controls">
        <button onclick="prev()">⏮️</button>
        <button onclick="togglePlay()">⏯️</button>
        <button onclick="stop()">⏹️</button>
        <button onclick="next()">⏭️</button>
      </div>
    </div>
  </div>

  <div id="player"></div>

  <script src="https://www.youtube.com/iframe_api"></script>
  <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
  <script>
    let playlist = [];
    let current = -1;
    let nextTrack = -1;
    let player;
    let paused = false;
    let timer;

    function formatTime(t) {
      let m = Math.floor(t / 60), s = Math.floor(t % 60);
      return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
    }

    function updateTotalTime() {
      let sum = playlist.reduce((acc, t) => acc + (t.duration || 0), 0);
      document.getElementById("totaltime").innerText = "Duración total: " + formatTime(sum);
    }

    function extractYouTubeIDs(text) {
      let regex = /(?:https?:\/\/)?(?:www\\.)?(?:youtube\\.com\\/(?:watch\\?v=|embed\\/)|youtu\\.be\\/)([\\w-]{11})/g;
      let matches = [...text.matchAll(regex)];
      return matches.map(m => m[1]);
    }

    function loadDurationForTrack(index) {
      if(index < 0 || index >= playlist.length) return;
      setTimeout(() => {
        let dur = player.getDuration();
        if(dur && dur > 0) {
          playlist[index].duration = Math.floor(dur);
          updateTotalTime();
          render();
        } else {
          loadDurationForTrack(index);
        }
      }, 500);
    }

    function getDurationForNewTrack(videoId, trackIndex) {
      // Use YouTube Data API or create temporary iframe to get duration
      fetch(`/extract_audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: `https://youtube.com/watch?v=${videoId}` })
      })
      .then(res => res.json())
      .then(data => {
        if (data.duration) {
          playlist[trackIndex].duration = data.duration;
          updateTotalTime();
          render();
        }
      })
      .catch(() => {
        // Fallback: duration will be loaded when track is played
      });
    }

    function add() {
      const input = document.getElementById("url");
      const ids = extractYouTubeIDs(input.value.trim());
      if (ids.length === 0) return alert("No se detectaron enlaces válidos de YouTube.");
      ids.forEach(id => {
        if (!playlist.some(t => t.id === id)) {
          // Add track immediately with placeholder duration
          let trackIndex = playlist.length;
          playlist.push({ id, title: `Cargando... (${id})`, duration: 0 });
          render();
          
          // Get title and duration
          fetch(`https://noembed.com/embed?url=https://youtube.com/watch?v=${id}`)
            .then(res => res.json())
            .then(data => {
              playlist[trackIndex].title = data.title || id;
              render();
              // Load duration by creating temporary player
              getDurationForNewTrack(id, trackIndex);
            });
        }
      });
      input.value = "";
    }

    function render() {
      const ul = document.getElementById("sortable");
      ul.innerHTML = "";
      playlist.forEach((track, i) => {
        let li = document.createElement("li");
        li.className = "track";
        if (i === current && !paused) li.classList.add("playing");
        else if (i === nextTrack) li.classList.add("next");
        else if (i > current) li.classList.add("queued");

        let durText = track.duration > 0 ? formatTime(track.duration) : "--:--";

        const spanText = document.createElement("span");
        spanText.className = "track-title";
        spanText.textContent = `${track.title} (${durText})`;
        spanText.ondblclick = () => setNextTrack(i);

        const btnUp = document.createElement("button");
        btnUp.className = "move-btn";
        btnUp.textContent = "↑";
        btnUp.disabled = (i === 0);
        btnUp.onclick = (e) => { e.stopPropagation(); moveTrack(i, i -1); };

        const btnDown = document.createElement("button");
        btnDown.className = "move-btn";
        btnDown.textContent = "↓";
        btnDown.disabled = (i === playlist.length -1);
        btnDown.onclick = (e) => { e.stopPropagation(); moveTrack(i, i +1); };

        li.appendChild(spanText);
        li.appendChild(btnUp);
        li.appendChild(btnDown);
        ul.appendChild(li);
      });
      document.getElementById("current").innerText = current >= 0 ? playlist[current].title : "Ninguna pista";
      document.getElementById("nexttrack").innerText = nextTrack >= 0 ? playlist[nextTrack].title : "Ninguna pista seleccionada";
      updateTotalTime();
    }

    function moveTrack(oldIndex, newIndex) {
      if(newIndex < 0 || newIndex >= playlist.length) return;
      const moved = playlist.splice(oldIndex, 1)[0];
      playlist.splice(newIndex, 0, moved);
      if (current === oldIndex) current = newIndex;
      else if (oldIndex < current && newIndex >= current) current--;
      else if (oldIndex > current && newIndex <= current) current++;
      
      if (nextTrack === oldIndex) nextTrack = newIndex;
      else if (oldIndex < nextTrack && newIndex >= nextTrack) nextTrack--;
      else if (oldIndex > nextTrack && newIndex <= nextTrack) nextTrack++;
      
      render();
    }

    function onYouTubeIframeAPIReady() {
      player = new YT.Player("player", {
        height: "0", width: "0", 
        playerVars: {
          'autoplay': 0,
          'controls': 0
        },
        events: {
          onReady: (event) => {
            console.log("YouTube player ready");
            if(current >= 0) loadDurationForTrack(current);
          },
          onStateChange: e => {
            if (e.data === YT.PlayerState.ENDED && document.getElementById("auto").checked) next();
            if(e.data === YT.PlayerState.PLAYING) { 
              paused = false;
              loadDurationForTrack(current); 
              updateTimer(); 
              render(); 
            }
            if(e.data === YT.PlayerState.PAUSED) { 
              paused = true; 
              stopTimer();
              render(); 
            }
            if(e.data === YT.PlayerState.UNSTARTED) { 
              stopTimer(); 
              paused = false; 
              render(); 
            }
          }
        }
      });
    }

    function play(i) {
      if (i < 0 || i >= playlist.length) return;
      if (!player || !player.loadVideoById) {
        console.log("Player not ready for playback");
        return;
      }
      
      current = i;
      paused = false;
      console.log("Playing track:", playlist[i].title, "ID:", playlist[i].id);
      
      try {
        player.loadVideoById(playlist[i].id);
        updateTimer();
        render();
      } catch (error) {
        console.error("Error loading video:", error);
      }
    }

    function togglePlay() {
      if (!player || !player.getPlayerState) {
        console.log("Player not ready");
        return;
      }
      
      try {
        const state = player.getPlayerState();
        console.log("Player state:", state);
        
        if (state === YT.PlayerState.PLAYING) { 
          paused = true; 
          player.pauseVideo(); 
        }
        else if (state === YT.PlayerState.PAUSED) { 
          paused = false; 
          player.playVideo(); 
          updateTimer(); 
        }
        else if (state === YT.PlayerState.ENDED || state === YT.PlayerState.UNSTARTED || state === YT.PlayerState.CUED) {
          if (playlist.length > 0) {
            play(current >= 0 ? current : 0);
          }
        }
        render();
      } catch (error) {
        console.error("Error in togglePlay:", error);
      }
    }

    function stop() {
      paused = false; current = -1;
      player.stopVideo(); stopTimer(); render();
    }

    function setNextTrack(i) {
      nextTrack = i;
      render();
    }

    function next() {
      if (nextTrack >= 0) {
        play(nextTrack);
        nextTrack = -1;
      } else if (current + 1 < playlist.length) {
        play(current + 1);
      } else {
        stop();
      }
    }

    function prev() {
      if (current > 0) play(current - 1);
    }

    function updateTimer() {
      stopTimer();
      timer = setInterval(() => {
        if (!player || !player.getDuration || !player.getCurrentTime) return;
        
        try {
          let dur = Math.floor(player.getDuration());
          let cur = Math.floor(player.getCurrentTime());
          if (dur > 0 && cur >= 0) {
            document.getElementById("dur").innerText = formatTime(dur);
            document.getElementById("left").innerText = formatTime(Math.max(0, dur - cur));
            if(current >= 0 && playlist[current] && playlist[current].duration !== dur) {
              playlist[current].duration = dur;
              updateTotalTime();
              render();
            }
          }
        } catch (error) {
          console.error("Timer error:", error);
        }
      }, 1000);
    }

    function stopTimer() {
      clearInterval(timer);
    }

    function setVolume(v) {
      if (player) player.setVolume(parseInt(v));
    }

    new Sortable(document.getElementById("sortable"), {
      animation: 150,
      onEnd: function (evt) {
        const moved = playlist.splice(evt.oldIndex, 1)[0];
        playlist.splice(evt.newIndex, 0, moved);
        if (current === evt.oldIndex) current = evt.newIndex;
        else if (evt.oldIndex < current && evt.newIndex >= current) current--;
        else if (evt.oldIndex > current && evt.newIndex <= current) current++;
        
        if (nextTrack === evt.oldIndex) nextTrack = evt.newIndex;
        else if (evt.oldIndex < nextTrack && evt.newIndex >= nextTrack) nextTrack--;
        else if (evt.oldIndex > nextTrack && evt.newIndex <= nextTrack) nextTrack++;
        
        render();
      }
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_PAGE)

@app.post("/extract_audio")
async def extract_audio(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return JSONResponse({"error": "URL vacía"}, status_code=400)

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "extract_flat": False,
        "forcejson": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "Sin título"),
                "duration": int(info.get("duration", 0)),
                "audio_url": info["url"]
            }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
