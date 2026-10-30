import sys
import os
import random
import time
import datetime
import html
import json
import math
import shutil
import tempfile
import threading
import wave
import struct
import ctypes
import base64
import subprocess
import re
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextBrowser, QSystemTrayIcon, QMenu, QInputDialog, QPushButton,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QMessageBox
)
from PySide6.QtGui import (
    QPixmap, QColor, QPainter, QTransform, QCursor, QIcon, QAction, QPen, QBrush,
    QPolygonF, QRadialGradient, QLinearGradient, QFont, QFontMetrics, QPainterPath, QTextDocument, QImage, QRegion
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QPoint, QPointF, QRectF, QObject, QUrl,
    QAbstractNativeEventFilter, QPropertyAnimation, QRect, QEasingCurve, QVariantAnimation
)
try:
    from PySide6.QtMultimedia import QSoundEffect
except Exception:
    QSoundEffect = None
try:
    import pygetwindow as gw
except Exception:
    gw = None

BASE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATAS = [os.path.join(BASE, "gengar_img"), "D:/IA-Modelos/gengar_img"]
RUTA_IMAGENES = next((r for r in _CANDIDATAS if os.path.isdir(r)), _CANDIDATAS[0])
RUTA_CARA = os.path.join(RUTA_IMAGENES, "cara_gengar.jpg")
RUTA_CONFIG = os.path.join(BASE, "gengar_config.json")
RUTA_SONIDOS = os.path.join(BASE, "sonidos")
FPS = 12
SPR = 130
W, H = SPR + 60, SPR + 100
SPR_X, SPR_Y = (W - SPR) // 2, H - SPR
SINK_PIE = 0
SINK_SENTADO = 25
OFFSET_PIE = 10
LIBRES = ("patrulla", "quieto_de_pie", "sentado")
ESTADOS_PERCHA = ("en_ventana", "claude", "poseer")
ESTADOS_BOB = ("espera", "flotar", "victoria", "teleport", "quieto_de_pie", "luna")
IDLE_ASOMARSE = 60
MIN_SUENO = 10
SEG_DISOLVER = 420
LUNA_LARGA_MIN = 8
LUNA_LARGA_ACC = 50
PUERTO = int(os.environ.get("GENGAR_PORT", "47831"))
RUTA_HOOK = os.path.join(BASE, "gengar_hook.py")
RUTA_SETTINGS_CLAUDE = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
MARCA_HOOK = "gengar_hook.py"
EVENTOS_HOOK = {
    "SessionStart": None, "UserPromptSubmit": None,
    "PreToolUse": "*", "PostToolUse": "*", "PostToolUseFailure": "*",
    "Notification": None, "Stop": None, "SubagentStop": None, "SessionEnd": None,
}
ESTILO_TICKER = ("background-color: rgba(14,10,23,240); color: #39ff88; border: 2px solid #7c4dff; "
                 "font-family: Consolas; font-size: 9px; font-weight: bold; padding: 0px 4px;")
VIOLETAS = ["#b388ff", "#8a63d2", "#6a4c93", "#d9c2ff"]
ROJOS = ["#ff3b5c", "#ff5252", "#ff8a80", "#ffffff"]
COLOR_PRIMARIO = "#39ff88"
COLOR_SECUNDARIO = "#7c4dff"
MODO_DND = False
ANIM_PATRULLA = ["shime2.png", "shime2b.png", "shime2.png", "shime2c.png", "shime2a.png"]
ANIM_QUIETO = ["shime1.png", "shime1.png", "shime1.png", "shime1.png", "shime1a.png"]
ANIM_SENTADO = ["shime30.png", "shime31.png", "shime31a.png", "shime31b.png", "shime32.png",
                "shime32a.png", "shime32b.png", "shime32c.png", "shime33.png"]
ANIM_PENSANDO = ["shime47.png", "shime47a.png", "shime47b.png", "shime47a.png"]
ANIM_DORMIR = ["shime20.png", "shime21.png", "shime20a.png", "shime21a.png"]
ANIM_BAILAR = ["dance1.png", "dance1b.png", "dance1c.png", "dance1d.png",
               "dance2.png", "dance2b.png", "dance3.png", "dance3b.png",
               "dance3c.png", "dance3d.png"]
ANIM_CASCOS = ["00.png", "01.png", "02.png", "03.png", "04.png", "05.png"]
ANIM_HIPNOSIS = ["shime38.png", "shime38a.png", "shime39.png", "shime39a.png",
                 "shime40.png", "shime40a.png", "shime41.png", "shime41a.png"]
ANIM_CAER = ["shime4.png"]
ANIM_BOLA = ["shime42.png", "shime42a.png", "shime43.png", "shime44.png",
             "shime45.png", "shime45a.png", "shime46.png", "shime46a.png"]
ANIM_HUMO = ["shime15.png", "shime16.png", "shime17.png"]
ANIM_ARRASTRADO = ["shime5.png", "shime6.png", "shime7.png", "shime6.png"]
ANIM_CARICIA = ["shime18.png", "shime19.png", "shime18.png"]
ANIM_TRAVESURA = ["shime34.png", "shime34a.png", "shime34b.png", "shime34c.png"]
ANIM_ASOMADO = ["shime9.png", "shime10.png"]
ANIM_PARED_IZQ = ["shime12.png", "shime12a.png", "shime13.png", "shime14.png"]
ANIM_PARED_DER = ["shime12.png", "shime12a.png", "shime13.png", "shime14.png"]
ANIM_FLOTAR = ["shime3.png", "shime3a.png", "shime3b.png", "shime3c.png"]
ANIM_ALERTA = ["shime23.png", "shime23a.png", "shime24.png", "shime25.png"]
ANIM_ERROR = ["shime4.png", "shime8.png", "shime9.png", "shime10.png"]
ANIM_VICTORIA = ["shime40.png", "shime40a.png", "shime41.png", "shime41a.png",
                 "shime38.png", "shime38a.png", "shime39.png", "shime39a.png"]
ANIM_RISA = ["shime22.png", "shime19.png", "shime22.png", "shime19.png"]
ANIM_SALUDO = ["shime1a.png", "shime22.png", "shime1a.png"]
ANIM_RESPLANDOR = ["shime26.png", "shime26a.png", "shime27.png"]
ANIMACIONES = {
    "patrulla": ANIM_PATRULLA, "trepar_ir": ANIM_PATRULLA,
    "quieto_de_pie": ANIM_QUIETO, "sentado": ANIM_SENTADO, "en_ventana": ANIM_SENTADO,
    "pensando": ANIM_PENSANDO, "dormir": ANIM_DORMIR, "bailar": ANIM_BAILAR,
    "baile_musica": ANIM_CASCOS,
    "hipnosis": ANIM_HIPNOSIS, "caer": ANIM_CAER, "bola_fantasma": ANIM_BOLA,
    "humo": ANIM_HUMO, "arrastrado": ANIM_ARRASTRADO, "caricia": ANIM_CARICIA,
    "travesura": ANIM_TRAVESURA, "cursor": ANIM_TRAVESURA, "asomado": ANIM_ASOMADO,
    "asomado_arriba": ANIM_ASOMADO,
    "trepar_izq": ANIM_PARED_IZQ, "trepar_der": ANIM_PARED_DER,
    "claude": ANIM_PENSANDO,
    "claude_leer": ANIM_PENSANDO, "claude_escribir": ANIM_SENTADO,
    "claude_cmd": ANIM_TRAVESURA, "claude_web": ANIM_HIPNOSIS, "claude_agente": ANIM_FLOTAR,
    "espera": ANIM_ALERTA, "error": ANIM_ERROR, "victoria": ANIM_VICTORIA, "risa": ANIM_RISA,
    "saludo": ANIM_SALUDO,
    "flotar": ANIM_FLOTAR, "teleport": ANIM_HUMO, "poseer": ANIM_HIPNOSIS,
    "dormir_largo": ANIM_DORMIR,
    "luna": ANIM_PENSANDO, "luna_mirar": ANIM_PENSANDO, "luna_alcanzar": ANIM_FLOTAR,
    "luna_carga": ANIM_TRAVESURA, "luna_rayo": ANIM_HIPNOSIS,
}
SIN_VOLTEAR = set()
HOLD = {"quieto_de_pie": 3, "sentado": 4, "en_ventana": 4, "dormir": 6, "pensando": 3,
        "hipnosis": 2, "humo": 4, "caricia": 4, "asomado": 5, "asomado_arriba": 5, "arrastrado": 2,
        "claude_leer": 3, "claude_escribir": 3, "claude_cmd": 2, "claude_web": 2, "claude_agente": 3,
        "claude": 3, "espera": 2, "error": 2, "victoria": 2, "risa": 2, "dormir_largo": 8,
        "flotar": 3, "luna": 4, "luna_mirar": 4, "luna_alcanzar": 3, "luna_carga": 2, "luna_rayo": 2,
        "saludo": 3, "teleport": 3, "baile_musica": 2}
HERRAMIENTAS = {
    "Read": ("LEE", "claude_leer"), "Grep": ("BUSCA", "claude_leer"), "Glob": ("LISTA", "claude_leer"),
    "Edit": ("EDITA", "claude_escribir"), "MultiEdit": ("EDITA", "claude_escribir"),
    "Write": ("ESCRIBE", "claude_escribir"), "NotebookEdit": ("EDITA", "claude_escribir"),
    "Bash": ("EJECUTA", "claude_cmd"),
    "WebFetch": ("WEB", "claude_web"), "WebSearch": ("WEB", "claude_web"),
    "Task": ("AGENTE", "claude_agente"), "Agent": ("AGENTE", "claude_agente"),
    "TodoWrite": ("PLAN", "claude_leer"),
}
ESCRITURA = ("Edit", "Write", "MultiEdit", "NotebookEdit")
HERRAMIENTAS_LUPA = ("Read", "Grep", "Glob", "WebFetch", "WebSearch", "NotebookRead", "LS")
LUPA_SEG = 8
GLOBO_IMG = 80
FRASES_PENSAMIENTOS = [
    "Qué aburrido estoy...", "Oye, ¿sigues ahí?", "Me apetece un café, tío.",
    "¿A que no sabes lo que he pensado?", "Estoy vigilando tu código...",
    "Tío, tienes muchas pestañas abiertas.", "Podríamos dominar el mundo, pero paso.",
    "¿Hacemos algo o qué?", "Esto está muy tranquilo... demasiado.", "Ruben, ¿me oyes?",
]
FRASES_CARICIA = ["Mmm... vale, un poquito.", "Eso se agradece, tío.", "No se lo cuentes a nadie.",
                  "Más a la izquierda...", "Qué manos más frías, tío."]
FRASES_ZAP = ["¡Zas!", "Jejeje... un cosquilleo.", "Te he pillado el ratón, tío."]
IGNORAR_TITULOS = ("Program Manager", "Chat con Padrino", "Windows Input Experience")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "GengarMascota"
DWMWA_EXTENDED_FRAME_BOUNDS = 9
DWMWA_CLOAKED = 13
TAMANOS = {"Pequeño": 100, "Normal": 130, "Grande": 170}

def cargar_config():
    try:
        with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def guardar_config(cfg):
    try:
        with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def cargar_frames_atlas(ruta_json, tam):
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
        ruta_atlas = os.path.join(os.path.dirname(ruta_json), meta.get("atlas", {}).get("file", "atlas.png"))
        if not os.path.exists(ruta_atlas):
            return []
        sheet = QPixmap(ruta_atlas)
        if sheet.isNull():
            return []
        frames = []
        for fr in meta.get("frames", []):
            rect = QRect(int(fr["x"]), int(fr["y"]), int(fr["width"]), int(fr["height"]))
            pm = sheet.copy(rect)
            pm = pm.scaled(tam, tam, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            frames.append(pm)
        return frames
    except Exception:
        return []

def get_visible_rect(hwnd):
    rect = wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect))
    return rect

def inicio_activo():
    if sys.platform != "win32":
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, RUN_NAME)
            return True
    except OSError:
        return False

def configurar_inicio(activo):
    if sys.platform != "win32":
        return
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if activo:
            if getattr(sys, "frozen", False):
                cmd = f'"{sys.executable}"'
            else:
                py = sys.executable
                pyw = py.replace("python.exe", "pythonw.exe")
                if os.path.exists(pyw):
                    py = pyw
                cmd = f'"{py}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except FileNotFoundError:
                pass

def ventana_cloaked(hwnd):
    try:
        v = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(v), ctypes.sizeof(v))
        return bool(v.value)
    except Exception:
        return False

def _comando_hook():
    py = sys.executable
    cand = os.path.join(os.path.dirname(py), "python.exe")
    if os.path.exists(cand):
        py = cand
    return f'"{py}" "{RUTA_HOOK}"'.replace("\\", "/")

def _es_nuestro(grupo):
    try:
        return any(MARCA_HOOK in h.get("command", "") for h in grupo.get("hooks", []))
    except Exception:
        return False

def _leer_settings_claude():
    if not os.path.exists(RUTA_SETTINGS_CLAUDE):
        return {}
    with open(RUTA_SETTINGS_CLAUDE, "r", encoding="utf-8") as f:
        txt = f.read()
    return json.loads(txt) if txt.strip() else {}

def _escribir_settings_claude(datos):
    os.makedirs(os.path.dirname(RUTA_SETTINGS_CLAUDE), exist_ok=True)
    with open(RUTA_SETTINGS_CLAUDE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

def instalar_hooks_claude():
    if not os.path.exists(RUTA_HOOK):
        raise FileNotFoundError(f"Falta {MARCA_HOOK} junto a este script")
    datos = _leer_settings_claude()
    if os.path.exists(RUTA_SETTINGS_CLAUDE):
        copia = RUTA_SETTINGS_CLAUDE + ".gengar-backup"
        if not os.path.exists(copia):
            shutil.copy2(RUTA_SETTINGS_CLAUDE, copia)
    hooks = datos.setdefault("hooks", {})
    cmd = _comando_hook()
    for ev, matcher in EVENTOS_HOOK.items():
        grupos = [g for g in hooks.get(ev, []) if not _es_nuestro(g)]
        grupo = {"hooks": [{"type": "command", "command": cmd}]}
        if matcher:
            grupo["matcher"] = matcher
        grupos.append(grupo)
        hooks[ev] = grupos
    _escribir_settings_claude(datos)

def quitar_hooks_claude():
    datos = _leer_settings_claude()
    hooks = datos.get("hooks", {})
    for ev in list(hooks.keys()):
        grupos = [g for g in hooks[ev] if not _es_nuestro(g)]
        if grupos:
            hooks[ev] = grupos
        else:
            del hooks[ev]
    if not hooks:
        datos.pop("hooks", None)
    _escribir_settings_claude(datos)

def hooks_instalados():
    try:
        hooks = _leer_settings_claude().get("hooks", {})
        return any(_es_nuestro(g) for gs in hooks.values() for g in gs)
    except Exception:
        return False

class Puente(QObject):
    evento = Signal(dict)
    def __init__(self, puerto):
        super().__init__()
        self.puerto = puerto
        self.servidor = None
    def iniciar(self):
        puente = self
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    if self.headers.get("X-Gengar") != "1":
                        raise ValueError("sin cabecera")
                    n = int(self.headers.get("Content-Length", "0"))
                    if n > 65536:
                        raise ValueError("demasiado grande")
                    datos = json.loads(self.rfile.read(n) or b"{}")
                    if isinstance(datos, dict):
                        puente.evento.emit(datos)
                    self.send_response(204)
                except Exception:
                    self.send_response(400)
                self.end_headers()
            def log_message(self, *a):
                pass
        try:
            self.servidor = ThreadingHTTPServer(("127.0.0.1", self.puerto), Handler)
        except OSError:
            return False
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        return True
    def parar(self):
        if self.servidor:
            try:
                self.servidor.shutdown()
            except Exception:
                pass

SONIDOS = {
    "teleport-out": [(1200, 180, 0.28, 0.5, "cuad")],
    "teleport-in": [(180, 1400, 0.25, 0.5, "cuad")],
    "done": [(523, 523, 0.09, 0.5, "sin"), (659, 659, 0.09, 0.5, "sin"),
             (784, 784, 0.09, 0.5, "sin"), (1047, 1047, 0.26, 0.5, "sin")],
    "alert": [(880, 880, 0.09, 0.4, "cuad"), (0, 0, 0.05, 0.0, "sin"), (880, 880, 0.09, 0.4, "cuad")],
    "error": [(160, 80, 0.35, 0.5, "cuad")],
    "hello": [(440, 660, 0.12, 0.4, "sin"), (660, 880, 0.14, 0.4, "sin")],
    "star": [(1500, 1500, 0.08, 0.3, "sin"), (0, 0, 0.08, 0.0, "sin"), (1800, 1800, 0.1, 0.3, "sin")],
    "land": [(120, 50, 0.12, 0.6, "sin")],
    "rise": [(200, 1600, 0.45, 0.45, "cuad")],
    "bolt": [(0, 0, 0.18, 0.45, "ruido")],
    "charge": [(150, 900, 0.6, 0.3, "sin")],
    "possess": [(300, 180, 0.2, 0.4, "cuad"), (250, 350, 0.2, 0.4, "cuad"), (300, 160, 0.25, 0.4, "cuad")],
    "blip": [(700, 700, 0.025, 0.16, "cuad")],
    "tick": [(1200, 1200, 0.03, 0.2, "sin")],
}

def _sintetizar(segmentos, ruta, sr=22050):
    datos = bytearray()
    fase = 0.0
    for f0, f1, dur, vol, onda in segmentos:
        n = max(1, int(sr * dur))
        for i in range(n):
            k = i / max(1, n - 1)
            fase += 2 * math.pi * (f0 + (f1 - f0) * k) / sr
            if onda == "sin":
                v = math.sin(fase)
            elif onda == "cuad":
                v = 1.0 if math.sin(fase) >= 0 else -1.0
            else:
                v = random.uniform(-1, 1)
            env = min(1.0, i / (sr * 0.004)) * (1.0 - k) ** 0.6
            datos += struct.pack("<h", int(max(-1.0, min(1.0, v * vol * env)) * 32767))
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(datos))

class Sonido:
    def __init__(self):
        self.activo = True
        self.efectos = {}
        self.dir = os.path.join(tempfile.gettempdir(), "gengar_sfx")
        self.t_blip = 0.0
        try:
            os.makedirs(self.dir, exist_ok=True)
        except Exception:
            pass
    def _ruta(self, nombre):
        propio = os.path.join(RUTA_SONIDOS, nombre + ".wav")
        if os.path.exists(propio):
            return propio
        ruta = os.path.join(self.dir, nombre + ".wav")
        if not os.path.exists(ruta):
            _sintetizar(SONIDOS[nombre], ruta)
        return ruta
    def reproducir(self, nombre):
        if not self.activo or nombre not in SONIDOS:
            return
        if nombre == "blip":
            ahora = time.time()
            if ahora - self.t_blip < 0.06:
                return
            self.t_blip = ahora
        try:
            ruta = self._ruta(nombre)
            if QSoundEffect is not None:
                ef = self.efectos.get(nombre)
                if ef is None:
                    ef = QSoundEffect()
                    ef.setSource(QUrl.fromLocalFile(ruta))
                    ef.setVolume(0.35)
                    self.efectos[nombre] = ef
                ef.play()
            elif sys.platform == "win32":
                import winsound
                winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

class FiltroAtajo(QAbstractNativeEventFilter):
    WM_HOTKEY = 0x0312
    ID = 0x6E67
    def __init__(self, callback, callback_voz=None):
        super().__init__()
        self.callback = callback
        self.callback_voz = callback_voz
        self.registrado = False
        if sys.platform == "win32":
            try:
                MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
                self.registrado = bool(ctypes.windll.user32.RegisterHotKey(
                    None, self.ID, MOD_ALT | MOD_CONTROL | MOD_NOREPEAT, ord("G")))
                ctypes.windll.user32.RegisterHotKey(None, self.ID + 1, MOD_ALT | MOD_CONTROL | MOD_NOREPEAT, ord("V"))
            except Exception:
                self.registrado = False
    def nativeEventFilter(self, eventType, message):
        try:
            if sys.platform == "win32" and bytes(eventType) == b"windows_generic_MSG":
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == self.WM_HOTKEY and msg.wParam == self.ID:
                    QTimer.singleShot(0, self.callback)
                elif msg.message == self.WM_HOTKEY and msg.wParam == self.ID + 1 and self.callback_voz:
                    QTimer.singleShot(0, self.callback_voz)
        except Exception:
            pass
        return False, 0
    def liberar(self):
        if self.registrado and sys.platform == "win32":
            try:
                ctypes.windll.user32.UnregisterHotKey(None, self.ID)
                ctypes.windll.user32.UnregisterHotKey(None, self.ID + 1)
            except Exception:
                pass
            self.registrado = False

PS_VOZ = r"""[Console]::InputEncoding=[Text.Encoding]::UTF8
Add-Type -AssemblyName System.Speech
$s=New-Object System.Speech.Synthesis.SpeechSynthesizer
$v=$s.GetInstalledVoices()|Where-Object{$_.VoiceInfo.Culture.Name -like 'es*'}|Select-Object -First 1
$c='es-ES'
if($v){$s.SelectVoice($v.VoiceInfo.Name);$c=$v.VoiceInfo.Culture.Name}
$t=[Security.SecurityElement]::Escape([Console]::In.ReadToEnd())
$s.SpeakSsml("<speak version='1.0' xml:lang='$c'><prosody pitch='low' rate='medium'>$t</prosody></speak>")"""

def texto_hablado(t):
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"[`*_#>|~\[\]{}<]", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:500]

class HablarTTS:
    def __init__(self):
        self.proc = None
    def hablando(self):
        return self.proc is not None and self.proc.poll() is None
    def parar(self):
        if self.hablando():
            try:
                self.proc.terminate()
            except Exception:
                pass
        self.proc = None
    def hablar(self, texto):
        self.parar()
        if sys.platform != "win32" or not texto.strip():
            return
        try:
            cod = base64.b64encode(PS_VOZ.encode("utf-16-le")).decode()
            self.proc = subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", cod],
                                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                         creationflags=0x08000000)
            self.proc.stdin.write(texto.encode("utf-8"))
            self.proc.stdin.close()
        except Exception:
            self.proc = None

TTS = HablarTTS()
_WHISPER = None

def ruta_whisper(nombre):
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos_whisper", nombre)
    if not os.path.exists(os.path.join(d, "model.bin")):
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=f"Systran/faster-whisper-{nombre}", local_dir=d)
    return d

class EscuchaVoz(QThread):
    texto = Signal(str)
    estado = Signal(str)
    def __init__(self):
        super().__init__()
        self._parar = False
    def cancelar(self):
        self._parar = True
    def run(self):
        global _WHISPER
        try:
            import numpy as np
            import sounddevice as sd
            from faster_whisper import WhisperModel
        except Exception:
            self.estado.emit("error:Faltan paquetes: pip install faster-whisper sounddevice")
            return
        try:
            from collections import deque
            if _WHISPER is None:
                self.estado.emit("cargando")
                _WHISPER = WhisperModel(ruta_whisper(os.environ.get("GENGAR_WHISPER", "small")), device="cpu", compute_type="int8")
            self.estado.emit("escuchando")
            bloques, previo = [], deque(maxlen=3)
            hablando, silencio, t0 = False, 0, time.time()
            with sd.InputStream(samplerate=16000, channels=1, dtype="float32", blocksize=1600) as st:
                ruido = [float(np.sqrt(np.mean(st.read(1600)[0] ** 2))) for _ in range(4)]
                umbral = max(0.012, 3 * float(np.mean(ruido)))
                while not self._parar and time.time() - t0 < 25:
                    d = st.read(1600)[0]
                    r = float(np.sqrt(np.mean(d ** 2)))
                    if r > umbral:
                        if not hablando:
                            bloques = list(previo)
                        hablando, silencio = True, 0
                    elif hablando:
                        silencio += 1
                    if hablando:
                        bloques.append(d.copy())
                        if silencio >= 9:
                            break
                    else:
                        previo.append(d.copy())
                        if time.time() - t0 > 8:
                            break
            if self._parar or not bloques:
                self.estado.emit("nada")
                return
            self.estado.emit("transcribiendo")
            audio = np.concatenate(bloques).flatten()
            segs, _ = _WHISPER.transcribe(audio, language="es", vad_filter=True, beam_size=1)
            txt = " ".join(x.text.strip() for x in segs).strip()
            if len(txt) < 2 or "Amara.org" in txt or "Subtítulos" in txt:
                self.estado.emit("nada")
                return
            self.texto.emit(txt)
        except Exception as e:
            self.estado.emit(f"error:Micrófono o modelo de voz: {e}")

class WorkerIA(QThread):
    respuesta_lista = Signal(str)
    accion = Signal()
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
    def run(self):
        try:
            import ia_puente
            respuesta = ia_puente.obtener_respuesta(self.prompt, self.accion.emit)
            self.respuesta_lista.emit(str(respuesta))
        except Exception as e:
            self.respuesta_lista.emit(f"Error: {e}")

class WorkerVision(QThread):
    lista = Signal(str)
    def run(self):
        try:
            import ia_puente
            self.lista.emit(str(ia_puente.padrino.comentar_pantalla("Comenta de forma sarcástica y corta lo que ves en mi pantalla")))
        except Exception as e:
            self.lista.emit(f"Error: {e}")

class WorkerSueno(QThread):
    lista = Signal(str)
    def run(self):
        try:
            import ia_puente
            p = ia_puente.padrino
            res = "\n".join(f"[{r['fecha']}] {r['resumen']}" for r in p._resumenes_previos) or "(sin conversaciones previas)"
            prompt = f"Genera un sueño corto, extraño y gracioso en español basado en estas conversaciones: {res}\nMáximo 2 frases. Responde solo con el sueño."
            r = p.ollama.chat(model=ia_puente.MODELO_GENGAR, messages=[{"role": "user", "content": prompt}],
                              options={"temperature": 1.0, "num_ctx": 2048}, keep_alive="30m")
            self.lista.emit((r.message.content or "").strip())
        except Exception:
            self.lista.emit("")

C_MORADO = "#7c4dff"
C_FONDO = "#0e0a17"
C_VERDE = "#39ff88"
C_ROJO = "#ff2d5a"
C_GRIS = "#8f89a3"
C_TEXTO = "#c9c3d9"

def poly_cortado(x, y, w, h, tl=0, tr=0, br=0, bl=0):
    return QPolygonF([QPointF(x + tl, y), QPointF(x + w - tr, y), QPointF(x + w, y + tr),
                      QPointF(x + w, y + h - br), QPointF(x + w - br, y + h), QPointF(x + bl, y + h),
                      QPointF(x, y + h - bl), QPointF(x, y + tl)])

def dibujar_cara_geo(p, r):
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    x, y, w, h = r.x(), r.y(), r.width(), r.height()
    P = lambda a, b: QPointF(x + a * w, y + b * h)
    p.setClipRect(r)
    p.fillRect(r, QColor("#ff1744"))
    rng = random.Random(11)
    p.setPen(Qt.PenStyle.NoPen)
    s = max(1.0, w / 28)
    for _ in range(int(w * h / 20)):
        c = QColor("#7a0020") if rng.random() < 0.55 else QColor("#ff7a98")
        c.setAlpha(150)
        p.setBrush(c)
        p.drawRect(QRectF(x + rng.random() * w, y + rng.random() * h, s, s))
    p.setBrush(QColor("#1fe06a"))
    p.drawPolygon(QPolygonF([P(.06, .2), P(.38, .2), P(.5, .36), P(.62, .2), P(.94, .2), P(.94, .78),
                             P(.74, .97), P(.26, .97), P(.06, .78)]))
    p.setBrush(QColor("#0b9d4a"))
    p.drawPolygon(QPolygonF([P(.06, .2), P(.38, .2), P(.32, .3), P(.06, .3)]))
    p.drawPolygon(QPolygonF([P(.94, .2), P(.62, .2), P(.68, .3), P(.94, .3)]))
    for cx in (.3, .7):
        c = P(cx, .5)
        rr = w * .17
        p.setBrush(QColor("#05051a"))
        p.drawEllipse(c, rr, rr)
        p.setBrush(QColor("#1f6bff"))
        p.drawEllipse(c, rr * .8, rr * .8)
        p.setBrush(QColor("#e6f6ff"))
        p.drawEllipse(c, rr * .45, rr * .45)
        p.setBrush(QColor("#05051a"))
        p.drawEllipse(c, rr * .2, rr * .2)
    p.setBrush(QColor("#05051a"))
    p.drawPolygon(QPolygonF([P(.16, .7), P(.84, .7), P(.76, .9), P(.24, .9)]))
    p.setPen(QPen(QColor("#ffffff"), max(1.5, w * .045), Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.MiterJoin))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPolyline(QPolygonF([P(.22, .82), P(.33, .74), P(.43, .86), P(.54, .74), P(.64, .86), P(.78, .76)]))
    p.restore()

_CARA_PM = None
def _cara_pixmap():
    global _CARA_PM
    if _CARA_PM is None:
        _CARA_PM = QPixmap(RUTA_CARA) if os.path.exists(RUTA_CARA) else QPixmap()
    return _CARA_PM

def dibujar_cara_gengar(p, r):
    pm = _cara_pixmap()
    if pm.isNull():
        dibujar_cara_geo(p, r)
        return
    p.save()
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.setClipRect(r, Qt.ClipOperation.IntersectClip)
    asp = r.width() / max(1.0, r.height())
    sw = min(float(pm.width()), 400.0 if asp <= 1.2 else 450.0)
    sh = sw / asp
    if sh > pm.height():
        sh = float(pm.height())
        sw = sh * asp
    cx, cy = pm.width() / 2, pm.height() * 0.49
    sx = max(0.0, min(cx - sw / 2, pm.width() - sw))
    sy = max(0.0, min(cy - sh / 2, pm.height() - sh))
    p.drawPixmap(r, pm, QRectF(sx, sy, sw, sh))
    p.restore()

class AvatarGeo(QWidget):
    def __init__(self, lado=60):
        super().__init__()
        self.setFixedSize(lado, lado)
    def paintEvent(self, ev):
        p = QPainter(self)
        dibujar_cara_gengar(p, QRectF(2, 2, self.width() - 4, self.height() - 4))
        p.setPen(QPen(QColor(C_MORADO), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(1, 1, self.width() - 2, self.height() - 2)

class PanelMisionCyberpunk(QWidget):
    PW = 350
    SO = 6
    COLA = 14
    M = 18
    AV = 52
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.tx = 80
        self.cola = True
        self.vis = 0
        self.f_nombre = QFont("Consolas")
        self.f_nombre.setPixelSize(12)
        self.f_nombre.setBold(True)
        self.f_nombre.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        self.f_sub = QFont("Consolas")
        self.f_sub.setPixelSize(11)
        self.f_titulo = QFont("Consolas")
        self.f_titulo.setPixelSize(15)
        self.f_titulo.setBold(True)
        self.f_cuerpo = QFont("Consolas")
        self.f_cuerpo.setPixelSize(12)
        self.f_stats = QFont("Consolas")
        self.f_stats.setPixelSize(11)
        self.f_stats.setBold(True)
        self.f_badge = QFont("Consolas")
        self.f_badge.setPixelSize(10)
        self.f_badge.setBold(True)
        self.f_badge.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        self.configurar("", "", "", "", "ok")
    @staticmethod
    def _envolver(txt, fm, ancho):
        out = []
        for par in txt.split("\n"):
            lin = ""
            for pal in par.split(" "):
                prueba = (lin + " " + pal) if lin else pal
                if lin and fm.horizontalAdvance(prueba) > ancho:
                    out.append(lin)
                    lin = pal
                else:
                    lin = prueba
            out.append(lin)
        return out
    def configurar(self, titulo, cuerpo, stats, badge, tipo):
        self.titulo, self.cuerpo, self.stats, self.badge, self.tipo = titulo, cuerpo, stats, badge, tipo
        self.vis = len(cuerpo)
        m = self.M
        self.xc = m + self.AV + 14
        self.wc = self.PW - self.xc - m
        self.fm_t = QFontMetrics(self.f_titulo)
        self.fm_c = QFontMetrics(self.f_cuerpo)
        self.fm_s = QFontMetrics(self.f_stats)
        self.fm_b = QFontMetrics(self.f_badge)
        self.lt = self._envolver(titulo, self.fm_t, self.wc) if titulo else []
        self.lc = self._envolver(cuerpo, self.fm_c, self.wc - 12) if cuerpo else []
        self.hl_c = self.fm_c.height() + 2
        y = m + 22
        self.y_t = y
        y += len(self.lt) * self.fm_t.height() + (8 if self.lt else 0)
        self.y_c = y
        if self.lc:
            y += len(self.lc) * self.hl_c + 8
        self.y_s = y
        if stats:
            y += self.fm_s.height() + 4
        self.h_main = max(y + m, m * 2 + self.AV)
        self.setFixedSize(self.PW + self.SO, self.h_main + self.SO + self.COLA)
        self.update()
    def reposicionar(self, pet):
        a = pet.area()
        cx = pet.x() + pet.width() // 2
        x = cx - self.width() + 60
        x = max(a.left() + 4, min(x, a.right() - self.width() - 4))
        y = pet.y() + SPR_Y + 14 - self.h_main - self.COLA
        y = max(a.top() + 2, y)
        self.tx = max(26, min(cx - x, self.PW - 26))
        self.move(int(x), int(y))
        self.update()
    def paintEvent(self, ev):
        p = QPainter(self)
        self.pintar(p)
    def pintar(self, p):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        PW, h, so, m = self.PW, self.h_main, self.SO, self.M
        morado = QColor(C_MORADO)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(morado)
        p.drawPolygon(poly_cortado(so, so, PW, h, 24, 12, 12, 0))
        tx = self.tx
        if self.cola:
            p.drawPolygon(QPolygonF([QPointF(tx - 14, h - 2), QPointF(tx + 14, h - 2), QPointF(tx + 8, h + self.COLA)]))
        p.setBrush(QColor(C_FONDO))
        p.setPen(QPen(morado, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))
        p.drawPolygon(poly_cortado(2, 2, PW - 4, h - 4, 24, 12, 12, 0))
        dibujar_cara_gengar(p, QRectF(m, m, self.AV, self.AV))
        p.setPen(QPen(morado, 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(QRectF(m, m, self.AV, self.AV))
        xc = self.xc
        bw = 0
        if self.badge:
            bw = self.fm_b.horizontalAdvance(self.badge) + 18
            bx, by = PW - m - bw, m - 2
            col, tcol = {"ok": (QColor(C_VERDE), QColor("#04140a")),
                         "error": (QColor(C_ROJO), QColor("#ffffff")),
                         "espera": (QColor("#ffb020"), QColor("#140c00"))}.get(self.tipo, (QColor(C_MORADO), QColor("#ffffff")))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(col)
            p.drawPolygon(QPolygonF([QPointF(bx + 5, by), QPointF(bx + bw, by), QPointF(bx + bw - 5, by + 17), QPointF(bx, by + 17)]))
            p.setFont(self.f_badge)
            p.setPen(tcol)
            p.drawText(QRectF(bx, by, bw, 17), Qt.AlignmentFlag.AlignCenter, self.badge)
        p.setFont(self.f_nombre)
        p.setPen(QColor("#ffffff"))
        p.drawText(QPointF(xc, m + 11), "GENGAR")
        nx = xc + QFontMetrics(self.f_nombre).horizontalAdvance("GENGAR") + 8
        p.setFont(self.f_sub)
        p.setPen(QColor(C_GRIS))
        disp = PW - m - bw - 10 - nx
        p.drawText(QPointF(nx, m + 11), QFontMetrics(self.f_sub).elidedText("/ CIUDAD-NOCTURNA-…", Qt.TextElideMode.ElideRight, int(max(10, disp))))
        p.setFont(self.f_titulo)
        p.setPen(QColor("#ffffff"))
        for i, l in enumerate(self.lt):
            p.drawText(QPointF(xc, self.y_t + i * self.fm_t.height() + self.fm_t.ascent()), l)
        if self.lc:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(morado)
            p.drawRect(QRectF(xc, self.y_c, 2, len(self.lc) * self.hl_c))
            p.setFont(self.f_cuerpo)
            p.setPen(QColor(C_TEXTO))
            resto = self.vis
            for i, l in enumerate(self.lc):
                if resto <= 0: break
                p.drawText(QPointF(xc + 10, self.y_c + i * self.hl_c + self.fm_c.ascent() + 1), l[:resto])
                resto -= len(l) + 1
        if self.stats:
            yy = self.y_s + self.fm_s.height() / 2
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(C_VERDE))
            p.drawPolygon(QPolygonF([QPointF(xc + 4, yy - 4), QPointF(xc + 8, yy), QPointF(xc + 4, yy + 4), QPointF(xc, yy)]))
            p.setFont(self.f_stats)
            p.setPen(QColor(C_VERDE))
            p.drawText(QPointF(xc + 14, self.y_s + self.fm_s.ascent()), self.fm_s.elidedText(self.stats, Qt.TextElideMode.ElideRight, self.wc - 14))

def tarjeta_pixmap(titulo, cuerpo, stats, badge, tipo):
    pn = PanelMisionCyberpunk()
    pn.cola = False
    pn.configurar(titulo, cuerpo, stats, badge, tipo)
    dpr = 2.0
    w, h = pn.PW + pn.SO, pn.h_main + pn.SO
    pm = QPixmap(int(w * dpr), int(h * dpr))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.GlobalColor.transparent)
    q = QPainter(pm)
    pn.pintar(q)
    q.end()
    pn.deleteLater()
    return pm

class VentanaChatCyberdeck(QWidget):
    mensaje_enviado = Signal(str)
    accion_rapida = Signal(str)
    pedir_voz = Signal()
    SO = 8
    _n_img = 0
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat con Gengar")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(440, 600)
        self.posicion_global_raton = QPoint()
        self.posicion_inicial_ventana = QPoint()
        self._configurar_interfaz()
        self.animacion_opacidad = QPropertyAnimation(self, b"windowOpacity")
        self.animacion_opacidad.setDuration(250)
        self.animacion_opacidad.setStartValue(0.0)
        self.animacion_opacidad.setEndValue(1.0)
        self.animacion_opacidad.start()
    def _configurar_interfaz(self):
        lp = QVBoxLayout(self)
        lp.setContentsMargins(20, 20, 20 + self.SO, 20 + self.SO)
        cab = QHBoxLayout()
        self.lbl_avatar = AvatarGeo(52)
        tit = QVBoxLayout()
        tit.setSpacing(4)
        self.lbl_titulo = QLabel(f"<span style='color:#fff; font-weight:bold; letter-spacing:2px;'>GENGAR</span><span style='color:{C_GRIS};'> / CIUDAD-NOCTURNA-…</span>")
        self.lbl_titulo.setStyleSheet("font-family: 'Consolas'; font-size: 12px;")
        self.lbl_estado = QLabel("EN LÍNEA")
        self.lbl_estado.setFixedHeight(16)
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        self.lbl_estado.setStyleSheet(f"background: {C_VERDE}; color: #04140a; font-family: 'Consolas'; font-size: 10px; font-weight: bold; padding: 0px 8px;")
        tit.addWidget(self.lbl_titulo)
        self.btn_limpiar = QPushButton("[↺]")
        self.btn_limpiar.setFixedSize(30, 30)
        self.btn_limpiar.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_MORADO}; font-weight: bold; font-family: 'Consolas'; border: 2px solid {C_MORADO}; }} QPushButton:hover {{ background: {C_MORADO}; color: #fff; }}")
        self.btn_limpiar.clicked.connect(self._limpiar_historial)
        self.btn_cerrar = QPushButton("[X]")
        self.btn_cerrar.setFixedSize(30, 30)
        self.btn_cerrar.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_ROJO}; font-weight: bold; font-family: 'Consolas'; border: 2px solid {C_ROJO}; }} QPushButton:hover {{ background: {C_ROJO}; color: #fff; }}")
        self.btn_cerrar.clicked.connect(self.hide)
        cab.addWidget(self.lbl_avatar)
        cab.addSpacing(10)
        cab.addLayout(tit)
        cab.addStretch()
        cab.addWidget(self.lbl_estado)
        cab.addWidget(self.btn_limpiar)
        cab.addWidget(self.btn_cerrar)
        self.historial = QTextBrowser()
        self.historial.setStyleSheet(f"QTextBrowser {{ background-color: transparent; border: none; color: {C_TEXTO}; font-family: 'Consolas', monospace; font-size: 13px; padding: 4px; }} QScrollBar:vertical {{ background: {C_FONDO}; width: 8px; }} QScrollBar::handle:vertical {{ background: {C_MORADO}; }} QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}")
        self.lbl_typing = QLabel("GENGAR ESCRIBE...")
        self.lbl_typing.setStyleSheet(f"color: {C_VERDE}; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        self.lbl_typing.hide()
        self.timer_typing = QTimer(self)
        self.timer_typing.timeout.connect(self._parpadear_typing)
        lb = QHBoxLayout()
        self.btn_bola = QPushButton(">> BOLA_FANTASMA")
        self.btn_bailar = QPushButton(">> BAILE_FORZADO")
        self.btn_dormir = QPushButton(">> MODO_SUEÑO")
        estilo = f"QPushButton {{ background-color: {C_FONDO}; color: {C_VERDE}; border: 2px solid {C_MORADO}; padding: 8px; font-family: 'Consolas'; font-size: 11px; font-weight: bold; }} QPushButton:hover {{ background-color: {C_MORADO}; color: #fff; }}"
        for b in (self.btn_bola, self.btn_bailar, self.btn_dormir):
            b.setStyleSheet(estilo)
            lb.addWidget(b)
        self.btn_bola.clicked.connect(lambda: self.accion_rapida.emit("bola"))
        self.btn_bailar.clicked.connect(lambda: self.accion_rapida.emit("bailar"))
        self.btn_dormir.clicked.connect(lambda: self.accion_rapida.emit("dormir"))
        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText(">> ESCRIBE TU COMANDO, TÍO...")
        self.input_texto.setStyleSheet(f"QLineEdit {{ background-color: #080510; color: #fff; border: 2px solid {C_MORADO}; padding: 12px; font-family: 'Consolas'; font-size: 14px; font-weight: bold; selection-background-color: {C_MORADO}; }} QLineEdit:focus {{ border: 2px solid {C_VERDE}; }}")
        self.input_texto.returnPressed.connect(self._enviar_mensaje)
        lp.addLayout(cab)
        lp.addSpacing(15)
        lp.addWidget(self.historial)
        lp.addWidget(self.lbl_typing)
        lp.addSpacing(15)
        lp.addLayout(lb)
        est = f"QPushButton {{ background: #080510; color: {C_TEXTO}; border: 2px solid {C_MORADO}; font-size: 16px; }} QPushButton:hover {{ border: 2px solid {C_VERDE}; }}"
        self.btn_mic = QPushButton("🎤")
        self.btn_voz = QPushButton("🔊")
        for b in (self.btn_mic, self.btn_voz):
            b.setFixedSize(46, 46)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(est)
        self.btn_voz.setCheckable(True)
        self.btn_voz.setChecked(True)
        self.btn_voz.toggled.connect(lambda on: self.btn_voz.setText("🔊" if on else "🔇"))
        self.btn_mic.clicked.connect(lambda: self.pedir_voz.emit())
        self.input_texto.setFixedHeight(46)
        fila_in = QHBoxLayout()
        fila_in.setSpacing(6)
        fila_in.addWidget(self.input_texto)
        fila_in.addWidget(self.btn_mic)
        fila_in.addWidget(self.btn_voz)
        lp.addLayout(fila_in)
    def set_mic(self, activo):
        self.btn_mic.setText("⏺" if activo else "🎤")
        self.btn_mic.setStyleSheet(self.btn_mic.styleSheet().replace(C_ROJO if not activo else C_TEXTO, C_TEXTO if not activo else C_ROJO))
    def keyPressEvent(self, event):
        global MODO_DND
        if event.key() == Qt.Key_F1:
            self.hide()
        elif event.key() == Qt.Key_F4:
            MODO_DND = not MODO_DND
            self.agregar_mensaje("Sistema", f"MODO DND {'ACTIVADO' if MODO_DND else 'DESACTIVADO'}.")
        else:
            super().keyPressEvent(event)
    def _parpadear_typing(self):
        self.lbl_typing.setVisible(not self.lbl_typing.isVisible())
    def iniciar_typing(self):
        self.lbl_typing.show()
        self.timer_typing.start(500)
    def detener_typing(self):
        self.lbl_typing.hide()
        self.timer_typing.stop()
    def _limpiar_historial(self):
        self.historial.clear()
        self.agregar_mensaje("Sistema", "Log de terminal purgado.")
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h, so = self.width() - self.SO, self.height() - self.SO, self.SO
        morado = QColor(C_MORADO)
        p.setPen(Qt.NoPen)
        p.setBrush(morado)
        p.drawPolygon(poly_cortado(so, so, w, h, 24, 12, 12, 0))
        p.setBrush(QColor(C_FONDO))
        p.setPen(QPen(morado, 4, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        p.drawPolygon(poly_cortado(2, 2, w - 4, h - 4, 24, 12, 12, 0))
    def agregar_tarjeta(self, texto, titulo, badge, tipo, stats):
        self._n_img += 1
        nombre = f"tarjeta{self._n_img}"
        pm = tarjeta_pixmap(titulo, texto, stats, badge, tipo)
        self.historial.document().addResource(QTextDocument.ResourceType.ImageResource, QUrl(nombre), pm)
        self.historial.append(f'<div style="margin: 10px 0;"><img src="{nombre}" width="{int(pm.width() / pm.devicePixelRatio())}"></div>')
        QTimer.singleShot(30, lambda: self.historial.verticalScrollBar().setValue(self.historial.verticalScrollBar().maximum()))
    def agregar_mensaje(self, remitente, texto, titulo="", badge="", tipo="ok", stats=""):
        if remitente == "Gengar":
            self.agregar_tarjeta(texto, titulo or "Misión cumplida, tío.", badge or "TERMINADO", tipo, stats)
            return
        if remitente == "Tú":
            prefijo, c1, color = "tú >", "#ffffff", "#ffffff"
        elif remitente == "Sistema":
            prefijo, c1, color = "SISTEMA:", C_ROJO, C_ROJO
        else:
            prefijo, c1, color = "GENGAR >", C_VERDE, C_TEXTO
        self.historial.append(f'<div style="margin: 8px 0;"><span style="color:{c1}; font-weight:bold;">{prefijo}</span> <span style="color:{color};">{html.escape(texto)}</span></div>')
        self.historial.verticalScrollBar().setValue(self.historial.verticalScrollBar().maximum())
    def _enviar_mensaje(self):
        texto = self.input_texto.text().strip()
        if not texto:
            return
        self.input_texto.clear()
        self.agregar_mensaje("Tú", texto)
        if texto.startswith("/"):
            comando = texto.lower().strip()
            if comando == "/cascos":  # --- FIX: comando manual /cascos
                self.accion_rapida.emit("cascos")
                self.agregar_mensaje("Sistema", "Globo de cascos forzado durante 15 segundos.")
                return
            ok = {"/bailar": ("bailar", "Bailar activado."), "/dormir": ("dormir", "Dormir activado."),
                  "/bola": ("bola", "Bola Fantasma activado."), "/hipnosis": ("hipnosis", "Hipnosis activada."),
                  "/auriculares": ("baile_musica", "Cabeceo con auriculares.")}
            if comando in ok:
                self.accion_rapida.emit(ok[comando][0])
                self.agregar_mensaje("Sistema", "ANULACIÓN: " + ok[comando][1])
            else:
                self.agregar_mensaje("Sistema", "ERROR: Comando no reconocido.")
        else:
            self.mensaje_enviado.emit(texto)
            self.iniciar_typing()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.posicion_global_raton = event.globalPosition().toPoint()
            self.posicion_inicial_ventana = self.pos()
            event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.posicion_inicial_ventana + event.globalPosition().toPoint() - self.posicion_global_raton)
            event.accept()

class OverlayGlitch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.barras = []
        self.paso = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._paso)
    def lanzar(self, geom):
        self.setGeometry(geom)
        self.paso = 0
        self._generar()
        self.show()
        self.timer.start(220)
    def _generar(self):
        self.barras = []
        for _ in range(random.randint(6, 12)):
            y = random.randint(0, max(1, self.height() - 40))
            alto = random.randint(3, 28)
            color = QColor(random.choice(["#b388ff", "#00e5ff", "#ff5252"]))
            color.setAlpha(45)
            self.barras.append((y, alto, color))
    def _paso(self):
        self.paso += 1
        if self.paso >= 3:
            self.timer.stop()
            self.hide()
            return
        self._generar()
        self.update()
    def paintEvent(self, ev):
        p = QPainter(self)
        for y, alto, color in self.barras:
            p.fillRect(0, y, self.width(), alto, color)

class NotaHack(QLabel):
    def __init__(self, geom):
        super().__init__("⚠ ¡HAS SIDO HACKEADO! ⚠\n\n(es Gengar, tranquilo)\nClic para cerrar")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("background-color:#0b0b0b; color:#39ff14; border:2px solid #39ff14; font-family:Consolas; font-size:13px; padding:10px;")
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()
        x = random.randint(geom.left() + 50, max(geom.left() + 51, geom.right() - self.width() - 50))
        y = random.randint(geom.top() + 50, max(geom.top() + 51, geom.bottom() - self.height() - 50))
        self.move(x, y)
        QTimer.singleShot(7000, self.close)
    def mousePressEvent(self, ev):
        self.close()

def _pt(v):
    if callable(v):
        v = v()
    if hasattr(v, "x") and callable(v.x):
        return float(v.x()), float(v.y())
    return float(v[0]), float(v[1])

def _suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def _color(c, alfa=1.0):
    q = QColor(c)
    q.setAlphaF(max(0.0, min(1.0, alfa)))
    return q

class Fx:
    dur = 1.0
    def __init__(self):
        self.t = 0.0
        self.vivo = True
    def paso(self, dt):
        self.t += dt
        if self.t >= self.dur:
            self.vivo = False
    @property
    def p(self):
        return min(1.0, self.t / self.dur) if self.dur > 0 else 1.0
    def dibujar(self, p):
        pass

class Particulas(Fx):
    def __init__(self, x, y, n=18, colores=None, vel=(60, 260), grav=500, dur=0.9, tam=(2, 6), cono=None, hacia=None, glifo=False):
        super().__init__()
        self.dur = dur
        self.grav = grav
        self.hacia = hacia
        self.glifo = glifo
        self.fuente = QFont("Consolas", 9)
        colores = colores or VIOLETAS
        self.ps = []
        for _ in range(n):
            ang = random.uniform(0, 2 * math.pi) if cono is None else random.uniform(cono[0], cono[1])
            v = random.uniform(*vel)
            if hacia is not None:
                r = random.uniform(70, 160)
                a2 = random.uniform(0, 2 * math.pi)
                px, py = _pt(hacia)
                self.ps.append([px + math.cos(a2) * r, py + math.sin(a2) * r, 0.0, 0.0, random.uniform(*tam), QColor(random.choice(colores)), random.uniform(0, 6.28), random.choice("01▒░<>/{}#$%")])
            else:
                self.ps.append([x, y, math.cos(ang) * v, math.sin(ang) * v, random.uniform(*tam), QColor(random.choice(colores)), random.uniform(0, 6.28), random.choice("01▒░<>/{}#$%")])
    def paso(self, dt):
        super().paso(dt)
        for q in self.ps:
            if self.hacia is not None:
                tx, ty = _pt(self.hacia)
                dx, dy = tx - q[0], ty - q[1]
                d = math.hypot(dx, dy) or 1.0
                q[2] += (dx / d * 1100 + (-dy / d) * 500) * dt
                q[3] += (dy / d * 1100 + (dx / d) * 500) * dt
                q[2] *= 0.95
                q[3] *= 0.95
            else:
                q[3] += self.grav * dt
            q[0] += q[2] * dt
            q[1] += q[3] * dt
            q[6] += dt * 6
    def dibujar(self, p):
        a = max(0.0, 1.0 - self.p)
        for q in self.ps:
            c = QColor(q[5])
            c.setAlphaF(a)
            p.save()
            p.translate(q[0], q[1])
            if self.glifo:
                p.setPen(c)
                p.setFont(self.fuente)
                p.drawText(QPointF(0, 0), q[7])
            else:
                p.rotate(math.degrees(q[6]))
                s = q[4]
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(c)
                p.drawPolygon(QPolygonF([QPointF(0, -s), QPointF(s * 0.6, s), QPointF(-s * 0.6, s)]))
            p.restore()

class Onda(Fx):
    def __init__(self, x, y, r_max=320, color="#b388ff", dur=0.7, grosor=6):
        super().__init__()
        self.x, self.y, self.r_max, self.color, self.dur, self.grosor = x, y, r_max, color, dur, grosor
    def dibujar(self, p):
        k = 1 - (1 - self.p) ** 3
        pen = QPen(_color(self.color, 1 - self.p), max(1.0, self.grosor * (1 - self.p)))
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(self.x, self.y), self.r_max * k, self.r_max * k)

class LineasVelocidad(Fx):
    def __init__(self, x, y, dur=0.7, n=34, r0=80, r1=440, color="#ffffff"):
        super().__init__()
        self.x, self.y, self.dur, self.n, self.r0, self.r1, self.color = x, y, dur, n, r0, r1, color
        self._gen = -1
        self.lineas = []
    def _generar(self):
        self.lineas = [(random.uniform(0, 2 * math.pi), random.uniform(0.0, 0.5), random.uniform(0.25, 0.7), random.uniform(1, 3)) for _ in range(self.n)]
    def dibujar(self, p):
        paso = int(self.t * 20)
        if paso != self._gen:
            self._gen = paso
            self._generar()
        a = max(0.0, 1 - self.p)
        for ang, ini, largo, gr in self.lineas:
            r_a = self.r0 + (self.r1 - self.r0) * ini
            r_b = r_a + (self.r1 - self.r0) * largo * (1 - self.p * 0.5)
            p.setPen(QPen(_color(self.color, 0.55 * a), gr))
            p.drawLine(QPointF(self.x + math.cos(ang) * r_a, self.y + math.sin(ang) * r_a), QPointF(self.x + math.cos(ang) * r_b, self.y + math.sin(ang) * r_b))

class Columna(Fx):
    def __init__(self, x, y_base, y_top, ancho=70, color="#ff3b5c", dur=0.6):
        super().__init__()
        self.x, self.yb, self.yt, self.ancho, self.color, self.dur = x, y_base, y_top, ancho, color, dur
    def dibujar(self, p):
        a = 1 - self.p
        w = self.ancho * (0.25 + 0.75 * a ** 0.5)
        g = QLinearGradient(self.x - w / 2, 0, self.x + w / 2, 0)
        g.setColorAt(0.0, _color(self.color, 0))
        g.setColorAt(0.35, _color(self.color, 0.8 * a))
        g.setColorAt(0.5, _color("#ffffff", a))
        g.setColorAt(0.65, _color(self.color, 0.8 * a))
        g.setColorAt(1.0, _color(self.color, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawRect(QRectF(self.x - w / 2, self.yt, w, self.yb - self.yt))

class Rayo(Fx):
    def __init__(self, a, b, color="#ff3b5c", dur=0.25, grosor=4, segmentos=14, jitter=22, fino=False):
        super().__init__()
        self.a, self.b, self.color, self.dur = a, b, color, dur
        self.grosor, self.n, self.jitter, self.fino = grosor, segmentos, jitter, fino
        self._gen = -1
        self.pts = []
    def _generar(self):
        ax, ay = _pt(self.a)
        bx, by = _pt(self.b)
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        self.pts = []
        for i in range(self.n + 1):
            t = i / self.n
            off = random.uniform(-1, 1) * self.jitter * math.sin(math.pi * t)
            self.pts.append(QPointF(ax + dx * t + nx * off, ay + dy * t + ny * off))
    def dibujar(self, p):
        paso = int(self.t * 30)
        if paso != self._gen or not self.pts:
            self._gen = paso
            self._generar()
        a = 1 - self.p * 0.6
        for ancho, col, alfa in ((self.grosor * 3.2, self.color, 0.25), (self.grosor * 1.6, self.color, 0.7), (max(1.0, self.grosor * 0.6), "#ffffff", 1.0)):
            for i in range(len(self.pts) - 1):
                k = 1 - (i / self.n) * (0.8 if self.fino else 0.0)
                p.setPen(QPen(_color(col, alfa * a), max(1.0, ancho * k), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(self.pts[i], self.pts[i + 1])

class Rendija(Fx):
    def __init__(self, x, y, alto=150, dur=0.45):
        super().__init__()
        self.x, self.y, self.alto, self.dur = x, y, alto, dur
    def dibujar(self, p):
        w = (1 - abs(2 * self.p - 1)) * 30 + 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 235))
        p.drawEllipse(QPointF(self.x, self.y), w / 2, self.alto / 2)
        p.setPen(QPen(QColor(255, 59, 92, 240), 2))
        p.drawLine(QPointF(self.x, self.y - self.alto / 2 + 6), QPointF(self.x, self.y + self.alto / 2 - 6))

class CutIn(Fx):
    def __init__(self, pm, x, y, w=270, h=104, dur=1.1, color="#7c4dff"):
        super().__init__()
        self.pm, self.x, self.y, self.w, self.h, self.dur, self.color = pm, x, y, w, h, dur, color
    def dibujar(self, p):
        entra = _suave(self.t / 0.16)
        sale = _suave((self.dur - self.t) / 0.22)
        a = min(entra, sale)
        dx = (1 - entra) * 140
        x, y, w, h = self.x + dx, self.y, self.w, self.h
        sk = 22
        marco = QPolygonF([QPointF(x + sk, y), QPointF(x + w, y), QPointF(x + w - sk, y + h), QPointF(x, y + h)])
        sombra = QPolygonF([QPointF(x + sk + 6, y + 6), QPointF(x + w + 6, y + 6), QPointF(x + w - sk + 6, y + h + 6), QPointF(x + 6, y + h + 6)])
        ruta = QPainterPath()
        ruta.addPolygon(marco)
        ruta.closeSubpath()
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(a)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(C_MORADO))
        p.drawPolygon(sombra)
        p.fillPath(ruta, QColor(C_FONDO))
        p.save()
        p.setClipPath(ruta)
        for i in range(9):
            yy = y + 8 + i * (h - 16) / 8
            p.setPen(QPen(QColor(255, 255, 255, 70 if i % 2 else 130), 1))
            p.drawLine(QPointF(x + 10, yy), QPointF(x + w - 10, yy))
        lado = h - 24
        fx_, fy_ = x + w / 2 - lado * 0.9, y + 12
        g = random.uniform(0.0, 1.0)
        jx = random.uniform(-6, 6) * g
        p.setOpacity(a * 0.55)
        p.save()
        p.translate(-4 - 3 * g, 0)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        p.fillRect(QRectF(fx_ - 40, fy_ + lado * 0.35, 36, 3), QColor(255, 30, 80))
        p.restore()
        p.setOpacity(a)
        dibujar_cara_gengar(p, QRectF(fx_ + jx, fy_, lado * 1.8, lado))
        p.setPen(QPen(QColor(C_MORADO), 3))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(QRectF(fx_ + jx, fy_, lado * 1.8, lado))
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(4):
            p.setBrush(QColor(255, 30, 80) if random.random() < 0.5 else QColor(40, 255, 120))
            p.drawRect(QRectF(x + random.uniform(10, w - 30), y + random.uniform(4, h - 8), random.uniform(6, 26), 2))
        p.restore()
        p.setPen(QPen(QColor(C_MORADO), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolygon(marco)
        p.restore()

class Luna(Fx):
    def __init__(self, area, x_inicio, dur=22.0, vel=26):
        super().__init__()
        self.dur = dur
        self.x0 = max(area.left() + 80, min(x_inicio, area.right() - 80))
        self.vel = vel
        self.y = area.top() + 70
        self.pulsos = []
    def pos(self):
        return (self.x0 + self.vel * self.t, self.y + 8 * math.sin(self.t * 0.6))
    def titilar(self, veces=2):
        self.pulsos.append((self.t, veces))
    def _brillo(self):
        b = 0.0
        for t0, veces in self.pulsos:
            dt = self.t - t0
            if 0 <= dt < 0.5 * veces:
                b = max(b, abs(math.sin(dt / 0.5 * math.pi)))
        return b
    def dibujar(self, p):
        a = min(_suave(self.t / 1.2), _suave((self.dur - self.t) / 1.5))
        x, y = self.pos()
        b = self._brillo()
        rad = 18 + 6 * b
        g = QRadialGradient(QPointF(x, y), 70 + 40 * b)
        g.setColorAt(0.0, _color("#d9c2ff", (0.35 + 0.4 * b) * a))
        g.setColorAt(1.0, _color("#d9c2ff", 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QPointF(x, y), 70 + 40 * b, 70 + 40 * b)
        disco = QPainterPath()
        disco.addEllipse(QPointF(x, y), rad, rad)
        corte = QPainterPath()
        corte.addEllipse(QPointF(x + rad * 0.45, y - rad * 0.2), rad * 0.88, rad * 0.88)
        p.fillPath(disco.subtracted(corte), _color("#efe6ff", a))
        if b > 0.05:
            p.setPen(QPen(_color("#ffffff", b * a), 2))
            l = 30 * b + 10
            p.drawLine(QPointF(x - l, y), QPointF(x + l, y))
            p.drawLine(QPointF(x, y - l), QPointF(x, y + l))

class SecuenciaLuna(Fx):
    T_HUSH, T_REACH, T_COIL, T_BOLT = 1.3, 3.0, 4.0, 4.8
    def __init__(self, mano, luna, dur=6.8):
        super().__init__()
        self.mano, self.luna, self.dur = mano, luna, dur
        self.est = [(random.uniform(-70, 70), random.uniform(-110, -30), random.uniform(2.0, 4.5)) for _ in range(22)]
    def _estrella(self, p, x, y, s, a):
        p.setPen(QPen(_color("#ffffff", a), 1.4))
        p.drawLine(QPointF(x - s, y), QPointF(x + s, y))
        p.drawLine(QPointF(x, y - s), QPointF(x, y + s))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_color("#ffffff", a))
        p.drawEllipse(QPointF(x, y), s * 0.35, s * 0.35)
    def dibujar(self, p):
        t = self.t
        mx, my = _pt(self.mano)
        lx, ly = _pt(self.luna.pos)
        n = len(self.est)
        for i, (ox, oy, s) in enumerate(self.est):
            cx, cy = mx + ox, my + oy
            f = (i + 1) / (n + 1)
            rx, ry = mx + (lx - mx) * f, my + (ly - my) * f
            if t < self.T_HUSH:
                k = _suave(t / self.T_HUSH)
                x, y, a = cx, cy - 30 * k, k
            elif t < self.T_REACH:
                k = _suave((t - self.T_HUSH) / (self.T_REACH - self.T_HUSH))
                x, y, a = cx + (rx - cx) * k, cy + (ry - cy) * k, 1.0
            elif t < self.T_BOLT:
                x, y, a = rx, ry + math.sin(t * 10 + i) * 2, 1.0
            else:
                k = _suave((t - self.T_BOLT) / (self.dur - self.T_BOLT))
                x, y, a = rx + (mx - rx) * k, ry + (my - ry) * k, 1.0 - 0.8 * k
            self._estrella(p, x, y, s, a)
        if self.T_REACH - 1.2 < t < self.T_BOLT:
            k = _suave((t - (self.T_REACH - 1.2)) / 1.2)
            pen = QPen(_color("#ffffff", 0.3), 1.2, Qt.PenStyle.DashLine)
            p.setPen(pen)
            p.drawLine(QPointF(mx, my), QPointF(mx + (lx - mx) * k, my + (ly - my) * k))
        if self.T_REACH < t < self.T_COIL:
            for _ in range(4):
                a2 = random.uniform(0, 2 * math.pi)
                r = random.uniform(8, 26)
                p.setPen(QPen(_color("#ff5252", 0.9), 2))
                p.drawLine(QPointF(mx, my), QPointF(mx + math.cos(a2) * r, my + math.sin(a2) * r))

class Poseida(Fx):
    def __init__(self, rect, cursor, dur=2.4):
        super().__init__()
        self.r, self.cursor, self.dur = rect, cursor, dur
        self.ojos = [(random.uniform(0.12, 0.88), random.uniform(0.15, 0.7), random.uniform(0.8, 1.5)) for _ in range(6)]
        self.ojos.insert(0, (0.32, 0.38, 2.0))
        self.ojos.insert(1, (0.68, 0.38, 2.0))
    def _ojo(self, p, x, y, esc, a):
        mx, my = _pt(self.cursor)
        dx, dy = mx - x, my - y
        d = math.hypot(dx, dy) or 1.0
        w, h = 34 * esc, 20 * esc
        p.save()
        p.translate(x, y)
        p.rotate(-14 if x < self.r.center().x() else 14)
        p.setPen(QPen(QColor(10, 0, 20, int(220 * a)), 2))
        p.setBrush(QColor(255, 59, 92, int(235 * a)))
        p.drawEllipse(QPointF(0, 0), w / 2, h / 2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, int(240 * a)))
        p.drawEllipse(QPointF(dx / d * w * 0.12, dy / d * h * 0.12), w * 0.14, h * 0.28)
        p.restore()
    def dibujar(self, p):
        r = self.r
        a = min(_suave(self.t / 0.25), _suave((self.dur - self.t) / 0.3))
        p.save()
        p.setClipRect(r)
        p.fillRect(r, QColor(110, 50, 190, int(55 * a)))
        for _ in range(7):
            y = r.top() + random.random() * r.height()
            col = random.choice(["#00e5ff", "#ff3b5c", "#b388ff"])
            p.fillRect(QRectF(r.left(), y, r.width(), random.uniform(3, 22)), _color(col, 0.16 * a))
        p.restore()
        if self.t < 1.0:
            for (a1, a2) in ((r.topLeft(), r.topRight()), (r.topRight(), r.bottomRight()), (r.bottomRight(), r.bottomLeft()), (r.bottomLeft(), r.topLeft())):
                pts = [a1]
                for i in range(1, 12):
                    k = i / 12
                    pts.append(QPointF(a1.x() + (a2.x() - a1.x()) * k + random.uniform(-8, 8), a1.y() + (a2.y() - a1.y()) * k + random.uniform(-8, 8)))
                pts.append(a2)
                p.setPen(QPen(QColor(255, 59, 92, int(230 * a)), 2.5))
                p.drawPolyline(QPolygonF(pts))
        p.save()
        p.setClipRect(r)
        n = min(len(self.ojos), int(max(0.0, self.t - 0.45) / 0.18) + 1) if self.t > 0.45 else 0
        for ox, oy, esc in self.ojos[:n]:
            self._ojo(p, r.left() + ox * r.width(), r.top() + oy * r.height(), esc, a)
        if self.t > 0.5:
            y0 = r.top() + r.height() * 0.68
            ancho = r.width() * 0.66
            x0 = r.center().x() - ancho / 2
            pts = [QPointF(x0 + ancho * i / 14, y0 + (14 if i % 2 else -14) + 10 * math.sin(i / 14 * math.pi)) for i in range(15)]
            p.setPen(QPen(QColor(0, 0, 0, int(200 * a)), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.drawPolyline(QPolygonF(pts))
            p.setPen(QPen(QColor(255, 255, 255, int(245 * a)), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.drawPolyline(QPolygonF(pts))
        p.restore()

class FxOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.fxs = []
        self.geom = None
        self.t_prev = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
    def agregar(self, fx):
        self.fxs.append(fx)
        if not self.isVisible():
            self.geom = QApplication.primaryScreen().virtualGeometry()
            self.setGeometry(self.geom)
            self.show()
        if not self.timer.isActive():
            self.t_prev = time.time()
            self.timer.start(25)
        return fx
    def _tick(self):
        ahora = time.time()
        dt = min(0.06, ahora - self.t_prev)
        self.t_prev = ahora
        for f in self.fxs:
            f.paso(dt)
        self.fxs = [f for f in self.fxs if f.vivo]
        if not self.fxs:
            self.timer.stop()
            self.hide()
            return
        self.update()
    def paintEvent(self, ev):
        if self.geom is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(-self.geom.x(), -self.geom.y())
        for f in self.fxs:
            f.dibujar(p)

class SpriteView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.pm = None
        self.tinte = None
        self.glitch = 0.0
        self.cyber = 0.0
        self.sx = self.sy = 1.0
        self.rot180 = False
        self.bob_amp = 0.0
        self.violeta = True
        self._cache = {}
        self.glifos = []
        self._fuente = QFont("Consolas", 9)
    def soltar_glifo(self):
        self.glifos.append([random.uniform(SPR_X + 25, SPR_X + SPR - 25), SPR_Y + SPR * 0.3, 1.0, random.choice("01▒░<>/{}#$%")])
    def avanzar_glifos(self):
        for g in self.glifos:
            g[1] -= 4
            g[2] -= 0.09
        self.glifos = [g for g in self.glifos if g[2] > 0]
    def poner(self, pm):
        self.pm = pm
        self.update()
    def reset_fx(self):
        self.tinte = None
        self.glitch = 0.0
        self.sx = self.sy = 1.0
        self.update()
    def _tintada(self, pm, color):
        clave = (pm.cacheKey(), color.rgb())
        img = self._cache.get(clave)
        if img is None:
            if len(self._cache) > 500:
                self._cache.clear()
            img = QPixmap(pm.size())
            img.fill(Qt.transparent)
            q = QPainter(img)
            q.drawPixmap(0, 0, pm)
            q.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            q.fillRect(img.rect(), QColor(color.red(), color.green(), color.blue()))
            q.end()
            self._cache[clave] = img
        return img
    def paintEvent(self, ev):
        if self.pm is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pm = self.pm
        pw, ph = pm.width(), pm.height()
        if self.glifos:
            p.setFont(self._fuente)
            for gx, gy, vida, ch in self.glifos:
                p.setPen(_color("#d9c2ff", vida))
                p.drawText(QPointF(gx, gy), ch)
        bob = self.bob_amp * math.sin(time.time() * 3.0)
        if self.rot180:
            p.translate(SPR_X + SPR / 2, SPR_Y + SPR / 2)
            p.rotate(180)
            p.translate(-(SPR_X + SPR / 2), -(SPR_Y + SPR / 2))
        p.translate(SPR_X + SPR / 2, SPR_Y + SPR + bob)
        p.scale(self.sx, self.sy)
        x, y = -pw / 2, -(SPR + ph) / 2
        if self.violeta:
            p.setOpacity(0.45)
            p.drawPixmap(int(x + 3), int(y + 2), self._tintada(pm, QColor("#9a6bff")))
            p.setOpacity(1.0)
        g = max(self.glitch, self.cyber)
        if g > 0.02:
            d = 2 + 7 * g
            p.setOpacity(0.6)
            p.drawPixmap(int(x - d), int(y), self._tintada(pm, QColor(255, 30, 80)))
            p.drawPixmap(int(x + d), int(y + random.uniform(-1, 1) * g * 3), self._tintada(pm, QColor(40, 255, 120)))
            p.setOpacity(1.0)
        p.drawPixmap(int(x), int(y), pm)
        if g > 0.02:
            for _ in range(3 + int(5 * g)):
                by = random.uniform(0, ph - 10)
                bh = random.uniform(3, 14)
                dx = random.uniform(-14, 14) * g
                col = random.choice((QColor(255, 30, 80), QColor(40, 255, 120), None))
                p.save()
                p.setClipRect(QRectF(x - 24, y + by, pw + 48, bh))
                p.drawPixmap(int(x + dx), int(y), pm if col is None else self._tintada(pm, col))
                p.restore()
            p.setPen(Qt.PenStyle.NoPen)
            for _ in range(int(10 * g)):
                p.setBrush(QColor(255, 30, 80) if random.random() < 0.5 else QColor(40, 255, 120))
                p.drawRect(QRectF(x + random.uniform(0, pw), y + random.uniform(0, ph), random.uniform(2, 7), 2))
        if self.tinte is not None and self.tinte.alpha() > 0:
            p.setOpacity(self.tinte.alphaF())
            p.drawPixmap(int(x), int(y), self._tintada(pm, self.tinte))

class Chip(QWidget):
    clic = Signal()
    def __init__(self, pm_cara):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(60, 60)
        self.setCursor(Qt.PointingHandCursor)
        self.pm = pm_cara
        self.modo = "guardado"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
    def mostrar_en(self, x, y, modo):
        self.modo = modo
        self.move(int(x), int(y))
        self.show()
        self.raise_()
        self.timer.start(600)
    def ocultar(self):
        self.timer.stop()
        self.hide()
    def cerca(self, pos, radio):
        c = self.geometry().center()
        return math.hypot(pos.x() - c.x(), pos.y() - c.y()) < radio
    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        marco = QPainterPath()
        marco.addRoundedRect(QRectF(2, 2, 56, 56), 14, 14)
        p.setClipPath(marco)
        dibujar_cara_gengar(p, QRectF(2, 2, 56, 56))
        abre = (int(time.time()) % 7 == 0)
        p.fillRect(self.rect(), QColor(10, 6, 20, 35 if abre else 150))
        p.setClipping(False)
        p.setPen(QPen(QColor("#b388ff"), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(marco)
        if abre:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 59, 92))
            p.drawEllipse(QPointF(21, 26), 4.5, 2.6)
            p.drawEllipse(QPointF(39, 26), 4.5, 2.6)
    def mousePressEvent(self, ev):
        self.clic.emit()

def fijar_tamano(spr):
    global SPR, W, H, SPR_X, SPR_Y
    SPR = int(spr)
    W, H = SPR + 60, SPR + 100
    SPR_X, SPR_Y = (W - SPR) // 2, H - SPR

class GloboPensamientoCyberpunk(QWidget):
    MG = 8
    PW = 112
    PH = 112
    COLA_X = 34
    COLA_Y = 30
    PUNTA_X = 22
    PUNTA_Y = 149
    FPS_ANIM = 8
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.ancho = self.MG * 2 + self.COLA_X + self.PW
        self.alto = self.MG * 2 + self.PH + self.COLA_Y
        self.setFixedSize(self.ancho, self.alto)
        self.lado = "der"
        self._frames = []
        self._i = 0
        self._objetivo = False
        self._glitch = 0.12
        self._jit_x = 0.0
        self._bandas = []
        self._rafaga = 0
        self._cache = {}
        self.timer_anim = QTimer(self)
        self.timer_anim.setInterval(1000 // self.FPS_ANIM)
        self.timer_anim.timeout.connect(self._siguiente)
        self.timer_glitch = QTimer(self)
        self.timer_glitch.setInterval(70)
        self.timer_glitch.timeout.connect(self._tick_glitch)
        self.anim_opacidad = QPropertyAnimation(self, b"windowOpacity", self)
        self.anim_opacidad.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_opacidad.finished.connect(self._fin_fade)
    def _px(self):
        return float(self.MG + self.COLA_X) if self.lado == "der" else float(self.MG)
    def _cola(self):
        base = self.MG + self.PH
        px = self.MG + self.COLA_X
        pts = [(px + 12, base + 9, 14.0), (px - 6, base + 20, 10.0), (px - 20, base + 29, 6.0)]
        if self.lado == "izq":
            pts = [(self.ancho - x, y, s) for x, y, s in pts]
        return pts
    def _siguiente(self):
        if self._frames:
            self._i = (self._i + 1) % len(self._frames)
            self.update()
    def _tick_glitch(self):
        if self._rafaga > 0:
            self._rafaga -= 1
            self._glitch = random.choice((0.45, 0.7, 0.9, 1.0))
            self._jit_x = random.uniform(-4.0, 4.0)
            cols = (QColor(255, 30, 80), QColor(40, 255, 120), None)
            self._bandas = [(random.uniform(0, GLOBO_IMG - 6), random.uniform(3, 12), random.uniform(-10, 10), random.choice(cols)) for _ in range(random.randint(3, 6))]
        else:
            self._glitch = 0.12
            self._jit_x = 0.0
            self._bandas = []
            if random.random() < 0.09:
                self._rafaga = random.randint(2, 5)
        self.update()
    def _tintada(self, pm, color):
        clave = (pm.cacheKey(), color.rgb())
        img = self._cache.get(clave)
        if img is None:
            if len(self._cache) > 200:
                self._cache.clear()
            img = QPixmap(pm.size())
            img.fill(Qt.transparent)
            q = QPainter(img)
            q.drawPixmap(0, 0, pm)
            q.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            q.fillRect(img.rect(), QColor(color.red(), color.green(), color.blue()))
            q.end()
            self._cache[clave] = img
        return img
    def _fade(self, destino, ms):
        self.anim_opacidad.stop()
        self.anim_opacidad.setDuration(ms)
        self.anim_opacidad.setStartValue(self.windowOpacity())
        self.anim_opacidad.setEndValue(destino)
        self.anim_opacidad.start()
    def _fin_fade(self):
        if not self._objetivo:
            self.timer_anim.stop()
            self.timer_glitch.stop()
            self.hide()
            self._frames = []
            self._i = 0
    def _x_para(self, pet, lado):
        cx = pet.x() + pet.width() // 2
        sep = SPR * 0.30
        if lado == "der":
            return cx + sep - self.PUNTA_X
        return cx - sep - (self.ancho - self.PUNTA_X)
    def reposicionar(self, pet):
        a = pet.area()
        cx = pet.x() + pet.width() // 2
        mitad = a.center().x()
        pref = "der"  # --- FIX: Siempre a la derecha por defecto
        otro = "izq" if pref == "der" else "der"
        lado = pref
        x = self._x_para(pet, pref)
        if x < a.left() + 2 or x + self.ancho > a.right() - 2:
            x2 = self._x_para(pet, otro)
            if x2 >= a.left() + 2 and x2 + self.ancho <= a.right() - 2:
                lado, x = otro, x2
        x = max(a.left() + 2, min(x, a.right() - self.ancho - 2))
        y = max(a.top() + 2, pet.y() + SPR_Y + SPR * 0.18 - self.PUNTA_Y)
        if lado != self.lado:
            self.lado = lado
            self.update()
        self.move(int(x), int(y))
    def mostrar(self, pet, frames):
        if not frames:
            self.ocultar()
            return
        if frames is not self._frames:
            self._frames = frames
            self._i = 0
            self._rafaga = 4
        self.reposicionar(pet)
        if not self._objetivo or not self.isVisible():
            self._objetivo = True
            if not self.isVisible():
                self.setWindowOpacity(0.0)
                self.show()
            self.raise_()
            self.timer_anim.start()
            self.timer_glitch.start()
            self._fade(1.0, 220)
        self.update()
    def ocultar(self, inmediato=False):
        if inmediato:
            self._objetivo = False
            self.anim_opacidad.stop()
            self.timer_anim.stop()
            self.timer_glitch.stop()
            self._frames = []
            self._i = 0
            self.hide()
            return
        if not self._objetivo:
            return
        self._objetivo = False
        self._fade(0.0, 200)
    def paintEvent(self, ev):
        if not self._frames:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        g = self._glitch
        px, py = self._px(), float(self.MG)
        PW, PH = float(self.PW), float(self.PH)
        solid = Qt.PenStyle.SolidLine
        sq = Qt.PenCapStyle.SquareCap
        miter = Qt.PenJoinStyle.MiterJoin
        p.translate(self._jit_x, 0.0)
        colas = self._cola()
        forma = poly_cortado(px, py, PW, PH, 20, 8, 20, 8)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(124, 77, 255, 55), 8, solid, sq, miter))
        p.drawPolygon(forma)
        d = 1.5 + 6.0 * g
        dy = random.uniform(-1.0, 1.0) * g * 2.0
        for col, dx, oy in ((C_ROJO, -d, 0.0), (C_VERDE, d, dy)):
            c = QColor(col)
            c.setAlpha(int(110 + 120 * g))
            p.setPen(QPen(c, 2, solid, sq, miter))
            p.drawPolygon(poly_cortado(px + dx, py + oy, PW, PH, 20, 8, 20, 8))
            for cx, cy, s in colas:
                p.drawPolygon(poly_cortado(cx - s / 2 + dx, cy - s / 2 + oy, s, s, s * 0.3, 0, s * 0.3, 0))
        p.setBrush(QColor(C_FONDO))
        p.setPen(QPen(QColor(C_MORADO), 2, solid, sq, miter))
        for cx, cy, s in colas:
            p.drawPolygon(poly_cortado(cx - s / 2, cy - s / 2, s, s, s * 0.3, 0, s * 0.3, 0))
        p.setPen(QPen(QColor(C_MORADO), 3, solid, sq, miter))
        p.drawPolygon(forma)
        p.setPen(Qt.PenStyle.NoPen)
        for i, col in enumerate((C_ROJO, C_VERDE, "#b388ff")):
            p.setBrush(QColor(col))
            p.drawRect(QRectF(px + 24 + i * 9, py + 8, 5, 5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(C_VERDE), 2, solid, Qt.PenCapStyle.FlatCap))
        p.drawLine(QPointF(px + PW - 46, py + 10), QPointF(px + PW - 22, py + 10))
        p.drawLine(QPointF(px + 9, py + PH - 9), QPointF(px + 9, py + PH - 20))
        p.drawLine(QPointF(px + 9, py + PH - 9), QPointF(px + 20, py + PH - 9))
        p.setPen(QPen(QColor(C_ROJO), 2, solid, Qt.PenCapStyle.FlatCap))
        p.drawLine(QPointF(px + PW - 18, py + 10), QPointF(px + PW - 13, py + 10))
        pm = self._frames[self._i % len(self._frames)]
        ax = px + (PW - GLOBO_IMG) / 2.0
        ay = py + 18 + (PH - 28 - GLOBO_IMG) / 2.0
        x = ax + (GLOBO_IMG - pm.width()) / 2.0
        y = ay + (GLOBO_IMG - pm.height()) / 2.0
        p.save()
        p.setClipRect(QRectF(px + 4, py + 16, PW - 8, PH - 24), Qt.ClipOperation.IntersectClip)
        if g > 0.3:
            dd = 2.0 + 6.0 * g
            p.setOpacity(0.6)
            p.drawPixmap(QPointF(x - dd, y), self._tintada(pm, QColor(255, 30, 80)))
            p.drawPixmap(QPointF(x + dd, y + random.uniform(-1.0, 1.0) * g * 3.0), self._tintada(pm, QColor(40, 255, 120)))
            p.setOpacity(1.0)
        p.drawPixmap(QPointF(x, y), pm)
        if g > 0.3:
            for fy, fh, fdx, col in self._bandas:
                p.save()
                p.setClipRect(QRectF(px + 4, y + fy, PW - 8, fh), Qt.ClipOperation.IntersectClip)
                p.drawPixmap(QPointF(x + fdx * g, y), pm if col is None else self._tintada(pm, col))
                p.restore()
        p.setPen(QPen(QColor(0, 0, 0, 38), 1))
        sy = int(py + 18)
        while sy < int(py + PH - 8):
            p.drawLine(QPointF(px + 5, sy), QPointF(px + PW - 5, sy))
            sy += 3
        p.restore()
        if g > 0.3:
            p.setPen(Qt.PenStyle.NoPen)
            for _ in range(int(8 * g)):
                p.setBrush(QColor(255, 30, 80) if random.random() < 0.5 else QColor(40, 255, 120))
                p.drawRect(QRectF(px + random.uniform(4, PW - 12), py + random.uniform(4, PH - 6), random.uniform(3, 9), 2))

class PetGengar(QWidget):
    respuesta_para_chat = Signal(str, str, str, str, str)
    abrir_chat = Signal()
    notificar = Signal(str, str)
    tooltip = Signal(str)
    musica_evento = Signal(str, str)
    def __init__(self, chat_window, fx, snd, cfg):
        super().__init__()
        self.chat_window = chat_window
        self.fx = fx
        self.snd = snd
        self.cfg = cfg
        self.snd.activo = bool(cfg.get("sonido", True))
        fijar_tamano(TAMANOS.get(cfg.get("tamano", "Normal"), 130))
        self.pm_cara = QPixmap(RUTA_CARA) if os.path.exists(RUTA_CARA) else QPixmap()
        self.setFixedSize(W, H)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.vista = SpriteView(self)
        self.vista.setGeometry(0, 0, W, H)
        self.ticker = QLabel(self)
        self.ticker.setStyleSheet(ESTILO_TICKER)
        self.ticker.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.ticker.hide()
        self.timer_ticker = QTimer(self)
        self.timer_ticker.setSingleShot(True)
        self.timer_ticker.timeout.connect(self.quitar_ticker)
        self.bocadillo = PanelMisionCyberpunk()
        self.timer_bocadillo = QTimer(self)
        self.timer_bocadillo.setSingleShot(True)
        self.timer_bocadillo.timeout.connect(self.bocadillo.hide)
        self.globo_pensamiento = GloboPensamientoCyberpunk()
        self.anim_cascos = []
        self.anim_lupa = []
        self._lupa_activa = False
        self.timer_lupa = QTimer(self)
        self.timer_lupa.setSingleShot(True)
        self.timer_lupa.timeout.connect(self._lupa_off)
        self._frase, self._frase_i = "", 0
        self.timer_tecleo = QTimer(self)
        self.timer_tecleo.timeout.connect(self._teclear)
        self.animaciones = {}
        self.cargar_animaciones()
        self.estado = "patrulla"
        self.anim_sub = None
        self.frame = 0
        self.ticks = 0
        self.dir = 1
        self.dur = 4.0
        self.t_estado = time.time()
        self.velocidad_x = 4
        self.velocidad_y = 0
        self.pendientes = []
        self.alarmas = []
        self.worker = None
        self.contador = 0
        self.cl = {"fase": "idle", "t0": 0.0, "acciones": 0, "archivos": set(), "errores": 0,
                   "herr_actual": "", "ultimo": "", "resumen": "", "msg_espera": ""}
        self.anim_trabajo = "claude_leer"
        self.t_claude = 0.0
        self.t_error = 0.0
        self.t_zap = 0.0
        self.t_actividad = time.time()
        self.guardado = False
        self.chip_estado = None
        self.chip = Chip(self.pm_cara)
        self.chip.clic.connect(self._clic_chip)
        self.flota_obj = None
        self.flota_t = None
        self.luna = None
        self.presionado = False
        self.arrastrando = False
        self.press_global = QPoint()
        self.pos_raton_inicial = QPoint()
        self.ultima_pos_raton = QCursor.pos()
        self.t_raton_mov = time.time()
        self.t_seguir = 0.0
        self.fase_trepa = None
        self.lado_trepa = "izq"
        self.pared_x = 0
        self.ventana_ref = None
        self._vc = (0.0, [])
        self.modo_travesura = False
        self.fase_cursor = "ir"
        self.t_cursor = 0.0
        self.glitch = OverlayGlitch()
        self.nota = None
        self.estudio_fase = None
        self.estudio_fin = 0.0
        self.min_estudio = 25
        self.min_descanso = 5
        self.cambiar_estado("patrulla")
        self.timer_anim = self._timer(1000 // FPS, self.siguiente_frame)
        self.timer_mov = self._timer(30, self.mover)
        self.timer_comp = self._timer(8000, self.elegir_comportamiento)
        self.timer_pens = self._timer(45000, self.soltar_pensamiento)
        self.timer_raton = self._timer(500, self.comprobar_raton)
        self.timer_seguridad = self._timer(10000, self.vigilar_estado)
        self.timer_ventana = self._timer(80, self._vigilar_ventana, iniciar=False)
        self.timer_estudio = self._timer(1000, self._tick_estudio, iniciar=False)
        self.timer_glifos = self._timer(450, self._glifos)
        self.timer_cyber = self._timer(90, self._tick_cyber)
        self.timer_sueno = self._timer(5000, self.vigilar_sueno)
        self.timer_poseer = self._timer(60000, self.intentar_poseer)
        self.timer_luna_dia = self._timer(30000, self._luna_del_dia)
        self.timer_travesura = QTimer(self)
        self.timer_travesura.setSingleShot(True)
        self.timer_travesura.timeout.connect(self.hacer_travesura)
        self.programar_travesura()
        self._clip_ult = ""
        self.timer_clip = QTimer(self)
        self.timer_clip.setSingleShot(True)
        self.timer_clip.timeout.connect(self._clip_procesar)
        QApplication.clipboard().dataChanged.connect(lambda: self.timer_clip.start(2000))
        self.musica_activa = False
        self.musica_evento.connect(self._musica_evento)
        self.timer_baile = self._timer(4000, self._baile_musica, iniciar=False)
        self.timer_globo = self._timer(500, self._actualizar_globo)
        threading.Thread(target=self._enlazar_musica, daemon=True).start()
        self._w_vision = None
        self.timer_vision = QTimer(self)
        self.timer_vision.setSingleShot(True)
        self.timer_vision.timeout.connect(self.vision_proactiva)
        self.programar_vision()
        self._w_sueno = None
        self._sueno = ""
        self.timer_decir_sueno = QTimer(self)
        self.timer_decir_sueno.setSingleShot(True)
        self.timer_decir_sueno.timeout.connect(self._decir_sueno)
        self.move(100, 100)
        self.raise_()
    def _timer(self, ms, fn, iniciar=True):
        t = QTimer(self)
        t.timeout.connect(fn)
        if iniciar:
            t.start(ms)
        return t
    def tras(self, ms, fn):
        t = QTimer(self)
        t.setSingleShot(True)
        def _fin():
            if t in self.pendientes:
                self.pendientes.remove(t)
            t.deleteLater()
            fn()
        t.timeout.connect(_fin)
        t.start(ms)
        self.pendientes.append(t)
        return t
    def cancelar_pendientes(self):
        for t in self.pendientes:
            t.stop()
            t.deleteLater()
        self.pendientes.clear()
        self.setWindowOpacity(1.0)
        self.vista.reset_fx()
    def dpr(self):
        return QApplication.primaryScreen().devicePixelRatio()
    def pantalla(self):
        return QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
    def area(self):
        return self.pantalla().availableGeometry()
    def limites(self, sink=SINK_PIE):
        a = self.area()
        return (a.left() - SPR_X, a.right() + 1 - SPR_X - SPR, a.bottom() + 1 - H + sink)
    def centro_sprite(self):
        return QPoint(self.x() + W // 2, self.y() + SPR_Y + SPR // 2)
    def mano_xy(self):
        c = self.centro_sprite()
        return (c.x() + self.dir * SPR * 0.32, c.y() - SPR * 0.05)
    def sonido(self, nombre):
        self.snd.reproducir(nombre)
    def _tinte(self, color):
        self.vista.tinte = color
        self.vista.update()
    def impacto(self):
        self._tinte(QColor(255, 255, 255, 235))
        QTimer.singleShot(70, lambda: self._tinte(QColor(255, 60, 90, 170)))
        QTimer.singleShot(140, lambda: self._tinte(None))
    def decir(self, texto, ms=4500, maxlen=110, titulo="", badge="", tipo="ok", stats=""):
        if len(texto) > maxlen:
            texto = texto[:maxlen - 1] + "…"
        cuerpo = texto
        if not titulo:
            titulo, cuerpo = texto, ""
        self._frase, self._frase_i = cuerpo, 0
        self.bocadillo.configurar(titulo, cuerpo, stats, badge or "EN LÍNEA", tipo)
        self.bocadillo.vis = 0
        self.bocadillo.reposicionar(self)
        self.bocadillo.show()
        self.bocadillo.raise_()
        self.timer_tecleo.start(24)
        self.timer_bocadillo.start(ms + len(texto) * 24)
    def _teclear(self):
        self._frase_i = min(len(self._frase), self._frase_i + 2)
        self.bocadillo.vis = self._frase_i
        self.bocadillo.update()
        if self._frase_i % 6 == 0:
            self.sonido("blip")
        if self._frase_i >= len(self._frase):
            self.timer_tecleo.stop()
    def _tick_cyber(self):
        w = self.worker is not None and self.worker.isRunning()
        act = self.timer_tecleo.isActive() or w or (self.cl["fase"] == "trabajando" and self.ticker.isVisible())
        v = self.vista
        if act:
            v.cyber = random.choice((0.0, 0.25, 0.45, 0.7)) if random.random() < 0.55 else v.cyber * 0.5
            v.update()
        elif v.cyber:
            v.cyber = 0.0
            v.update()
    def moveEvent(self, e):
        super().moveEvent(e)
        if self.bocadillo.isVisible():
            self.bocadillo.reposicionar(self)
        if self.globo_pensamiento.isVisible():
            self.globo_pensamiento.reposicionar(self)
    def hideEvent(self, e):
        super().hideEvent(e)
        self.bocadillo.hide()
        self.globo_pensamiento.ocultar(inmediato=True)
    def poner_ticker(self, texto):
        fm = QFontMetrics(self.ticker.font())
        txt = fm.elidedText("▸ " + texto, Qt.ElideRight, W - 24)
        self.ticker.setText(txt)
        ancho = min(W - 6, fm.horizontalAdvance(txt) + 16)
        self.ticker.setGeometry((W - ancho) // 2, SPR_Y - 18, ancho, 16)
        self.ticker.show()
        self.timer_ticker.start(20000)
    def quitar_ticker(self):
        self.ticker.hide()
        self.timer_ticker.stop()
    def cargar_animaciones(self):
        self.animaciones = {}
        for nombre, archivos in ANIMACIONES.items():
            nat, vol = [], []
            for f in archivos:
                ruta = os.path.join(RUTA_IMAGENES, f)
                if not os.path.exists(ruta):
                    continue
                pm = QPixmap(ruta)
                if pm.isNull():
                    continue
                pm = pm.scaled(SPR, SPR, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                nat.append(pm)
                vol.append(pm if nombre in SIN_VOLTEAR else pm.transformed(QTransform().scale(-1, 1)))
            self.animaciones[nombre] = (nat, vol)
        base = None
        for k in ("patrulla", "quieto_de_pie"):
            v = self.animaciones.get(k)
            if v and v[0]:
                base = v
                break
        if base is None:
            print(f"[Gengar] No encuentro sprites en {RUTA_IMAGENES}")
            ph = QPixmap(SPR, SPR)
            ph.fill(QColor("#6a4c93"))
            base = ([ph], [ph])
        for k, v in self.animaciones.items():
            if not v[0]:
                self.animaciones[k] = base
        ruta_anim = os.path.join(RUTA_IMAGENES, "animation.json")
        if os.path.exists(ruta_anim):
            frames_aur = cargar_frames_atlas(ruta_anim, SPR)
            if frames_aur:
                vol = [pm.transformed(QTransform().scale(-1, 1)) for pm in frames_aur]
                self.animaciones["baile_musica"] = (frames_aur, vol)
        self.anim_cascos = self._cargar_secuencia([f"{i:02d}.png" for i in range(6)], ["cascos1.png"], "anim_cascos")
        self.anim_lupa = self._cargar_secuencia([f"lupa{i}.png" for i in range(1, 9)], [], "anim_lupa")
    def _cargar_secuencia(self, nombres, alternativa=(), etiqueta=""):
        print(f"[Gengar] {etiqueta}: buscando en RUTA_IMAGENES={RUTA_IMAGENES} y BASE={BASE}")
        for carpeta in (RUTA_IMAGENES, BASE):
            for lista in (nombres, alternativa):
                frames = []
                for f in lista:
                    ruta = os.path.join(carpeta, f)
                    if not os.path.isfile(ruta):
                        continue
                    pm = QPixmap(ruta)
                    if pm.isNull():
                        continue
                    frames.append(pm.scaled(GLOBO_IMG, GLOBO_IMG, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                if frames:
                    print(f"[Gengar] {etiqueta}: {len(frames)} frames cargados desde {carpeta}")
                    return frames
        print(f"[Gengar] {etiqueta}: no encuentro imágenes ({nombres[0]}...) en {RUTA_IMAGENES}; el globo no se mostrará.")
        return []
    def _es_herramienta_lupa(self, herr):
        if herr in HERRAMIENTAS_LUPA:
            return True
        if herr.startswith("mcp__"):
            bajo = herr.lower()
            return any(k in bajo for k in ("search", "fetch", "read", "browse", "grep"))
        return False
    def _lupa_on(self, seg=None):
        self._lupa_activa = True
        try:
            ms = int(float(seg) * 1000) if seg else LUPA_SEG * 1000
        except (TypeError, ValueError):
            ms = LUPA_SEG * 1000
        self.timer_lupa.start(max(500, min(ms, 60000)))
        self._actualizar_globo()
    def _lupa_off(self):
        self.timer_lupa.stop()
        self._lupa_activa = False
        self._actualizar_globo()
    def _globo_deseado(self):
        if self._callado() or not self.isVisible():
            return None
        if self._lupa_activa and self.anim_lupa:
            return self.anim_lupa
        if self.musica_activa and self.anim_cascos:
            return self.anim_cascos
        return None
    def _actualizar_globo(self):
        frames = self._globo_deseado()
        if frames:
            self.globo_pensamiento.mostrar(self, frames)
        else:
            self.globo_pensamiento.ocultar()
    def anim_actual(self):
        return self.anim_sub or self.estado
    def cambiar_estado(self, nuevo):
        self.estado = nuevo
        self.anim_sub = None
        self.frame = 0
        self.ticks = 0
        self.t_estado = time.time()
        self.dur = {"patrulla": random.uniform(3.0, 6.0), "quieto_de_pie": 1.0, "sentado": random.uniform(6.0, 12.0)}.get(nuevo, 0.0)
        if nuevo not in ESTADOS_PERCHA:
            self.ventana_ref = None
        self.vista.sx = self.vista.sy = 1.0
        self.vista.bob_amp = 3.0 if nuevo in ESTADOS_BOB else 0.0
        self.vista.rot180 = (nuevo == "asomado_arriba")
        if nuevo in ("patrulla", "quieto_de_pie", "sentado") and self.y() > 100:
            sink = SINK_SENTADO if nuevo == "sentado" else SINK_PIE
            _, _, suelo = self.limites(sink)
            if abs(self.y() - suelo) < 30:
                self.move(self.x(), suelo)
        self.dibujar()
    def dibujar(self):
        nat, vol = self.animaciones.get(self.anim_actual()) or self.animaciones["patrulla"]
        lista = vol if self.dir > 0 else nat
        self.vista.poner(lista[self.frame % len(lista)])
    def siguiente_frame(self):
        self.ticks += 1
        if self.ticks % HOLD.get(self.anim_actual(), 1) == 0:
            self.frame += 1
        self.vista.avanzar_glifos()
        self.dibujar()
    def _glifos(self):
        if self.estado == "claude" and self.isVisible():
            self.vista.soltar_glifo()
    def mover(self):
        e = self.estado
        if self.arrastrando or self.chip_estado or self.guardado:
            return
        if self.ventana_ref is not None and e in ESTADOS_PERCHA:
            return
        if e == "en_ventana" or e in ("victoria", "teleport"):
            return
        if e == "bola_fantasma":
            self._mover_bola()
            return
        if e in ("trepar_ir", "trepar_izq", "trepar_der"):
            self._mover_trepar()
            return
        if e == "cursor":
            self._mover_cursor()
            return
        if e == "espera":
            self._mover_espera()
            return
        if e == "flotar":
            self._mover_flotar()
            return
        if e == "error":
            self._mover_error()
            return
        t = time.time() - self.t_estado
        if e == "patrulla" and t > self.dur:
            self.velocidad_x = 0
            self.cambiar_estado("quieto_de_pie")
            if random.random() < 0.4:
                self.decir("Uf, un respiro...")
        elif e == "quieto_de_pie" and t > self.dur:
            self.cambiar_estado("sentado")
            if random.random() < 0.4:
                self.decir("Me voy a sentar un rato.")
        elif e == "sentado" and t > self.dur:
            self.velocidad_x = random.choice([-4, 4])
            self.dir = 1 if self.velocidad_x > 0 else -1
            self.cambiar_estado("patrulla")
        e = self.estado
        sink_actual = SINK_SENTADO if e == "sentado" else SINK_PIE
        min_x, max_x, suelo = self.limites(sink_actual)
        x, y = self.x(), self.y()
        a = self.area()
        if y < a.top() - H or y > a.bottom() + H or x < a.left() - W or x > a.right() + W:
            x = min(max(x, a.left()), a.right() - W)
            y = a.bottom() - H + sink_actual
            self.move(x, y)
            self.volver_a_patrullar()
            return
        if e == "patrulla":
            x += int(self.velocidad_x)
            if x > max_x:
                x = max_x
                self.velocidad_x = -4
            elif x < min_x:
                x = min_x
                self.velocidad_x = 4
            if self.velocidad_x:
                self.dir = 1 if self.velocidad_x > 0 else -1
        if y < suelo:
            self.velocidad_y += 2
            y_nuevo = min(y + int(self.velocidad_y), suelo)
            if e == "caer":
                self.vista.sy = 1.0 + min(0.35, self.velocidad_y * 0.025)
                self.vista.sx = 1.0 / self.vista.sy
                if sys.platform == "win32" and self.velocidad_y > 0:
                    rep = self._repisa(x + W // 2, y + H - OFFSET_PIE, y_nuevo + H - OFFSET_PIE)
                    if rep:
                        self._caer_en_repisa(rep)
                        return
            y = y_nuevo
            if y >= suelo:
                self.velocidad_y = 0
        elif y > suelo:
            y = suelo
            self.velocidad_y = 0
        self.move(x, y)
        if e == "caer" and y >= suelo:
            self._aterrizar()
    def _aterrizar(self):
        c = QPoint(self.x() + W // 2, self.y() + H - 6)
        self.sonido("land")
        self.fx.agregar(Particulas(c.x(), c.y(), n=10, colores=VIOLETAS, vel=(80, 220), grav=700, dur=0.6, cono=(-math.pi * 0.95, -math.pi * 0.05)))
        self.vista.sx, self.vista.sy = 1.3, 0.72
        self.vista.update()
        QTimer.singleShot(150, self._fin_squash)
        self._volver_tras_evento()
    def _fin_squash(self):
        self.vista.sx = self.vista.sy = 1.0
        self.vista.update()
    def _mover_espera(self):
        cur = QCursor.pos()
        tx, ty = self._pos_junto_a(cur)
        self.dir = -1 if cur.x() < self.x() + W // 2 else 1
        self.move(int(round(self.x() + (tx - self.x()) * 0.18)), int(round(self.y() + (ty - self.y()) * 0.18)))
    def _pos_junto_a(self, cur):
        a = self.area()
        cx = cur.x() + 90
        if cx + SPR // 2 > a.right():
            cx = cur.x() - 90
        cy = cur.y() - 25
        x = cx - W // 2
        y = cy - SPR_Y - SPR // 2
        x = max(a.left() - SPR_X, min(x, a.right() + 1 - SPR_X - SPR))
        y = max(a.top(), min(y, a.bottom() + 1 - H))
        return x, y
    def _mover_flotar(self):
        if self.flota_obj is None:
            self.velocidad_y = 0
            self.cambiar_estado("caer")
            return
        tx, ty = self.flota_obj
        x, y = self.x(), self.y()
        dx, dy = tx - x, ty - y
        d = math.hypot(dx, dy)
        if d > 6:
            paso = min(4.0, d)
            self.dir = 1 if dx > 0 else -1
            self.move(int(x + dx / d * paso), int(y + dy / d * paso))
        elif self.flota_t is None:
            self.flota_t = time.time()
        elif time.time() - self.flota_t > 4.0:
            self.flota_obj = None
            self.velocidad_y = 0
            self.cambiar_estado("caer")
            self.decir("Se acabó la gravedad cero...", 2500)
    def flotar(self):
        self.cancelar_pendientes()
        a = self.area()
        self.cambiar_estado("flotar")
        self.flota_obj = (random.randint(a.left(), max(a.left() + 1, a.right() - W)), random.randint(a.top() + 40, max(a.top() + 41, a.bottom() - H - 100)))
        self.flota_t = None
        self.decir(random.choice(["Voy a flotar un rato...", "Mira, sin gravedad."]), 2500)
    def _mover_error(self):
        min_x, max_x, suelo = self.limites(SINK_PIE)
        x = max(min_x, min(max_x, self.x() + int(self.velocidad_x)))
        self.velocidad_x *= 0.88
        self.velocidad_y += 2
        y = self.y() + int(self.velocidad_y)
        if y >= suelo:
            y = suelo
            self.velocidad_y = 0
        self.move(x, y)
    def volver_a_patrullar(self):
        if self.cl["fase"] != "idle":
            self._volver_tras_evento()
            return
        self._patrullar()
    def _patrullar(self):
        self.cancelar_pendientes()
        self.arrastrando = False
        self.velocidad_x = random.choice([-4, 4])
        self.dir = 1 if self.velocidad_x > 0 else -1
        self.cambiar_estado("patrulla")
    def _volver_tras_evento(self):
        f = self.cl["fase"]
        if f == "espera":
            self._ir_a_espera()
        elif f == "trabajando":
            self.entrar_trabajo(forzar=True)
        else:
            self._patrullar()
    def vigilar_estado(self):
        if self.arrastrando or self.estado in LIBRES or self.estado in ("en_ventana", "asomado", "asomado_arriba", "claude", "espera", "luna", "victoria", "teleport", "poseer", "dormir_largo", "flotar", "error"):
            return
        if self.estado == "pensando" and self.worker is not None and self.worker.isRunning():
            return
        if time.time() - self.t_estado > 45:
            self.volver_a_patrullar()
    def elegir_comportamiento(self):
        if (self.estado not in LIBRES or self.arrastrando or self.estudio_fase == "estudio" or self.chip_estado or self.guardado):
            return
        self.contador += 1
        hora = datetime.datetime.now().hour
        peso_dormir = 0.8 if (hora >= 22 or hora <= 6) else 0.2
        peso_bailar = 0.6 if (10 <= hora <= 20) else 0.2
        if random.random() < 0.55:
            opciones = ["dormir", "bailar", "hipnosis", "bola_fantasma", "humo", "ventana", "teleport", "flotar", "luna"]
            pesos = [peso_dormir, peso_bailar, 0.3, 0.25, 0.15, 0.35, 0.15, 0.25 if self.cfg.get("vagar", True) else 0.0, 0.06]
            self.ejecutar(random.choices(opciones, weights=pesos, k=1)[0])
        elif random.random() < 0.15:
            self.trepar_pared()
    def ejecutar(self, accion):
        if accion == "ventana":
            self.ir_a_ventana()
            return
        if accion == "teleport":
            min_x, max_x, suelo = self.limites(SINK_PIE)
            self.teletransportar(random.randint(min_x, max(min_x + 1, max_x)), suelo)
            return
        if accion == "flotar":
            self.flotar()
            return
        if accion == "luna":
            self.mirar_luna(False)
            return
        self.cancelar_pendientes()
        if accion == "dormir":
            self.cambiar_estado("dormir")
            self.decir("Zzz... no molestar, tío.")
            self.tras(5000, self.volver_a_patrullar)
        elif accion == "bailar":
            self.cambiar_estado("bailar")
            self.decir("¡Esto va por ti, Ruben!")
            self.tras(4000, self.volver_a_patrullar)
        elif accion == "baile_musica":
            self.cambiar_estado("baile_musica")
            self.decir("¡Con auriculares, tío!")
            self.tras(4000, self.volver_a_patrullar)
        elif accion == "hipnosis":
            self.cambiar_estado("hipnosis")
            self.decir("¡Mírame a los ojos, tío!")
            self.tras(4000, self.volver_a_patrullar)
        elif accion == "bola_fantasma" or accion == "bola":
            self.rodar_bola()
        elif accion == "humo":
            self.decir("Hasta luego, tío...")
            self.desaparecer_con_humo()
    def soltar_pensamiento(self):
        if self.estado in LIBRES and not self.arrastrando and self.estudio_fase != "estudio":
            self.decir(random.choice(FRASES_PENSAMIENTOS))
    def rodar_bola(self):
        self.cambiar_estado("bola_fantasma")
        self.velocidad_x = random.choice([-6, 6])
        self.velocidad_y = -10
        self.decir("¡Allá voy!", 2500)
        self.tras(3500, self.volver_a_patrullar)
    def _mover_bola(self):
        min_x, max_x, suelo = self.limites(SINK_PIE)
        x = self.x() + int(self.velocidad_x)
        if x > max_x:
            x = max_x
            self.velocidad_x *= -1
        elif x < min_x:
            x = min_x
            self.velocidad_x *= -1
        self.dir = 1 if self.velocidad_x > 0 else -1
        self.velocidad_y += 2
        y = self.y() + int(self.velocidad_y)
        if y > suelo:
            y = suelo
            self.velocidad_y = -12
        self.move(x, y)
    def desaparecer_con_humo(self):
        self.cambiar_estado("humo")
        self.tras(800, lambda: self.setWindowOpacity(0.0))
        self.tras(1600, self._reaparecer)
    def _reaparecer(self):
        a = self.area()
        min_x, max_x, suelo = self.limites(SINK_PIE)
        x = random.randint(a.left() + 50, max(a.left() + 51, a.right() - W - 50))
        y = random.randint(a.top() + 50, max(a.top() + 51, suelo))
        self.move(x, y)
        self.volver_a_patrullar()
    def trepar_pared(self):
        if self.estado not in LIBRES or self.arrastrando:
            return
        self.cancelar_pendientes()
        a = self.area()
        min_x, max_x, suelo = self.limites(SINK_PIE)
        izq = self.x() + W // 2 < a.center().x()
        self.lado_trepa = "izq" if izq else "der"
        self.pared_x = min_x if izq else max_x
        self.velocidad_x = -5 if izq else 5
        self.dir = 1 if self.velocidad_x > 0 else -1
        self.fase_trepa = "ir"
        self.cambiar_estado("trepar_ir")
        self.decir("Voy a subir por aquí...")
    def _mover_trepar(self):
        a = self.area()
        min_x, max_x, suelo = self.limites(SINK_PIE)
        if self.estado == "trepar_ir":
            x = self.x() + int(self.velocidad_x)
            if (self.velocidad_x < 0 and x <= self.pared_x) or (self.velocidad_x > 0 and x >= self.pared_x):
                x = self.pared_x
                self.fase_trepa = "subir"
                self.cambiar_estado("trepar_izq" if self.lado_trepa == "izq" else "trepar_der")
                self.decir("¡Allá voy!")
            self.move(x, suelo)
        elif self.fase_trepa == "subir":
            tope = a.top() - SPR_Y
            y = self.y() - 5
            if y <= tope:
                y = tope
                self.fase_trepa = "pausa"
                self.decir("Uf, qué alto.")
                self.tras(1000, self._iniciar_bajada)
            self.move(self.x(), y)
        elif self.fase_trepa == "bajar":
            y = self.y() + 5
            if y >= suelo:
                self.move(self.x(), suelo)
                self.fase_trepa = None
                self.volver_a_patrullar()
                return
            self.move(self.x(), y)
    def _iniciar_bajada(self):
        if self.fase_trepa == "pausa":
            self.fase_trepa = "bajar"
    def ventanas_candidatas(self):
        if sys.platform != "win32":
            return []
        user32 = ctypes.windll.user32
        dpr, a, res = self.dpr(), self.area(), []
        hwnd_self = int(self.winId())
        hwnd_chat = int(self.chat_window.winId())
        def callback(hwnd, lParam):
            if hwnd == hwnd_self or hwnd == hwnd_chat:
                return True
            if not user32.IsWindowVisible(hwnd):
                return True
            if user32.IsIconic(hwnd) or user32.IsZoomed(hwnd):
                return True
            if ventana_cloaked(hwnd):
                return True
            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buf, 256)
            if class_buf.value in ("Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            titulo = buf.value
            if titulo in IGNORAR_TITULOS:
                return True
            rect = get_visible_rect(hwnd)
            l, t, r, b = rect.left / dpr, rect.top / dpr, rect.right / dpr, rect.bottom / dpr
            if (r - l) < 200 or (b - t) < 100:
                return True
            if r < a.left() or l > a.right() or b < a.top() or t > a.bottom():
                return True
            res.append((hwnd, l, t, r, titulo))
            return True
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(callback), 0)
        return res
    def ventanas_cache(self, ttl=0.2):
        ahora = time.time()
        if ahora - self._vc[0] > ttl:
            self._vc = (ahora, self.ventanas_candidatas())
        return self._vc[1]
    def ventana_frontal(self):
        c = self.ventanas_candidatas()
        return c[0] if c else None
    def _rect_ventana(self, hwnd):
        if sys.platform != "win32":
            return None
        try:
            u = ctypes.windll.user32
            if not u.IsWindow(hwnd) or not u.IsWindowVisible(hwnd) or u.IsIconic(hwnd) or u.IsZoomed(hwnd):
                return None
            r = get_visible_rect(hwnd)
            d = self.dpr()
            return (r.left / d, r.top / d, r.right / d, r.bottom / d)
        except Exception:
            return None
    def _pos_en_ventana(self, l, t, r):
        a = self.area()
        lo = max(a.left(), int(l) - SPR_X + 10)
        hi = min(a.right() - W, int(r) - SPR_X - SPR - 10)
        x = random.randint(lo, hi) if hi >= lo else (lo + hi) // 2
        y = max(a.top() + 10, int(t) - H + OFFSET_PIE)
        return x, y
    def _perchar(self, hwnd, l, t, estado):
        self.ventana_ref = (hwnd, l, t)
        self.cambiar_estado(estado)
        self.velocidad_y = 0
        if estado == "claude":
            self.anim_sub = self.anim_trabajo
            self.dibujar()
        self.timer_ventana.start(80)
    def ir_a_ventana(self, excluir=None):
        cand = [c for c in self.ventanas_candidatas() if c[0] != excluir]
        if not cand:
            self.decir("No veo ninguna ventana. Abre el Bloc de notas, tío.", 4000)
            return False
        hwnd, l, t, r, titulo = random.choice(cand)
        self.cancelar_pendientes()
        self.decir(f"Voy a ver el mundo desde '{titulo[:20]}...'")
        x, y = self._pos_en_ventana(l, t, r)
        self.teletransportar(x, y, despues=lambda: self._aparecer_en_ventana(hwnd))
        return True
    def _aparecer_en_ventana(self, hwnd):
        rect = self._rect_ventana(hwnd)
        if rect is None:
            self.volver_a_patrullar()
            return
        l, t = rect[0], rect[1]
        self.move(self.x(), max(self.area().top() + 10, int(t) - H + OFFSET_PIE))
        self._perchar(hwnd, l, t, "en_ventana")
        self.dir = random.choice([-1, 1])
        self.dibujar()
        self.decir("Vista panorámica, tío.")
        self.tras(random.randint(12000, 25000), self._bajar_de_ventana)
    def _vigilar_ventana(self):
        if self.ventana_ref is None or self.estado not in ESTADOS_PERCHA:
            self.timer_ventana.stop()
            return
        hwnd, l0, t0 = self.ventana_ref
        rect = self._rect_ventana(hwnd)
        if rect is None:
            self._bajar_de_ventana(forzar=True)
            return
        l, t = rect[0], rect[1]
        if l != l0 or t != t0:
            self.move(self.x() + int(l - l0), self.y() + int(t - t0))
            self.ventana_ref = (hwnd, l, t)
    def _bajar_de_ventana(self, forzar=False):
        if self.ventana_ref is None:
            return
        if not forzar and self.estado == "claude":
            self.tras(10000, self._bajar_de_ventana)
            return
        self.timer_ventana.stop()
        self.ventana_ref = None
        self.velocidad_y = 0
        self.cambiar_estado("caer")
        self.decir("¡Uy, que me caigo!")
    def _repisa(self, cx, pie0, pie1):
        for hwnd, l, t, r, titulo in self.ventanas_cache(0.15):
            if pie0 <= t + 2 and pie1 >= t and l + 30 <= cx <= r - 30:
                return (hwnd, l, t, r, titulo)
        return None
    def _repisa_cerca(self, cx, pie, tol):
        for hwnd, l, t, r, titulo in self.ventanas_cache(0.0):
            if abs(t - pie) <= tol and l + 30 <= cx <= r - 30:
                return (hwnd, l, t, r, titulo)
        return None
    def _caer_en_repisa(self, rep, soltado=False):
        hwnd, l, t, r, titulo = rep
        self.move(self.x(), int(t) - H + OFFSET_PIE)
        self._perchar(hwnd, l, t, "en_ventana")
        self.vista.sx, self.vista.sy = 1.25, 0.75
        QTimer.singleShot(150, self._fin_squash)
        self.sonido("land")
        self.decir("Aquí me quedo, tío." if soltado else "¡Ja! Me ha cogido la ventana.", 3000)
        self.tras(random.randint(12000, 25000), self._bajar_de_ventana)
    def comprobar_raton(self):
        pos = QCursor.pos()
        ahora = time.time()
        movido = pos != self.ultima_pos_raton
        if movido:
            self.ultima_pos_raton = pos
            self.t_raton_mov = ahora
            if self.estado in ("asomado", "asomado_arriba"):
                self.despertar_asomado()
                return
            if self.estado == "dormir_largo":
                c = self.centro_sprite()
                if math.hypot(pos.x() - c.x(), pos.y() - c.y()) < 260:
                    self.despertar()
                return
            if self.chip_estado == "dormido" and self.chip.cerca(pos, 160):
                self.despertar()
                return
        if self.arrastrando or self.guardado or self.chip_estado:
            return
        if self.estado in ("quieto_de_pie", "patrulla", "sentado"):
            c = self.centro_sprite()
            if math.hypot(pos.x() - c.x(), pos.y() - c.y()) < 300:
                if self.estado != "patrulla":
                    self.dir = 1 if pos.x() > c.x() else -1
                    self.dibujar()
                if (movido and self.estado in ("quieto_de_pie", "patrulla") and random.random() < 0.05 and ahora - self.t_zap > 45):
                    self.zap_cursor()
                    return
        if movido:
            return
        if self.estado not in LIBRES:
            return
        quieto = ahora - self.t_raton_mov
        if quieto > IDLE_ASOMARSE:
            self.asomarse()
            return
        if quieto > 5 and ahora - self.t_seguir > 5:
            self.t_seguir = ahora
            centro = self.x() + W // 2
            if pos.x() > centro + 100:
                self.dir = 1
            elif pos.x() < centro - 100:
                self.dir = -1
            else:
                return
            if self.estado == "patrulla":
                self.velocidad_x = 3 * self.dir
    def zap_cursor(self):
        self.t_zap = time.time()
        self.cancelar_pendientes()
        cur = QCursor.pos()
        self.dir = 1 if cur.x() > self.centro_sprite().x() else -1
        self.cambiar_estado("travesura")
        self.fx.agregar(Rayo(self.mano_xy, (cur.x(), cur.y()), color="#b388ff", dur=0.4, grosor=3))
        self.sonido("bolt")
        self.decir(random.choice(FRASES_ZAP), 2500)
        self.tras(1500, self.volver_a_patrullar)
    def asomarse(self):
        self.cancelar_pendientes()
        a = self.area()
        min_x, max_x, suelo = self.limites(SINK_PIE)
        modo = random.choice(["izq", "der", "arriba"])
        self.bocadillo.hide()
        self.velocidad_y = 0
        if modo == "arriba":
            self.cambiar_estado("asomado_arriba")
            self.dir = random.choice([-1, 1])
            self.move(random.randint(a.left() + 50, max(a.left() + 51, a.right() - W - 50)), a.top() - SPR // 2 - SPR_Y)
        else:
            izq = modo == "izq"
            self.cambiar_estado("asomado")
            self.dir = 1 if izq else -1
            self.move(a.left() - W // 2 if izq else a.right() + 1 - W // 2, suelo)
        self.dibujar()
    def despertar_asomado(self):
        if self.estado == "asomado_arriba":
            self.velocidad_y = 0
            self.cambiar_estado("caer")
            self.decir("¡Eh! Me has pillado...")
            return
        a = self.area()
        min_x, max_x, suelo = self.limites(SINK_PIE)
        dentro = 1 if self.x() < a.center().x() else -1
        self.volver_a_patrullar()
        self.velocidad_x = 4 * dentro
        self.dir = dentro
        self.move(min_x if dentro > 0 else max_x, suelo)
        self.decir("¡Eh! Me has pillado...")
    def alternar_visible(self):
        if self.guardado:
            self.desguardar()
        elif self.chip_estado == "dormido":
            self.despertar()
        elif self.isVisible():
            self.hide()
        else:
            self.show()
    def programar_travesura(self):
        self.timer_travesura.start(random.randint(45000, 90000))
    def hacer_travesura(self):
        self.programar_travesura()
        if (not self.modo_travesura or self.estado not in LIBRES or self.arrastrando or self.estudio_fase == "estudio" or not self.isVisible()):
            return
        opciones = [self.robar_cursor, self.glitch_pantalla, self.nota_hackeo]
        if gw is not None:
            opciones.append(self.tirar_ventana)
        random.choice(opciones)()
    def robar_cursor(self):
        self.cancelar_pendientes()
        self.cambiar_estado("cursor")
        self.fase_cursor = "ir"
        self.t_cursor = time.time()
        self.decir("Psst... dame eso.")
    def _mover_cursor(self):
        min_x, max_x, suelo = self.limites(SINK_PIE)
        ahora = time.time()
        cur = QCursor.pos()
        if self.fase_cursor == "ir":
            dx = (cur.x() - W // 2) - self.x()
            if abs(dx) <= 8 or ahora - self.t_cursor > 6:
                self.fase_cursor = "llevar"
                self.t_cursor = ahora
                self.velocidad_x = random.choice([-3, 3])
                self.decir("¡Mío!", 2500)
            else:
                paso = 8 if dx > 0 else -8
                self.dir = 1 if paso > 0 else -1
                self.move(self.x() + paso, suelo)
        else:
            if ahora - self.t_cursor > 2.5:
                self.volver_a_patrullar()
                self.decir("Jajaja, toma, ya está.")
                return
            x = self.x() + int(self.velocidad_x)
            if x < min_x or x > max_x:
                self.velocidad_x *= -1
                x = max(min_x, min(x, max_x))
            self.dir = 1 if self.velocidad_x > 0 else -1
            self.move(x, suelo)
            QCursor.setPos(self.x() + W // 2, self.y() + SPR_Y + 40)
    def glitch_pantalla(self):
        self.cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("¡Interferencias!")
        self.glitch.lanzar(self.pantalla().geometry())
        self.tras(1800, self.volver_a_patrullar)
    def nota_hackeo(self):
        self.cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("Jejeje...")
        self.nota = NotaHack(self.pantalla().geometry())
        self.nota.show()
        self.tras(1800, self.volver_a_patrullar)
    def tirar_ventana(self):
        if gw is None:
            return
        seguras = ["Notepad", "Bloc de notas", "Calculator", "Calculadora", "Paint", "mspaint"]
        try:
            ventanas = [w for w in gw.getAllWindows() if w.title and any(s in w.title for s in seguras)]
        except Exception:
            return
        if not ventanas:
            return
        w = random.choice(ventanas)
        a, dpr = self.area(), self.dpr()
        try:
            x = random.randint(a.left() + 50, max(a.left() + 51, a.right() - 350))
            y = random.randint(a.top() + 50, max(a.top() + 51, a.bottom() - 250))
            w.moveTo(int(x * dpr), int(y * dpr))
        except Exception:
            return
        self.cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("¡Toma esa ventana, tío!")
        self.tras(1500, self.volver_a_patrullar)
    def avisar(self, texto):
        self.notificar.emit("Gengar", texto)
        QApplication.beep()
        self.decir(texto, 12000)
        if self.arrastrando:
            return
        self.cancelar_pendientes()
        self.cambiar_estado("bailar")
        self.tras(6000, self.volver_a_patrullar)
    def iniciar_estudio(self, min_estudio=25, min_descanso=5):
        self.min_estudio, self.min_descanso = min_estudio, min_descanso
        self.estudio_fase = "estudio"
        self.estudio_fin = time.time() + min_estudio * 60
        self.timer_estudio.start()
        self.decir(f"¡A estudiar {min_estudio} min! Yo vigilo.", 5000)
    def parar_estudio(self):
        self.estudio_fase = None
        self.timer_estudio.stop()
        self.tooltip.emit("Gengar")
        self.decir("Vale, se acabó el estudio.")
    def _tick_estudio(self):
        if not self.estudio_fase:
            self.timer_estudio.stop()
            return
        resta = int(self.estudio_fin - time.time())
        if resta <= 0:
            if self.estudio_fase == "estudio":
                self.estudio_fase = "descanso"
                self.estudio_fin = time.time() + self.min_descanso * 60
                self.avisar(f"¡Descanso de {self.min_descanso} min! Levántate y estira.")
            else:
                self.estudio_fase = "estudio"
                self.estudio_fin = time.time() + self.min_estudio * 60
                self.avisar("¡Vuelta al estudio!")
            return
        m, s = divmod(resta, 60)
        self.tooltip.emit(f"Gengar - {self.estudio_fase}: {m:02d}:{s:02d}")
    def programar_alarma(self, ms, etiqueta):
        t = QTimer(self)
        t.setSingleShot(True)
        def _sonar():
            if t in self.alarmas:
                self.alarmas.remove(t)
            self.avisar(f"¡Alarma! ({etiqueta})")
        t.timeout.connect(_sonar)
        t.start(ms)
        self.alarmas.append(t)
        self.decir(f"Alarma puesta ({etiqueta}).")
    def cancelar_alarmas(self):
        for t in self.alarmas:
            t.stop()
        self.alarmas.clear()
        self.decir("Alarmas canceladas.")
    def escuchar(self):
        if TTS.hablando():
            TTS.parar()
            return
        e = getattr(self, "escucha", None)
        if e is not None and e.isRunning():
            e.cancelar()
            return
        self.escucha = EscuchaVoz()
        self.escucha.estado.connect(self._estado_voz)
        self.escucha.texto.connect(self._voz_recibida)
        self.escucha.finished.connect(lambda: self.chat_window.set_mic(False))
        self.chat_window.set_mic(True)
        self.escucha.start()
    def _estado_voz(self, e):
        if e == "cargando":
            self.decir("Calentando el oído, tío...", 900000, badge="EN CURSO", tipo="info")
        elif e == "escuchando":
            self.decir("Te escucho, habla.", 25000, badge="ESCUCHANDO", tipo="info")
        elif e == "transcribiendo":
            self.decir("Procesando lo que dices...", 30000, badge="EN CURSO", tipo="info")
        elif e == "nada":
            self.decir("No he oído nada, tío.", 3000, badge="SILENCIO", tipo="info")
        elif e.startswith("error:"):
            self.decir(e[6:], 8000, maxlen=160, badge="ERROR", tipo="error")
            self.chat_window.agregar_mensaje("Sistema", e[6:])
    def _voz_recibida(self, txt):
        self.por_voz = True
        self.chat_window.agregar_mensaje("Tú", txt)
        self.chat_window.iniciar_typing()
        self.recibir_mensaje(txt)
    def recibir_mensaje(self, prompt):
        self.t_actividad = time.time()
        self.cancelar_pendientes()
        self.cambiar_estado("pensando")
        self.decir("Gengar está tramando algo...", 60000, badge="EN CURSO", tipo="info")
        self.ia_n = 0
        self.ia_t0 = time.time()
        self.worker = WorkerIA(prompt)
        self.worker.respuesta_lista.connect(self.mostrar_respuesta)
        self.worker.accion.connect(self._contar_accion)
        self.worker.accion.connect(self.fx_accion)
        self.worker.start()
    def _contar_accion(self):
        self.ia_n += 1
    def fx_accion(self):
        ahora = time.time()
        if ahora - getattr(self, "t_fx_accion", 0.0) < 1.5 or self.guardado or self.chip_estado:
            return
        self.t_fx_accion = ahora
        c = self.centro_sprite()
        self.sonido("charge")
        self.fx.agregar(Onda(c.x(), c.y(), r_max=380, dur=0.8))
        self.fx.agregar(LineasVelocidad(c.x(), c.y(), dur=0.9))
        self.fx.agregar(Particulas(c.x(), c.y(), n=26, colores=VIOLETAS + ["#ffffff"], vel=(120, 420), grav=300, dur=1.0))
        self.cutin()
        self.impacto()
        self.vista.glitch = 0.8
        QTimer.singleShot(900, lambda: setattr(self.vista, "glitch", 0.0))
    def mostrar_respuesta(self, texto):
        err = texto.startswith(("Error", "Ollama no responde", "Fallo al", "[ERROR"))
        seg = int(time.time() - getattr(self, "ia_t0", time.time()))
        tt = f"{seg} s" if seg < 60 else f"{seg // 60} min {seg % 60} s"
        n = getattr(self, "ia_n", 0)
        stats = f"{n} {'acción' if n == 1 else 'acciones'} · {tt}" if n else tt
        titulo, badge, tipo = ("Fallo, tío.", "ERROR", "error") if err else ("Misión cumplida, tío.", "TERMINADO", "ok")
        self.respuesta_para_chat.emit(texto, titulo, badge, tipo, stats)
        self.cancelar_pendientes()
        self.cambiar_estado("bailar")
        self.decir(texto, max(6000, len(texto) * 70), maxlen=220, titulo=titulo, badge=badge, tipo=tipo, stats=stats)
        self.tras(3000, self.volver_a_patrullar)
        if getattr(self, "por_voz", False) or self.chat_window.btn_voz.isChecked():
            TTS.hablar("Algo ha fallado, tío." if err else texto_hablado(texto))
        self.por_voz = False
    def evento_claude(self, d):
        ev = d.get("ev", "")
        if ev == "Lupa":
            print(f"[Gengar] evento_claude Lupa recibido: {d}")
            if d.get("on", True):
                self._lupa_on(d.get("seg"))
            elif self._lupa_activa:
                self.timer_lupa.start(3000)
            return
        self.t_claude = time.time()
        if self.estado == "dormir_largo" or self.chip_estado == "dormido":
            self.despertar(msg="")
        cl = self.cl
        if ev == "SessionStart":
            if not (self.guardado or self.chip_estado):
                self.sonido("hello")
                self.decir("¡Sesión abierta, tío! Yo vigilo.", 4000)
        elif ev == "UserPromptSubmit":
            cl.update(fase="trabajando", t0=time.time(), acciones=0, archivos=set(), errores=0, herr_actual="", ultimo="", resumen="")
            self.iniciar_trabajo(d.get("prompt", ""))
        elif ev == "PreToolUse":
            self.herramienta(d)
        elif ev == "PostToolUse":
            self.herramienta_fin(d, bool(d.get("error")))
        elif ev == "PostToolUseFailure":
            self.herramienta_fin(d, True)
        elif ev == "Notification":
            self.notificacion(d)
        elif ev == "Stop":
            self.terminar(d.get("ultimo", ""))
        elif ev == "SubagentStop":
            if cl["fase"] != "idle":
                self.poner_ticker("AGENTE listo")
        elif ev == "SessionEnd":
            cl["fase"] = "idle"
            self._lupa_off()
            self.quitar_ticker()
            if not (self.guardado or self.chip_estado) and self.estado in ("claude", "espera"):
                self.decir("Sesión cerrada. Hasta luego.", 3000)
                self._patrullar()
    def iniciar_trabajo(self, prompt):
        if self.guardado or self.chip_estado or self.arrastrando:
            return
        self.sonido("tick")
        self.decir(("Entendido: «" + prompt[:60] + "»") if prompt else "¡Manos a la obra!", 3500)
        ya_montado = self.ventana_ref is not None
        self.cancelar_pendientes()
        dest = None
        if self.cfg.get("perchar", True) and not ya_montado and sys.platform == "win32":
            dest = self.ventana_frontal()
        if dest:
            hwnd, l, t, r, _ = dest
            x, y = self._pos_en_ventana(l, t, r)
            self.teletransportar(x, y, despues=lambda: self._perchar_trabajo(hwnd))
        else:
            self.entrar_trabajo(forzar=True)
    def _perchar_trabajo(self, hwnd):
        rect = self._rect_ventana(hwnd)
        if rect is None or self.cl["fase"] != "trabajando":
            self._volver_tras_evento()
            return
        self.move(self.x(), max(self.area().top() + 10, int(rect[1]) - H + OFFSET_PIE))
        self._perchar(hwnd, rect[0], rect[1], "claude")
    def entrar_trabajo(self, forzar=False):
        if self.guardado or self.chip_estado or self.arrastrando:
            return
        if self.estado == "claude":
            if self.anim_sub != self.anim_trabajo:
                self.anim_sub = self.anim_trabajo
                self.frame = 0
                self.dibujar()
            return
        if not forzar and self.estado in ("espera", "teleport", "victoria", "error", "luna", "poseer"):
            return
        self.cancelar_pendientes()
        self.cambiar_estado("claude")
        self.anim_sub = self.anim_trabajo
        min_x, max_x, _ = self.limites()
        self.move(max(min_x, min(self.x(), max_x)), self.y())
        self.dibujar()
    def herramienta(self, d):
        herr = d.get("herr", "")
        if herr in HERRAMIENTAS:
            verbo, anim = HERRAMIENTAS[herr]
        elif herr.startswith("mcp__"):
            verbo, anim = "MCP", "claude_web"
        else:
            verbo, anim = "USA", "claude_leer"
        cl = self.cl
        if cl["fase"] == "espera":
            self.salir_espera()
        elif cl["fase"] == "idle":
            cl.update(fase="trabajando", t0=cl["t0"] or time.time())
        cl["acciones"] += 1
        cl["herr_actual"] = (verbo + " " + d.get("detalle", "")).strip()
        self.anim_trabajo = anim
        if self.guardado or self.chip_estado:
            return
        if self._es_herramienta_lupa(herr):
            self._lupa_on()
        else:
            self._lupa_off()
        self.poner_ticker(cl["herr_actual"])
        self.entrar_trabajo()
        if anim in ("claude_cmd", "claude_web") and self.estado == "claude" and self.isVisible():
            mx, my = self.mano_xy()
            self.fx.agregar(Particulas(mx, my, n=6, colores=ROJOS, vel=(60, 200), grav=200, dur=0.5, cono=(-math.pi * 0.9, -math.pi * 0.1)))
    def herramienta_fin(self, d, error):
        cl = self.cl
        if self._lupa_activa:
            self.timer_lupa.start(3000)
        if cl["fase"] == "espera":
            self.salir_espera()
        if error:
            cl["errores"] += 1
            herr = d.get("herr", "")
            linea = d.get("err_linea") or d.get("detalle") or "algo ha fallado"
            if herr == "Bash" or herr.startswith("mcp__"):
                self.error_comando(linea)
            else:
                self.poner_ticker("FALLO " + (d.get("detalle") or herr))
        elif d.get("herr") in ESCRITURA and d.get("archivo"):
            cl["archivos"].add(d["archivo"])
    def error_comando(self, linea):
        if self.guardado or self.chip_estado or self.arrastrando or self.estado == "espera":
            return
        ahora = time.time()
        if ahora - self.t_error < 2.0:
            return
        self.t_error = ahora
        self.cancelar_pendientes()
        self.cambiar_estado("error")
        self.sonido("error")
        self._tinte(QColor(255, 40, 70, 190))
        QTimer.singleShot(120, lambda: self._tinte(None))
        self.vista.glitch = 1.0
        self.velocidad_x = -12 * self.dir
        self.velocidad_y = -7
        self.decir(linea, 6000, maxlen=118, titulo="Fallo, tío.", badge="ERROR", tipo="error")
        self.tras(600, lambda: setattr(self.vista, "glitch", 0.0))
        self.tras(1800, self._volver_tras_evento)
    def notificacion(self, d):
        msg = d.get("msg", "") or ""
        tipo = d.get("tipo", "") or ""
        bajo = msg.lower()
        if tipo == "permission_prompt" or "permission" in bajo or "permiso" in bajo:
            self.pedir_atencion(msg or "Claude necesita tu permiso")
        elif tipo == "elicitation_dialog":
            self.pedir_atencion(msg or "Claude te hace una pregunta")
        elif tipo == "idle_prompt" or "waiting" in bajo:
            self.pedir_atencion("Claude espera tu respuesta, tío.")
        elif msg and not (self.guardado or self.chip_estado):
            self.decir(msg, 5000)
    def pedir_atencion(self, msg):
        if self.cl["fase"] == "espera":
            return
        self.cl["fase"] = "espera"
        self.cl["msg_espera"] = msg
        self.sonido("alert")
        self.notificar.emit("Gengar", msg)
        self.poner_ticker("ESPERA TU RESPUESTA" if "respuesta" in msg.lower() else "ESPERA PERMISO")
        if self.chip_estado == "dormido":
            self.despertar(msg="")
            return
        if self.guardado:
            self.desguardar(auto=True)
        if self.arrastrando:
            return
        self._ir_a_espera()
    def _ir_a_espera(self):
        if self.cl["fase"] != "espera" or self.arrastrando:
            return
        x, y = self._pos_junto_a(QCursor.pos())
        self.teletransportar(x, y, despues=self._empezar_espera)
    def _empezar_espera(self):
        if self.cl["fase"] != "espera":
            self._volver_tras_evento()
            return
        self.cambiar_estado("espera")
        c = self.centro_sprite()
        self.fx.agregar(Onda(c.x(), c.y(), r_max=220, color="#ff5252", dur=0.6))
        self.cutin()
        self.decir(self.cl["msg_espera"], 20000, maxlen=118, titulo="Te necesito, tío.", badge="EN ESPERA", tipo="espera")
    def salir_espera(self):
        self.cl["fase"] = "trabajando"
        if self.estado == "espera":
            self.bocadillo.hide()
            self.velocidad_y = 0
            self.cambiar_estado("caer")
            self.anim_sub = None
    def cutin(self):
        c = self.centro_sprite()
        a = self.area()
        w, h = 270, 104
        x = c.x() + SPR // 2 + 10
        if x + w > a.right():
            x = c.x() - SPR // 2 - 10 - w
        y = max(a.top() + 10, c.y() - h - 20)
        self.fx.agregar(CutIn(self.pm_cara, x, y, w, h))
    def terminar(self, ultimo):
        cl = self.cl
        self._lupa_off()
        dur = time.time() - cl["t0"] if cl["t0"] else 0.0
        acc, narch = cl["acciones"], len(cl["archivos"])
        m, s = divmod(int(dur), 60)
        resumen = f"{acc} acciones · {narch} archivos · {m}m {s:02d}s" if acc else ""
        tt = f"{s} s" if not m else f"{m} min {s} s"
        cl.update(fase="idle", ultimo=ultimo, resumen=resumen, t0=0.0, t_fin=time.time(), stats=f"{acc} acciones · {narch} archivos modificados · {tt}" if acc else "")
        self.quitar_ticker()
        largo = dur >= LUNA_LARGA_MIN * 60 or acc >= LUNA_LARGA_ACC
        if self.guardado or self.chip_estado:
            self.sonido("done")
            self.notificar.emit("Gengar", (resumen + " — " if resumen else "") + (ultimo or "Claude ha terminado"))
            return
        if self.arrastrando:
            return
        self.cancelar_pendientes()
        if acc == 0:
            self.sonido("done")
            self.cambiar_estado("bailar")
            self.decir(ultimo or "", 6000, maxlen=118, titulo="Misión cumplida, tío.", badge="TERMINADO", tipo="ok")
            self.tras(3000, self.volver_a_patrullar)
            return
        a = self.area()
        self.teletransportar(a.center().x() - W // 2, a.center().y() - H // 2 - 30, despues=lambda: self._victoria(resumen, ultimo, largo))
    def _victoria(self, resumen, ultimo, largo):
        if self.cl["fase"] != "idle":
            self._volver_tras_evento()
            return
        self.cambiar_estado("victoria")
        self.sonido("charge")
        self.vista.sx, self.vista.sy = 1.12, 0.84
        self.tras(450, self._v_smear)
        self.tras(650, self._v_pose)
        self.tras(2300, self._v_risa)
        self.tras(3600, lambda: self._v_fin(resumen, ultimo, largo))
    def _v_smear(self):
        self.vista.sx, self.vista.sy = 0.78, 1.32
        self.sonido("rise")
    def _v_pose(self):
        self.vista.sx = self.vista.sy = 1.0
        c = self.centro_sprite()
        self.fx.agregar(Onda(c.x(), c.y(), r_max=380, dur=0.8))
        self.fx.agregar(LineasVelocidad(c.x(), c.y(), dur=0.9))
        self.fx.agregar(Particulas(c.x(), c.y(), n=26, colores=VIOLETAS + ["#ffffff"], vel=(120, 420), grav=300, dur=1.0))
        self.cutin()
        self.sonido("done")
        self.impacto()
        self.vista.glitch = 0.5
    def _v_risa(self):
        self.vista.glitch = 0.0
        self.anim_sub = "risa"
        self.frame = 0
        self.dibujar()
    def _v_fin(self, resumen, ultimo, largo):
        self.decir(ultimo or "", 14000, maxlen=150, titulo="Misión cumplida, tío.", badge="TERMINADO", tipo="ok", stats=self.cl.get("stats", ""))
        self.velocidad_y = 0
        self.cambiar_estado("caer")
        if largo:
            QTimer.singleShot(5500, lambda: self.mirar_luna(True) if self.cl["fase"] == "idle" else None)
    def reportar_estado(self):
        cl = self.cl
        if cl["fase"] == "espera":
            self.decir("Claude espera tu respuesta, tío. ¡Ve!", 4000)
        elif cl["fase"] == "trabajando":
            self.decir(f"Claude trabaja: {cl['acciones']} acciones. Ahora: {cl['herr_actual'] or 'pensando'}", 5000)
        elif cl["resumen"]:
            self.decir("Último trabajo: " + cl["resumen"], 5000)
        else:
            self.decir("Claude está tranquilo. Yo vigilo.", 3000)
    def teletransportar(self, x, y, despues=None, oculto=False):
        self.cancelar_pendientes()
        self.cambiar_estado("teleport")
        self.velocidad_y = 0
        c0 = self.centro_sprite()
        if oculto:
            self.setWindowOpacity(0.0)
            retardo = 150
        else:
            self.sonido("teleport-out")
            self._tinte(QColor(179, 136, 255, 150))
            self.fx.agregar(Particulas(c0.x(), c0.y(), n=14, colores=VIOLETAS, vel=(80, 300), grav=300, dur=0.7))
            self.tras(300, lambda: self._tp_rendija(c0))
            retardo = 600
        self.tras(retardo, lambda: self._tp_llegada(int(x), int(y)))
        self.tras(retardo + 420, lambda: despues() if despues else self.volver_a_patrullar())
    def _tp_rendija(self, c0):
        self.fx.agregar(Rendija(c0.x(), c0.y(), alto=SPR + 10))
        self._tinte(None)
        self.setWindowOpacity(0.0)
    def _tp_llegada(self, x, y):
        self.move(x, y)
        c1 = self.centro_sprite()
        a = self.area()
        self.setWindowOpacity(1.0)
        self.fx.agregar(Columna(c1.x(), c1.y() + SPR // 2, a.top() - 40))
        self.fx.agregar(Rayo((c1.x(), a.top() - 20), (c1.x(), c1.y() - SPR // 4), grosor=5, dur=0.25, jitter=14))
        self.fx.agregar(Particulas(0, 0, n=16, colores=ROJOS + VIOLETAS, dur=0.55, hacia=lambda: (self.centro_sprite().x(), self.centro_sprite().y())))
        self.sonido("teleport-in")
        self.impacto()
    def mirar_luna(self, completa=False):
        if (self.estado not in LIBRES or self.arrastrando or self.guardado or self.chip_estado or self.cl["fase"] != "idle"):
            return
        self.cancelar_pendientes()
        a = self.area()
        c = self.centro_sprite()
        luna = Luna(a, c.x() - 200, dur=24.0 if completa else 17.0)
        self.luna = luna
        self.fx.agregar(luna)
        self.cambiar_estado("luna")
        self.anim_sub = "luna_mirar"
        self.dir = 1 if luna.pos()[0] > c.x() else -1
        self.dibujar()
        if completa:
            self._luna_completa(luna)
        else:
            self._luna_simple(luna)
    def _luna_anim(self, clave, snd):
        if self.estado != "luna":
            return
        self.anim_sub = clave
        self.frame = 0
        self.dibujar()
        if snd:
            self.sonido(snd)
    def _luna_simple(self, luna):
        self.decir("¿Ves esa luna, tío?", 3000)
        self.tras(3000, lambda: self._luna_anim("luna_alcanzar", "star"))
        self.tras(5000, luna.titilar)
        self.tras(5000, lambda: self.sonido("star"))
        self.tras(6500, lambda: self._luna_anim("luna_mirar", None))
        self.tras(6600, lambda: self.decir("Algún día llegamos hasta allí...", 3500))
        self.tras(10500, self.volver_a_patrullar)
    def _luna_completa(self, luna):
        self.fx.agregar(SecuenciaLuna(self.mano_xy, luna))
        self.sonido("star")
        self.decir("Shhh... mira.", 2200)
        self.tras(1300, lambda: self._luna_anim("luna_alcanzar", None))
        self.tras(1400, lambda: self.decir("¿Y si pudiéramos subir hasta allí?", 2400))
        self.tras(3000, lambda: self._luna_anim("luna_carga", "charge"))
        self.tras(4000, lambda: self._luna_rayo(luna))
        self.tras(4800, luna.titilar)
        self.tras(4800, lambda: self.sonido("star"))
        self.tras(5300, lambda: self.sonido("star"))
        self.tras(6800, lambda: self._luna_anim("luna_mirar", None))
        self.tras(6900, lambda: self.decir("...(suspiro)", 2500))
        self.tras(8500, self.volver_a_patrullar)
    def _luna_rayo(self, luna):
        self._luna_anim("luna_rayo", "rise")
        mx, my = self.mano_xy()
        self.fx.agregar(Rayo(self.mano_xy, luna.pos, color="#ff3b5c", dur=0.6, grosor=8, segmentos=22, jitter=30, fino=True))
        self.fx.agregar(Onda(mx, my, r_max=160, color="#ff5252", dur=0.5))
        self.impacto()
    def _luna_del_dia(self):
        hoy = datetime.date.today().isoformat()
        if self.cfg.get("luna_fecha") == hoy:
            self.timer_luna_dia.stop()
            return
        if (self.estado in LIBRES and not self.arrastrando and not self.guardado and not self.chip_estado and self.estudio_fase != "estudio" and self.cl["fase"] == "idle"):
            self.cfg["luna_fecha"] = hoy
            guardar_config(self.cfg)
            self.timer_luna_dia.stop()
            self.mirar_luna(True)
    def intentar_poseer(self):
        if random.random() < 0.3:
            self.poseer_ventana()
    def poseer_ventana(self):
        if sys.platform != "win32" or not self.cfg.get("poseer", True):
            return
        if self.estado != "en_ventana" or self.ventana_ref is None or self.cl["fase"] != "idle":
            return
        hwnd = self.ventana_ref[0]
        if ctypes.windll.user32.GetForegroundWindow() != hwnd:
            return
        rect = self._rect_ventana(hwnd)
        if rect is None:
            return
        r = QRectF(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
        self.cancelar_pendientes()
        self.cambiar_estado("poseer")
        self._perchar(hwnd, rect[0], rect[1], "poseer")
        self.anim_sub = None
        self.sonido("possess")
        self.decir("¡Me meto dentro!", 1500)
        self.tras(350, lambda: self._poseer_dentro(r))
        self.tras(2900, lambda: self._salir_de_ventana(hwnd))
    def _poseer_dentro(self, r):
        self.fx.agregar(Poseida(r, QCursor.pos, dur=2.4))
        self.setWindowOpacity(0.0)
    def _salir_de_ventana(self, hwnd):
        self.timer_ventana.stop()
        self.ventana_ref = None
        cand = [c for c in self.ventanas_candidatas() if c[0] != hwnd]
        if not cand:
            self.setWindowOpacity(1.0)
            self.velocidad_y = 0
            self.cambiar_estado("caer")
            return
        h2, l, t, r, titulo = random.choice(cand)
        x, y = self._pos_en_ventana(l, t, r)
        self.teletransportar(x, y, despues=lambda: self._aparecer_en_ventana(h2), oculto=True)
        self.decir("¡Sorpresa! Salgo de otra ventana.", 3000)
    def _callado(self):
        return self.arrastrando or self.guardado or bool(self.chip_estado) or self.estado == "dormir_largo"
    def _ocupado(self):
        return (self.estado not in LIBRES or self.arrastrando or self.guardado or bool(self.chip_estado) or self.estudio_fase == "estudio" or self.cl["fase"] != "idle")
    def _clip_procesar(self):
        if self._callado():
            return
        md = QApplication.clipboard().mimeData()
        if md is None or not md.hasText():
            return
        t = md.text().strip()
        if not t or t == self._clip_ult:
            return
        self._clip_ult = t
        if len(t) > 1000:
            self.decir("Vaya testamento has copiado, hermanito.", 4000)
        elif len(t) < 400 and re.search(r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com/(?:watch|shorts|live)|youtu\.be/)\S+", t, re.I):
            self.decir("Tío, ¿me pones ese vídeo?", 4000)
    def _enlazar_musica(self):
        try:
            try:
                import winrt.windows.media.control  # noqa: F401
                print("[Gengar] winrt instalado: detección de música activa.")
            except ImportError:
                print("[Gengar] AVISO: winrt NO instalado. Fallback por ventana.")
            import ia_puente
            r = ia_puente.iniciar_conciencia_musical(self.musica_evento.emit)
            print(f"[Gengar] Música enlazada: {r}")
        except Exception:
            import traceback
            traceback.print_exc()
    def _musica_evento(self, ev, texto):
        print(f"[Gengar] _musica_evento: ev={ev!r}")
        self.musica_activa = (ev != "silencio")
        self._actualizar_globo()
    def _baile_musica(self):
        if not self.musica_activa:
            self.timer_baile.stop()
            self._actualizar_globo()
            return
        self._actualizar_globo()
    def programar_vision(self):
        self.timer_vision.start(random.randint(900000, 1500000))
    def vision_proactiva(self):
        if self._ocupado() or (self.worker is not None and self.worker.isRunning()):
            self.timer_vision.start(120000)
            return
        self.cancelar_pendientes()
        self.cambiar_estado("pensando")
        self.decir("Déjame ver qué haces, tío...", 60000, badge="MIRANDO", tipo="info")
        self._w_vision = WorkerVision()
        self.worker = self._w_vision
        self._w_vision.lista.connect(self._vision_lista)
        self._w_vision.start()
    def _vision_lista(self, texto):
        self.programar_vision()
        self.cancelar_pendientes()
        if not texto or texto.startswith(("Error", "[VISION ERROR]")):
            self.bocadillo.hide()
            self.volver_a_patrullar()
            return
        self.decir(texto, max(5000, len(texto) * 60), maxlen=220, titulo="Gengar te ve", badge="PANTALLA", tipo="info")
        self.tras(5000, self.volver_a_patrullar)
    def iniciar_sueno(self):
        self._sueno = ""
        if self._w_sueno is None or not self._w_sueno.isRunning():
            self._w_sueno = WorkerSueno()
            self._w_sueno.lista.connect(self._sueno_listo)
            self._w_sueno.start()
        self.timer_decir_sueno.start(300000)
    def _sueno_listo(self, t):
        self._sueno = t
    def _decir_sueno(self):
        if self.estado != "dormir_largo" or not self.isVisible() or not self._sueno:
            return
        self.decir(self._sueno, 8000, maxlen=240, titulo="Zzz... (susurrando)", badge="SUEÑO", tipo="info")
    def cancelar_sueno(self):
        self.timer_decir_sueno.stop()
        self._sueno = ""
    def vigilar_sueno(self):
        if self.guardado or self.chip_estado == "dormido":
            return
        ahora = time.time()
        inactivo = ahora - max(self.t_raton_mov, self.t_claude, self.t_actividad)
        if (self.estado in LIBRES and self.cl["fase"] == "idle" and not self.arrastrando and self.estudio_fase is None and inactivo > MIN_SUENO * 60):
            self.cancelar_pendientes()
            self.cambiar_estado("dormir_largo")
            self.decir("Zzz...", 3000)
            self.iniciar_sueno()
        elif self.estado == "dormir_largo" and ahora - self.t_estado > SEG_DISOLVER:
            self.disolver_en_chip()
    def disolver_en_chip(self):
        c = self.centro_sprite()
        self.fx.agregar(Particulas(c.x(), c.y(), n=26, colores=VIOLETAS, vel=(40, 180), grav=-60, dur=1.3))
        self.sonido("teleport-out")
        self.chip_estado = "dormido"
        self.bocadillo.hide()
        self.hide()
        self.chip.mostrar_en(c.x() - 30, self.y() + H - 70, "dormido")
    def despertar(self, msg="¡Eh! ¿Qué pasa?"):
        self.cancelar_sueno()
        if self.chip_estado == "dormido":
            self.chip.ocultar()
            self.chip_estado = None
            self.show()
            self.sonido("teleport-in")
            self.fx.agregar(Particulas(0, 0, n=20, colores=VIOLETAS, dur=0.6, hacia=lambda: (self.centro_sprite().x(), self.centro_sprite().y())))
        self.t_actividad = time.time()
        self.cancelar_pendientes()
        self.volver_a_patrullar()
        if msg:
            self.decir(msg, 2500)
    def alternar_guardado(self):
        if self.guardado:
            self.desguardar()
        else:
            self.guardar()
    def guardar(self):
        if self.chip_estado == "dormido":
            self.chip.ocultar()
            self.chip_estado = None
        self.cancelar_pendientes()
        a = self.area()
        c = self.centro_sprite()
        self.fx.agregar(Particulas(c.x(), c.y(), n=22, colores=VIOLETAS, dur=0.7, hacia=lambda: (a.left() + 42, a.bottom() - 42)))
        self.sonido("teleport-out")
        self.guardado = True
        self.chip_estado = "guardado"
        self.bocadillo.hide()
        self.hide()
        self.chip.mostrar_en(a.left() + 12, a.bottom() - 72, "guardado")
    def desguardar(self, auto=False):
        self.chip.ocultar()
        self.guardado = False
        self.chip_estado = None
        min_x, max_x, suelo = self.limites(SINK_PIE)
        self.move(min_x + 20, suelo)
        self.show()
        self.setWindowOpacity(1.0)
        self.sonido("teleport-in")
        c = self.centro_sprite()
        self.fx.agregar(Onda(c.x(), c.y(), r_max=200, dur=0.5))
        if not auto:
            self.volver_a_patrullar()
            self.decir("¡Ya estoy aquí!", 2500)
    def _clic_chip(self):
        if self.guardado:
            self.desguardar()
        elif self.chip_estado == "dormido":
            self.despertar()
    def set_tamano(self, nombre):
        pie_y, cx = self.y() + H, self.x() + W // 2
        fijar_tamano(TAMANOS.get(nombre, 130))
        self.cfg["tamano"] = nombre
        guardar_config(self.cfg)
        self.setFixedSize(W, H)
        self.vista.setGeometry(0, 0, W, H)
        self.cargar_animaciones()
        self.bocadillo.hide()
        self.quitar_ticker()
        self.move(cx - W // 2, pie_y - H)
        self.dibujar()
    def set_cfg(self, clave, valor):
        self.cfg[clave] = valor
        guardar_config(self.cfg)
        if clave == "sonido":
            self.snd.activo = bool(valor)
    def teletransportar_aleatorio(self):
        if self.guardado or self.chip_estado:
            return
        a = self.area()
        self.teletransportar(random.randint(a.left(), max(a.left() + 1, a.right() - W)), random.randint(a.top() + 40, max(a.top() + 41, a.bottom() - H)), despues=lambda: (setattr(self, "velocidad_y", 0), self.cambiar_estado("caer")))
    def demo(self):
        guion = [
            (0, {"ev": "SessionStart"}),
            (1500, {"ev": "UserPromptSubmit", "prompt": "arregla la paginación de gigs.ts"}),
            (5000, {"ev": "PreToolUse", "herr": "Read", "detalle": "gigs.ts"}),
            (7000, {"ev": "PreToolUse", "herr": "Grep", "detalle": '"paginate"'}),
            (9000, {"ev": "PreToolUse", "herr": "Edit", "detalle": "gigs.ts", "archivo": "src/gigs.ts"}),
            (10000, {"ev": "PostToolUse", "herr": "Edit", "archivo": "src/gigs.ts"}),
            (11000, {"ev": "PreToolUse", "herr": "WebFetch", "detalle": "docs.ejemplo.com/api"}),
            (13000, {"ev": "PreToolUse", "herr": "Task", "detalle": "revisar los tests"}),
            (15000, {"ev": "PreToolUse", "herr": "Bash", "detalle": "npm test"}),
            (16500, {"ev": "PostToolUseFailure", "herr": "Bash", "err_linea": "AssertionError: esperaba 10, recibió 9"}),
            (20500, {"ev": "PreToolUse", "herr": "Bash", "detalle": "rm -rf build"}),
            (21500, {"ev": "Notification", "tipo": "permission_prompt", "msg": "Claude necesita tu permiso para usar Bash"}),
            (30000, {"ev": "PostToolUse", "herr": "Bash"}),
            (32000, {"ev": "Stop", "ultimo": "Listo: arreglé la paginación y los tests pasan."}),
        ]
        for ms, d in guion:
            QTimer.singleShot(ms, lambda d=d: self.evento_claude(d))
    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.t_actividad = time.time()
            self.presionado = True
            self.arrastrando = False
            self.press_global = ev.globalPosition().toPoint()
            self.pos_raton_inicial = self.press_global - self.pos()
            ev.accept()
    def mouseMoveEvent(self, ev):
        if not self.presionado:
            return
        g = ev.globalPosition().toPoint()
        if not self.arrastrando and (g - self.press_global).manhattanLength() > 5:
            self.arrastrando = True
            self.cancelar_pendientes()
            self.timer_ventana.stop()
            self.velocidad_y = 0
            self.cambiar_estado("arrastrado")
            self.decir("¡Eh, suéltame, tío!", 3000)
        if self.arrastrando:
            self.move(g - self.pos_raton_inicial)
            ev.accept()
    def mouseReleaseEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            return
        self.presionado = False
        if self.arrastrando:
            self.arrastrando = False
            rep = None
            if sys.platform == "win32":
                rep = self._repisa_cerca(self.x() + W // 2, self.y() + H - OFFSET_PIE, 28)
            if rep:
                self._caer_en_repisa(rep, soltado=True)
            else:
                self.velocidad_y = 2
                self.cambiar_estado("caer")
                self.decir("¡Uf! Menos mal.", 3000)
        else:
            self._clic(ev.position().y())
        ev.accept()
    def _clic(self, y_local):
        if self.estado in ("bola_fantasma", "humo", "trepar_ir", "trepar_izq", "trepar_der", "cursor", "teleport", "victoria"):
            return
        if self.cl["fase"] != "idle" or (self.cl["resumen"] and time.time() - self.cl.get("t_fin", 0) < 180):
            self.reportar_estado()
            return
        if SPR_Y <= y_local <= SPR_Y + 55:
            self.cancelar_pendientes()
            self.cambiar_estado("caricia")
            self.decir(random.choice(FRASES_CARICIA), 3000)
            self.tras(2500, self.volver_a_patrullar)
        else:
            self.decir("¡Eh, que me haces cosquillas!", 2500)
    def mouseDoubleClickEvent(self, ev):
        self.abrir_chat.emit()

def icono_app():
    ruta = os.path.join(RUTA_IMAGENES, "shime1.png")
    pm = QPixmap(ruta) if os.path.exists(ruta) else QPixmap()
    if pm.isNull():
        pm = QPixmap(32, 32)
        pm.fill(QColor("#6a4c93"))
    return QIcon(pm)

def crear_tray(app, pet, mostrar_chat):
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None
    tray = QSystemTrayIcon(icono_app(), app)
    tray.setToolTip("Gengar")
    menu = QMenu()
    def accion(texto, fn, checkable=False, marcado=False, destino=None):
        a = QAction(texto, destino or menu)
        if checkable:
            a.setCheckable(True)
            a.setChecked(marcado)
            a.toggled.connect(fn)
        else:
            a.triggered.connect(lambda checked=False: fn())
        (destino or menu).addAction(a)
        return a
    def pedir_alarma():
        txt, ok = QInputDialog.getText(None, "Alarma", "Hora (HH:MM) o minutos desde ahora (ej: 15):")
        txt = txt.strip()
        if not ok or not txt:
            return
        try:
            if ":" in txt:
                h, m = map(int, txt.split(":"))
                ahora = datetime.datetime.now()
                objetivo = ahora.replace(hour=h, minute=m, second=0, microsecond=0)
                if objetivo <= ahora:
                    objetivo += datetime.timedelta(days=1)
                segundos = (objetivo - ahora).total_seconds()
                etiqueta = objetivo.strftime("%H:%M")
            else:
                segundos = float(txt.replace(",", ".")) * 60
                etiqueta = f"en {txt} min"
            if segundos <= 0:
                raise ValueError
        except ValueError:
            pet.decir("Eso no parece una hora, tío.")
            return
        pet.programar_alarma(int(segundos * 1000), etiqueta)
    def cambiar_inicio(activo):
        try:
            configurar_inicio(activo)
        except Exception as e:
            pet.decir(f"No pude cambiar el inicio: {e}")
    def instalar():
        try:
            instalar_hooks_claude()
            pet.decir("Hooks instalados. Reinicia tus sesiones de Claude Code.", 6000)
        except Exception as e:
            pet.decir(f"No pude instalar los hooks: {e}", 7000)
    def quitar():
        try:
            quitar_hooks_claude()
            pet.decir("Hooks quitados de Claude Code.", 4000)
        except Exception as e:
            pet.decir(f"No pude quitar los hooks: {e}", 7000)
    accion("Mostrar / ocultar a Gengar", pet.alternar_visible)
    accion("Guardar / sacar (Ctrl+Alt+G)", pet.alternar_guardado)
    accion("Abrir chat", mostrar_chat)
    menu.addSeparator()
    accion("Instalar hooks de Claude Code", instalar)
    accion("Quitar hooks de Claude Code", quitar)
    accion("Demo (sesión de Claude simulada)", pet.demo)
    accion("Sentarse en la ventana de delante al trabajar", lambda v: pet.set_cfg("perchar", v), True, pet.cfg.get("perchar", True))
    menu.addSeparator()
    accion("Teletransportar", pet.teletransportar_aleatorio)
    accion("Mirar la luna", lambda: pet.mirar_luna(True))
    accion("Cabecear con música (auriculares)", lambda: pet.ejecutar("baile_musica"))
    accion("Vagar flotando", lambda v: pet.set_cfg("vagar", v), True, pet.cfg.get("vagar", True))
    accion("Poseer mis ventanas", lambda v: pet.set_cfg("poseer", v), True, pet.cfg.get("poseer", True))
    accion("Sonido", lambda v: pet.set_cfg("sonido", v), True, pet.cfg.get("sonido", True))
    sub = menu.addMenu("Tamaño")
    for nombre in TAMANOS:
        accion(nombre, (lambda n: lambda: pet.set_tamano(n))(nombre), destino=sub)
    menu.addSeparator()
    accion("Modo travesura", lambda v: setattr(pet, "modo_travesura", v), True, False)
    accion("Estudio (25 min / 5 descanso)", pet.iniciar_estudio)
    accion("Parar estudio", pet.parar_estudio)
    accion("Poner alarma...", pedir_alarma)
    accion("Cancelar alarmas", pet.cancelar_alarmas)
    menu.addSeparator()
    if sys.platform == "win32":
        accion("Iniciar con Windows", cambiar_inicio, True, inicio_activo())
        menu.addSeparator()
    accion("Salir", app.quit)
    tray.setContextMenu(menu)
    tray._menu = menu
    tray.activated.connect(lambda r: pet.alternar_visible() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
    pet.tooltip.connect(tray.setToolTip)
    pet.notificar.connect(lambda t, m: tray.showMessage(t, m, QSystemTrayIcon.MessageIcon.Information, 5000))
    tray.show()
    return tray

RUTA_SPRITE = os.path.join(RUTA_IMAGENES, "shime_flotar.png")
if not os.path.exists(RUTA_SPRITE):
    RUTA_SPRITE = os.path.join(RUTA_IMAGENES, "shime3.png")
_I_MORADO_PROFUNDO = QColor(74, 20, 120)
_I_MORADO_NEON = QColor(150, 60, 220)
_I_VERDE_NEON = QColor(57, 255, 120)
_I_ROJO = QColor(215, 50, 70)

class IntroLuna(QWidget):
    def __init__(self, parent=None, diametro=150):
        super().__init__(parent)
        self.diametro = diametro
        self.alfa = 1.0
        self._pulso = 0.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        lado = int(diametro * 3.4)
        self.resize(lado, lado)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
    def _tick(self):
        self._pulso += 0.05
        self.update()
    def paintEvent(self, _):
        p = QPainter(self)
        p.setOpacity(self.alfa)
        p.setRenderHint(QPainter.Antialiasing)
        c = QPointF(self.width() / 2, self.height() / 2)
        r = self.diametro / 2
        pulso = 0.5 + 0.5 * math.sin(self._pulso)
        radio_halo = r * 3.2
        g = QRadialGradient(c, radio_halo)
        g.setColorAt(0.0, QColor(150, 90, 230, int(110 + 40 * pulso)))
        g.setColorAt(0.3, QColor(110, 40, 180, int(70 + 30 * pulso)))
        g.setColorAt(0.6, QColor(57, 255, 120, int(14 + 10 * pulso)))
        g.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(c, radio_halo, radio_halo)
        gl = QRadialGradient(QPointF(c.x() - r * 0.25, c.y() - r * 0.25), r * 1.2)
        gl.setColorAt(0.0, QColor(235, 230, 255))
        gl.setColorAt(0.7, QColor(190, 180, 225))
        gl.setColorAt(1.0, QColor(140, 120, 190))
        p.setBrush(QBrush(gl))
        p.drawEllipse(c, r, r)
        p.setBrush(QColor(120, 105, 165, 110))
        for dx, dy, rr in ((-0.35, -0.2, 0.18), (0.25, 0.1, 0.24), (-0.1, 0.45, 0.14), (0.4, -0.4, 0.1), (-0.5, 0.25, 0.1)):
            p.drawEllipse(QPointF(c.x() + dx * r, c.y() + dy * r), rr * r, rr * r)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(57, 255, 120, 60), 2))
        p.drawEllipse(c, r + 3, r + 3)
        p.end()

class IntroNiebla(QWidget):
    def __init__(self, parent, ancho, alto, cy_luna):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(ancho, alto)
        self._ancho = ancho
        self.alfa = 1.0
        self._t = 0.0
        colores = [(120, 80, 190), (55, 150, 100), (95, 70, 135), (150, 60, 160)]
        self._bancos = []
        for i in range(20):
            capa = i % 4
            if capa == 0:
                y = random.uniform(cy_luna - 60, cy_luna + 40)
            elif capa == 1:
                y = random.uniform(cy_luna + 40, cy_luna + 220)
            elif capa == 2:
                y = random.uniform(alto * 0.4, alto * 0.7)
            else:
                y = random.uniform(alto * 0.8, alto * 1.0)
            self._bancos.append({
                "x": random.uniform(-200, ancho + 200),
                "y": y,
                "r": random.uniform(260, 520),
                "v": random.uniform(6, 20) * random.choice((-1, 1)),
                "a": random.randint(26, 52),
                "c": random.choice(colores),
                "f": random.uniform(0.3, 0.8),
                "ph": random.uniform(0, 6.28),
            })
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
    def _tick(self):
        self._t += 0.04
        for b in self._bancos:
            b["x"] += b["v"] * 0.04
            if b["x"] > self._ancho + b["r"]:
                b["x"] = -b["r"]
            elif b["x"] < -b["r"]:
                b["x"] = self._ancho + b["r"]
        self.update()
    def paintEvent(self, _):
        p = QPainter(self)
        p.setOpacity(self.alfa)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        for b in self._bancos:
            y = b["y"] + 12 * math.sin(self._t * b["f"] + b["ph"])
            a = int(b["a"] * (0.75 + 0.25 * math.sin(self._t * 0.6 + b["ph"])))
            r, g, bl = b["c"]
            grad = QRadialGradient(QPointF(0, 0), b["r"])
            grad.setColorAt(0.0, QColor(r, g, bl, a))
            grad.setColorAt(0.55, QColor(r, g, bl, a // 3))
            grad.setColorAt(1.0, QColor(r, g, bl, 0))
            p.save()
            p.translate(b["x"], y)
            p.scale(1.0, 0.3)
            p.setBrush(QBrush(grad))
            p.drawEllipse(QPointF(0, 0), b["r"], b["r"])
            p.restore()
        p.end()

class IntroOjo(QWidget):
    """Ojo cyberpunk estilo Nmap dibujado por completo con QPainter.

    Linea de tiempo (segundos):
      0.0-0.5   PRIMER INTENTO FALLIDO: abre ~20 %, se traba, tiembla (glitch) y vuelve a cerrarse
      0.5-1.0   pausa con el ojo cerrado
      1.0-2.0   SEGUNDO INTENTO: los parpados se abren lentamente del todo (lluvia binaria de fondo)
                (la esclerotica lleva binarios "pegados" que se mueven/escalan con el ojo y la camara)
      2.6-3.7   dos parpadeos rapidos (200 ms cerrar + 200 ms abrir)
      4.1-8.6   mira DERECHA -> IZQUIERDA -> CENTRO (1.5 s cada paso, camara con paneo y zoom)
      7.7-10.5  Gengar aparece fantasmal dentro de la pupila + particulas cian
      10.5-10.8 cierre rapido de los parpados
      10.8-11.1 fundido a negro total -> emite `terminado` (arranca la grieta al instante)
    """
    terminado = Signal()
    gengar_aparecio = Signal()
    C_CIAN = QColor(60, 225, 255)
    C_VERDE_OSC = QColor(22, 165, 95)
    C_CIAN_OSC = QColor(14, 135, 185)
    T_AB0 = 1.0
    T_AB1 = 2.0
    T_FALLO_SUBE = 0.15
    T_FALLO_FIN = 0.50
    T_FALLO_CIERRA = 0.40
    FALLO_MAX = 0.20
    T_TIEMBLA = (0.15, 0.48)
    T_PARP = (2.6, 3.3)
    T_PARP_DUR = 0.2
    T_MIRA = 4.1
    T_PASO = 1.5
    T_GENGAR_ENTRA = 0.8
    T_GENGAR_FLOTA = 2.0
    T_CIERRE = 0.3
    T_NEGRO = 0.3
    def __init__(self, parent, ancho, alto, pix_gengar):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.ancho = int(ancho)
        self.alto = int(alto)
        self.resize(self.ancho, self.alto)
        self.pix_gengar = pix_gengar
        self._dpr = max(1.0, float(QApplication.primaryScreen().devicePixelRatio()))
        self._cx = self.ancho / 2.0
        self._cy = self.alto / 2.0
        self._a = min(self.ancho * 0.34, self.alto * 0.62)
        self._b = self._a * 0.46
        self._ri = self._b * 0.92
        self._rp0 = self._ri * 0.36
        self._desp_x = self._a * 0.36
        self._desp_y = self._b * 0.10
        self.ojo_abierto = 0.0
        self.pupila_x = 0.0
        self.pupila_y = 0.0
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.zoom = 1.0
        self._ang_iris = 0.0
        self._dilat = 1.0
        self._g_prog = 0.0
        self._g_escala = 0.0
        self._g_alfa = 0.0
        self._g_emitido = False
        self._negro = 0.0
        self._fin = False
        self._t = 0.0
        self._t_prev = 0.0
        self._t0 = None
        self._particulas = []
        self._acum_part = 0.0
        self._lh = 17.0
        self._paso_col = 20.0
        self._f_bin = QFont("Consolas", 12, QFont.Bold)
        self._tiembla = 0.0
        self._jit = (0.0, 0.0)
        self._filas_esc = []
        self.t_s1 = self.T_MIRA
        self.t_s2 = self.t_s1 + self.T_PASO
        self.t_s3 = self.t_s2 + self.T_PASO
        self.t_g0 = self.t_s3 + 0.6
        self.t_cierre = self.t_g0 + self.T_GENGAR_ENTRA + self.T_GENGAR_FLOTA
        self.t_negro = self.t_cierre + self.T_CIERRE
        self.t_fin = self.t_negro + self.T_NEGRO
        self._crear_keyframes()
        self._ruta_max = self._ruta_ojo(1.0)
        self._pm_iris = self._crear_iris_digitos()
        self._tex_scan = self._crear_textura_scan()
        self._crear_binarios_esclera()
        self._cols = []
        self._crear_lluvia()
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.timeout.connect(self._tick)
    @staticmethod
    def _col(c, a):
        q = QColor(c)
        q.setAlpha(int(max(0, min(255, a))))
        return q
    def _crear_keyframes(self):
        E = QEasingCurve
        lin = E(E.Linear)
        io = E(E.InOutSine)
        cub = E(E.InOutCubic)
        out = E(E.OutCubic)
        ine = E(E.InQuad)
        self._c_back = E(E.OutBack)
        d = self.T_PARP_DUR
        s1, s2, s3 = self.t_s1, self.t_s2, self.t_s3
        k = [(0.0, 0.0, lin),
             (self.T_FALLO_SUBE, self.FALLO_MAX, out),
             (self.T_FALLO_CIERRA, self.FALLO_MAX, lin),
             (self.T_FALLO_FIN, 0.0, ine),
             (self.T_AB0, 0.0, lin),
             (self.T_AB1, 1.0, io)]
        for tp in self.T_PARP:
            k += [(tp, 1.0, lin), (tp + d, 0.0, io), (tp + 2.0 * d, 1.0, io)]
        k += [(self.t_cierre, 1.0, lin), (self.t_cierre + self.T_CIERRE, 0.0, ine)]
        self._kf_abierto = k
        self._kf_px = [(0.0, 0.0, lin), (s1, 0.0, lin), (s1 + 0.55, 1.0, cub), (s2, 1.0, lin),
                       (s2 + 0.7, -1.0, cub), (s3, -1.0, lin), (s3 + 0.6, 0.0, cub)]
        self._kf_py = [(0.0, 0.0, lin), (s1, 0.0, lin), (s1 + 0.55, -0.25, cub), (s2, -0.25, lin),
                       (s2 + 0.7, 0.2, cub), (s3, 0.2, lin), (s3 + 0.6, 0.0, cub)]
        self._kf_cx = [(0.0, 0.0, lin), (s1, 0.0, lin), (s1 + 1.1, 0.9, out), (s2, 0.9, lin),
                       (s2 + 1.2, -0.9, out), (s3, -0.9, lin), (s3 + 1.1, 0.0, out)]
        self._kf_zoom = [(0.0, 1.0, lin), (s1, 1.08, io), (s1 + 1.2, 1.28, out), (s2, 1.28, lin),
                         (s2 + 1.2, 1.42, out), (s3, 1.42, lin), (s3 + 1.2, 1.65, out),
                         (self.t_cierre, 1.76, io)]
    @staticmethod
    def _kf(pts, t):
        if t <= pts[0][0]:
            return pts[0][1]
        for (t0, v0, _c0), (t1, v1, c1) in zip(pts, pts[1:]):
            if t <= t1:
                u = (t - t0) / max(1e-6, t1 - t0)
                return v0 + (v1 - v0) * c1.valueForProgress(u)
        return pts[-1][1]
    def _crear_textura_scan(self):
        t = QPixmap(2, 3)
        t.fill(Qt.transparent)
        q = QPainter(t)
        q.fillRect(0, 0, 2, 1, QColor(0, 0, 0, 40))
        q.end()
        return t
    def _pm_columna(self, n):
        lh = self._lh
        w = self._paso_col
        h = n * lh
        dpr = self._dpr
        pm = QPixmap(max(1, int(w * dpr)), max(1, int(h * dpr)))
        pm.setDevicePixelRatio(dpr)
        pm.fill(Qt.transparent)
        q = QPainter(pm)
        q.setRenderHint(QPainter.TextAntialiasing)
        q.setFont(self._f_bin)
        q.setPen(random.choice((self.C_VERDE_OSC, self.C_VERDE_OSC, self.C_CIAN_OSC)))
        for i in range(n - 1):
            q.drawText(QPointF(3.0, i * lh + lh * 0.82), random.choice("01"))
        q.setPen(QColor(170, 255, 225))
        q.drawText(QPointF(3.0, (n - 1) * lh + lh * 0.82), random.choice("01"))
        q.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        g = QLinearGradient(0.0, 0.0, 0.0, h)
        g.setColorAt(0.0, QColor(0, 0, 0, 0))
        g.setColorAt(0.7, QColor(0, 0, 0, 150))
        g.setColorAt(1.0, QColor(0, 0, 0, 255))
        q.fillRect(QRectF(0.0, 0.0, w, h), QBrush(g))
        q.end()
        return pm
    def _crear_lluvia(self):
        x = -0.25 * self.ancho
        while x < 1.25 * self.ancho:
            n = random.randint(12, 34)
            self._cols.append({
                "x": x, "n": n, "h": n * self._lh, "pm": self._pm_columna(n),
                "y": random.uniform(-0.2 * self.alto, 1.2 * self.alto),
                "v": random.uniform(140.0, 380.0), "op": random.uniform(0.35, 0.85),
            })
            x += self._paso_col
    def _crear_iris_digitos(self):
        ss = 2.0
        R = self._ri * ss
        lado = max(16, int(2.0 * R))
        pm = QPixmap(lado, lado)
        pm.fill(Qt.transparent)
        q = QPainter(pm)
        q.setRenderHint(QPainter.Antialiasing)
        q.setRenderHint(QPainter.TextAntialiasing)
        f = QFont("Consolas")
        f.setBold(True)
        f.setPixelSize(max(8, int(R * 0.085)))
        q.setFont(f)
        cw = QFontMetrics(f).horizontalAdvance("0")
        for k, (rf, alfa) in enumerate(((0.60, 150), (0.76, 190), (0.91, 230))):
            rr = R * rf
            n = max(8, int(2.0 * math.pi * rr / (cw * 1.35)))
            for i in range(n):
                q.save()
                q.translate(R, R)
                q.rotate(360.0 * i / n + k * 7.0)
                q.translate(0.0, -rr)
                q.setPen(QColor(150, 235, 255, alfa))
                q.drawText(QPointF(-cw / 2.0, 0.0), random.choice("01"))
                q.restore()
        q.end()
        return pm
    def _crear_binarios_esclera(self):
        f = QFont("Consolas")
        f.setBold(True)
        f.setPixelSize(max(9, int(self._b * 0.075)))
        f.setHintingPreference(QFont.PreferNoHinting)
        fm = QFontMetrics(f)
        self._f_esc = f
        self._lh_esc = float(fm.height())
        cw = float(max(1, fm.horizontalAdvance("0")))
        w = self._a * 2.0 * 1.35
        h = self._b * 2.0 * 1.35
        self._esc_x0 = self._cx - w / 2.0
        self._esc_y0 = self._cy - h / 2.0
        ntok = max(8, int(w / (cw * 2.0)))
        nfil = max(4, int(h / self._lh_esc) + 1)
        cols = (QColor(120, 250, 255), QColor(150, 255, 200), QColor(190, 255, 235))
        self._filas_esc = []
        for _ in range(nfil):
            v = random.uniform(3.0, 14.0) * random.choice((-1, 1))
            self._filas_esc.append({
                "s": "".join(random.choice("01") + " " for _ in range(ntok)),
                "v": v, "acc": random.uniform(0.0, 1.0),
                "alfa": random.randint(120, 225), "col": random.choice(cols),
            })
    def _mover_binarios_esclera(self, dt):
        for r in self._filas_esc:
            r["acc"] += r["v"] * dt
            n = int(r["acc"])
            s = r["s"]
            if n:
                r["acc"] -= n
                k = (2 * n) % len(s)
                s = s[k:] + s[:k]
            if random.random() < 0.18:
                i = random.randrange(len(s) // 2) * 2
                s = s[:i] + random.choice("01") + s[i + 1:]
            r["s"] = s
    def _pintar_binarios_esclera(self, p, ruta):
        p.save()
        p.setClipPath(ruta, Qt.IntersectClip)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(2, 22, 60, 125))
        p.drawPath(ruta)
        p.setFont(self._f_esc)
        t = self._t
        px = self.pupila_x * self._desp_x * 0.55
        py = self.pupila_y * self._desp_y * 0.55
        x = self._esc_x0 + px
        lh = self._lh_esc
        for i, r in enumerate(self._filas_esc):
            parp = 0.82 + 0.18 * math.sin(t * 3.1 + i * 0.7)
            p.setPen(self._col(r["col"], r["alfa"] * parp))
            p.drawText(QPointF(x, self._esc_y0 + py + (i + 1) * lh), r["s"])
        p.restore()
    def _ruta_ojo(self, o):
        cx, cy, a, b = self._cx, self._cy, self._a, self._b
        sup = 1.35 * b * o
        inf = 1.10 * b * o
        r = QPainterPath()
        r.moveTo(cx - a, cy)
        r.cubicTo(cx - a * 0.35, cy - sup, cx + a * 0.35, cy - sup, cx + a, cy)
        r.cubicTo(cx + a * 0.35, cy + inf, cx - a * 0.35, cy + inf, cx - a, cy)
        r.closeSubpath()
        return r
    def _centro_iris(self):
        return (self._cx + self.pupila_x * self._desp_x, self._cy + self.pupila_y * self._desp_y)
    def showEvent(self, e):
        super().showEvent(e)
        if self._t0 is None and not self._fin:
            self._t0 = time.perf_counter()
            self._t_prev = 0.0
            self._timer.start(16)
    def saltar(self):
        self._finalizar()
    def _finalizar(self):
        if self._fin:
            return
        self._fin = True
        self._timer.stop()
        self.terminado.emit()
    def _tick(self):
        if self._t0 is None:
            self._t0 = time.perf_counter()
        t = time.perf_counter() - self._t0
        dt = max(0.001, min(0.05, t - self._t_prev))
        self._t_prev = t
        self._t = t
        o = self._kf(self._kf_abierto, t)
        if self.T_TIEMBLA[0] <= t <= self.T_TIEMBLA[1]:
            self._tiembla = 1.0 if random.random() < 0.75 else 0.35
            if o > 0.01:
                o += random.uniform(-0.06, 0.08) * self._tiembla
            self._jit = (random.uniform(-1.0, 1.0) * 5.0 * self._tiembla,
                         random.uniform(-1.0, 1.0) * 2.0 * self._tiembla)
        else:
            self._tiembla = 0.0
            self._jit = (0.0, 0.0)
        self.ojo_abierto = max(0.0, min(1.0, o))
        self._mover_binarios_esclera(dt)
        self.pupila_x = self._kf(self._kf_px, t)
        self.pupila_y = self._kf(self._kf_py, t)
        self.cam_x = self._kf(self._kf_cx, t) * self._desp_x
        self.cam_y = self.pupila_y * self._desp_y * 0.9
        self.zoom = self._kf(self._kf_zoom, t)
        self._ang_iris += 12.0 * dt
        gp = max(0.0, min(1.0, (t - self.t_g0) / self.T_GENGAR_ENTRA))
        if gp > 0.0 and not self._g_emitido:
            self._g_emitido = True
            self.gengar_aparecio.emit()
        self._g_prog = gp
        self._g_escala = max(0.0, self._c_back.valueForProgress(gp))
        self._g_alfa = 0.3 * min(1.0, gp * 3.0) * (1.0 + 0.12 * math.sin(t * 2.6))
        self._dilat = 1.0 + 0.3 * gp
        for c in self._cols:
            c["y"] += c["v"] * dt
            if c["y"] - c["h"] > self.alto * 1.05:
                c["y"] = random.uniform(0.0, 0.15 * self.alto)
                c["v"] = random.uniform(140.0, 380.0)
                c["pm"] = self._pm_columna(c["n"])
        if gp > 0.0 and t < self.t_cierre:
            self._acum_part += 70.0 * dt
            n = int(self._acum_part)
            self._acum_part -= n
            if n and len(self._particulas) < 140:
                ix, iy = self._centro_iris()
                rp = self._rp0 * self._dilat
                for _ in range(n):
                    ang = random.uniform(0.0, 6.2832)
                    rad = rp * random.uniform(0.95, 1.4)
                    v = random.uniform(15.0, 70.0)
                    self._particulas.append({
                        "x": ix + math.cos(ang) * rad, "y": iy + math.sin(ang) * rad,
                        "vx": math.cos(ang) * v, "vy": math.sin(ang) * v - random.uniform(8.0, 36.0),
                        "life": 1.0, "dur": random.uniform(0.8, 1.6), "r": random.uniform(1.5, 4.2),
                    })
        if self._particulas:
            for q in self._particulas:
                q["x"] += q["vx"] * dt
                q["y"] += q["vy"] * dt
                q["life"] -= dt / q["dur"]
            self._particulas = [q for q in self._particulas if q["life"] > 0.0]
        self._negro = max(0.0, min(1.0, (t - self.t_negro) / self.T_NEGRO))
        self.update()
        if t >= self.t_fin:
            self._finalizar()
    def _transform_camara(self):
        tr = QTransform()
        tr.translate(self._jit[0], self._jit[1])
        tr.translate(self._cx, self._cy)
        tr.scale(self.zoom, self.zoom)
        tr.translate(-(self._cx + self.cam_x), -(self._cy + self.cam_y))
        return tr
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.fillRect(self.rect(), QColor(0, 4, 10))
        p.save()
        p.setTransform(self._transform_camara())
        self._pintar_lluvia(p)
        self._pintar_ojo(p)
        p.restore()
        self._pintar_pantalla(p)
        p.end()
    def _pintar_lluvia(self, p):
        for c in self._cols:
            p.setOpacity(c["op"])
            p.drawPixmap(QPointF(c["x"], c["y"] - c["h"]), c["pm"])
        p.setOpacity(1.0)
    def _pintar_pliegues(self, p, o):
        cx, cy, a, b = self._cx, self._cy, self._a, self._b
        sup = b * (1.9 + 0.5 * o)
        inf = b * 1.35
        arriba = QPainterPath()
        arriba.moveTo(cx - a * 1.04, cy)
        arriba.cubicTo(cx - a * 0.30, cy - sup, cx + a * 0.30, cy - sup, cx + a * 1.04, cy)
        abajo = QPainterPath()
        abajo.moveTo(cx - a * 1.04, cy)
        abajo.cubicTo(cx - a * 0.30, cy + inf, cx + a * 0.30, cy + inf, cx + a * 1.04, cy)
        p.setBrush(Qt.NoBrush)
        for ruta in (arriba, abajo):
            p.setPen(QPen(self._col(self.C_CIAN, 26), 7.0))
            p.drawPath(ruta)
            p.setPen(QPen(self._col(self.C_CIAN, 95), 1.6))
            p.drawPath(ruta)
    def _pintar_ojo(self, p):
        o = self.ojo_abierto
        cx, cy, a, b = self._cx, self._cy, self._a, self._b
        p.setPen(Qt.NoPen)
        ha = 0.25 + 0.75 * o
        gh = QRadialGradient(QPointF(cx, cy), a * 1.2)
        gh.setColorAt(0.0, QColor(20, 120, 230, int(95 * ha)))
        gh.setColorAt(0.55, QColor(10, 70, 170, int(55 * ha)))
        gh.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(gh))
        p.drawEllipse(QPointF(cx, cy), a * 1.2, a * 0.8)
        p.setBrush(QColor(3, 12, 30, 225))
        p.drawPath(self._ruta_max)
        self._pintar_pliegues(p, o)
        ruta = self._ruta_ojo(o)
        ix, iy = self._centro_iris()
        ri = self._ri
        rp = self._rp0 * self._dilat * (1.0 + 0.02 * math.sin(self._t * 3.0))
        p.save()
        p.setClipPath(ruta)
        gs = QRadialGradient(QPointF(cx, cy), a)
        gs.setColorAt(0.0, QColor(150, 235, 255))
        gs.setColorAt(0.5, QColor(40, 170, 240))
        gs.setColorAt(1.0, QColor(6, 70, 150))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(gs))
        p.drawPath(ruta)
        self._pintar_binarios_esclera(p, ruta)
        gi = QRadialGradient(QPointF(ix, iy), ri)
        gi.setColorAt(0.0, QColor(80, 230, 255))
        gi.setColorAt(0.45, QColor(20, 160, 240))
        gi.setColorAt(0.80, QColor(10, 90, 190))
        gi.setColorAt(1.0, QColor(4, 50, 120))
        p.setBrush(QBrush(gi))
        p.drawEllipse(QPointF(ix, iy), ri, ri)
        p.save()
        p.translate(ix, iy)
        p.rotate(self._ang_iris)
        p.drawPixmap(QRectF(-ri, -ri, 2.0 * ri, 2.0 * ri), self._pm_iris, QRectF(self._pm_iris.rect()))
        p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(90, 225, 255, 200), max(2.0, ri * 0.03)))
        p.drawEllipse(QPointF(ix, iy), ri, ri)
        sh = QLinearGradient(QPointF(cx, cy - b), QPointF(cx, cy + b))
        sh.setColorAt(0.0, QColor(0, 20, 60, 175))
        sh.setColorAt(0.35, QColor(0, 20, 60, 0))
        sh.setColorAt(0.75, QColor(0, 20, 60, 0))
        sh.setColorAt(1.0, QColor(0, 20, 60, 140))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(sh))
        p.drawRect(QRectF(cx - a, cy - b * 1.6, 2.0 * a, b * 3.2))
        gp = QRadialGradient(QPointF(ix, iy), rp * 1.35)
        gp.setColorAt(0.0, QColor(0, 0, 0, 255))
        gp.setColorAt(0.74, QColor(0, 0, 0, 255))
        gp.setColorAt(1.0, QColor(0, 10, 30, 0))
        p.setBrush(QBrush(gp))
        p.drawEllipse(QPointF(ix, iy), rp * 1.35, rp * 1.35)
        if self._g_prog > 0.0:
            ga = QRadialGradient(QPointF(ix, iy), rp)
            ga.setColorAt(0.0, QColor(60, 220, 255, int(70 * self._g_prog)))
            ga.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(ga))
            p.drawEllipse(QPointF(ix, iy), rp, rp)
            if self._g_escala > 0.001 and not self.pix_gengar.isNull():
                clip = QPainterPath()
                clip.addEllipse(QPointF(ix, iy), rp, rp)
                p.save()
                p.setClipPath(clip, Qt.IntersectClip)
                pw = float(self.pix_gengar.width())
                ph = float(self.pix_gengar.height())
                lado = rp * 2.0 * 0.95
                if pw >= ph:
                    w, h = lado, lado * ph / max(1.0, pw)
                else:
                    w, h = lado * pw / max(1.0, ph), lado
                w *= self._g_escala
                h *= self._g_escala
                fy = math.sin((self._t - self.t_g0) * 1.8) * rp * 0.10
                p.setOpacity(self._g_alfa)
                p.drawPixmap(QRectF(ix - w / 2.0, iy - h / 2.0 + fy, w, h), self.pix_gengar,
                             QRectF(self.pix_gengar.rect()))
                p.setOpacity(1.0)
                p.restore()
        p.setBrush(QColor(255, 255, 255, 120))
        p.drawEllipse(QPointF(ix - ri * 0.40, iy - ri * 0.42), ri * 0.10, ri * 0.06)
        if self._particulas:
            p.setCompositionMode(QPainter.CompositionMode_Plus)
            for q in self._particulas:
                al = max(0.0, q["life"])
                p.setBrush(self._col(self.C_CIAN, 55.0 * al))
                p.drawEllipse(QPointF(q["x"], q["y"]), q["r"] * 3.2, q["r"] * 3.2)
                p.setBrush(QColor(190, 250, 255, int(230 * al)))
                p.drawEllipse(QPointF(q["x"], q["y"]), q["r"], q["r"])
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        p.restore()
        p.setBrush(Qt.NoBrush)
        if self._tiembla > 0.0:
            p.setCompositionMode(QPainter.CompositionMode_Plus)
            for col, d in ((QColor(255, 45, 90), -4.0), (QColor(57, 255, 136), 4.0)):
                p.setPen(QPen(self._col(col, 150.0 * self._tiembla), 2.0))
                p.save()
                p.translate(d, 0.0)
                p.drawPath(ruta)
                p.restore()
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        for grosor, al in ((16.0, 28.0), (8.0, 70.0), (3.0, 235.0)):
            p.setPen(QPen(self._col(self.C_CIAN, al), grosor, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawPath(ruta)
    def _pintar_pantalla(self, p):
        w = float(self.width())
        h = float(self.height())
        p.fillRect(self.rect(), QBrush(self._tex_scan))
        y = (self._t * 180.0) % (h + 80.0) - 40.0
        p.fillRect(QRectF(0.0, y, w, 3.0), QColor(60, 225, 255, 28))
        gv = QRadialGradient(QPointF(w / 2.0, h / 2.0), max(w, h) * 0.72)
        gv.setColorAt(0.0, QColor(0, 0, 0, 0))
        gv.setColorAt(0.6, QColor(0, 0, 0, 60))
        gv.setColorAt(1.0, QColor(0, 0, 0, 210))
        p.fillRect(self.rect(), QBrush(gv))
        if self._negro > 0.0:
            p.fillRect(self.rect(), QColor(0, 0, 0, int(255 * self._negro)))


class IntroBocadillo(QWidget):
    def __init__(self, parent, texto):
        super().__init__(parent)
        self.texto = texto
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(280, 90)
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cuerpo = QRectF(4, 4, self.width() - 8, self.height() - 26)
        path = QPainterPath()
        path.addRoundedRect(cuerpo, 14, 14)
        cx = self.width() / 2
        cola = QPainterPath()
        cola.moveTo(cx - 12, cuerpo.bottom())
        cola.lineTo(cx, self.height() - 3)
        cola.lineTo(cx + 12, cuerpo.bottom())
        cola.closeSubpath()
        path = path.united(cola)
        p.setBrush(QColor(14, 4, 24, 240))
        p.setPen(QPen(_I_MORADO_NEON, 2))
        p.drawPath(path)
        p.setPen(QPen(QColor(57, 255, 120, 80), 1))
        p.drawRoundedRect(cuerpo.adjusted(5, 5, -5, -5), 10, 10)
        p.setFont(QFont("Consolas", 16, QFont.Bold))
        p.setPen(_I_VERDE_NEON)
        p.drawText(cuerpo.toRect(), Qt.AlignCenter, self.texto)
        p.end()

N_MORADO = QColor("#7c4dff")
N_VERDE = QColor("#39ff88")
N_ROJO = QColor("#ff2d5a")
N_FONDO = QColor("#0e0a17")
def _localizar_cara():
    for r in (RUTA_CARA, os.path.join(BASE, "cara_gengar.jpg"), os.path.join(BASE, "gengar_face.jpg"),
              os.path.join(RUTA_IMAGENES, "gengar_face.jpg"), os.path.join(BASE, "gengar_img", "cara_gengar.jpg")):
        if os.path.exists(r):
            return r
    return None

class IntroAnimacion(QWidget):
    intro_terminada = Signal()
    C_ROJO = QColor("#ff2d5a")
    C_VERDE = QColor("#39ff88")
    C_VIOLETA = QColor("#7c4dff")
    C_MORADO = QColor("#7c4dff")
    _COLS = (C_ROJO, C_VERDE, C_VIOLETA)
    _COLS_N = (C_VERDE, C_VERDE, C_VIOLETA, C_VIOLETA, C_ROJO)
    def __init__(self, sonido=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.ArrowCursor)
        pantalla = QApplication.primaryScreen().geometry()
        self.ancho = pantalla.width()
        self.alto = pantalla.height()
        self.setGeometry(pantalla)
        self.snd = sonido if sonido is not None else Sonido()
        for n in ("alert", "teleport-in", "teleport-out", "land"):
            try:
                ruta = self.snd._ruta(n)
                if QSoundEffect is not None and n not in self.snd.efectos:
                    ef = QSoundEffect()
                    ef.setSource(QUrl.fromLocalFile(ruta))
                    ef.setVolume(0.35)
                    self.snd.efectos[n] = ef
            except Exception:
                pass
        self._fase = 1
        self._cerrando = False
        self._alfa_fondo = 1.0
        self._distorsion_progreso = 0.0
        self._glitch = 0.0
        self._t = 0.0
        self._t_prev = 0.0
        self._t0 = time.perf_counter()
        self._frame_count = 0
        self._humo = []
        self._barras = []
        self._ruido = []
        self._particulas = []
        self._bandas = [(0.0, 1.0, 0.0)]
        self._sprite_jit = (0.0, 0.0)
        self._aber = 0.0
        self._portal = 0.0
        self._vent = 0.0
        self._reveal = 0.0
        self._flash = 0.0
        self._tb0 = 0.0
        self._tb = 0.0
        self._boot_on = False
        self._lluvia_rate = 0.0
        self._lluvia = []
        self._fx = []
        self._tears = []
        self._bandas_v = [(0.0, 1.0, 0.0)]
        self._cy_vent = self.alto * 0.47
        self._destino = QPointF(self.ancho / 2.0, self.alto * 0.85)
        self._timers = []
        self._anim_grieta = None
        self._anim_glitch = None
        self._anim_aber = None
        self._anim_portal = None
        self._anim_vent = None
        self._anim_reveal = None
        self._anim_flash = None
        self._desliz = 0.0
        self._anim_desliz = None
        self._term_alfa = 1.0
        self._anim_term = None
        self._rotura = 0.0
        self._anim_rotura = None
        self._pm_rotura = None
        self._pm_rot_r = None
        self._pm_rot_g = None
        self._franjas = []
        self._frag = []
        self._esc_final = 0.62
        self._anim_fondo = None
        self._regenerar_grieta()
        self.sprite = QLabel(self)
        self.sprite.setAttribute(Qt.WA_TranslucentBackground)
        self.sprite.setStyleSheet("background: transparent;")
        pix = QPixmap(RUTA_SPRITE)
        if pix.isNull():
            pix = QPixmap(160, 160)
            pix.fill(Qt.transparent)
            q = QPainter(pix)
            q.setRenderHint(QPainter.Antialiasing)
            q.setBrush(_I_MORADO_PROFUNDO)
            q.setPen(QPen(_I_MORADO_NEON, 3))
            q.drawEllipse(10, 10, 140, 140)
            q.end()
        self.sprite.setPixmap(pix)
        self.sprite.resize(pix.size())
        self.sprite.move((self.ancho - pix.width()) // 2, -200)
        self.sprite.hide()
        self._pix_sprite = pix
        self._preparar_ventana()
        self.ojo = IntroOjo(self, self.ancho, self.alto, self._pix_sprite)
        self.ojo.move(0, 0)
        self.ojo.terminado.connect(self._al_cerrar_ojo)
        self.ojo.gengar_aparecio.connect(lambda: self.snd.reproducir("teleport-in"))
        self.ojo.show()
        self._timer_fx = QTimer(self)
        self._timer_fx.timeout.connect(self._tick_fx)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()
    def _preparar_ventana(self):
        ruta = _localizar_cara()
        pm = QPixmap(ruta) if ruta else QPixmap()
        if pm.isNull():
            pm = QPixmap(480, 744)
            pm.fill(N_FONDO)
            q = QPainter(pm)
            dibujar_cara_geo(q, QRectF(0, 0, 480, 744))
            q.end()
        dpr = max(1.0, float(QApplication.primaryScreen().devicePixelRatio()))
        self._dpr = dpr
        asp = pm.width() / float(max(1, pm.height()))
        ih = min(self.alto * 0.52, 560.0)
        iw = ih * asp
        tope = self.ancho * 0.42
        if iw > tope:
            iw = tope
            ih = iw / asp
        cara = pm.scaled(max(1, int(iw * dpr)), max(1, int(ih * dpr)), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        cara.setDevicePixelRatio(dpr)
        self._cara = cara
        self._iw = int(round(cara.width() / dpr))
        self._ih = int(round(cara.height() / dpr))
        self._cara_r = self._canal(cara, QColor(255, 0, 0))
        self._cara_g = self._canal(cara, QColor(0, 255, 0))
        self._cara_b = self._canal(cara, QColor(0, 0, 255))
        self._pad = 16
        self._barra = 34
        self._pie = 48
        self._wv = self._iw + 2 * self._pad
        self._hv = self._barra + 8 + self._ih + 10 + self._pie
        self._tex_scan = self._textura_scan(3, 70)
        self._tex_scan_pant = self._textura_scan(4, 26)
        self._f_term = QFont("Consolas", 12, QFont.Bold)
        self._f_term_p = QFont("Consolas", 10, QFont.Bold)
        self._f_tit = QFont("Consolas", 10, QFont.Bold)
        self._f_gr = QFont("Consolas", 24, QFont.Bold)
        self._f_bin = QFont("Consolas", 12, QFont.Bold)
        self._mx = [{"x": random.uniform(0.05, 0.95), "v": random.uniform(60.0, 170.0), "o": random.uniform(0.0, 600.0),
                     "s": "".join(random.choice("01") for _ in range(18))} for _ in range(10)]
        self._lineas = [
            ("L", 0.06, "> SYSTEM BOOT...", 0.10, N_VERDE, False),
            ("L", 0.20, "> KERNEL.GHOST v4.1 [OK]", 0.55, N_MORADO, False),
            ("L", 0.34, "> MOUNTING /dev/spectre [OK]", 0.95, N_VERDE, False),
            ("L", 0.48, "> BYPASSING FIREWALL...", 1.30, N_ROJO, False),
            ("L", 0.62, "> ECTOPLASM CORE: ONLINE", 1.70, N_VERDE, False),
            ("R", 0.10, "> GENGAR.EXE LOADED", 1.00, N_VERDE, False),
            ("R", 0.26, "> NEURAL LINK: 100%", 1.40, N_MORADO, False),
            ("R", 0.42, "> GLITCH ENGINE: ARMED", 1.80, N_ROJO, False),
            ("R", 0.58, "> SPECTRAL SYNC: OK", 2.10, N_VERDE, False),
            ("B", 0.0, "> WELCOME, RUBEN", 2.00, N_VERDE, True),
        ]
    @staticmethod
    def _col(c, a):
        q = QColor(c)
        q.setAlpha(int(max(0, min(255, a))))
        return q
    @staticmethod
    def _tintar(pix, color):
        out = QPixmap(pix.size())
        out.fill(Qt.transparent)
        q = QPainter(out)
        q.drawPixmap(0, 0, pix)
        q.setCompositionMode(QPainter.CompositionMode_SourceIn)
        q.fillRect(out.rect(), color)
        q.end()
        return out
    @staticmethod
    def _canal(pix, color):
        out = pix.copy()
        out.setDevicePixelRatio(pix.devicePixelRatio())
        q = QPainter(out)
        q.setCompositionMode(QPainter.CompositionMode_Multiply)
        q.fillRect(out.rect(), color)
        q.end()
        return out
    @staticmethod
    def _textura_scan(paso, alfa):
        t = QPixmap(2, paso)
        t.fill(Qt.transparent)
        q = QPainter(t)
        q.fillRect(0, 0, 2, 1, QColor(0, 0, 0, alfa))
        q.end()
        return t
    @staticmethod
    def _saludo_hora():
        h = datetime.datetime.now().hour
        if 6 <= h < 13: return "¡Buenos días, tío!"
        if 13 <= h < 21: return "¡Buenas tardes, tío!"
        if h >= 21 or h < 2: return "¡Buenas noches, tío!"
        return "¿Aún despierto, tío?"
    def _anim(self, nombre, ini, fin, dur, curva, slot, al_fin=None):
        previa = getattr(self, nombre, None)
        if previa is not None:
            previa.stop()
        a = QVariantAnimation(self)
        a.setStartValue(float(ini))
        a.setEndValue(float(fin))
        a.setDuration(int(dur))
        a.setEasingCurve(curva)
        a.valueChanged.connect(slot)
        if al_fin is not None:
            a.finished.connect(al_fin)
        setattr(self, nombre, a)
        a.start()
        return a
    def _tras(self, ms, fn):
        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(fn)
        t.start(int(ms))
        self._timers.append(t)
        return t
    def _regenerar_grieta(self):
        n = 36
        self._g_l = [random.random() for _ in range(n + 1)]
        self._g_r = [random.random() for _ in range(n + 1)]
        w = 0.0
        wand = []
        for _ in range(n + 1):
            w = w * 0.9 + random.uniform(-10.0, 10.0)
            wand.append(w)
        self._g_wander = wand
        self._g_jit_l = [0.0] * (n + 1)
        self._g_jit_r = [0.0] * (n + 1)
    def _regenerar_glitch(self):
        g = max(self._glitch, self._aber)
        ap = self._distorsion_progreso
        barras = []
        for _ in range(int(3 + 15 * g)):
            larga = random.random() < 0.3
            barras.append({
                "dx": random.uniform(-90.0, 90.0),
                "y": random.uniform(0.08, 0.92) * self.alto,
                "w": random.uniform(0.25, 0.7) * self.ancho if larga else random.uniform(60.0, 440.0),
                "h": random.uniform(1.0, 2.5) if larga else random.uniform(3.0, 26.0),
                "c": random.choice(self._COLS),
                "a": random.randint(90, 220),
                "ph": random.uniform(0.0, 6.283),
                "sp": random.random() < 0.45,
            })
        self._barras = barras
        self._ruido = [(random.gauss(0.0, 120.0 + 120.0 * ap), random.gauss(0.0, self.alto * 0.2), random.choice((2, 2, 3, 4, 6)), random.choice((1, 1, 2, 4)), random.randrange(3)) for _ in range(int(30 + 190 * g))]
        lim = [0.0] + sorted(random.uniform(0.05, 0.95) for _ in range(6)) + [1.0]
        self._bandas = [(lim[i], lim[i + 1], random.uniform(-30.0, 30.0) if random.random() < 0.45 else 0.0) for i in range(len(lim) - 1)]
        limv = [0.0] + sorted(random.uniform(0.03, 0.97) for _ in range(9)) + [1.0]
        self._bandas_v = [(limv[i], limv[i + 1], random.uniform(-26.0, 26.0) if random.random() < 0.5 else 0.0) for i in range(len(limv) - 1)]
        self._tears = [(random.uniform(0.0, self.alto), random.uniform(3.0, 10.0 + 40.0 * g), random.uniform(-160.0, 160.0),
                        random.uniform(0.0, self.ancho * 0.5), random.uniform(self.ancho * 0.2, self.ancho * 0.7)) for _ in range(int(4 + 12 * g))]
        self._sprite_jit = (random.uniform(-9.0, 9.0), random.uniform(-3.5, 3.5))
        self._g_jit_l = [random.uniform(-1.0, 1.0) for _ in self._g_jit_l]
        self._g_jit_r = [random.uniform(-1.0, 1.0) for _ in self._g_jit_r]
    def _soltar_humo(self, x, y, n, ancho, subir):
        for _ in range(n):
            self._humo.append({
                "x": x + random.uniform(-ancho, ancho),
                "y": y + random.uniform(-14.0, 14.0),
                "r0": random.uniform(14.0, 26.0),
                "r1": random.uniform(55.0, 110.0),
                "vx": random.uniform(-40.0, 40.0),
                "vy": random.uniform(-120.0, -40.0) if subir else random.uniform(-30.0, 8.0),
                "t0": self._t + random.uniform(0.0, 0.25),
                "dur": random.uniform(0.9, 1.6),
                "a": random.uniform(70.0, 140.0),
                "c": QColor(random.choice(VIOLETAS)),
            })
    def _lanzar_onda(self, x, y, rmax, color, dur, grosor):
        self._fx.append(Onda(x, y, r_max=rmax, color=color, dur=dur, grosor=grosor))
    def _actualizar_lluvia(self, dt):
        if self._lluvia_rate > 0.0 and len(self._lluvia) < 260:
            n = self._lluvia_rate * dt * 30.0
            k = int(n) + (1 if random.random() < n - int(n) else 0)
            x0 = self.ancho / 2.0 - self._wv / 2.0
            top = self._cy_vent - self._hv / 2.0
            for _ in range(k):
                self._lluvia.append({
                    "x": x0 + random.uniform(-10.0, self._wv + 10.0),
                    "y": top + random.uniform(40.0, self._hv),
                    "vy": random.uniform(160.0, 460.0), "life": 1.0, "dc": random.uniform(0.3, 0.65),
                    "ch": random.choice("01"),
                    "c": random.choice((N_VERDE, N_VERDE, N_VERDE, N_MORADO, N_MORADO, N_ROJO)),
                })
        if self._lluvia:
            for q in self._lluvia:
                q["vy"] += 380.0 * dt
                q["y"] += q["vy"] * dt
                q["life"] -= q["dc"] * dt
            self._lluvia = [q for q in self._lluvia if q["life"] > 0.0 and q["y"] < self.alto + 20.0]
    def _pulso_glitch(self):
        self._anim("_anim_glitch", 0.7, 0.12, 260, QEasingCurve.OutQuad, self._set_glitch)
        self._anim("_anim_aber", 0.4, 0.0, 300, QEasingCurve.OutQuad, self._set_aber)
    def _tick_fx(self):
        self._t = time.perf_counter() - self._t0
        dt = max(0.001, min(0.08, self._t - self._t_prev))
        self._t_prev = self._t
        self._frame_count += 1
        if self._boot_on:
            self._tb = self._t - self._tb0
        if max(self._glitch, self._aber) > 0.01 and self._frame_count % 2 == 0:
            self._regenerar_glitch()
        if self._fase in (3, 4, 5) and self._distorsion_progreso > 0.1:
            if random.random() < 0.4:
                lado = random.choice([-1, 1])
                self._particulas.append({
                    "x": self.ancho / 2 + lado * random.uniform(10, 60),
                    "y": random.uniform(self.alto * 0.2, self.alto * 0.8),
                    "vx": random.uniform(-30, 30),
                    "vy": random.uniform(-80, -20),
                    "life": 1.0,
                    "color": random.choice(self._COLS)
                })
        for pt in self._particulas:
            pt["x"] += pt["vx"] * 0.03
            pt["y"] += pt["vy"] * 0.03
            pt["life"] -= 0.02
        self._particulas = [pt for pt in self._particulas if pt["life"] > 0]
        if self._humo:
            self._humo = [h for h in self._humo if self._t - h["t0"] < h["dur"]]
        if ((self._fase == 6 and self._boot_on and self._tb > 2.5) or self._fase == 8) and random.random() < 0.015:
            self._pulso_glitch()
        self._actualizar_lluvia(dt)
        self._actualizar_fragmentos(dt)
        if self._fx:
            for f in self._fx:
                f.paso(dt)
            self._fx = [f for f in self._fx if f.vivo]
        if self._fase == 8:
            self.update(self._rect_ventana(60))
        else:
            self.update()
    def _set_distorsion(self, v):
        self._distorsion_progreso = float(v)
        self.update()
    def _set_glitch(self, v):
        self._glitch = float(v)
        self.update()
    def _set_fondo(self, v):
        self._alfa_fondo = float(v)
        self.update()
    def _set_aber(self, v):
        self._aber = float(v)
        self.update()
    def _set_portal(self, v):
        self._portal = float(v)
        self.update()
    def _set_vent(self, v):
        self._vent = float(v)
        self.update()
    def _set_reveal(self, v):
        self._reveal = float(v)
        self.update()
    def _set_flash(self, v):
        self._flash = float(v)
        self.update()
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            if self._fase == 1:
                self.ojo.saltar()
                return
            if self._fase == 8:
                self._romper_ventana()
                return
        super().keyPressEvent(e)
    def mousePressEvent(self, e):
        if self._fase == 8 and e.button() == Qt.LeftButton and self._rect_ventana(10).contains(e.position().toPoint()):
            self._romper_ventana()
            return
        super().mousePressEvent(e)
    def _al_cerrar_ojo(self):
        if self._fase != 1:
            return
        self.ojo.hide()
        self.ojo.deleteLater()
        self._iniciar_distorsion()
    def _iniciar_distorsion(self):
        self._fase = 3
        self._t0 = time.perf_counter()
        self._t = 0.0
        self._t_prev = 0.0
        self._timer_fx.start(33)
        self._anim("_anim_grieta", 0.0, 1.0, 1100, QEasingCurve.OutCubic, self._set_distorsion)
        self._anim("_anim_glitch", 0.0, 1.0, 900, QEasingCurve.InQuad, self._set_glitch)
        self._tras(850, self._emerger_ventana)
    def _emerger_ventana(self):
        self._fase = 5
        self.snd.reproducir("teleport-out")
        self._cy_vent = self.alto * 0.47
        self._anim("_anim_glitch", self._glitch, 1.0, 260, QEasingCurve.OutQuad, self._set_glitch)
        self._anim("_anim_aber", 0.0, 1.0, 320, QEasingCurve.OutQuad, self._set_aber)
        self._anim("_anim_portal", 0.0, 1.0, 900, QEasingCurve.OutCubic, self._set_portal)
        self._tras(750, self._materializar_ventana)
    def _materializar_ventana(self):
        self.snd.reproducir("teleport-in")
        self._anim("_anim_vent", 0.0, 1.0, 1000, QEasingCurve.Linear, self._set_vent)
        self._anim("_anim_aber", max(self._aber, 1.0), 0.0, 1600, QEasingCurve.OutQuad, self._set_aber)
        self._anim("_anim_glitch", 1.0, 0.3, 1200, QEasingCurve.OutQuad, self._set_glitch)
        self._anim("_anim_flash", 1.0, 0.0, 450, QEasingCurve.OutQuad, self._set_flash)
        self._lluvia_rate = 3.0
        rm = max(self.ancho, self.alto) * 0.5
        for i, (r, c, gr) in enumerate(((rm, "#7c4dff", 9), (rm * 0.8, "#39ff88", 6), (rm * 0.6, "#ff2d5a", 4))):
            self._tras(i * 170, lambda r=r, c=c, gr=gr: self._lanzar_onda(self.ancho / 2.0, self._cy_vent, r, c, 0.95, gr))
        self._tras(60, lambda: self.snd.reproducir("land"))
        self._tras(500, self._colapsar_portal)
        self._tras(1000, self._iniciar_boot)
    def _colapsar_portal(self):
        self._anim("_anim_portal", self._portal, 0.0, 900, QEasingCurve.InCubic, self._set_portal)
        self._anim("_anim_grieta", self._distorsion_progreso, 0.0, 1100, QEasingCurve.InCubic, self._set_distorsion)
    def _iniciar_boot(self):
        self._fase = 6
        self._tb0 = self._t
        self._tb = 0.0
        self._boot_on = True
        self._anim("_anim_reveal", 0.0, 1.0, 1500, QEasingCurve.InOutSine, self._set_reveal)
        self._anim("_anim_glitch", self._glitch, 0.12, 900, QEasingCurve.OutQuad, self._set_glitch)
        self._lluvia_rate = 1.4
        self._tras(3400, self._deslizar_a_borde)
    def _set_term(self, v):
        self._term_alfa = float(v)
        self.update()
    def _set_desliz(self, v):
        self._desliz = float(v)
        self.update()
    def _set_rotura(self, v):
        self._rotura = float(v)
        self.update()
    def _rect_ventana(self, pad=0):
        w = self._wv * self._esc_final + 2.0 * pad
        h = self._hv * self._esc_final + 2.0 * pad
        return QRect(int(self._destino.x() - w / 2.0), int(self._destino.y() - h / 2.0), int(w), int(h))
    def _deslizar_a_borde(self):
        if self._fase >= 7:
            return
        self._fase = 7
        self._lluvia_rate = 0.0
        self.snd.reproducir("teleport-out")
        wf = self._wv * self._esc_final
        self._destino = QPointF(self.ancho - 28.0 - wf / 2.0, self.alto * 0.5)
        self.sprite.move(int(self._destino.x() - self.sprite.width() / 2.0), 0)
        self._pulso_glitch()
        self._anim("_anim_term", 1.0, 0.0, 350, QEasingCurve.OutQuad, self._set_term)
        self._anim("_anim_fondo", self._alfa_fondo, 0.0, 1000, QEasingCurve.InOutQuad, self._set_fondo)
        self._anim("_anim_desliz", 0.0, 1.0, 1000, QEasingCurve.InOutCubic, self._set_desliz, self._al_llegar_borde)
    def _al_llegar_borde(self):
        self._fase = 8
        self._desliz = 1.0
        self._alfa_fondo = 0.0
        self._boot_on = False
        self.setMask(QRegion(self._rect_ventana(46)))
        self.setCursor(Qt.PointingHandCursor)
        self.snd.reproducir("land")
        self.update()
    def _tinte_pm(self, pm, color):
        out = pm.copy()
        out.setDevicePixelRatio(self._dpr)
        q = QPainter(out)
        q.setCompositionMode(QPainter.CompositionMode_SourceIn)
        q.fillRect(QRectF(0.0, 0.0, out.width() / self._dpr, out.height() / self._dpr), color)
        q.end()
        return out
    def _renderizar_ventana(self):
        m = 16.0
        dpr = self._dpr
        pm = QPixmap(int((self._wv + 2.0 * m) * dpr) + 1, int((self._hv + 2.0 * m) * dpr) + 1)
        pm.setDevicePixelRatio(dpr)
        pm.fill(Qt.transparent)
        q = QPainter(pm)
        q.setRenderHint(QPainter.Antialiasing)
        q.setRenderHint(QPainter.TextAntialiasing)
        q.translate(m, m)
        self._dibujar_ventana(q, float(self._wv), float(self._hv))
        q.end()
        return pm
    def _romper_ventana(self):
        if self._fase != 8:
            return
        self._fase = 9
        self.clearMask()
        self.setCursor(Qt.ArrowCursor)
        self.snd.reproducir("teleport-out")
        px = self._destino.x()
        py = self._destino.y() + 6.0 * math.sin(self._t * 1.9)
        self._pm_rotura = self._renderizar_ventana()
        self._pm_rot_r = self._tinte_pm(self._pm_rotura, N_ROJO)
        self._pm_rot_g = self._tinte_pm(self._pm_rotura, N_VERDE)
        cortes = [0.0] + sorted(random.uniform(0.04, 0.96) for _ in range(9)) + [1.0]
        self._franjas = [(cortes[i], cortes[i + 1], random.uniform(-1.0, 1.0) if random.random() < 0.7 else 0.0,
                          random.uniform(-1.0, 1.0), random.random()) for i in range(len(cortes) - 1)]
        w = self._wv * self._esc_final
        h = self._hv * self._esc_final
        for _ in range(110):
            self._frag.append({
                "x": px + random.uniform(-w / 2.0, w / 2.0), "y": py + random.uniform(-h / 2.0, h / 2.0),
                "vx": random.uniform(-380.0, 380.0), "vy": random.uniform(-320.0, 120.0),
                "ch": random.choice("01"), "c": random.choice(self._COLS_N),
                "life": 1.0, "dur": random.uniform(0.6, 1.2),
            })
        self._lanzar_onda(px, py, 280.0, "#39ff88", 0.7, 6)
        self._soltar_humo(px, py, 12, w * 0.4, True)
        self._anim("_anim_glitch", 1.0, 0.0, 850, QEasingCurve.OutQuad, self._set_glitch)
        self._anim("_anim_aber", 1.0, 0.0, 850, QEasingCurve.OutQuad, self._set_aber)
        self._anim("_anim_rotura", 0.0, 1.0, 850, QEasingCurve.Linear, self._set_rotura, self._terminar)
    def _actualizar_fragmentos(self, dt):
        if not self._frag:
            return
        for q in self._frag:
            q["x"] += q["vx"] * dt
            q["y"] += q["vy"] * dt
            q["vy"] += 240.0 * dt
            q["life"] -= dt / q["dur"]
        self._frag = [q for q in self._frag if q["life"] > 0.0]
    def _pintar_fragmentos(self, p):
        if not self._frag:
            return
        p.setFont(self._f_bin)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for q in self._frag:
            p.setPen(self._col(q["c"], 255.0 * q["life"]))
            p.drawText(QPointF(q["x"], q["y"]), q["ch"])
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    def _pintar_rotura(self, p, px, py, esc):
        pm = self._pm_rotura
        if pm is None:
            return
        r = self._rotura
        m = 16.0
        W = float(self._wv) + 2.0 * m
        H = float(self._hv) + 2.0 * m
        dpr = self._dpr
        p.save()
        p.translate(px, py)
        p.scale(esc, esc)
        p.translate(-W / 2.0, -H / 2.0)
        for f0, f1, dx, dy, st in self._franjas:
            rr = max(0.0, min(1.0, (r - 0.30 * st) / 0.70))
            y0 = f0 * H
            h = (f1 - f0) * H
            if h <= 0.0:
                continue
            src_r = QRectF(0.0, y0 * dpr, W * dpr, h * dpr)
            ox = dx * rr * 300.0 + (random.uniform(-5.0, 5.0) * (1.0 - rr) if dx else 0.0)
            oy = y0 + dy * rr * 50.0
            al = max(0.0, 1.0 - rr ** 1.4)
            sep = 6.0 + 26.0 * rr
            p.setCompositionMode(QPainter.CompositionMode_Plus)
            p.setOpacity(al * 0.8)
            p.drawPixmap(QRectF(ox - sep, oy, W, h), self._pm_rot_r, src_r)
            p.drawPixmap(QRectF(ox + sep, oy, W, h), self._pm_rot_g, src_r)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.setOpacity(al * (1.0 - 0.5 * rr))
            p.drawPixmap(QRectF(ox, oy, W, h), pm, src_r)
        p.restore()
    def _terminar(self):
        if self._cerrando:
            return
        self._cerrando = True
        for t in self._timers:
            t.stop()
        self._timer_fx.stop()
        self.close()
        self.intro_terminada.emit()
    def _poligono_grieta(self, dx=0.0, dy=0.0, esc=1.0):
        ap = self._distorsion_progreso
        n = len(self._g_l) - 1
        cx = self.ancho / 2.0
        cy = self.alto / 2.0
        largo = self.alto * (0.78 + 0.24 * self._portal) * min(1.0, ap * 1.3)
        semi = 64.0 * (ap ** 0.85) * esc * (1.0 + 3.0 * self._portal)
        top = cy - largo / 2.0
        izq = []
        der = []
        for i in range(n + 1):
            u = i / n
            y = top + u * largo + dy
            env = math.sin(math.pi * u) ** 0.75
            wand = self._g_wander[i] * env * ap
            hl = semi * env * (0.55 + 0.9 * self._g_l[i]) + self._g_jit_l[i] * 5.0 * self._glitch
            hr = semi * env * (0.55 + 0.9 * self._g_r[i]) + self._g_jit_r[i] * 5.0 * self._glitch
            izq.append(QPointF(cx + wand + dx - hl, y))
            der.append(QPointF(cx + wand + dx + hr, y))
        return QPolygonF(izq + der[::-1])
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setOpacity(self._alfa_fondo)
        p.fillRect(self.rect(), QColor(0, 0, 0))
        if self._fase >= 5:
            p.setOpacity(self._alfa_fondo * min(1.0, 0.4 + max(self._glitch, self._aber)))
            p.fillRect(self.rect(), QBrush(self._tex_scan_pant))
        p.setOpacity(1.0)
        if self._fase < 3:
            p.end()
            return
        amp = max(self._aber, self._glitch * 0.25) * 7.0
        if amp > 0.3:
            p.translate(random.uniform(-amp, amp), random.uniform(-amp * 0.4, amp * 0.4))
        if self._distorsion_progreso > 0.001:
            self._pintar_grieta(p)
            self._pintar_glitch(p)
            self._pintar_particulas(p)
        self._pintar_tears(p)
        self._pintar_humo(p)
        self._pintar_lluvia(p)
        self._pintar_ventana(p)
        self._pintar_terminal(p)
        self._pintar_fx(p)
        self._pintar_fragmentos(p)
        p.end()
    def _pintar_particulas(self, p):
        p.setPen(Qt.NoPen)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for pt in self._particulas:
            p.setBrush(self._col(pt["color"], 200 * pt["life"]))
            s = 4 * pt["life"]
            p.drawRect(QRectF(pt["x"], pt["y"], s, s))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    def _pintar_grieta(self, p):
        ap = self._distorsion_progreso
        g = self._glitch
        k = min(1.0, ap * 2.0)
        sep = (3.0 + 18.0 * g) * k
        p.setPen(Qt.NoPen)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for dx, dy, col, a in ((-sep, 0.0, self.C_ROJO, 150), (sep, 0.0, self.C_VERDE, 150), (0.0, -sep * 0.5, self.C_VIOLETA, 100)):
            p.setBrush(self._col(col, a * k))
            p.drawPolygon(self._poligono_grieta(dx, dy, 1.06))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        poli = self._poligono_grieta()
        p.setBrush(Qt.NoBrush)
        for ancho, a in ((16, 26), (9, 56), (4, 120)):
            p.setPen(QPen(self._col(self.C_VIOLETA, a * k), ancho, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawPolygon(poli)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0))
        p.drawPolygon(poli)
        if self._portal > 0.02:
            ruta = QPainterPath()
            ruta.addPolygon(poli)
            p.save()
            p.setClipPath(ruta)
            gr = QRadialGradient(QPointF(self.ancho / 2.0, self.alto / 2.0), self.alto * 0.5)
            gr.setColorAt(0.0, self._col(self.C_VERDE, 130.0 * self._portal))
            gr.setColorAt(0.35, self._col(self.C_VIOLETA, 110.0 * self._portal))
            gr.setColorAt(1.0, self._col(self.C_VIOLETA, 0))
            p.setBrush(QBrush(gr))
            p.drawRect(self.rect())
            p.restore()
        p.setPen(QPen(self._col(self.C_VIOLETA, 235.0 * k), 1.4))
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(poli)
    def _pintar_glitch(self, p):
        g = self._glitch
        if g < 0.01: return
        ap = self._distorsion_progreso
        cx = self.ancho / 2.0
        cy = self.alto / 2.0
        fase = ap * 6.283
        p.setPen(Qt.NoPen)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for b in self._barras:
            y = b["y"] + 26.0 * g * math.sin(fase + b["ph"])
            w = b["w"] * (0.35 + 0.65 * ap)
            h = b["h"] * (0.6 + 0.4 * g)
            x = cx + b["dx"] + 40.0 * g * math.sin(fase * 0.7 + b["ph"])
            a = b["a"] * g
            p.setBrush(self._col(b["c"], a))
            p.drawRect(QRectF(x - w / 2.0, y, w, h))
            if b["sp"]:
                p.setBrush(self._col(self.C_ROJO, a * 0.6))
                p.drawRect(QRectF(x - w / 2.0 - 7.0, y + 1.0, w, h))
                p.setBrush(self._col(self.C_VERDE, a * 0.6))
                p.drawRect(QRectF(x - w / 2.0 + 7.0, y - 1.0, w, h))
        esp = 0.3 + 0.7 * ap
        for nx, ny, s, f, ci in self._ruido:
            p.setBrush(self._col(self._COLS[ci], 210.0 * g))
            p.drawRect(QRectF(cx + nx * esp, cy + ny, s * f, s))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    def _pintar_tears(self, p):
        k = max(self._aber, self._glitch * 0.6)
        if k < 0.05 or not self._tears: return
        p.setPen(Qt.NoPen)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        a = 95.0 * k
        for y, h, dx, x0, w in self._tears:
            p.setBrush(self._col(self.C_ROJO, a))
            p.drawRect(QRectF(x0 + dx * k, y, w, h))
            p.setBrush(self._col(self.C_VERDE, a))
            p.drawRect(QRectF(x0 - dx * k, y + 1.0, w, h))
            p.setBrush(self._col(self.C_VIOLETA, a * 0.5))
            p.drawRect(QRectF(x0, y - 1.0, w, max(1.0, h * 0.35)))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    def _pintar_humo(self, p):
        if not self._humo: return
        p.setPen(Qt.NoPen)
        for h in self._humo:
            age = (self._t - h["t0"]) / h["dur"]
            if age <= 0.0 or age >= 1.0: continue
            x = h["x"] + h["vx"] * age * h["dur"]
            y = h["y"] + h["vy"] * age * h["dur"]
            r = h["r0"] + (h["r1"] - h["r0"]) * age
            a = h["a"] * min(1.0, age * 6.0) * (1.0 - age) ** 1.4
            grad = QRadialGradient(QPointF(x, y), r)
            grad.setColorAt(0.0, self._col(h["c"], a))
            grad.setColorAt(0.55, self._col(h["c"], a * 0.45))
            grad.setColorAt(1.0, self._col(h["c"], 0))
            p.setBrush(QBrush(grad))
            p.drawEllipse(QPointF(x, y), r, r * 0.82)
    def _pintar_lluvia(self, p):
        if not self._lluvia: return
        p.setFont(self._f_bin)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for q in self._lluvia:
            p.setPen(self._col(q["c"], 230.0 * q["life"]))
            p.drawText(QPointF(q["x"], q["y"]), q["ch"])
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    def _pintar_fx(self, p):
        if self._flash > 0.01:
            p.fillRect(self.rect(), self._col(N_MORADO, 120.0 * self._flash))
        if not self._fx: return
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for f in self._fx:
            f.dibujar(p)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
    def _pintar_ventana(self, p):
        v = self._vent
        if v <= 0.001 or self._rotura >= 1.0:
            return
        wv = float(self._wv)
        hv = float(self._hv)
        cx = self.ancho / 2.0
        cy = self._cy_vent
        d = self._desliz
        bob = 6.0 * math.sin(self._t * 1.9) if self._fase >= 6 else 0.0
        px = cx + (self._destino.x() - cx) * d
        py = cy + (self._destino.y() - cy) * d + bob
        esc = 1.0 - (1.0 - self._esc_final) * d
        if self._rotura > 0.0:
            self._pintar_rotura(p, px, py, esc)
            return
        if v < 0.3:
            k = v / 0.3
            sx = max(0.02, k * k)
            sy = 3.0 / hv
            linea = True
        else:
            k = (v - 0.3) / 0.7
            sx = 1.0
            sy = max(3.0 / hv, 1.0 - (1.0 - k) ** 3)
            linea = False
        p.save()
        p.translate(px, py)
        p.scale(esc * sx, esc * sy)
        p.translate(-wv / 2.0, -hv / 2.0)
        p.setOpacity(1.0)
        if linea:
            p.setPen(Qt.NoPen)
            p.setCompositionMode(QPainter.CompositionMode_Plus)
            p.setBrush(self._col(N_MORADO, 120))
            p.drawRect(QRectF(0.0, -hv * 1.5, wv, hv * 4.0))
            p.setBrush(self._col(N_VERDE, 255))
            p.drawRect(QRectF(0.0, 0.0, wv, hv))
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        else:
            self._dibujar_ventana(p, wv, hv)
        p.restore()
    def _dibujar_ventana(self, p, wv, hv):
        t = self._t
        ab = self._aber
        g = max(self._glitch, ab)
        sep = 2.0 + 26.0 * ab + 5.0 * self._glitch
        pad = float(self._pad)
        barra = float(self._barra)
        iw = float(self._iw)
        ih = float(self._ih)
        ix = pad
        iy = barra + 8.0
        poli = poly_cortado(0.0, 0.0, wv, hv, 22.0, 8.0, 22.0, 8.0)
        ruta = QPainterPath()
        ruta.addPolygon(poli)
        p.setPen(Qt.NoPen)
        p.setBrush(self._col(N_FONDO, 248))
        p.drawPolygon(poli)
        p.save()
        p.setClipPath(ruta)
        gt = QLinearGradient(QPointF(0.0, 0.0), QPointF(wv, 0.0))
        gt.setColorAt(0.0, self._col(N_MORADO, 120))
        gt.setColorAt(1.0, self._col(N_MORADO, 28))
        p.setBrush(QBrush(gt))
        p.drawRect(QRectF(0.0, 0.0, wv, barra))
        p.setPen(QPen(self._col(N_VERDE, 170), 1.2))
        p.drawLine(QPointF(0.0, barra), QPointF(wv, barra))
        p.setFont(self._f_tit)
        jx = random.uniform(-4.0, 4.0) * g if g > 0.3 else 0.0
        p.setPen(self._col(N_VERDE, 255))
        p.drawText(QPointF(pad + 8.0 + jx, barra * 0.68), "GENGAR.EXE")
        p.setPen(Qt.NoPen)
        for k, col in enumerate((N_ROJO, N_VERDE, N_MORADO)):
            p.setBrush(self._col(col, 230))
            p.drawRect(QRectF(wv - pad - 12.0 - k * 16.0, barra / 2.0 - 5.0, 10.0, 10.0))
        rv = self._reveal
        p.save()
        p.setClipRect(QRectF(ix, iy, iw, ih), Qt.IntersectClip)
        p.fillRect(QRectF(ix, iy, iw, ih), QColor(5, 3, 10))
        self._pintar_matrix(p, ix, iy, iw, ih, rv)
        if rv > 0.0:
            p.save()
            p.setClipRect(QRectF(ix, iy, iw, ih * min(1.0, rv)), Qt.IntersectClip)
            if rv < 1.0:
                p.setOpacity(p.opacity() * random.uniform(0.7, 1.0))
            self._cara_bandas(p, ix, iy, sep, g, ab)
            p.restore()
        p.fillRect(QRectF(ix, iy, iw, ih), QBrush(self._tex_scan))
        yb = iy + ((t * 0.42) % 1.4 - 0.2) * ih
        gs = QLinearGradient(QPointF(0.0, yb - 34.0), QPointF(0.0, yb + 34.0))
        gs.setColorAt(0.0, self._col(N_VERDE, 0))
        gs.setColorAt(0.5, self._col(N_VERDE, 70))
        gs.setColorAt(1.0, self._col(N_VERDE, 0))
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        p.fillRect(QRectF(ix, yb - 34.0, iw, 68.0), QBrush(gs))
        if 0.0 < rv < 1.0:
            ye = iy + ih * rv
            ge = QLinearGradient(QPointF(0.0, ye - 14.0), QPointF(0.0, ye + 3.0))
            ge.setColorAt(0.0, self._col(N_VERDE, 0))
            ge.setColorAt(1.0, self._col(N_VERDE, 230))
            p.fillRect(QRectF(ix, ye - 14.0, iw, 17.0), QBrush(ge))
        if g > 0.1:
            for _ in range(int(2 + 8 * g)):
                yy = iy + random.random() * ih
                p.fillRect(QRectF(ix, yy, iw, random.uniform(1.0, 3.0)), self._col(random.choice(self._COLS), 80.0 * g + 40.0))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(self._col(N_VERDE, 90), 1.0))
        p.drawRect(QRectF(ix, iy, iw, ih))
        p.setPen(QPen(self._col(N_VERDE, 240), 2.2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        L = 16.0
        for ax, ay, sx_, sy_ in ((ix, iy, 1.0, 1.0), (ix + iw, iy, -1.0, 1.0), (ix, iy + ih, 1.0, -1.0), (ix + iw, iy + ih, -1.0, -1.0)):
            p.drawLine(QPointF(ax, ay), QPointF(ax + sx_ * L, ay))
            p.drawLine(QPointF(ax, ay), QPointF(ax, ay + sy_ * L))
        fy = iy + ih + 10.0
        if self._fase >= 7:
            pb = 1.0
        elif self._boot_on:
            pb = max(0.0, min(1.0, (self._tb - 0.15) / 2.2))
        else:
            pb = 0.0
        nseg = 24
        llenos = int(pb * nseg)
        listo = pb >= 1.0
        p.setFont(self._f_term_p)
        izq_t = "SYSTEM READY" if listo else "BOOTING" + "." * (int(t * 4.0) % 4)
        if self._fase == 8:
            izq_t = "CLICK PARA ENTRAR" + ("_" if int(t * 2.0) % 2 == 0 else "")
        p.setPen(self._col(N_VERDE if listo else N_MORADO, 255))
        p.drawText(QPointF(pad, fy + 14.0), izq_t)
        s_pc = "%3d%%" % int(pb * 100)
        p.setPen(self._col(N_VERDE, 255))
        p.drawText(QPointF(wv - pad - QFontMetrics(self._f_term_p).horizontalAdvance(s_pc), fy + 14.0), s_pc)
        seg_g = 3.0
        seg_w = (iw - seg_g * (nseg - 1)) / nseg
        p.setPen(Qt.NoPen)
        for i in range(nseg):
            if i < llenos:
                p.setBrush(self._col(N_VERDE, 255))
            else:
                p.setBrush(self._col(N_MORADO, 55))
            p.drawRect(QRectF(ix + i * (seg_w + seg_g), fy + 24.0, seg_w, 14.0))
        p.restore()
        parp = int(t * 7.0) % 2
        if random.random() < 0.05 + 0.2 * g:
            parp ^= 1
        c1 = N_MORADO if parp == 0 else N_VERDE
        c2 = N_VERDE if parp == 0 else N_MORADO
        fl = 0.8 + 0.2 * math.sin(t * 23.0)
        p.setBrush(Qt.NoBrush)
        if ab > 0.05 or self._glitch > 0.3:
            p.setCompositionMode(QPainter.CompositionMode_Plus)
            for col, d in ((N_ROJO, -sep * 0.6), (N_VERDE, sep * 0.6)):
                p.setPen(QPen(self._col(col, 170), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.save()
                p.translate(d, 0.0)
                p.drawPolygon(poli)
                p.restore()
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        for ancho, a in ((14.0, 22.0), (8.0, 50.0), (3.2, 255.0)):
            p.setPen(QPen(self._col(c1, a * fl), ancho, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawPolygon(poli)
        p.setPen(QPen(self._col(c2, 150.0 * fl), 1.2))
        p.drawPolygon(poly_cortado(7.0, 7.0, wv - 14.0, hv - 14.0, 16.0, 4.0, 16.0, 4.0))
    def _pintar_matrix(self, p, ix, iy, iw, ih, rv):
        if rv >= 0.999: return
        p.save()
        p.setClipRect(QRectF(ix, iy + ih * rv, iw, ih * (1.0 - rv) + 1.0), Qt.IntersectClip)
        p.setFont(self._f_bin)
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        for c in self._mx:
            x = ix + c["x"] * iw
            yh = iy + ((c["o"] + self._t * c["v"]) % (ih + 280.0)) - 140.0
            for i, ch in enumerate(c["s"]):
                y = yh - i * 14.0
                if y < iy or y > iy + ih: continue
                p.setPen(self._col(N_VERDE, 230.0 * (1.0 - i / 18.0)))
                p.drawText(QPointF(x, y), ch)
        p.restore()
    def _bandas_img(self, p, pix, x, y, bandas, f):
        dpr = self._dpr
        ph = pix.height()
        pw = pix.width()
        for f0, f1, dx in bandas:
            r0 = int(round(f0 * ph))
            r1 = int(round(f1 * ph))
            if r1 <= r0: continue
            p.drawPixmap(QRectF(x + dx * f, y + r0 / dpr, pw / dpr, (r1 - r0) / dpr), pix, QRectF(0.0, float(r0), float(pw), float(r1 - r0)))
    def _cara_bandas(self, p, ix, iy, sep, g, ab):
        f = min(1.0, g * 1.6) * (1.0 + 1.5 * ab)
        bandas = self._bandas_v if g > 0.05 else [(0.0, 1.0, 0.0)]
        if sep > 3.0:
            p.setCompositionMode(QPainter.CompositionMode_Plus)
            for pix, d in ((self._cara_r, -sep), (self._cara_g, 0.0), (self._cara_b, sep)):
                self._bandas_img(p, pix, ix + d, iy, bandas, f)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        else:
            self._bandas_img(p, self._cara, ix, iy, bandas, f)
    def _pintar_terminal(self, p):
        if self._fase < 6 or self._vent < 0.99: return
        ov = self._term_alfa
        if ov <= 0.01: return
        t = self._t
        tb = self._tb
        g = max(self._glitch, self._aber)
        cx = self.ancho / 2.0
        cy = self._cy_vent + 6.0 * math.sin(t * 1.9)
        izq = cx - self._wv / 2.0
        der = cx + self._wv / 2.0
        arriba = cy - self._hv / 2.0
        abajo = cy + self._hv / 2.0
        ultimo = len(self._lineas) - 1
        p.save()
        p.setOpacity(ov)
        for i, (lado, fy, txt, t0, col, grande) in enumerate(self._lineas):
            n = int((tb - t0) * (26.0 if grande else 34.0))
            if n <= 0: continue
            fuente = self._f_gr if grande else self._f_term
            fm = QFontMetrics(fuente)
            ancho_t = fm.horizontalAdvance(txt)
            completo = n >= len(txt)
            s = txt[:min(n, len(txt))]
            if g > 0.4 and len(s) > 3 and random.random() < 0.3:
                k = random.randrange(len(s))
                s = s[:k] + random.choice("01#$%&@") + s[k + 1:]
            if lado == "L":
                x = max(8.0, izq - 34.0 - ancho_t)
                y = arriba + fy * self._hv + fm.ascent()
            elif lado == "R":
                x = der + 34.0
                y = arriba + fy * self._hv + fm.ascent()
            else:
                x = cx - ancho_t / 2.0
                y = abajo + 56.0
            if lado != "B":
                ym = y - fm.ascent() * 0.4
                p.setPen(QPen(self._col(N_MORADO, 90), 1.0))
                if lado == "L":
                    p.drawLine(QPointF(x + ancho_t + 8.0, ym), QPointF(izq - 8.0, ym))
                else:
                    p.drawLine(QPointF(der + 8.0, ym), QPointF(x - 8.0, ym))
            p.setFont(fuente)
            if g > 0.25:
                p.setCompositionMode(QPainter.CompositionMode_Plus)
                p.setPen(self._col(N_ROJO, 130.0 * g))
                p.drawText(QPointF(x - 3.0 * g, y), s)
                p.setPen(self._col(N_VERDE, 130.0 * g))
                p.drawText(QPointF(x + 3.0 * g, y), s)
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.setPen(self._col(col, 255))
            p.drawText(QPointF(x, y), s)
            if not completo or (i == ultimo and int(t * 3.0) % 2 == 0):
                p.setPen(Qt.NoPen)
                p.setBrush(self._col(col, 230))
                p.drawRect(QRectF(x + fm.horizontalAdvance(s) + 2.0, y - fm.ascent() + 2.0, fm.averageCharWidth() * 0.8, fm.ascent()))
        p.restore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    cfg = cargar_config()
    refs = {}
    def iniciar_mascota():
        snd = Sonido()
        fx = FxOverlay()
        chat_window = VentanaChatCyberdeck()
        pet_window = PetGengar(chat_window, fx, snd, cfg)
        def mostrar_chat():
            chat_window.show()
            chat_window.raise_()
            chat_window.activateWindow()
        chat_window.mensaje_enviado.connect(pet_window.recibir_mensaje)
        chat_window.pedir_voz.connect(pet_window.escuchar)
        pet_window.respuesta_para_chat.connect(lambda t, ti, b, tp, st: chat_window.agregar_mensaje("Gengar", t, ti, b, tp, st))
        pet_window.respuesta_para_chat.connect(lambda *a: chat_window.detener_typing())
        pet_window.abrir_chat.connect(mostrar_chat)
        def accion_chat(a):
            if a == "cascos":
                print("[Gengar] /cascos: forzando globo de cascos durante 15 s")
                pet_window._musica_evento("normal", "Prueba /cascos")
                QTimer.singleShot(15000, lambda: pet_window._musica_evento("silencio", ""))
                return
            mapeo = {"bola": "bola_fantasma"}
            pet_window.ejecutar(mapeo.get(a, a))
        chat_window.accion_rapida.connect(accion_chat)
        puente = Puente(PUERTO)
        puente.evento.connect(pet_window.evento_claude)
        if not puente.iniciar():
            print(f"[Gengar] El puerto {PUERTO} esta ocupado: ¿ya hay otro Gengar abierto?")
        atajo = FiltroAtajo(pet_window.alternar_guardado, pet_window.escuchar)
        app.installNativeEventFilter(atajo)
        app.aboutToQuit.connect(atajo.liberar)
        app.aboutToQuit.connect(TTS.parar)
        app.aboutToQuit.connect(puente.parar)
        tray = crear_tray(app, pet_window, mostrar_chat)
        x_caida = intro.sprite.x() + intro.sprite.width() // 2 - W // 2
        min_x, max_x, suelo = pet_window.limites(SINK_PIE)
        pet_window.move(max(min_x, min(max_x, x_caida)), suelo)
        pet_window.show()
        refs.update(snd=snd, fx=fx, chat=chat_window, pet=pet_window, puente=puente, atajo=atajo, tray=tray)
    intro = IntroAnimacion()
    intro.intro_terminada.connect(iniciar_mascota)
    sys.exit(app.exec())