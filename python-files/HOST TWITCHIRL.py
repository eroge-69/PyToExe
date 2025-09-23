# Write v2.1 single-file with auto-switch watcher and OBS helpers
path = "/mnt/data/twitch_remote_host_single.py"

code = r'''"""
Twitch Remote Host — SINGLE FILE (Python) — v2.1 (auto-switch + integrated endpoints)
By: Ricardito

What it does:
- Connects to Twitch Chat (twitchio) and listens for commands
- Controls OBS via WebSocket v5 (obsws-python)
- HTTP panel (FastAPI + Uvicorn) with endpoints:
  * GET  /status
  * GET  /start
  * GET  /stop
  * GET  /scenes
  * GET  /switch?name=...
  * GET  /rec?state=on|off
  * GET  /audio/mute?source=Mic/Aux&state=on|off
  * GET  /source/visibility?scene=SCENE&source=SOURCE&visible=1|0
  * GET  /overlay/config?scene=SCENE
  * POST /overlay/config   JSON: {"scene": "...", "overlay": {"chat":true,"alerts":false,"camFrame":true,"ticker":false}}
- AUTO-SWITCH: watches an input (e.g., SRT Media Source "iPhoneSRT"); when signal becomes active/playing, switches to a scene (e.g., "Cena iPhone").
  Optionally switches back to a fallback scene when signal disappears for a grace period.
- Designed for iPhone camera/mic via Larix (SRT) feeding into OBS Media Source (listener)

Run (Windows VM suggested):
  pip install twitchio obsws-python python-dotenv fastapi uvicorn
  python twitch_remote_host_single.py --twitch-channel SEU_CANAL --twitch-token oauth:xxxx --obs-password SUA_SENHA

Build .EXE (PyInstaller):
  pip install pyinstaller
  pyinstaller --onefile --name twitch-remote-host twitch_remote_host_single.py

ENV VARS / CLI (flags override env):
  TWITCH_CHANNEL, TWITCH_TOKEN, OBS_HOST, OBS_PORT, OBS_PASSWORD
  HTTP_PANEL(true/false), HTTP_HOST, HTTP_PORT
  AUTHORIZED_USERS (comma)
  DEFAULT_SCENES (comma)
  AUTO_SWITCH_ENABLED(true/false)
  AUTO_SWITCH_INPUT (e.g., iPhoneSRT)
  AUTO_SWITCH_SCENE (e.g., Cena iPhone)
  AUTO_SWITCH_FALLBACK (optional, e.g., Starting Soon)
  AUTO_SWITCH_INTERVAL_SEC (default 2)
  AUTO_SWITCH_GRACE_SEC (signal must persist this many seconds; default 2)
"""
import os
import argparse
import asyncio
import json
import time
import threading
from typing import Optional, Dict, Any

# ----- Optional dotenv -----
try:
    from dotenv import load_dotenv
    _has_dotenv = True
except Exception:
    _has_dotenv = False

# ----- TwitchIO -----
try:
    from twitchio.ext import commands
    _has_twitchio = True
except Exception as e:
    _has_twitchio = False
    _twitchio_err = e

# ----- OBS WebSocket v5 client -----
try:
    from obsws_python import reqs
    from obsws_python.error import OBSSDKRequestError
    from obsws_python import obsws
    _has_obsws = True
except Exception as e:
    _has_obsws = False
    _obsws_err = e

# ----- HTTP panel -----
try:
    from fastapi import FastAPI, Body
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    _has_fastapi = True
except Exception as e:
    _has_fastapi = False
    _fastapi_err = e

# --------------------
# Config & CLI
# --------------------
def load_config():
    if _has_dotenv:
        here = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(here, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)

    parser = argparse.ArgumentParser(description="Twitch Remote Host (single-file v2.1)")
    parser.add_argument("--twitch-channel", default=os.getenv("TWITCH_CHANNEL", ""), help="Twitch channel (sem @)")
    parser.add_argument("--twitch-token", default=os.getenv("TWITCH_TOKEN", ""), help="Token TMI do chat (oauth:xxxx)")
    parser.add_argument("--obs-host", default=os.getenv("OBS_HOST", "127.0.0.1"), help="Host OBS WebSocket")
    parser.add_argument("--obs-port", type=int, default=int(os.getenv("OBS_PORT", "4455")), help="Porta OBS WebSocket")
    parser.add_argument("--obs-password", default=os.getenv("OBS_PASSWORD", ""), help="Senha do OBS WebSocket")
    parser.add_argument("--http-panel", default=os.getenv("HTTP_PANEL", "true"), help="Ativar painel HTTP (true/false)")
    parser.add_argument("--http-host", default=os.getenv("HTTP_HOST", "0.0.0.0"), help="Host do painel HTTP")
    parser.add_argument("--http-port", type=int, default=int(os.getenv("HTTP_PORT", "8088")), help="Porta do painel HTTP")
    parser.add_argument("--auth-users", default=os.getenv("AUTHORIZED_USERS", ""), help="Usuários autorizados extras, separados por vírgula")
    parser.add_argument("--default-scenes", default=os.getenv("DEFAULT_SCENES", "Cena iPhone,Gameplay,Be Right Back,Starting Soon"), help="Lista de cenas (apenas exibição)")

    # Auto-switch flags
    parser.add_argument("--auto-switch-enabled", default=os.getenv("AUTO_SWITCH_ENABLED", "true"), help="Ativar auto-switch (true/false)")
    parser.add_argument("--auto-switch-input", default=os.getenv("AUTO_SWITCH_INPUT", "iPhoneSRT"), help="Nome da Input (OBS) a monitorar (ex: Media Source SRT)")
    parser.add_argument("--auto-switch-scene", default=os.getenv("AUTO_SWITCH_SCENE", "Cena iPhone"), help="Cena para comutar quando o sinal ficar ativo")
    parser.add_argument("--auto-switch-fallback", default=os.getenv("AUTO_SWITCH_FALLBACK", ""), help="Cena fallback quando perder sinal (opcional)")
    parser.add_argument("--auto-switch-interval-sec", type=float, default=float(os.getenv("AUTO_SWITCH_INTERVAL_SEC", "2")), help="Intervalo de checagem (s)")
    parser.add_argument("--auto-switch-grace-sec", type=float, default=float(os.getenv("AUTO_SWITCH_GRACE_SEC", "2")), help="Sinal deve permanecer ativo por X segundos")

    args = parser.parse_args()

    cfg = {
        "TWITCH_CHANNEL": args.twitch_channel,
        "TWITCH_TOKEN": args.twitch_token,
        "OBS_HOST": args.obs_host,
        "OBS_PORT": int(args.obs_port),
        "OBS_PASSWORD": args.obs_password,
        "HTTP_PANEL": str(args.http_panel).lower() == "true",
        "HTTP_HOST": args.http_host,
        "HTTP_PORT": int(args.http_port),
        "AUTHORIZED_USERS": set(u.strip().lower() for u in args.auth_users.split(",") if u.strip()),
        "DEFAULT_SCENES": [s.strip() for s in args.default_scenes.split(",") if s.strip()],
        # Auto-switch
        "AUTO_SWITCH_ENABLED": str(args.auto_switch_enabled).lower() == "true",
        "AUTO_SWITCH_INPUT": args.auto_switch_input,
        "AUTO_SWITCH_SCENE": args.auto_switch_scene,
        "AUTO_SWITCH_FALLBACK": args.auto_switch_fallback,
        "AUTO_SWITCH_INTERVAL_SEC": float(args.auto_switch_interval_sec),
        "AUTO_SWITCH_GRACE_SEC": float(args.auto_switch_grace_sec),
    }
    if not _has_fastapi:
        cfg["HTTP_PANEL"] = False
    return cfg

# --------------------
# OBS Client Wrapper (thread-safe)
# --------------------
class OBSController:
    def __init__(self, host: str, port: int, password: str):
        if not _has_obsws:
            raise RuntimeError(f"obsws-python não está instalado: {_obsws_err}")
        self.host = host
        self.port = port
        self.password = password
        self._client: Optional[obsws] = None
        self._lock = threading.Lock()

    def connect(self):
        with self._lock:
            if self._client:
                return
            self._client = obsws(host=self.host, port=self.port, password=self.password, timeout=5)
            self._client.connect()
            print(f"[OBS] Conectado em {self.host}:{self.port}")

    def disconnect(self):
        with self._lock:
            if self._client:
                self._client.disconnect()
                self._client = None
                print("[OBS] Desconectado")

    def _call(self, request):
        if not self._client:
            raise RuntimeError("OBS não conectado")
        try:
            return self._client.call(request)
        except OBSSDKRequestError as e:
            raise RuntimeError(f"OBS error: {e}")

    # ---- High-level actions ----
    def start_stream(self):
        with self._lock:
            return self._call(reqs.StartStreamRequest())

    def stop_stream(self):
        with self._lock:
            return self._call(reqs.StopStreamRequest())

    def start_record(self):
        with self._lock:
            return self._call(reqs.StartRecordRequest())

    def stop_record(self):
        with self._lock:
            return self._call(reqs.StopRecordRequest())

    def switch_scene(self, scene_name: str):
        with self._lock:
            return self._call(reqs.SetCurrentProgramSceneRequest(sceneName=scene_name))

    def current_program_scene(self) -> str:
        with self._lock:
            res = self._call(reqs.GetCurrentProgramSceneRequest())
            return res.currentProgramSceneName

    def list_scenes(self):
        with self._lock:
            res = self._call(reqs.GetSceneListRequest())
            return [s.sceneName for s in res.scenes]

    def mute(self, source: str, mute: bool):
        with self._lock:
            return self._call(reqs.SetInputMuteRequest(inputName=source, inputMuted=mute))

    def get_scene_item_id(self, scene: str, source: str) -> int:
        res = self._call(reqs.GetSceneItemListRequest(sceneName=scene))
        for item in res.sceneItems:
            if item.sourceName == source:
                return item.sceneItemId
        raise RuntimeError(f"Fonte '{source}' não encontrada na cena '{scene}'")

    def toggle_source_visibility(self, scene: str, source: str, visible: bool):
        with self._lock:
            scene_item_id = self.get_scene_item_id(scene, source)
            return self._call(reqs.SetSceneItemEnabledRequest(sceneName=scene, sceneItemId=scene_item_id, sceneItemEnabled=visible))

    def get_source_visibility(self, scene: str, source: str) -> Optional[bool]:
        with self._lock:
            scene_item_id = self.get_scene_item_id(scene, source)
            try:
                res = self._call(reqs.GetSceneItemEnabledRequest(sceneName=scene, sceneItemId=scene_item_id))
                return bool(res.sceneItemEnabled)
            except Exception:
                return None

    def status(self) -> Dict[str, Any]:
        with self._lock:
            s = self._call(reqs.GetStreamStatusRequest())
            r = self._call(reqs.GetRecordStatusRequest())
            return {
                "streaming": s.outputActive,
                "recording": r.outputActive,
                "bytes": s.outputBytes,
                "skipped_frames": s.outputSkippedFrames,
                "total_frames": s.outputTotalFrames,
                "congestion": s.outputCongestion,
            }

    # ---- Auto-switch helpers ----
    def get_input_active(self, input_name: str) -> Optional[bool]:
        """Returns True if input is active on the program (v5: GetInputActive)."""
        with self._lock:
            try:
                res = self._call(reqs.GetInputActiveRequest(inputName=input_name))
                return bool(res.inputActive)
            except Exception:
                return None

    def get_media_input_playing(self, input_name: str) -> Optional[bool]:
        """Returns True if a 'Media Source' input is playing (v5: GetMediaInputStatus)."""
        with self._lock:
            try:
                res = self._call(reqs.GetMediaInputStatusRequest(inputName=input_name))
                # In v5 responses: mediaState might be an enum; here we test common states
                # We treat 'playing' (or non-paused non-stopped) as active.
                is_playing = getattr(res, "mediaState", None)
                if isinstance(is_playing, str):
                    return is_playing.upper() in ("OBS_MEDIA_STATE_PLAYING", "PLAYING")
                # Fallback heuristics
                return bool(getattr(res, "mediaDuration", 1))  # if it exists, assume active
            except Exception:
                return None

# --------------------
# Auto-switch Task
# --------------------
async def auto_switch_task(cfg, obsctl: OBSController):
    if not cfg.get("AUTO_SWITCH_ENABLED", True):
        return
    input_name = cfg.get("AUTO_SWITCH_INPUT", "iPhoneSRT")
    target_scene = cfg.get("AUTO_SWITCH_SCENE", "Cena iPhone")
    fallback_scene = cfg.get("AUTO_SWITCH_FALLBACK", "").strip() or None
    interval = float(cfg.get("AUTO_SWITCH_INTERVAL_SEC", 2.0))
    grace = float(cfg.get("AUTO_SWITCH_GRACE_SEC", 2.0))

    last_active_ts = 0.0
    was_active = False
    print(f"[AUTO] Watching input='{input_name}' -> scene='{target_scene}' (fallback='{fallback_scene or '-'}') every {interval}s; grace={grace}s")

    while True:
        try:
            # Prefer GetInputActive (program active), fallback to media playing
            active = obsctl.get_input_active(input_name)
            if active is None:
                active = obsctl.get_media_input_playing(input_name)

            now = time.time()
            if active:
                if not was_active:
                    last_active_ts = now
                # Only switch if sustained for grace seconds
                if (now - last_active_ts) >= grace:
                    current = obsctl.current_program_scene()
                    if current != target_scene:
                        try:
                            obsctl.switch_scene(target_scene)
                            print(f"[AUTO] Switched to '{target_scene}' (signal detected)")
                        except Exception as e:
                            print(f\"[AUTO] Switch error: {e}\")
                was_active = True
            else:
                # No signal
                was_active = False
                last_active_ts = 0.0
                if fallback_scene:
                    # Optional: if currently on target_scene and no signal, switch back
                    try:
                        current = obsctl.current_program_scene()
                        if current == target_scene:
                            obsctl.switch_scene(fallback_scene)
                            print(f\"[AUTO] Fallback to '{fallback_scene}' (no signal)\")
                    except Exception as e:
                        print(f\"[AUTO] Fallback error: {e}\")
        except Exception as e:
            print(f\"[AUTO] Watch error: {e}\")

        await asyncio.sleep(interval)

# --------------------
# Twitch Bot
# --------------------
def build_bot(cfg, obsctl: OBSController):
    if not _has_twitchio:
        raise RuntimeError(f"twitchio não está instalado: {_twitchio_err}")

    class TwitchBot(commands.Bot):
        def __init__(self):
            super().__init__(
                token=cfg["TWITCH_TOKEN"],
                prefix="!",
                initial_channels=[cfg["TWITCH_CHANNEL"]] if cfg["TWITCH_CHANNEL"] else [],
            )

        async def event_ready(self):
            print(f"[TWITCH] Logado como {self.nick}")
            try:
                obsctl.connect()
            except Exception as e:
                print(f"[OBS] Falha ao conectar: {e}")

        async def event_message(self, message):
            if message.echo:
                return
            await self.handle_commands(message)

        def _is_authorized(self, ctx) -> bool:
            name = (getattr(ctx.author, "name", "") or "").lower()
            is_mod = bool(getattr(ctx.author, "is_mod", False))
            is_broadcaster = False
            try:
                is_broadcaster = bool(getattr(ctx.author, "is_broadcaster", False))
            except Exception:
                pass
            try:
                badges = getattr(ctx.author, "badges", None)
                if isinstance(badges, dict):
                    is_broadcaster = is_broadcaster or ("broadcaster" in badges)
                elif isinstance(badges, (list, tuple)):
                    is_broadcaster = is_broadcaster or any((getattr(b, "name", "").lower() == "broadcaster") for b in badges)
            except Exception:
                pass
            if cfg["AUTHORIZED_USERS"]:
                return name in cfg["AUTHORIZED_USERS"]
            return is_mod or is_broadcaster or (name == cfg["TWITCH_CHANNEL"].lower())

        # ---- Commands ----
        @commands.command(name="start")
        async def start_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            try:
                obsctl.start_stream()
                await ctx.send("▶️ Live iniciada.")
            except Exception as e:
                await ctx.send(f"Erro ao iniciar: {e}")

        @commands.command(name="stop")
        async def stop_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            try:
                obsctl.stop_stream()
                await ctx.send("⏹️ Live finalizada.")
            except Exception as e:
                await ctx.send(f"Erro ao parar: {e}")

        @commands.command(name="rec")
        async def rec_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            arg = (ctx.message.content.strip().split(" ") + [""])[1].lower()
            try:
                if arg in ("on", "start"):
                    obsctl.start_record()
                    await ctx.send("⏺️ Gravação ON.")
                elif arg in ("off", "stop"):
                    obsctl.stop_record()
                    await ctx.send("⏹️ Gravação OFF.")
                else:
                    await ctx.send("Uso: !rec on|off")
            except Exception as e:
                await ctx.send(f"Erro grav.: {e}")

        @commands.command(name="cena")
        async def scene_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            parts = ctx.message.content.strip().split(" ", 1)
            if len(parts) == 1:
                try:
                    scenes = obsctl.list_scenes()
                    await ctx.send("Cenas: " + ", ".join(scenes))
                except Exception as e:
                    await ctx.send(f"Erro listando cenas: {e}")
                return
            scene = parts[1]
            try:
                obsctl.switch_scene(scene)
                await ctx.send(f"🎬 Cena: {scene}")
            except Exception as e:
                await ctx.send(f"Erro cena: {e}")

        @commands.command(name="mute")
        async def mute_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            parts = ctx.message.content.strip().split(" ")
            if len(parts) < 3:
                await ctx.send("Uso: !mute <FonteDeAudio> on|off")
                return
            source, state = parts[1], parts[2].lower()
            try:
                obsctl.mute(source, state in ("on", "true", "1"))
                await ctx.send(f"🔇 {source}: {state}")
            except Exception as e:
                await ctx.send(f"Erro mute: {e}")

        @commands.command(name="show")
        async def show_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            parts = ctx.message.content.strip().split(" ")
            if len(parts) < 3:
                await ctx.send("Uso: !show <Cena> <Fonte>")
                return
            scene, source = parts[1], parts[2]
            try:
                obsctl.toggle_source_visibility(scene, source, True)
                await ctx.send(f"👁️ {source} visível em {scene}")
            except Exception as e:
                await ctx.send(f"Erro show: {e}")

        @commands.command(name="hide")
        async def hide_cmd(self, ctx: commands.Context):
            if not self._is_authorized(ctx): return
            parts = ctx.message.content.strip().split(" ")
            if len(parts) < 3:
                await ctx.send("Uso: !hide <Cena> <Fonte>")
                return
            scene, source = parts[1], parts[2]
            try:
                obsctl.toggle_source_visibility(scene, source, False)
                await ctx.send(f"🙈 {source} oculto em {scene}")
            except Exception as e:
                await ctx.send(f"Erro hide: {e}")

        @commands.command(name="status")
        async def status_cmd(self, ctx: commands.Context):
            try:
                st = obsctl.status()
                await ctx.send(f"Status — Streaming: {st['streaming']} | Recording: {st['recording']} | Frames: {st['total_frames']}")
            except Exception as e:
                await ctx.send(f"Erro status: {e}")

    return TwitchBot()

# --------------------
# HTTP Panel (integrated endpoints)
# --------------------
def build_http_app(cfg, obsctl: OBSController):
    if not _has_fastapi:
        return None

    app = FastAPI(title="Twitch Remote Host Panel v2.1")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/")
    def root():
        return {"ok": True, "routes": [
            "/status", "/start", "/stop", "/scenes", "/switch?name=",
            "/rec?state=on|off",
            "/audio/mute?source=&state=on|off",
            "/source/visibility?scene=&source=&visible=1|0",
            "/overlay/config (GET/POST)"
        ]}

    @app.get("/status")
    def status():
        try:
            return obsctl.status()
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/start")
    def start_stream():
        try:
            obsctl.start_stream()
            return {"ok": True}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/stop")
    def stop_stream():
        try:
            obsctl.stop_stream()
            return {"ok": True}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/scenes")
    def scenes():
        try:
            return {"scenes": obsctl.list_scenes()}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/switch")
    def switch(name: str):
        try:
            obsctl.switch_scene(name)
            return {"ok": True, "switched_to": name}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/rec")
    def rec(state: str):
        try:
            st = state.lower()
            if st in ("on", "start"):
                obsctl.start_record()
            elif st in ("off", "stop"):
                obsctl.stop_record()
            else:
                return JSONResponse({"error": "Parâmetro state deve ser on|off"}, status_code=400)
            return {"ok": True, "record": st}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/audio/mute")
    def audio_mute(source: str, state: str):
        try:
            obsctl.mute(source, state.lower() in ("on", "true", "1"))
            return {"ok": True, "source": source, "muted": state.lower() in ("on", "true", "1")}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.get("/source/visibility")
    def source_visibility(scene: str, source: str, visible: int):
        try:
            vis = bool(int(visible))
            obsctl.toggle_source_visibility(scene, source, vis)
            return {"ok": True, "scene": scene, "source": source, "visible": vis}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    OVERLAY_KEYS = {
        "chat": "Overlay.Chat",
        "alerts": "Overlay.Alerts",
        "camFrame": "Overlay.CamFrame",
        "ticker": "Overlay.Ticker",
    }

    @app.get("/overlay/config")
    def overlay_get(scene: str):
        try:
            out = {}
            for key, src in OVERLAY_KEYS.items():
                try:
                    vis = obsctl.get_source_visibility(scene, src)
                except Exception:
                    vis = None
                out[key] = vis
            return {"scene": scene, "overlay": out}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/overlay/config")
    def overlay_set(payload: Dict[str, Any] = Body(...)):
        try:
            scene = payload.get("scene") or ""
            overlay_cfg = payload.get("overlay") or {}
            if not scene:
                return JSONResponse({"error": "scene é obrigatório"}, status_code=400)

            results = {}
            for key, src in OVERLAY_KEYS.items():
                if key in overlay_cfg:
                    target = bool(overlay_cfg[key])
                    try:
                        obsctl.toggle_source_visibility(scene, src, target)
                        results[key] = {"source": src, "visible": target, "ok": True}
                    except Exception as e:
                        results[key] = {"source": src, "visible": None, "ok": False, "error": str(e)}
                else:
                    results[key] = {"source": src, "visible": None, "ok": True, "skipped": True}

            return {"ok": True, "scene": scene, "results": results}
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return app

# --------------------
# Entrypoint
# --------------------
async def main_async():
    cfg = load_config()

    if not cfg["TWITCH_CHANNEL"] or not cfg["TWITCH_TOKEN"]:
        print("[WARN] Defina TWITCH_CHANNEL e TWITCH_TOKEN via CLI ou env para conectar ao chat da Twitch.")
    if not _has_twitchio:
        print(f"[WARN] twitchio ausente: {_twitchio_err}")
    if not _has_obsws:
        print(f"[WARN] obsws-python ausente: {_obsws_err}")
    if cfg["HTTP_PANEL"] and not _has_fastapi:
        print(f"[WARN] FastAPI/Uvicorn não instalados — painel HTTP desativado: {_fastapi_err}")

    obsctl = OBSController(cfg["OBS_HOST"], cfg["OBS_PORT"], cfg["OBS_PASSWORD"])

    tasks = []

    # Twitch bot
    if _has_twitchio and cfg["TWITCH_CHANNEL"] and cfg["TWITCH_TOKEN"]:
        bot = build_bot(cfg, obsctl)
        tasks.append(bot.start())

    # HTTP panel
    if cfg["HTTP_PANEL"] and _has_fastapi:
        loop = asyncio.get_running_loop()
        def run_panel():
            uvicorn.run(build_http_app(cfg, obsctl), host=cfg["HTTP_HOST"], port=cfg["HTTP_PORT"], log_level="info")
        tasks.append(loop.run_in_executor(None, run_panel))

    # Auto-switch watcher
    if cfg.get("AUTO_SWITCH_ENABLED", True):
        tasks.append(auto_switch_task(cfg, obsctl))

    if tasks:
        await asyncio.gather(*tasks)
    else:
        print("Nenhuma tarefa ativa. Verifique as dependências e configurações.")

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass
'''
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

path
