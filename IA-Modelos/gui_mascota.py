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
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextBrowser, QSystemTrayIcon, QMenu, QInputDialog, QPushButton,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QMessageBox
)
from PySide6.QtGui import (
    QPixmap, QColor, QPainter, QTransform, QCursor, QIcon, QAction, QPen, QBrush,
    QPolygonF, QRadialGradient, QLinearGradient, QFont, QFontMetrics, QPainterPath
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
_CANDIDATAS = ["D:/IA-Modelos/gengar_img", os.path.join(BASE, "gengar_img")]
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
SEG_DISOLVER = 150
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
        "saludo": 3, "teleport": 3}
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
def get_visible_rect(hwnd):
    rect = wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect)
    )
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
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.registrado = False
        if sys.platform == "win32":
            try:
                MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
                self.registrado = bool(ctypes.windll.user32.RegisterHotKey(
                    None, self.ID, MOD_ALT | MOD_CONTROL | MOD_NOREPEAT, ord("G")))
            except Exception:
                self.registrado = False
    def nativeEventFilter(self, eventType, message):
        try:
            if sys.platform == "win32" and bytes(eventType) == b"windows_generic_MSG":
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == self.WM_HOTKEY and msg.wParam == self.ID:
                    QTimer.singleShot(0, self.callback)
        except Exception:
            pass
        return False, 0
    def liberar(self):
        if self.registrado and sys.platform == "win32":
            try:
                ctypes.windll.user32.UnregisterHotKey(None, self.ID)
            except Exception:
                pass
            self.registrado = False
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
    p.setPen(QPen(QColor("#ffffff"), max(1.5, w * .045), Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap,
                  Qt.PenJoinStyle.MiterJoin))
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
        self.vis = 0
        self.f_nombre = QFont("Consolas")
        self.f_nombre.setPixelSize(12)
        self.f_nombre.setBold(True)
        self.f_nombre.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        self.f_sub = QFont("Consolas")
        self.f_sub.setPixelSize(11)
        self.f_titulo = QFont("Segoe UI")
        self.f_titulo.setPixelSize(16)
        self.f_titulo.setBold(True)
        self.f_cuerpo = QFont("Segoe UI")
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
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        PW, h, so, m = self.PW, self.h_main, self.SO, self.M
        morado = QColor(C_MORADO)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(morado)
        p.drawPolygon(poly_cortado(so, so, PW, h, 24, 12, 12, 0))
        tx = self.tx
        p.drawPolygon(QPolygonF([QPointF(tx - 14, h - 2), QPointF(tx + 14, h - 2),
                                 QPointF(tx + 8, h + self.COLA)]))
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
                         "espera": (QColor("#ffb020"), QColor("#140c00"))}.get(
                self.tipo, (QColor(C_MORADO), QColor("#ffffff")))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(col)
            p.drawPolygon(QPolygonF([QPointF(bx + 5, by), QPointF(bx + bw, by), QPointF(bx + bw - 5, by + 17),
                                     QPointF(bx, by + 17)]))
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
        p.drawText(QPointF(nx, m + 11),
                   QFontMetrics(self.f_sub).elidedText("/ CIUDAD-NOCTURNA-…", Qt.TextElideMode.ElideRight, int(max(10, disp))))
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
                if resto <= 0:
                    break
                p.drawText(QPointF(xc + 10, self.y_c + i * self.hl_c + self.fm_c.ascent() + 1), l[:resto])
                resto -= len(l) + 1
        if self.stats:
            yy = self.y_s + self.fm_s.height() / 2
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(C_VERDE))
            p.drawPolygon(QPolygonF([QPointF(xc + 4, yy - 4), QPointF(xc + 8, yy), QPointF(xc + 4, yy + 4),
                                     QPointF(xc, yy)]))
            p.setFont(self.f_stats)
            p.setPen(QColor(C_VERDE))
            p.drawText(QPointF(xc + 14, self.y_s + self.fm_s.ascent()),
                       self.fm_s.elidedText(self.stats, Qt.TextElideMode.ElideRight, self.wc - 14))
class VentanaChatCyberdeck(QWidget):
    mensaje_enviado = Signal(str)
    accion_rapida = Signal(str)
    SO = 8
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat con Gengar")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 720)
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
        lp.setContentsMargins(28, 28, 28 + self.SO, 28 + self.SO)
        cab = QHBoxLayout()
        self.lbl_avatar = AvatarGeo(60)
        tit = QVBoxLayout()
        tit.setSpacing(4)
        self.lbl_titulo = QLabel(f"<span style='color:#fff; font-weight:bold; letter-spacing:2px;'>GENGAR</span>"
                                 f" <span style='color:{C_GRIS};'>/ CIUDAD-NOCTURNA-2077</span>")
        self.lbl_titulo.setStyleSheet("font-family: 'Consolas'; font-size: 14px;")
        self.lbl_estado = QLabel("EN LÍNEA")
        self.lbl_estado.setFixedHeight(16)
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        self.lbl_estado.setStyleSheet(f"background: {C_VERDE}; color: #04140a; font-family: 'Consolas'; "
                                      "font-size: 10px; font-weight: bold; padding: 0px 8px;")
        fila = QHBoxLayout()
        fila.addWidget(self.lbl_estado)
        fila.addStretch()
        tit.addWidget(self.lbl_titulo)
        tit.addLayout(fila)
        self.btn_limpiar = QPushButton("[PURGAR_LOG]")
        self.btn_limpiar.setFixedSize(95, 30)
        self.btn_limpiar.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_MORADO}; "
                                       f"font-weight: bold; font-family: 'Consolas'; border: 2px solid {C_MORADO}; }}"
                                       f"QPushButton:hover {{ background: {C_MORADO}; color: #fff; }}")
        self.btn_limpiar.clicked.connect(self._limpiar_historial)
        self.btn_cerrar = QPushButton("[X]")
        self.btn_cerrar.setFixedSize(30, 30)
        self.btn_cerrar.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_ROJO}; font-weight: bold; "
                                      f"font-family: 'Consolas'; border: 2px solid {C_ROJO}; }}"
                                      f"QPushButton:hover {{ background: {C_ROJO}; color: #fff; }}")
        self.btn_cerrar.clicked.connect(self.hide)
        cab.addWidget(self.lbl_avatar)
        cab.addSpacing(10)
        cab.addLayout(tit)
        cab.addStretch()
        cab.addWidget(self.btn_limpiar)
        cab.addWidget(self.btn_cerrar)
        self.historial = QTextBrowser()
        self.historial.setStyleSheet(f"""
            QTextBrowser {{
                background-color: rgba(6, 4, 12, 235);
                border: none;
                border-left: 3px solid {C_MORADO};
                color: {C_TEXTO};
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 10px;
            }}
            QScrollBar:vertical {{ background: {C_FONDO}; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {C_MORADO}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self.lbl_typing = QLabel("GENGAR ESCRIBE...")
        self.lbl_typing.setStyleSheet(f"color: {C_VERDE}; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        self.lbl_typing.hide()
        self.timer_typing = QTimer(self)
        self.timer_typing.timeout.connect(self._parpadear_typing)
        lb = QHBoxLayout()
        self.btn_bola = QPushButton(">> BOLA_FANTASMA")
        self.btn_bailar = QPushButton(">> BAILE_FORZADO")
        self.btn_dormir = QPushButton(">> MODO_SUEÑO")
        estilo = f"""
            QPushButton {{
                background-color: {C_FONDO};
                color: {C_VERDE};
                border: 2px solid {C_MORADO};
                padding: 8px;
                font-family: 'Consolas';
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {C_MORADO}; color: #fff; }}
        """
        for b in (self.btn_bola, self.btn_bailar, self.btn_dormir):
            b.setStyleSheet(estilo)
            lb.addWidget(b)
        self.btn_bola.clicked.connect(lambda: self.accion_rapida.emit("bola"))
        self.btn_bailar.clicked.connect(lambda: self.accion_rapida.emit("bailar"))
        self.btn_dormir.clicked.connect(lambda: self.accion_rapida.emit("dormir"))
        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText(">> ESCRIBE TU COMANDO, TÍO...")
        self.input_texto.setStyleSheet(f"""
            QLineEdit {{
                background-color: #080510;
                color: #fff;
                border: 2px solid {C_MORADO};
                padding: 12px;
                font-family: 'Consolas';
                font-size: 14px;
                font-weight: bold;
                selection-background-color: {C_MORADO};
            }}
            QLineEdit:focus {{ border: 2px solid {C_VERDE}; }}
        """)
        self.input_texto.returnPressed.connect(self._enviar_mensaje)
        lp.addLayout(cab)
        lp.addSpacing(15)
        lp.addWidget(self.historial)
        lp.addWidget(self.lbl_typing)
        lp.addSpacing(15)
        lp.addLayout(lb)
        lp.addWidget(self.input_texto)
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
        p.drawPolygon(poly_cortado(so, so, w, h, 34, 16, 16, 0))
        p.setBrush(QColor(C_FONDO))
        p.setPen(QPen(morado, 4, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        p.drawPolygon(poly_cortado(2, 2, w - 4, h - 4, 34, 16, 16, 0))
    def agregar_mensaje(self, remitente, texto):
        if remitente == "Tú":
            prefijo, c1, color = "tú >", "#ffffff", "#ffffff"
        elif remitente == "Sistema":
            prefijo, c1, color = "SISTEMA:", C_ROJO, C_ROJO
        else:
            prefijo, c1, color = "GENGAR >", C_VERDE, C_TEXTO
        self.historial.append(
            f'<div style="margin: 8px 0;"><span style="color:{c1}; font-weight:bold;">{prefijo}</span> '
            f'<span style="color:{color};">{html.escape(texto)}</span></div>')
        self.historial.verticalScrollBar().setValue(self.historial.verticalScrollBar().maximum())
    def _enviar_mensaje(self):
        texto = self.input_texto.text().strip()
        if not texto:
            return
        self.input_texto.clear()
        self.agregar_mensaje("Tú", texto)
        if texto.startswith("/"):
            comando = texto.lower().strip()
            ok = {"/bailar": ("bailar", "Bailar activado."), "/dormir": ("dormir", "Dormir activado."),
                  "/bola": ("bola", "Bola Fantasma activado."), "/hipnosis": ("hipnosis", "Hipnosis activada.")}
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
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                            | Qt.Tool | Qt.WindowTransparentForInput)
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
        self.setStyleSheet("background-color:#0b0b0b; color:#39ff14; border:2px solid #39ff14; "
                           "font-family:Consolas; font-size:13px; padding:10px;")
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
    def __init__(self, x, y, n=18, colores=None, vel=(60, 260), grav=500, dur=0.9,
                 tam=(2, 6), cono=None, hacia=None, glifo=False):
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
                self.ps.append([px + math.cos(a2) * r, py + math.sin(a2) * r, 0.0, 0.0,
                                random.uniform(*tam), QColor(random.choice(colores)),
                                random.uniform(0, 6.28), random.choice("01▒░<>/{}#$%")])
            else:
                self.ps.append([x, y, math.cos(ang) * v, math.sin(ang) * v, random.uniform(*tam),
                                QColor(random.choice(colores)), random.uniform(0, 6.28),
                                random.choice("01▒░<>/{}#$%")])
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
        self.lineas = [(random.uniform(0, 2 * math.pi), random.uniform(0.0, 0.5),
                        random.uniform(0.25, 0.7), random.uniform(1, 3)) for _ in range(self.n)]
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
            p.drawLine(QPointF(self.x + math.cos(ang) * r_a, self.y + math.sin(ang) * r_a),
                       QPointF(self.x + math.cos(ang) * r_b, self.y + math.sin(ang) * r_b))
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
        for ancho, col, alfa in ((self.grosor * 3.2, self.color, 0.25), (self.grosor * 1.6, self.color, 0.7),
                                 (max(1.0, self.grosor * 0.6), "#ffffff", 1.0)):
            for i in range(len(self.pts) - 1):
                k = 1 - (i / self.n) * (0.8 if self.fino else 0.0)
                p.setPen(QPen(_color(col, alfa * a), max(1.0, ancho * k), Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap))
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
        self._escala = None
    def dibujar(self, p):
        entra = _suave(self.t / 0.16)
        sale = _suave((self.dur - self.t) / 0.22)
        a = min(entra, sale)
        dx = (1 - entra) * 140
        x, y, w, h = self.x + dx, self.y, self.w, self.h
        sk = 22
        marco = QPolygonF([QPointF(x + sk, y), QPointF(x + w, y), QPointF(x + w - sk, y + h), QPointF(x, y + h)])
        sombra = QPolygonF([QPointF(x + sk + 6, y + 6), QPointF(x + w + 6, y + 6),
                            QPointF(x + w - sk + 6, y + h + 6), QPointF(x + 6, y + h + 6)])
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
            p.drawRect(QRectF(x + random.uniform(10, w - 30), y + random.uniform(4, h - 8),
                              random.uniform(6, 26), 2))
        p.restore()
        p.setPen(QPen(QColor(C_MORADO), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap,
                      Qt.PenJoinStyle.MiterJoin))
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
        self.est = [(random.uniform(-70, 70), random.uniform(-110, -30), random.uniform(2.0, 4.5))
                    for _ in range(22)]
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
        self.ojos = [(random.uniform(0.12, 0.88), random.uniform(0.15, 0.7), random.uniform(0.8, 1.5))
                     for _ in range(6)]
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
            for (a1, a2) in ((r.topLeft(), r.topRight()), (r.topRight(), r.bottomRight()),
                             (r.bottomRight(), r.bottomLeft()), (r.bottomLeft(), r.topLeft())):
                pts = [a1]
                for i in range(1, 12):
                    k = i / 12
                    pts.append(QPointF(a1.x() + (a2.x() - a1.x()) * k + random.uniform(-8, 8),
                                       a1.y() + (a2.y() - a1.y()) * k + random.uniform(-8, 8)))
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
            pts = [QPointF(x0 + ancho * i / 14, y0 + (14 if i % 2 else -14) + 10 * math.sin(i / 14 * math.pi))
                   for i in range(15)]
            p.setPen(QPen(QColor(0, 0, 0, int(200 * a)), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                          Qt.PenJoinStyle.RoundJoin))
            p.drawPolyline(QPolygonF(pts))
            p.setPen(QPen(QColor(255, 255, 255, int(245 * a)), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                          Qt.PenJoinStyle.RoundJoin))
            p.drawPolyline(QPolygonF(pts))
        p.restore()
class FxOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                            | Qt.Tool | Qt.WindowTransparentForInput)
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
        self.glifos.append([random.uniform(SPR_X + 25, SPR_X + SPR - 25), SPR_Y + SPR * 0.3,
                            1.0, random.choice("01▒░<>/{}#$%")])
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
class PetGengar(QWidget):
    respuesta_para_chat = Signal(str)
    abrir_chat = Signal()
    notificar = Signal(str, str)
    tooltip = Signal(str)
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
        return (a.left() - SPR_X,
                a.right() + 1 - SPR_X - SPR,
                a.bottom() + 1 - H + sink)
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
    def decir(self, texto, ms=4500, maxlen=110, titulo="", badge="", tipo="info", stats=""):
        if len(texto) > maxlen:
            texto = texto[:maxlen - 1] + "…"
        self._frase, self._frase_i = texto, 0
        self.bocadillo.configurar(titulo, texto, stats, badge, tipo)
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
    def hideEvent(self, e):
        super().hideEvent(e)
        self.bocadillo.hide()
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
    def anim_actual(self):
        return self.anim_sub or self.estado
    def cambiar_estado(self, nuevo):
        self.estado = nuevo
        self.anim_sub = None
        self.frame = 0
        self.ticks = 0
        self.t_estado = time.time()
        self.dur = {"patrulla": random.uniform(3.0, 6.0),
                    "quieto_de_pie": 1.0,
                    "sentado": random.uniform(6.0, 12.0)}.get(nuevo, 0.0)
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
        self.fx.agregar(Particulas(c.x(), c.y(), n=10, colores=VIOLETAS, vel=(80, 220), grav=700, dur=0.6,
                                   cono=(-math.pi * 0.95, -math.pi * 0.05)))
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
        self.flota_obj = (random.randint(a.left(), max(a.left() + 1, a.right() - W)),
                          random.randint(a.top() + 40, max(a.top() + 41, a.bottom() - H - 100)))
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
        if self.arrastrando or self.estado in LIBRES or self.estado in (
                "en_ventana", "asomado", "asomado_arriba", "claude", "espera", "luna", "victoria",
                "teleport", "poseer", "dormir_largo", "flotar", "error"):
            return
        if self.estado == "pensando" and self.worker is not None and self.worker.isRunning():
            return
        if time.time() - self.t_estado > 45:
            self.volver_a_patrullar()
    def elegir_comportamiento(self):
        if (self.estado not in LIBRES or self.arrastrando or self.estudio_fase == "estudio"
                or self.chip_estado or self.guardado):
            return
        self.contador += 1
        hora = datetime.datetime.now().hour
        peso_dormir = 0.8 if (hora >= 22 or hora <= 6) else 0.2
        peso_bailar = 0.6 if (10 <= hora <= 20) else 0.2
        if random.random() < 0.55:
            opciones = ["dormir", "bailar", "hipnosis", "bola_fantasma", "humo", "ventana",
                        "teleport", "flotar", "luna"]
            pesos = [peso_dormir, peso_bailar, 0.3, 0.25, 0.15, 0.35,
                     0.15, 0.25 if self.cfg.get("vagar", True) else 0.0, 0.06]
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
                if (movido and self.estado in ("quieto_de_pie", "patrulla") and random.random() < 0.05
                        and ahora - self.t_zap > 45):
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
            self.move(random.randint(a.left() + 50, max(a.left() + 51, a.right() - W - 50)),
                      a.top() - SPR // 2 - SPR_Y)
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
        if (not self.modo_travesura or self.estado not in LIBRES or self.arrastrando
                or self.estudio_fase == "estudio" or not self.isVisible()):
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
    def recibir_mensaje(self, prompt):
        self.t_actividad = time.time()
        self.cancelar_pendientes()
        self.cambiar_estado("pensando")
        self.decir("Gengar está tramando algo...", 60000, badge="EN CURSO", tipo="info")
        self.worker = WorkerIA(prompt)
        self.worker.respuesta_lista.connect(self.mostrar_respuesta)
        self.worker.accion.connect(self.fx_accion)
        self.worker.start()
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
        self.respuesta_para_chat.emit(texto)
        self.cancelar_pendientes()
        self.cambiar_estado("bailar")
        self.decir(texto, max(6000, len(texto) * 70), maxlen=220)
        self.tras(3000, self.volver_a_patrullar)
    def evento_claude(self, d):
        ev = d.get("ev", "")
        self.t_claude = time.time()
        if self.estado == "dormir_largo" or self.chip_estado == "dormido":
            self.despertar(msg="")
        cl = self.cl
        if ev == "SessionStart":
            if not (self.guardado or self.chip_estado):
                self.sonido("hello")
                self.decir("¡Sesión abierta, tío! Yo vigilo.", 4000)
        elif ev == "UserPromptSubmit":
            cl.update(fase="trabajando", t0=time.time(), acciones=0, archivos=set(), errores=0,
                      herr_actual="", ultimo="", resumen="")
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
        self.poner_ticker(cl["herr_actual"])
        self.entrar_trabajo()
        if anim in ("claude_cmd", "claude_web") and self.estado == "claude" and self.isVisible():
            mx, my = self.mano_xy()
            self.fx.agregar(Particulas(mx, my, n=6, colores=ROJOS, vel=(60, 200), grav=200, dur=0.5,
                                       cono=(-math.pi * 0.9, -math.pi * 0.1)))
    def herramienta_fin(self, d, error):
        cl = self.cl
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
        dur = time.time() - cl["t0"] if cl["t0"] else 0.0
        acc, narch = cl["acciones"], len(cl["archivos"])
        m, s = divmod(int(dur), 60)
        resumen = f"{acc} acciones · {narch} archivos · {m}m {s:02d}s" if acc else ""
        tt = f"{s} s" if not m else f"{m} min {s} s"
        cl.update(fase="idle", ultimo=ultimo, resumen=resumen, t0=0.0, t_fin=time.time(),
                  stats=f"{acc} acciones · {narch} archivos modificados · {tt}" if acc else "")
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
        self.teletransportar(a.center().x() - W // 2, a.center().y() - H // 2 - 30,
                             despues=lambda: self._victoria(resumen, ultimo, largo))
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
        self.fx.agregar(Particulas(c.x(), c.y(), n=26, colores=VIOLETAS + ["#ffffff"], vel=(120, 420),
                                   grav=300, dur=1.0))
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
        self.decir(ultimo or "", 14000, maxlen=150, titulo="Misión cumplida, tío.", badge="TERMINADO",
                   tipo="ok", stats=self.cl.get("stats", ""))
        self.velocidad_y = 0
        self.cambiar_estado("caer")
        if largo:
            QTimer.singleShot(5500, lambda: self.mirar_luna(True)
                              if self.cl["fase"] == "idle" else None)
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
        self.fx.agregar(Particulas(0, 0, n=16, colores=ROJOS + VIOLETAS, dur=0.55,
                                   hacia=lambda: (self.centro_sprite().x(), self.centro_sprite().y())))
        self.sonido("teleport-in")
        self.impacto()
    def mirar_luna(self, completa=False):
        if (self.estado not in LIBRES or self.arrastrando or self.guardado or self.chip_estado
                or self.cl["fase"] != "idle"):
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
        self.fx.agregar(Rayo(self.mano_xy, luna.pos, color="#ff3b5c", dur=0.6, grosor=8,
                             segmentos=22, jitter=30, fino=True))
        self.fx.agregar(Onda(mx, my, r_max=160, color="#ff5252", dur=0.5))
        self.impacto()
    def _luna_del_dia(self):
        hoy = datetime.date.today().isoformat()
        if self.cfg.get("luna_fecha") == hoy:
            self.timer_luna_dia.stop()
            return
        if (self.estado in LIBRES and not self.arrastrando and not self.guardado and not self.chip_estado
                and self.estudio_fase != "estudio" and self.cl["fase"] == "idle"):
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
    def vigilar_sueno(self):
        if self.guardado or self.chip_estado == "dormido":
            return
        ahora = time.time()
        inactivo = ahora - max(self.t_raton_mov, self.t_claude, self.t_actividad)
        if (self.estado in LIBRES and self.cl["fase"] == "idle" and not self.arrastrando
                and self.estudio_fase is None and inactivo > MIN_SUENO * 60):
            self.cancelar_pendientes()
            self.cambiar_estado("dormir_largo")
            self.decir("Zzz...", 3000)
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
        if self.chip_estado == "dormido":
            self.chip.ocultar()
            self.chip_estado = None
            self.show()
            self.sonido("teleport-in")
            self.fx.agregar(Particulas(0, 0, n=20, colores=VIOLETAS, dur=0.6,
                                       hacia=lambda: (self.centro_sprite().x(), self.centro_sprite().y())))
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
        self.fx.agregar(Particulas(c.x(), c.y(), n=22, colores=VIOLETAS, dur=0.7,
                                   hacia=lambda: (a.left() + 42, a.bottom() - 42)))
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
        self.teletransportar(random.randint(a.left(), max(a.left() + 1, a.right() - W)),
                             random.randint(a.top() + 40, max(a.top() + 41, a.bottom() - H)),
                             despues=lambda: (setattr(self, "velocidad_y", 0), self.cambiar_estado("caer")))
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
            (16500, {"ev": "PostToolUseFailure", "herr": "Bash",
                     "err_linea": "AssertionError: esperaba 10, recibió 9"}),
            (20500, {"ev": "PreToolUse", "herr": "Bash", "detalle": "rm -rf build"}),
            (21500, {"ev": "Notification", "tipo": "permission_prompt",
                     "msg": "Claude necesita tu permiso para usar Bash"}),
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
        if self.estado in ("bola_fantasma", "humo", "trepar_ir", "trepar_izq", "trepar_der", "cursor",
                           "teleport", "victoria"):
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
    accion("Sentarse en la ventana de delante al trabajar", lambda v: pet.set_cfg("perchar", v),
           True, pet.cfg.get("perchar", True))
    menu.addSeparator()
    accion("Teletransportar", pet.teletransportar_aleatorio)
    accion("Mirar la luna", lambda: pet.mirar_luna(True))
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
    tray.activated.connect(
        lambda r: pet.alternar_visible() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
    pet.tooltip.connect(tray.setToolTip)
    pet.notificar.connect(
        lambda t, m: tray.showMessage(t, m, QSystemTrayIcon.MessageIcon.Information, 5000))
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
class IntroPanelLlamada(QWidget):
    def __init__(self, parent, ruta_cara):
        super().__init__(parent)
        self.setFixedSize(980, 420)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.cara = QPixmap(ruta_cara)
        self._cw, self._ch = 150, 250
        self._fw, self._fh = self._cw - 16, self._ch - 16 - 46
        self.face_pm = self._preparar_cara(self._fw, self._fh)
        self._glitch = False
        self._gx = 0
        self._rects = []
        self._slices = []
        self._banda = 150
        self._ticks = 0
        self._parpadeo = True
        self._barras = [(random.randint(0, 120), random.randint(1, 3)) for _ in range(26)]
        self.rect_answer = QRect(344, 304, 270, 70)
        self.rect_reject = QRect(644, 304, 270, 70)
        self.callback_answer = None
        self.callback_reject = None
        self._hover = None
        self._t_glitch = QTimer(self)
        self._t_glitch.timeout.connect(self._tick)
        self._t_glitch.start(70)
        self._t_parp = QTimer(self)
        self._t_parp.timeout.connect(self._parp)
        self._t_parp.start(600)
    def _preparar_cara(self, w, h):
        base = QPixmap(w, h)
        base.fill(QColor(10, 0, 14))
        q = QPainter(base)
        if not self.cara.isNull():
            img = self.cara.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            q.drawPixmap((w - img.width()) // 2, (h - img.height()) // 2, img)
            q.fillRect(0, 0, w, h, QColor(225, 30, 60, 100))
            q.setPen(QPen(QColor(0, 0, 0, 80), 1))
            for yy in range(0, h, 3):
                q.drawLine(0, yy, w, yy)
        else:
            q.setPen(_I_ROJO)
            q.setFont(QFont("Consolas", 11, QFont.Bold))
            q.drawText(QRect(0, 0, w, h), Qt.AlignCenter, "SIN SEÑAL")
        q.end()
        return base
    def _parp(self):
        self._parpadeo = not self._parpadeo
        self.update()
    def _tick(self):
        self._ticks += 1
        prob = 0.7 if self._ticks < 10 else 0.2
        if random.random() < prob:
            self._glitch = True
            self._gx = random.randint(-9, 9)
            self._rects = [
                QRect(random.randint(0, 760), random.randint(20, 400), random.randint(40, 260), random.randint(2, 6))
                for _ in range(random.randint(2, 5))
            ]
            self._slices = [
                (random.randint(0, self._fh - 20), random.randint(4, 18), random.randint(-14, 14))
                for _ in range(random.randint(1, 3))
            ]
            self._banda = random.randint(140, 200)
        else:
            self._glitch = False
            self._gx = 0
            self._rects = []
            self._slices = []
        self.update()
    def mouseMoveEvent(self, e):
        pos = e.position().toPoint()
        nuevo = None
        if self.rect_answer.contains(pos):
            nuevo = "answer"
        elif self.rect_reject.contains(pos):
            nuevo = "reject"
        if nuevo != self._hover:
            self._hover = nuevo
            self.setCursor(Qt.PointingHandCursor if nuevo else Qt.ArrowCursor)
            self.update()
    def mousePressEvent(self, e):
        pos = e.position().toPoint()
        if self.rect_answer.contains(pos) and self.callback_answer:
            self.callback_answer()
        elif self.rect_reject.contains(pos) and self.callback_reject:
            self.callback_reject()
    def _ruta_corte(self, x, y, w, h, corte=22):
        path = QPainterPath()
        path.moveTo(x + corte, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - corte)
        path.lineTo(x + w - corte, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y + corte)
        path.closeSubpath()
        return path
    def _texto(self, p, x, y, texto, fuente, color, brillo=1.0, dx=0):
        path = QPainterPath()
        path.addText(x + dx, y, fuente, texto)
        if brillo > 0:
            for grosor, a in ((9, 22), (5, 45), (2.5, 80)):
                c = QColor(color)
                c.setAlpha(int(a * brillo))
                p.strokePath(path, QPen(c, grosor, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.fillPath(path, color)
    def _dibujar_telefono(self, p):
        c = _I_MORADO_NEON
        cuerpo = QRectF(30, 76, 40, 74)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(150, 60, 220, 60), 6))
        p.drawRoundedRect(cuerpo, 7, 7)
        p.setPen(QPen(c, 2))
        p.drawRoundedRect(cuerpo, 7, 7)
        p.setPen(QPen(QColor(150, 60, 220, 150), 1))
        p.drawRect(QRectF(35, 84, 30, 48))
        p.setBrush(c)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(50, 141), 2.5, 2.5)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(c, 2))
        for r in (9, 16, 23):
            p.drawArc(QRectF(50 - r, 66 - r, 2 * r, 2 * r), 40 * 16, 100 * 16)
        p.setPen(QPen(QColor(150, 60, 220, 90), 1))
        p.drawLine(18, 40, 18, 160)
        p.drawLine(18, 40, 30, 40)
    def _dibujar_cartas(self, p):
        cx, cy = 215, 195
        w, h = self._cw, self._ch
        for k in (3, 2, 1):
            p.save()
            p.translate(cx - k * 13, cy - k * 11)
            p.rotate(-5 - k * 1.2)
            ruta = self._ruta_corte(-w / 2, -h / 2, w, h)
            p.setPen(QPen(QColor(215, 50, 70, 90 - k * 20), 1.5))
            p.setBrush(QColor(120, 15, 35, 26))
            p.drawPath(ruta)
            p.restore()
        p.save()
        p.translate(cx, cy)
        p.rotate(-5)
        x, y = -w / 2, -h / 2
        ruta = self._ruta_corte(x, y, w, h)
        p.fillPath(ruta, QColor(30, 4, 10, 235))
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(215, 50, 70, 70), 9))
        p.drawPath(ruta)
        p.setPen(QPen(QColor(225, 55, 75), 3))
        p.drawPath(ruta)
        fx, fy = int(x + 8), int(y + 8)
        p.save()
        p.setClipRect(QRect(fx, fy, self._fw, self._fh))
        p.drawPixmap(fx, fy, self.face_pm)
        if self._glitch:
            p.setOpacity(0.35)
            p.drawPixmap(fx + 5, fy, self.face_pm)
            p.setOpacity(1.0)
            for sy, sh, sdx in self._slices:
                p.drawPixmap(QRect(fx + sdx, fy + sy, self._fw, sh), self.face_pm, QRect(0, sy, self._fw, sh))
        p.restore()
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        p.setPen(QColor(225, 55, 75))
        p.drawText(QPointF(x + 10, y + h - 28), "GENGAR // ID_0666")
        p.setPen(Qt.NoPen)
        for bx, bw in self._barras:
            p.setBrush(QColor(215, 50, 70, 170))
            p.drawRect(QRectF(x + 8 + bx, y + h - 20, bw, 9))
        for i in range(7):
            p.fillRect(QRectF(x - 14, y + 30 + i * 16, 5, 5), QColor(215, 50, 70, 170 - i * 20))
        p.restore()
    def _dibujar_textos(self, p):
        x0 = 350
        p.setFont(QFont("Consolas", 11))
        p.setPen(QColor(140, 125, 175, 160))
        p.drawText(QPointF(x0, 116), "GNG_ECTO_000666")
        fn = QFont("Bahnschrift", 54, QFont.Bold)
        fn.setLetterSpacing(QFont.AbsoluteSpacing, 4)
        if self._glitch:
            self._texto(p, x0, 204, "GENGAR", fn, QColor(200, 40, 60, 150), 0, dx=-5)
            self._texto(p, x0, 204, "GENGAR", fn, QColor(150, 60, 220, 130), 0, dx=5)
        self._texto(p, x0, 204, "GENGAR", fn, _I_VERDE_NEON, 1.0)
        if self._glitch:
            p.save()
            p.setClipRect(QRectF(x0 - 20, self._banda, 640, 12))
            self._texto(p, x0, 204, "GENGAR", fn, QColor(57, 255, 120, 220), 0, dx=14)
            p.restore()
        fi = QFont("Bahnschrift", 28, QFont.Bold)
        fi.setLetterSpacing(QFont.AbsoluteSpacing, 3)
        col = QColor(215, 48, 68, 255 if self._parpadeo else 170)
        self._texto(p, x0, 262, "INCOMING CALL", fi, col, 0.9)
    def _dibujar_botones(self, p):
        for rect, texto, hover, muesca in (
            (self.rect_answer, "ANSWER", self._hover == "answer", False),
            (self.rect_reject, "REJECT", self._hover == "reject", True),
        ):
            kx, ky = rect.x() + 6, rect.y() + 8
            ruta = self._ruta_corte(kx, ky, 54, 54, corte=12)
            p.fillPath(ruta, QColor(215, 50, 70, 110 if hover else 30))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(215, 50, 70, 70), 7))
            p.drawPath(ruta)
            p.setPen(QPen(_I_ROJO, 2.5))
            p.drawPath(ruta)
            p.setFont(QFont("Bahnschrift", 24, QFont.Bold))
            p.setPen(QColor(255, 255, 255) if hover else _I_ROJO)
            p.drawText(QRect(kx, ky, 54, 54), Qt.AlignCenter, "T")
            p.setPen(Qt.NoPen)
            p.setBrush(_I_ROJO)
            p.drawEllipse(QPointF(kx + 40, ky + 9), 1.8, 1.8)
            if muesca:
                p.drawPolygon(QPolygonF([QPointF(kx + 22, ky + 54), QPointF(kx + 32, ky + 54), QPointF(kx + 27, ky + 62)]))
            ft = QFont("Bahnschrift", 24, QFont.Bold)
            ft.setLetterSpacing(QFont.AbsoluteSpacing, 2)
            self._texto(p, kx + 76, ky + 38, texto, ft, QColor(190, 255, 215) if hover else _I_VERDE_NEON, 1.0 if hover else 0.6)
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.save()
        p.translate(self._gx // 3 if self._glitch else 0, 0)
        self._dibujar_telefono(p)
        self._dibujar_cartas(p)
        self._dibujar_textos(p)
        self._dibujar_botones(p)
        p.restore()
        if self._glitch:
            p.setPen(Qt.NoPen)
            for r in self._rects:
                p.setBrush(QColor(150, 60, 220, 110))
                p.drawRect(r)
        p.end()
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
class IntroAnimacion(QWidget):
    intro_terminada = Signal()
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.ArrowCursor)
        pantalla = QApplication.primaryScreen().geometry()
        self.ancho = pantalla.width()
        self.alto = pantalla.height()
        self.setGeometry(pantalla)
        self._fase = 1
        self._cerrando = False
        self._anim_caida = None
        self._anim_flotar = None
        self._anim_salida = None
        self._timer_espera = None
        self._alfa_fondo = 1.0
        self._anim_desv = None
        self.luna = IntroLuna(self, diametro=150)
        self.luna.move(self.ancho // 2 - self.luna.width() // 2, 30 - (self.luna.height() - 150) // 2)
        self.luna.show()
        self.niebla = IntroNiebla(self, self.ancho, self.alto, 105)
        self.niebla.move(0, 0)
        self.niebla.show()
        self.panel = IntroPanelLlamada(self, RUTA_CARA)
        self.panel.move((self.ancho - self.panel.width()) // 2, (self.alto - self.panel.height()) // 2 + 70)
        self.panel.callback_answer = self._responder
        self.panel.callback_reject = self._rechazar
        self.panel.show()
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
        self.bocadillo_intro = IntroBocadillo(self, "¿Que pasa tio?")
        self.bocadillo_intro.hide()
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()
    def paintEvent(self, _):
        p = QPainter(self)
        p.setOpacity(self._alfa_fondo)
        p.fillRect(self.rect(), QColor(0, 0, 0))
        g = QRadialGradient(QPointF(self.ancho / 2, 100), self.ancho * 0.6)
        g.setColorAt(0.0, QColor(40, 10, 70, 90))
        g.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), QBrush(g))
        p.end()
    def keyPressEvent(self, e):
        if self._fase == 1 and e.key() == Qt.Key_T:
            self._responder()
        elif self._fase == 1 and e.key() == Qt.Key_Escape:
            self._rechazar()
        else:
            super().keyPressEvent(e)
    def _rechazar(self):
        if self._fase != 1:
            return
        QApplication.quit()
        sys.exit()
    def _responder(self):
        if self._fase != 1:
            return
        self._fase = 3
        self.panel._t_glitch.stop()
        self.panel._t_parp.stop()
        self.panel.hide()
        self.panel.deleteLater()
        self._iniciar_caida()
    def _centro_y(self):
        return (self.alto - self.sprite.height()) // 2
    def _iniciar_caida(self):
        x = (self.ancho - self.sprite.width()) // 2
        self.sprite.move(x, -200)
        self.sprite.show()
        self.sprite.raise_()
        self._anim_caida = QPropertyAnimation(self.sprite, b"pos", self)
        self._anim_caida.setDuration(1400)
        self._anim_caida.setStartValue(QPoint(x, -200))
        self._anim_caida.setEndValue(QPoint(x, self._centro_y()))
        self._anim_caida.setEasingCurve(QEasingCurve.OutBounce)
        self._anim_caida.finished.connect(self._al_llegar_centro)
        self._anim_caida.start()
    def _al_llegar_centro(self):
        x = (self.ancho - self.sprite.width()) // 2
        y = self._centro_y()
        self._anim_flotar = QPropertyAnimation(self.sprite, b"pos", self)
        self._anim_flotar.setDuration(2000)
        self._anim_flotar.setLoopCount(-1)
        self._anim_flotar.setStartValue(QPoint(x, y))
        self._anim_flotar.setKeyValueAt(0.5, QPoint(x, y - 28))
        self._anim_flotar.setEndValue(QPoint(x, y))
        self._anim_flotar.setEasingCurve(QEasingCurve.InOutSine)
        self._anim_flotar.start()
        self._iniciar_desvanecer()
        bx = x + self.sprite.width() // 2 - self.bocadillo_intro.width() // 2
        by = y - self.bocadillo_intro.height() - 50
        self.bocadillo_intro.move(bx, by)
        self.bocadillo_intro.show()
        self.bocadillo_intro.raise_()
        self._timer_espera = QTimer(self)
        self._timer_espera.setSingleShot(True)
        self._timer_espera.timeout.connect(self._iniciar_salida)
        self._timer_espera.start(3000)
    def _iniciar_desvanecer(self):
        self._anim_desv = QVariantAnimation(self)
        self._anim_desv.setDuration(2800)
        self._anim_desv.setStartValue(1.0)
        self._anim_desv.setEndValue(0.0)
        self._anim_desv.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim_desv.valueChanged.connect(self._set_desvanecer)
        self._anim_desv.start()
    def _set_desvanecer(self, v):
        v = float(v)
        self._alfa_fondo = v
        self.luna.alfa = v
        self.niebla.alfa = v
        self.update()
    def _iniciar_salida(self):
        if self._anim_flotar is not None:
            self._anim_flotar.stop()
        self.bocadillo_intro.hide()
        inicio = self.sprite.pos()
        self._anim_salida = QPropertyAnimation(self.sprite, b"pos", self)
        self._anim_salida.setDuration(450)
        self._anim_salida.setStartValue(inicio)
        self._anim_salida.setEndValue(QPoint(inicio.x(), self.alto))
        self._anim_salida.setEasingCurve(QEasingCurve.InCubic)
        self._anim_salida.finished.connect(self._terminar)
        self._anim_salida.start()
    def _terminar(self):
        if self._cerrando:
            return
        self._cerrando = True
        self.luna._timer.stop()
        self.niebla._timer.stop()
        self.close()
        self.intro_terminada.emit()
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
        pet_window.respuesta_para_chat.connect(lambda t: chat_window.agregar_mensaje("Gengar", t))
        pet_window.respuesta_para_chat.connect(lambda t: chat_window.detener_typing())
        pet_window.abrir_chat.connect(mostrar_chat)
        def accion_chat(a):
            mapeo = {"bola": "bola_fantasma"}
            pet_window.ejecutar(mapeo.get(a, a))
        chat_window.accion_rapida.connect(accion_chat)
        puente = Puente(PUERTO)
        puente.evento.connect(pet_window.evento_claude)
        if not puente.iniciar():
            print(f"[Gengar] El puerto {PUERTO} esta ocupado: ¿ya hay otro Gengar abierto?")
        atajo = FiltroAtajo(pet_window.alternar_guardado)
        app.installNativeEventFilter(atajo)
        app.aboutToQuit.connect(atajo.liberar)
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