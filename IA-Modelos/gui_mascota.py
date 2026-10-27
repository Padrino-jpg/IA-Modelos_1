"""
================================================================================
GENGAR - COMPAÑERO DE ESCRITORIO (EDICIÓN CYBERDECK OVERDRIVE X1000 PRO MAX)
================================================================================
Autor: Ruben / Asistente IA
Estilo: Cyberpunk 2077 / Ghost in the Shell / Matrix / Capri.
Descripción:
Este script representa el pináculo del proyecto Padrino. Incluye:
1. Un motor de físicas 2D para la mascota (gravedad, arrastre, colisiones).
2. Un sistema de animaciones sprites cargadas dinámicamente.
3. Una interfaz de chat totalmente rediseñada con estética CRT (pantalla de tubo),
   líneas de escaneo, bordes neón animados y fuentes monoespaciadas.
4. Integración profunda con la IA Padrino mediante hilos (QThread) para no
   bloquear la interfaz de usuario.
5. Integración con el hardware (CPU/RAM) en tiempo real mediante 'psutil'.
6. Sistema de "Sueño Profundo" con efecto visual de ojos flotantes.
7. "Posesión" de ventanas de Windows (tinte rojo y ojos glitcheados).
8. Drag & Drop para analizar archivos directamente.
9. Panel de Misión Cyberpunk flotante al recibir respuestas de la IA.
10. Efectos de sonido nativos generados por la placa base (winsound).
11. Pantalla de llamada entrante de Delamain (Réplica exacta Cyberpunk 2077).
12. Rastro de partículas, respiración idle, sombra dinámica y holograma.
13. Historial de chat con avatares, typing indicator y atajos de teclado.
14. Modo Cazador de Cursor, Reacción a la Música y Cyberpsychosis.
15. Selector de Skin, Focus Mode visual y Modo DND.
================================================================================
"""

import sys
import os
import random
import time
import datetime
import html
import ctypes
import math
import json
import threading
import traceback

# Importación de tipos de datos de Windows para interactuar con la API nativa
from ctypes import wintypes

# Intentar importar psutil para el monitoreo de hardware (HUD)
try:
    import psutil
except ImportError:
    psutil = None
    print("[AVISO] psutil no está instalado. El HUD no mostrará datos reales.")

# Intentar importar winsound para los efectos de sonido nativos
try:
    import winsound
except ImportError:
    winsound = None
    print("[AVISO] winsound no está disponible. Los sonidos no funcionarán.")

# Intentar importar pycaw para la detección de audio (Reacción a la música)
try:
    from pycaw.pycaw import AudioUtilities
    _PYCAW_OK = True
except ImportError:
    _PYCAW_OK = False
    print("[AVISO] pycaw no está instalado. La reacción a la música no funcionará.")

# Importaciones de PySide6 (Qt) para toda la interfaz gráfica
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextBrowser,
    QSystemTrayIcon,
    QMenu,
    QInputDialog,
    QPushButton,
    QDialog,
    QFormLayout,
    QSpinBox,
    QColorDialog,
    QDialogButtonBox,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QMessageBox,
    QSizePolicy
)
from PySide6.QtGui import (
    QPixmap,
    QColor,
    QPainter,
    QTransform,
    QCursor,
    QIcon,
    QAction,
    QPen,
    QBrush,
    QFont,
    QPainterPath,
    QPolygon,
    QLinearGradient,
    QRadialGradient,
    QFontMetrics,
    QImage
)
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QTimer,
    QPoint,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QParallelAnimationGroup,
    QSize
)

# Intentar importar pygetwindow para interactuar con las ventanas del SO
try:
    import pygetwindow as gw
except Exception:
    gw = None
    print("[AVISO] pygetwindow no está instalado. La interacción con ventanas no funcionará.")

# ==============================================================================
# SECCIÓN 1: CONFIGURACIÓN GLOBAL Y CONSTANTES
# ==============================================================================

# Determinamos la ruta base del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Posibles rutas para las imágenes de Gengar
RUTAS_POSIBLES_IMAGENES = [
    "D:/IA-Modelos/gengar_img",
    os.path.join(BASE_DIR, "gengar_img")
]

# Seleccionamos la primera ruta que exista
RUTA_IMAGENES = RUTAS_POSIBLES_IMAGENES[0]
for ruta in RUTAS_POSIBLES_IMAGENES:
    if os.path.isdir(ruta):
        RUTA_IMAGENES = ruta
        break

# Ruta específica para la cara del Gengar (usada en el chat y paneles)
RUTA_CARA_GENGAR = os.path.join(RUTA_IMAGENES, "cara_gengar.jpg")

# Constantes de animación
FRAMES_POR_SEGUNDO = 12
TAMANO_SPRITE = 130

# AUMENTAMOS EL ANCHO Y ALTO DE LA VENTANA para que quepa el texto
ANCHO_VENTANA_PET = 350
ALTO_VENTANA_PET = 400

# Coordenadas para centrar el sprite en la ventana (El sprite se mantiene pegado al suelo)
SPRITE_X = (ANCHO_VENTANA_PET - TAMANO_SPRITE) // 2
SPRITE_Y = ALTO_VENTANA_PET - TAMANO_SPRITE

# Ajustes de hundimiento en el suelo (para que no flote)
SINK_DE_PIE = 0
SINK_SENTADO = 25

# Estados en los que Gengar puede tomar decisiones autónomas
ESTADOS_LIBRES = ("patrulla", "quieto_de_pie", "sentado")

# Tiempo en segundos para entrar en modo de sueño profundo por inactividad
TIEMPO_SUENO_PROFUNDO = 180

# Tiempo en segundos para asomarse por el borde si no se mueve el ratón
TIEMPO_ASOMARSE = 60

# Títulos de ventanas que el script debe ignorar (no intentar sentarse en ellas)
TITULOS_IGNORADOS = (
    "Program Manager",
    "Chat con Padrino",
    "Windows Input Experience",
    "GengarMascota",
    "Configuración de Gengar",
    "CYBERDECK OVERRIDE"
)

# Configuración del registro de Windows para el inicio automático
CLAVE_REGISTRO_INICIO = r"Software\Microsoft\Windows\CurrentVersion\Run"
NOMBRE_REGISTRO_INICIO = "GengarMascotaCyberdeck"

# Constante de la API de Windows para obtener el borde exacto de la ventana
DWMWA_EXTENDED_FRAME_BOUNDS = 9

# COLORES GLOBALES (Se pueden cambiar con el Skin Selector)
COLOR_PRIMARIO = "#00ffff"    # Cian
COLOR_SECUNDARIO = "#ff00ff"  # Magenta

# Variable global para el modo DND (No Molestar)
MODO_DND = False

# ==============================================================================
# SECCIÓN 2: DEFINICIÓN DE ANIMACIONES
# ==============================================================================

# Animación de patrulla (caminar)
ANIM_PATRULLA = ["shime2.png", "shime2b.png", "shime2.png", "shime2c.png", "shime2a.png"]
# Animación de estar quieto de pie (respirando/pestañeando)
ANIM_QUIETO = ["shime1.png", "shime1.png", "shime1.png", "shime1.png", "shime1a.png"]
# Animación de estar sentado
ANIM_SENTADO = ["shime30.png", "shime31.png", "shime31a.png", "shime31b.png", "shime32.png", "shime32a.png", "shime32b.png", "shime32c.png", "shime33.png"]
# Animación de pensando
ANIM_PENSANDO = ["shime47.png", "shime47a.png", "shime47b.png", "shime47a.png"]
# Animación de dormir
ANIM_DORMIR = ["shime20.png", "shime21.png", "shime20a.png", "shime21a.png"]
# Animación de baile
ANIM_BAILAR = ["dance1.png", "dance1b.png", "dance1c.png", "dance1d.png", "dance2.png", "dance2b.png", "dance3.png", "dance3b.png", "dance3c.png", "dance3d.png"]
# Animación de hipnosis
ANIM_HIPNOSIS = ["shime38.png", "shime38a.png", "shime39.png", "shime39a.png", "shime40.png", "shime40a.png", "shime41.png", "shime41a.png"]
# Animación de caída
ANIM_CAER = ["shime4.png"]
# Animación de bola fantasma
ANIM_BOLA = ["shime42.png", "shime42a.png", "shime43.png", "shime44.png", "shime45.png", "shime45a.png", "shime46.png", "shime46a.png"]
# Animación de humo (desaparecer)
ANIM_HUMO = ["shime15.png", "shime16.png", "shime17.png"]
# Animación de ser arrastrado
ANIM_ARRASTRADO = ["shime5.png", "shime6.png", "shime7.png", "shime6.png"]
# Animación de caricia (clic en la cabeza)
ANIM_CARICIA = ["shime18.png", "shime19.png", "shime18.png"]
# Animación de travesura
ANIM_TRAVESURA = ["shime34.png", "shime34a.png", "shime34b.png", "shime34c.png"]
# Animación de asomado
ANIM_ASOMADO = ["shime9.png", "shime10.png"]
# Animación de trepar pared izquierda
ANIM_PARED_IZQUIERDA = ["shime12.png", "shime12a.png", "shime13.png", "shime14.png"]
# Animación de trepar pared derecha
ANIM_PARED_DERECHA = ["shime12.png", "shime12a.png", "shime13.png", "shime14.png"]

# Diccionario maestro de animaciones
DICCIONARIO_ANIMACIONES = {
    "patrulla": ANIM_PATRULLA, "trepar_ir": ANIM_PATRULLA, "quieto_de_pie": ANIM_QUIETO,
    "sentado": ANIM_SENTADO, "en_ventana": ANIM_SENTADO, "pensando": ANIM_PENSANDO,
    "dormir": ANIM_DORMIR, "bailar": ANIM_BAILAR, "hipnosis": ANIM_HIPNOSIS,
    "caer": ANIM_CAER, "bola_fantasma": ANIM_BOLA, "humo": ANIM_HUMO,
    "arrastrado": ANIM_ARRASTRADO, "caricia": ANIM_CARICIA, "travesura": ANIM_TRAVESURA,
    "cursor": ANIM_TRAVESURA, "asomado": ANIM_ASOMADO, "trepar_izq": ANIM_PARED_IZQUIERDA,
    "trepar_der": ANIM_PARED_DERECHA,
}

# Animaciones que no deben ser volteadas horizontalmente
ANIMACIONES_SIN_VOLTEAR = set()

# Multiplicador de frames para ralentizar ciertas animaciones
MULTIPLICADOR_FRAMES = {
    "quieto_de_pie": 3, "sentado": 4, "en_ventana": 4, "dormir": 6,
    "pensando": 3, "hipnosis": 2, "humo": 4, "caricia": 4, "asomado": 5, "arrastrado": 2
}

# Frases aleatorias para cuando Gengar está aburrido
FRASES_PENSAMIENTOS = [
    "Qué aburrido estoy...", "Oye, ¿sigues ahí?", "Me apetece un café, tío.",
    "¿A que no sabes lo que he pensado?", "Estoy vigilando tu código...",
    "Tío, tienes muchas pestañas abiertas.", "Podríamos dominar el mundo, pero paso.",
    "¿Hacemos algo o qué?", "Esto está muy tranquilo... demasiado.", "Ruben, ¿me oyes?"
]

# Frases para cuando le acaricias la cabeza
FRASES_CARICIA = [
    "Mmm... vale, un poquito.", "Eso se agradece, tío.", "No se lo cuentes a nadie.",
    "Más a la izquierda...", "Qué manos más frías, tío."
]

# ==============================================================================
# SECCIÓN 3: UTILIDADES Y EFECTOS (SONIDO, VENTANAS, REGISTRO)
# ==============================================================================

def reproducir_sonido(tipo="pop"):
    if winsound and sys.platform == "win32":
        try:
            if tipo == "pop": winsound.Beep(1200, 30)
            elif tipo == "type": winsound.Beep(2000, 10)
            elif tipo == "error": winsound.Beep(400, 150); winsound.Beep(300, 200)
            elif tipo == "success": winsound.Beep(800, 50); winsound.Beep(1200, 80)
            elif tipo == "bostezo": winsound.Beep(300, 400)
        except Exception: pass
    else: QApplication.beep()

def obtener_rectangulo_visible(hwnd):
    rectangulo = wintypes.RECT()
    try:
        ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rectangulo), ctypes.sizeof(rectangulo))
    except Exception:
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rectangulo))
    return rectangulo

def comprobar_inicio_automatico():
    if sys.platform != "win32": return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLAVE_REGISTRO_INICIO) as clave:
            winreg.QueryValueEx(clave, NOMBRE_REGISTRO_INICIO)
            return True
    except OSError: return False

def configurar_inicio_automatico(activar):
    if sys.platform != "win32": return
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLAVE_REGISTRO_INICIO, 0, winreg.KEY_SET_VALUE) as clave:
            if activar:
                if getattr(sys, "frozen", False): comando = f'"{sys.executable}"'
                else:
                    python_path = sys.executable
                    pythonw_path = python_path.replace("python.exe", "pythonw.exe")
                    if os.path.exists(pythonw_path): python_path = pythonw_path
                    comando = f'"{python_path}" "{os.path.abspath(__file__)}"'
                winreg.SetValueEx(clave, NOMBRE_REGISTRO_INICIO, 0, winreg.REG_SZ, comando)
            else:
                try: winreg.DeleteValue(clave, NOMBRE_REGISTRO_INICIO)
                except FileNotFoundError: pass
    except Exception as e: print(f"Error al configurar el inicio: {e}")

def obtener_pico_audio():
    if not _PYCAW_OK: return 0
    try:
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        meter = device._dev.Activate(volume._dev._iid, 0, None)
        return int(meter.GetMeterInformation().GetPeakValue() * 100)
    except Exception: return 0

# ==============================================================================
# SECCIÓN 4: PANEL DE MISIÓN CYBERPUNK (ESTILO CAPRI)
# ==============================================================================

class PanelMisionCyberpunk(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(440, 190)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.lbl_avatar = QLabel(self)
        self.lbl_avatar.setGeometry(25, 25, 64, 64)
        self.lbl_avatar.setStyleSheet(f"border: 3px solid {COLOR_PRIMARIO}; background-color: #000;")
        if os.path.exists(RUTA_CARA_GENGAR):
            pixmap = QPixmap(RUTA_CARA_GENGAR).scaled(64, 64, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.lbl_avatar.setPixmap(pixmap)
        
        self.lbl_header = QLabel(self)
        self.lbl_header.setGeometry(110, 25, 300, 20)
        self.lbl_header.setStyleSheet(f"color: {COLOR_SECUNDARIO}; font-family: 'Consolas', monospace; font-weight: bold; font-size: 12px;")
        
        self.lbl_tag = QLabel(self)
        self.lbl_tag.setGeometry(340, 25, 75, 22)
        self.lbl_tag.setAlignment(Qt.AlignCenter)
        
        self.lbl_titulo = QLabel(self)
        self.lbl_titulo.setGeometry(110, 50, 300, 20)
        self.lbl_titulo.setStyleSheet("color: #ffffff; font-family: 'Consolas', monospace; font-weight: bold; font-size: 15px; text-transform: uppercase;")
        
        self.lbl_desc = QLabel(self)
        self.lbl_desc.setGeometry(110, 80, 305, 55)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet(f"color: {COLOR_PRIMARIO}; font-family: 'Consolas', monospace; font-size: 11px;")
        
        self.lbl_stats = QLabel(self)
        self.lbl_stats.setGeometry(110, 145, 300, 20)
        self.lbl_stats.setStyleSheet(f"color: {COLOR_SECUNDARIO}; font-family: 'Consolas', monospace; font-size: 11px;")
        
        self.timer_ocultar = QTimer(self)
        self.timer_ocultar.setSingleShot(True)
        self.timer_ocultar.timeout.connect(self.hide)

    def mostrar_mision(self, titulo, descripcion, exito=True, tiempo_total=0.0):
        self.lbl_header.setText("PADRINO.EXE // NET_RUNNER")
        if exito:
            self.lbl_tag.setText("[ OK ]")
            self.lbl_tag.setStyleSheet(f"background-color: {COLOR_PRIMARIO}; color: #000000; font-weight: bold; font-family: 'Consolas'; font-size: 11px; border-radius: 2px;")
            self.lbl_titulo.setText("HACKEO COMPLETADO")
        else:
            self.lbl_tag.setText("[ FAIL ]")
            self.lbl_tag.setStyleSheet("background-color: #ff0000; color: #ffffff; font-weight: bold; font-family: 'Consolas'; font-size: 11px; border-radius: 2px;")
            self.lbl_titulo.setText("FALLO DE SISTEMA")
        texto_corto = descripcion[:120] + "..." if len(descripcion) > 120 else descripcion
        self.lbl_desc.setText(texto_corto)
        self.lbl_stats.setText(f"// 1 ACCION // {tiempo_total:.1f}s // ENCRIPTADO")
        self.show()
        self.raise_()
        self.timer_ocultar.start(8000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        ancho, alto = self.width(), self.height()
        path.moveTo(30, 0); path.lineTo(ancho - 30, 0); path.lineTo(ancho, 30)
        path.lineTo(ancho, alto - 30); path.lineTo(ancho - 30, alto); path.lineTo(30, alto)
        path.lineTo(0, alto - 30); path.lineTo(0, 30); path.closeSubpath()
        
        gradiente = QLinearGradient(0, 0, ancho, alto)
        gradiente.setColorAt(0, QColor(10, 5, 20, 240))
        gradiente.setColorAt(1, QColor(20, 0, 30, 240))
        painter.fillPath(path, gradiente)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(COLOR_PRIMARIO), 15, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setOpacity(0.2); painter.drawPath(path); painter.setOpacity(1.0)
        
        painter.setPen(QPen(QColor(COLOR_SECUNDARIO), 3))
        painter.drawLine(30, 0, 60, 0); painter.drawLine(0, 30, 0, 60)
        painter.drawLine(ancho - 30, alto, ancho - 60, alto); painter.drawLine(ancho, alto - 30, ancho, alto - 60)

# ==============================================================================
# SECCIÓN 5: COMPONENTES DE LA INTERFAZ
# ==============================================================================

class OverlayParticulas(QWidget):
    """Capa invisible a pantalla completa para dibujar las partículas del rastro."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.particulas = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar)
        self.timer.start(30)

    def agregar_particula(self, x, y, color_str):
        self.particulas.append({
            "x": x, "y": y, "color": QColor(color_str),
            "alpha": 255, "dy": random.uniform(-1.5, 1.5)
        })

    def _actualizar(self):
        for p in self.particulas:
            p["y"] += p["dy"]
            p["alpha"] -= 15
        self.particulas = [p for p in self.particulas if p["alpha"] > 0]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        for p in self.particulas:
            color = QColor(p["color"])
            color.setAlpha(p["alpha"])
            painter.setBrush(color)
            painter.drawEllipse(int(p["x"]), int(p["y"]), 6, 6)

class SombraMascota(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(TAMANO_SPRITE, 20)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.factor_escala = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 0, 0, 120)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        ancho = int(self.width() * self.factor_escala)
        alto = int(self.height() * self.factor_escala)
        painter.drawEllipse((self.width() - ancho) // 2, 0, ancho, alto)

class BocadilloComic(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: transparent; color: {COLOR_PRIMARIO}; font-size: 13px; font-family: 'Consolas'; font-weight: bold;")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMargin(10)
        
        self.sombra = QGraphicsDropShadowEffect(self)
        self.sombra.setBlurRadius(15)
        self.sombra.setColor(QColor(COLOR_PRIMARIO))
        self.sombra.setOffset(0, 0)
        self.setGraphicsEffect(self.sombra)
        
        self.texto_completo = ""
        self.texto_actual = ""
        self.indice = 0
        
        self.timer_typewriter = QTimer(self)
        self.timer_typewriter.timeout.connect(self._efecto_maquina_escribir)

    def establecer_texto(self, texto):
        self.texto_completo = texto
        self.texto_actual = ""
        self.indice = 0
        self.setText("")
        
        metrics = QFontMetrics(self.font())
        ancho_util = ANCHO_VENTANA_PET - 30
        rect = metrics.boundingRect(0, 0, ancho_util, 1000, Qt.TextWordWrap, texto)
        alto_necesario = max(60, min(rect.height() + 30, 280))
        
        nuevo_x = (ANCHO_VENTANA_PET - ancho_util) // 2
        nuevo_y = SPRITE_Y - alto_necesario - 10
        self.setGeometry(nuevo_x, nuevo_y, ancho_util, alto_necesario)
        self.timer_typewriter.start(25)

    def _efecto_maquina_escribir(self):
        if self.indice < len(self.texto_completo):
            self.texto_actual += self.texto_completo[self.indice]
            self.setText(self.texto_actual + "_")
            self.indice += 1
            if self.indice % 3 == 0: reproducir_sonido("type")
        else:
            self.timer_typewriter.stop()
            self.setText(self.texto_completo)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(4, 4, -4, -15)
        
        gradiente = QLinearGradient(0, 0, 0, self.height())
        gradiente.setColorAt(0, QColor(10, 0, 20, 220))
        gradiente.setColorAt(1, QColor(0, 10, 20, 220))
        painter.setBrush(gradiente)
        painter.setPen(Qt.NoPen)
        
        puntos = [QPoint(15, rect.top()), QPoint(rect.right() - 15, rect.top()),
                  QPoint(rect.right(), rect.top() + 15), QPoint(rect.right(), rect.bottom()),
                  QPoint(rect.left(), rect.bottom()), QPoint(rect.left(), rect.top() + 15)]
        painter.drawPolygon(puntos)
        
        puntos_cola = [QPoint(self.width() // 2 - 10, rect.bottom()),
                       QPoint(self.width() // 2 + 10, rect.bottom()), QPoint(self.width() // 2, self.height())]
        painter.setBrush(QColor(0, 10, 20, 220))
        painter.drawPolygon(puntos_cola)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(COLOR_PRIMARIO), 3))
        painter.drawPolygon(puntos); painter.drawPolygon(puntos_cola)
        
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawPolygon(puntos)
        painter.drawLine(puntos_cola[0], puntos_cola[2]); painter.drawLine(puntos_cola[2], puntos_cola[1])
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        
        super().paintEvent(event)

class HUDHardware(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(150, 95)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.parent = parent
        
        self.lbl_stats = QLabel(self)
        self.lbl_stats.setGeometry(0, 0, 150, 95)
        self.lbl_stats.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_stats.setStyleSheet(f"background-color: rgba(5, 5, 10, 220); color: {COLOR_PRIMARIO}; border: 1px solid {COLOR_SECUNDARIO}; padding-left: 10px; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(10)
        sombra.setColor(QColor(COLOR_SECUNDARIO))
        sombra.setOffset(0, 0)
        self.lbl_stats.setGraphicsEffect(sombra)
        
        self.timer_actualizar = QTimer(self)
        self.timer_actualizar.timeout.connect(self.actualizar_datos)
        self.timer_actualizar.start(1000)
        self.actualizar_datos()

    def actualizar_datos(self):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        focus_str = ""
        if getattr(self.parent, 'fase_estudio', None):
            resta = int(self.parent.fin_estudio - time.time())
            if resta > 0:
                m, s = divmod(resta, 60)
                focus_str = f"\nFOCUS: {m:02d}:{s:02d}"
        
        if psutil:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            texto = f"SYS.TIME: {hora}\nCPU.LOAD: {cpu}%\nRAM.USED: {ram}%\nSTATUS: ONLINE{focus_str}"
        else:
            texto = f"SYS.TIME: {hora}\nCPU.LOAD: --\nRAM.USED: --\nSTATUS: ONLINE{focus_str}"
            
        self.lbl_stats.setText(texto)

    def showEvent(self, event):
        super().showEvent(event)
        self.move(self.parent.x() + self.parent.width() + 10, self.parent.y() + 20)

# ==============================================================================
# SECCIÓN 6: OVERLAYS
# ==============================================================================

class OverlayGlitch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.barras_glitch = []
        self.paso_actual = 0
        self.timer_animacion = QTimer(self)
        self.timer_animacion.timeout.connect(self._siguiente_paso)

    def lanzar_glitch(self, geometria):
        self.setGeometry(geometria)
        self.paso_actual = 0
        self._generar_barras()
        self.show()
        self.timer_animacion.start(50)

    def _generar_barras(self):
        self.barras_glitch = []
        for _ in range(random.randint(15, 30)):
            y = random.randint(0, self.height())
            alto = random.randint(5, 50)
            color = QColor(random.choice([COLOR_PRIMARIO, COLOR_SECUNDARIO, "#ff0000"]))
            self.barras_glitch.append((y, alto, color))

    def _siguiente_paso(self):
        self.paso_actual += 1
        if self.paso_actual >= 8:
            self.timer_animacion.stop()
            self.hide()
            return
        self._generar_barras()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        for y, alto, color in self.barras_glitch:
            color.setAlpha(80)
            painter.fillRect(0, y, self.width(), alto, color)

class OverlayPosesion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hwnd_objetivo = 0
        self.parpadeo = 0
        self.timer_seguimiento = QTimer(self)
        self.timer_seguimiento.timeout.connect(self._actualizar_posicion)

    def poseer_ventana(self, hwnd):
        self.hwnd_objetivo = hwnd
        self.timer_seguimiento.start(50)
        self.show()

    def _actualizar_posicion(self):
        if not self.hwnd_objetivo or not ctypes.windll.user32.IsWindowVisible(self.hwnd_objetivo):
            self.timer_seguimiento.stop()
            self.hide()
            return
        rect = obtener_rectangulo_visible(self.hwnd_objetivo)
        dpr = QApplication.primaryScreen().devicePixelRatio()
        self.setGeometry(int(rect.left/dpr), int(rect.top/dpr), int((rect.right-rect.left)/dpr), int((rect.bottom-rect.top)/dpr))
        self.parpadeo = (self.parpadeo + 1) % 20
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 0, 50, 40))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0, 220))
        centro_y = self.height() // 2
        alto_ojo = 5 if self.parpadeo < 2 else 50
        painter.drawEllipse(self.width()//2 - 85, centro_y - alto_ojo//2, 50, alto_ojo)
        painter.drawEllipse(self.width()//2 + 35, centro_y - alto_ojo//2, 50, alto_ojo)

class IndicadorPensando(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(60, 20)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.puntos = 0
        self.timer_animacion = QTimer(self)
        self.timer_animacion.timeout.connect(self._siguiente_punto)

    def iniciar(self):
        self.puntos = 0
        self.timer_animacion.start(300)
        self.show()

    def detener(self):
        self.timer_animacion.stop()
        self.hide()

    def _siguiente_punto(self):
        self.puntos = (self.puntos + 1) % 4
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("Consolas", 12, QFont.Bold))
        painter.setPen(QColor(COLOR_PRIMARIO))
        painter.drawText(self.rect(), Qt.AlignCenter, ">>> " + "." * self.puntos)

# ==============================================================================
# SECCIÓN 7: HILO DE EJECUCIÓN DE LA IA
# ==============================================================================

class HiloIA(QThread):
    respuesta_lista = Signal(str)
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            import ia_puente
            if MODO_DND:
                try:
                    import agente_padrino
                    agente_padrino.MODO_DND = True
                except Exception: pass
            respuesta = ia_puente.obtener_respuesta(self.prompt)
            self.respuesta_lista.emit(str(respuesta))
        except Exception as e:
            self.respuesta_lista.emit(f"Error: {e}")

# ==============================================================================
# SECCIÓN 8: VENTANA DE CHAT CYBERPUNK X1000
# ==============================================================================

class VentanaChatCyberdeck(QWidget):
    mensaje_enviado = Signal(str)
    accion_rapida = Signal(str)
    
    def __init__(self):
        super().__init__()
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
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)

        layout_cabecera = QHBoxLayout()
        self.lbl_avatar = QLabel()
        self.lbl_avatar.setFixedSize(60, 60)
        self.lbl_avatar.setStyleSheet(f"border: 2px solid {COLOR_PRIMARIO}; background: black;")
        if os.path.exists(RUTA_CARA_GENGAR):
            pixmap = QPixmap(RUTA_CARA_GENGAR).scaled(60, 60, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.lbl_avatar.setPixmap(pixmap)
            
        layout_titulos = QVBoxLayout()
        self.lbl_titulo = QLabel("PADRINO.EXE // NIGHT_CITY_2077")
        self.lbl_titulo.setStyleSheet(f"color: {COLOR_SECUNDARIO}; font-family: 'Consolas'; font-weight: bold; font-size: 14px;")
        self.lbl_estado = QLabel("[ SYSTEM: ONLINE ] [ ENCRYPTION: AES-256 ]")
        self.lbl_estado.setStyleSheet(f"color: {COLOR_PRIMARIO}; font-family: 'Consolas'; font-size: 10px;")
        layout_titulos.addWidget(self.lbl_titulo)
        layout_titulos.addWidget(self.lbl_estado)
        
        self.btn_limpiar = QPushButton("[PURGE_LOG]")
        self.btn_limpiar.setFixedSize(85, 30)
        self.btn_limpiar.setStyleSheet(f"background: transparent; color: {COLOR_PRIMARIO}; font-weight: bold; font-family: 'Consolas'; border: 1px solid {COLOR_PRIMARIO};")
        self.btn_limpiar.clicked.connect(self._limpiar_historial)
        
        self.btn_cerrar = QPushButton("[X]")
        self.btn_cerrar.setFixedSize(30, 30)
        self.btn_cerrar.setStyleSheet("background: transparent; color: #ff0000; font-weight: bold; font-family: 'Consolas'; border: 1px solid #ff0000;")
        self.btn_cerrar.clicked.connect(self.hide)
        
        layout_cabecera.addWidget(self.lbl_avatar)
        layout_cabecera.addLayout(layout_titulos)
        layout_cabecera.addStretch()
        layout_cabecera.addWidget(self.btn_limpiar)
        layout_cabecera.addWidget(self.btn_cerrar)

        self.historial = QTextBrowser()
        self.historial.setStyleSheet(f"""
            QTextBrowser {{ background-color: rgba(0, 0, 0, 150); border: 1px solid {COLOR_PRIMARIO}; color: {COLOR_PRIMARIO}; font-family: 'Consolas', monospace; font-size: 13px; padding: 10px; }}
            QScrollBar:vertical {{ background: #000; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {COLOR_SECUNDARIO}; }}
        """)
        
        self.lbl_typing = QLabel("PADRINO IS TYPING...")
        self.lbl_typing.setStyleSheet(f"color: {COLOR_PRIMARIO}; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        self.lbl_typing.hide()
        self.timer_typing = QTimer(self)
        self.timer_typing.timeout.connect(self._parpadear_typing)
        
        layout_botones = QHBoxLayout()
        self.btn_bola = QPushButton(">> GHOST_ROLL")
        self.btn_bailar = QPushButton(">> OVERRIDE_DANCE")
        self.btn_dormir = QPushButton(">> SLEEP_MODE")
        
        estilo_boton = f"""
            QPushButton {{ background-color: rgba(255, 0, 255, 50); color: {COLOR_SECUNDARIO}; border: 1px solid {COLOR_SECUNDARIO}; padding: 8px; font-family: 'Consolas'; font-size: 11px; font-weight: bold; border-radius: 3px; }}
            QPushButton:hover {{ background-color: {COLOR_SECUNDARIO}; color: #000; }}
        """
        for btn in [self.btn_bola, self.btn_bailar, self.btn_dormir]:
            btn.setStyleSheet(estilo_boton)
            sombra = QGraphicsDropShadowEffect(self)
            sombra.setBlurRadius(10)
            sombra.setColor(QColor(COLOR_SECUNDARIO))
            sombra.setOffset(0, 0)
            btn.setGraphicsEffect(sombra)
        
        self.btn_bola.clicked.connect(lambda: self.accion_rapida.emit("bola"))
        self.btn_bailar.clicked.connect(lambda: self.accion_rapida.emit("bailar"))
        self.btn_dormir.clicked.connect(lambda: self.accion_rapida.emit("dormir"))
        
        layout_botones.addWidget(self.btn_bola)
        layout_botones.addWidget(self.btn_bailar)
        layout_botones.addWidget(self.btn_dormir)

        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText(">> INGRESA COMANDO O MENSAJE...")
        self.input_texto.setStyleSheet(f"background-color: #000; color: {COLOR_PRIMARIO}; border: 1px solid {COLOR_PRIMARIO}; padding: 12px; font-family: 'Consolas'; font-size: 14px; font-weight: bold;")
        
        sombra_input = QGraphicsDropShadowEffect(self)
        sombra_input.setBlurRadius(10)
        sombra_input.setColor(QColor(COLOR_PRIMARIO))
        sombra_input.setOffset(0, 0)
        self.input_texto.setGraphicsEffect(sombra_input)
        self.input_texto.returnPressed.connect(self._enviar_mensaje)

        layout_principal.addLayout(layout_cabecera)
        layout_principal.addSpacing(15)
        layout_principal.addWidget(self.historial)
        layout_principal.addWidget(self.lbl_typing)
        layout_principal.addSpacing(15)
        layout_principal.addLayout(layout_botones)
        layout_principal.addWidget(self.input_texto)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1: self.hide()
        elif event.key() == Qt.Key_F4:
            global MODO_DND
            MODO_DND = not MODO_DND
            self.agregar_mensaje("Sistema", f"MODO DND {'ACTIVADO' if MODO_DND else 'DESACTIVADO'}.")
        else: super().keyPressEvent(event)

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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        ancho, alto = self.width(), self.height()
        path.moveTo(30, 0); path.lineTo(ancho - 30, 0); path.lineTo(ancho, 30)
        path.lineTo(ancho, alto - 30); path.lineTo(ancho - 30, alto); path.lineTo(30, alto)
        path.lineTo(0, alto - 30); path.lineTo(0, 30); path.closeSubpath()
        
        gradiente = QLinearGradient(0, 0, ancho, alto)
        gradiente.setColorAt(0, QColor(5, 5, 15, 240))
        gradiente.setColorAt(1, QColor(15, 0, 20, 240))
        painter.fillPath(path, gradiente)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(COLOR_SECUNDARIO), 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setOpacity(0.15); painter.drawPath(path); painter.setOpacity(1.0)
        
        painter.setPen(QPen(QColor(COLOR_PRIMARIO), 4))
        painter.drawLine(30, 0, 60, 0); painter.drawLine(0, 30, 0, 60)
        painter.drawLine(ancho - 30, alto, ancho - 60, alto); painter.drawLine(ancho, alto - 30, ancho, alto - 60)

        painter.setPen(QPen(QColor(0, 255, 255, 15), 1))
        for y in range(0, alto, 4): painter.drawLine(0, y, ancho, y)
        if random.random() < 0.05:
            painter.setPen(QPen(QColor(0, 255, 255, 100), 2))
            painter.drawLine(0, random.randint(0, alto), ancho, random.randint(0, alto))

    def agregar_mensaje(self, remitente, texto):
        if remitente == "Tú":
            prefijo = "root@night_city:~#"; color = "#ffffff"; avatar_html = "<span style='color:#fff; font-weight:bold;'>[TÚ]</span>"
        elif remitente == "Sistema":
            prefijo = "SYS_ERR:"; color = "#ff0000"; avatar_html = "<span style='color:#ff0000; font-weight:bold;'>[SYS]</span>"
        else:
            prefijo = "PADRINO.AI >"; color = COLOR_PRIMARIO; avatar_html = f"<span style='color:{COLOR_SECUNDARIO}; font-weight:bold;'>[IA]</span>"

        html_mensaje = f'''
        <div style="margin: 8px 0; text-shadow: 0 0 5px {color};">
            {avatar_html} <span style="color: {COLOR_SECUNDARIO}; font-weight: bold;">{prefijo}</span> 
            <span style="color: {color};">{html.escape(texto)}</span>
        </div>
        '''
        self.historial.append(html_mensaje)
        self.historial.verticalScrollBar().setValue(self.historial.verticalScrollBar().maximum())

    def _enviar_mensaje(self):
        texto = self.input_texto.text().strip()
        if not texto: return
        self.input_texto.clear()
        self.agregar_mensaje("Tú", texto)
        
        if texto.startswith("/"):
            comando = texto.lower().strip()
            if comando == "/bailar": self.accion_rapida.emit("bailar"); self.agregar_mensaje("Sistema", "OVERRIDE: Bailar activado.")
            elif comando == "/dormir": self.accion_rapida.emit("dormir"); self.agregar_mensaje("Sistema", "OVERRIDE: Dormir activado.")
            elif comando == "/bola": self.accion_rapida.emit("bola"); self.agregar_mensaje("Sistema", "OVERRIDE: Bola Fantasma activado.")
            elif comando == "/hipnosis": self.accion_rapida.emit("hipnosis"); self.agregar_mensaje("Sistema", "OVERRIDE: Hipnosis activada.")
            else: self.agregar_mensaje("Sistema", "ERROR: Comando no reconocido.")
        else:
            self.mensaje_enviado.emit(texto)
            self.iniciar_typing()
            reproducir_sonido("pop")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.posicion_global_raton = event.globalPosition().toPoint()
            self.posicion_inicial_ventana = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.posicion_global_raton
            self.move(self.posicion_inicial_ventana + delta)
            event.accept()

# ==============================================================================
# SECCIÓN 9: VENTANA DE CONFIGURACIÓN
# ==============================================================================

class VentanaConfiguracion(QDialog):
    def __init__(self, mascota):
        super().__init__()
        self.mascota = mascota
        self.setWindowTitle("Configuración de Gengar")
        self.setFixedSize(320, 220)
        self.setStyleSheet("background-color: #111; color: #00ffff; font-family: 'Consolas'; border: 1px solid #ff00ff;")
        
        layout = QFormLayout(self)
        self.spin_velocidad = QSpinBox()
        self.spin_velocidad.setRange(1, 10)
        self.spin_velocidad.setValue(mascota.velocidad_base)
        self.spin_velocidad.setStyleSheet("background: #000; color: #00ffff; border: 1px solid #00ffff;")
        layout.addRow("Velocidad (1-10):", self.spin_velocidad)
        
        self.btn_color = QPushButton("Cambiar Color de Neón")
        self.btn_color.setStyleSheet("background: #222; color: #00ffff; border: 1px solid #00ffff;")
        self.btn_color.clicked.connect(lambda: QColorDialog.getColor())
        layout.addRow(self.btn_color)
        
        self.btn_hud = QPushButton("Alternar HUD (Hardware)")
        self.btn_hud.setStyleSheet("background: #222; color: #00ffff; border: 1px solid #00ffff;")
        self.btn_hud.clicked.connect(self._alternar_hud)
        layout.addRow(self.btn_hud)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self._guardar)
        botones.rejected.connect(self.reject)
        botones.setStyleSheet("color: #ff00ff;")
        layout.addRow(botones)

    def _alternar_hud(self):
        self.mascota.mostrar_hud = not self.mascota.mostrar_hud
        if self.mascota.mostrar_hud: self.mascota.hud.show()
        else: self.mascota.hud.hide()

    def _guardar(self):
        self.mascota.velocidad_base = self.spin_velocidad.value()
        self.accept()

# ==============================================================================
# SECCIÓN 10: LA MASCOTA (LÓGICA PRINCIPAL)
# ==============================================================================

class MascotaGengar(QWidget):
    respuesta_para_chat = Signal(str, str)
    solicitar_abrir_chat = Signal()
    notificacion_sistema = Signal(str, str)
    actualizar_tooltip = Signal(str)

    def __init__(self, ventana_chat):
        super().__init__()
        self.ventana_chat = ventana_chat
        self.setFixedSize(ANCHO_VENTANA_PET, ALTO_VENTANA_PET)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAcceptDrops(True)

        self.overlay_particulas = OverlayParticulas()
        self.overlay_particulas.show()

        self._configurar_ui()
        self._inicializar_estado()
        self._configurar_timers()

        self.move(100, 100)
        self.raise_()

    def _configurar_ui(self):
        self.lbl_sprite = QLabel(self)
        self.lbl_sprite.setGeometry(SPRITE_X, SPRITE_Y, TAMANO_SPRITE, TAMANO_SPRITE)
        self.lbl_sprite.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(35)
        sombra.setOffset(0, 0)
        sombra.setColor(QColor(COLOR_SECUNDARIO))
        self.lbl_sprite.setGraphicsEffect(sombra)

        self.sombra_suelo = SombraMascota(self)
        self.sombra_suelo.move(SPRITE_X, SPRITE_Y + TAMANO_SPRITE - 10)

        self.bocadillo = BocadilloComic(self)
        self.bocadillo.setGeometry(0, SPRITE_Y - 60, ANCHO_VENTANA_PET, 50)
        self.bocadillo.hide()
        
        self.timer_ocultar_bocadillo = QTimer(self)
        self.timer_ocultar_bocadillo.setSingleShot(True)
        self.timer_ocultar_bocadillo.timeout.connect(self.bocadillo.hide)

        self.hud = HUDHardware(self)
        self.mostrar_hud = False
        
        self.indicador_pensando = IndicadorPensando(self)
        self.indicador_pensando.move(ANCHO_VENTANA_PET // 2 - 30, SPRITE_Y - 30)
        
        self.panel_mision = PanelMisionCyberpunk()

    def _inicializar_estado(self):
        self.animaciones = {}
        self._cargar_animaciones()
        
        self.estado_actual = "patrulla"
        self.frame_actual = 0
        self.ticks = 0
        self.direccion = 1
        self.duracion_estado = 4.0
        self.tiempo_estado = time.time()
        
        self.velocidad_base = 4
        self.velocidad_x = 4
        self.velocidad_y = 0
        
        self.pendientes = []
        self.hilo_ia = None
        self.tiempo_inicio_hilo = 0.0
        
        self.presionado = False
        self.arrastrando = False
        self.posicion_presion = QPoint()
        self.offset_arrastre = QPoint()
        
        self.ultima_pos_raton = QCursor.pos()
        self.tiempo_movimiento_raton = time.time()
        self.tiempo_ultimo_movimiento_global = time.time()
        
        self.squash_active = False
        self.timer_squash = QTimer(self)
        self.timer_squash.setSingleShot(True)
        self.timer_squash.timeout.connect(self._fin_squash)
        
        self.sueno_profundo = False
        
        self.glitch = OverlayGlitch()
        self.posesion = OverlayPosesion()
        
        self.fase_trepa = None
        self.lado_trepa = "izq"
        self.pared_x = 0
        self.referencia_ventana = None
        
        self.modo_travesura = False
        self.fase_estudio = None
        self.fin_estudio = 0.0
        self.min_estudio = 25
        self.min_descanso = 5
        
        self.clics_recientes = []
        self.tiempo_ultima_particula = 0
        self.contador_respiracion = 0

        self.cambiar_estado("patrulla")

    def _configurar_timers(self):
        self.timer_animacion = self._crear_timer(1000 // FRAMES_POR_SEGUNDO, self._siguiente_frame)
        self.timer_movimiento = self._crear_timer(30, self._mover)
        self.timer_comportamiento = self._crear_timer(8000, self._elegir_comportamiento)
        self.timer_pensamientos = self._crear_timer(45000, self._soltar_pensamiento)
        self.timer_raton = self._crear_timer(200, self._comprobar_raton)
        self.timer_seguridad = self._crear_timer(10000, self._vigilar_estado)
        self.timer_estudio = self._crear_timer(1000, self._tick_estudio, iniciar=False)
        
        self.timer_travesura = QTimer(self)
        self.timer_travesura.setSingleShot(True)
        self.timer_travesura.timeout.connect(self._hacer_travesura)
        self._programar_travesura()

    def _crear_timer(self, ms, funcion, iniciar=True):
        timer = QTimer(self)
        timer.timeout.connect(funcion)
        if iniciar: timer.start(ms)
        return timer

    def _tras(self, ms, funcion):
        timer = QTimer(self)
        timer.setSingleShot(True)
        def _ejecutar():
            if timer in self.pendientes: self.pendientes.remove(timer)
            timer.deleteLater()
            funcion()
        timer.timeout.connect(_ejecutar)
        timer.start(ms)
        self.pendientes.append(timer)
        return timer

    def _cancelar_pendientes(self):
        for timer in self.pendientes:
            timer.stop(); timer.deleteLater()
        self.pendientes.clear()
        self.setWindowOpacity(1.0)

    def _obtener_dpr(self): return QApplication.primaryScreen().devicePixelRatio()
    def _obtener_pantalla(self): return QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
    def _obtener_area(self): return self._obtener_pantalla().availableGeometry()

    def _obtener_limites(self, hundimiento=SINK_DE_PIE):
        area = self._obtener_area()
        return (area.left() - SPRITE_X, area.right() + 1 - SPRITE_X - TAMANO_SPRITE, area.bottom() + 1 - ALTO_VENTANA_PET + hundimiento)

    def decir(self, texto, ms=4500):
        if len(texto) > 110: texto = texto[:107] + "..."
        self.bocadillo.establecer_texto(texto)
        self.bocadillo.show()
        self.timer_ocultar_bocadillo.start(ms)
        reproducir_sonido("pop")

    def alternar_visibilidad(self):
        if self.isVisible(): self.hide()
        else: self.show()

    def _cargar_animaciones(self):
        self.animaciones = {}
        for nombre_estado, lista_archivos in DICCIONARIO_ANIMACIONES.items():
            frames_normales, frames_volteados = [], []
            for nombre_archivo in lista_archivos:
                ruta = os.path.join(RUTA_IMAGENES, nombre_archivo)
                if not os.path.exists(ruta): continue
                pixmap = QPixmap(ruta)
                if pixmap.isNull(): continue
                pixmap = pixmap.scaled(TAMANO_SPRITE, TAMANO_SPRITE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                frames_normales.append(pixmap)
                if nombre_estado in ANIMACIONES_SIN_VOLTEAR: frames_volteados.append(pixmap)
                else: frames_volteados.append(pixmap.transformed(QTransform().scale(-1, 1)))
            self.animaciones[nombre_estado] = (frames_normales, frames_volteados)
            
        base = None
        for key in ("patrulla", "quieto_de_pie"):
            if key in self.animaciones and self.animaciones[key][0]:
                base = self.animaciones[key]
                break
        if base is None:
            print(f"[Gengar] No se encontraron sprites en {RUTA_IMAGENES}")
            placeholder = QPixmap(TAMANO_SPRITE, TAMANO_SPRITE)
            placeholder.fill(QColor("#6a4c93"))
            base = ([placeholder], [placeholder])
        for key, value in self.animaciones.items():
            if not value[0]: self.animaciones[key] = base

    def cambiar_estado(self, nuevo_estado):
        self.estado_actual = nuevo_estado
        self.frame_actual = 0
        self.ticks = 0
        self.tiempo_estado = time.time()
        
        self.duracion_estado = {"patrulla": random.uniform(3.0, 6.0), "quieto_de_pie": 1.0, "sentado": random.uniform(6.0, 12.0)}.get(nuevo_estado, 0.0)
        
        if nuevo_estado in ("patrulla", "quieto_de_pie", "sentado") and self.y() > 100:
            hundimiento = SINK_SENTADO if nuevo_estado == "sentado" else SINK_DE_PIE
            _, _, suelo = self._obtener_limites(hundimiento)
            if abs(self.y() - suelo) < 30: self.move(self.x(), suelo)
                
        if nuevo_estado == "pensando": self.indicador_pensando.iniciar()
        else: self.indicador_pensando.detener()
        self._dibujar_frame()

    def _dibujar_frame(self):
        frames_normales, frames_volteados = self.animaciones[self.estado_actual]
        lista = frames_volteados if self.direccion > 0 else frames_normales
        pixmap = lista[self.frame_actual % len(lista)]
        
        if self.estado_actual in ("quieto_de_pie", "sentado") and not self.squash_active:
            factor = 1.0 + math.sin(time.time() * 3) * 0.02
            nuevo_tam = int(TAMANO_SPRITE * factor)
            pixmap = pixmap.scaled(nuevo_tam, nuevo_tam, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        if self.squash_active:
            pixmap = pixmap.scaled(int(TAMANO_SPRITE * 1.3), int(TAMANO_SPRITE * 0.7), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        self.lbl_sprite.setPixmap(pixmap)

    def _siguiente_frame(self):
        self.ticks += 1
        multiplicador = MULTIPLICADOR_FRAMES.get(self.estado_actual, 1)
        if self.ticks % multiplicador == 0: self.frame_actual += 1
        self._dibujar_frame()

    def _fin_squash(self):
        self.squash_active = False
        self._dibujar_frame()

    def _mover(self):
        estado = self.estado_actual
        
        if self.hud.isVisible(): self.hud.move(self.x() + self.width() + 10, self.y() + 20)
        if self.arrastrando or estado == "en_ventana": return
        if estado in ("bola_fantasma", "cursor"): return
        if estado in ("trepar_ir", "trepar_izq", "trepar_der"): self._mover_trepar(); return

        tiempo_transcurrido = time.time() - self.tiempo_estado
        
        if estado == "patrulla" and tiempo_transcurrido > self.duracion_estado:
            self.velocidad_x = 0; self.cambiar_estado("quieto_de_pie")
        elif estado == "quieto_de_pie" and tiempo_transcurrido > self.duracion_estado:
            self.cambiar_estado("sentado"); reproducir_sonido("bostezo")
        elif estado == "sentado" and tiempo_transcurrido > self.duracion_estado:
            self.velocidad_x = random.choice([-self.velocidad_base, self.velocidad_base])
            self.direccion = 1 if self.velocidad_x > 0 else -1
            self.cambiar_estado("patrulla")
            
        estado = self.estado_actual
        hundimiento = SINK_SENTADO if estado == "sentado" else SINK_DE_PIE
        min_x, max_x, suelo = self._obtener_limites(hundimiento)
        
        x, y = self.x(), self.y()

        if estado == "patrulla":
            x += int(self.velocidad_x)
            if x > max_x: x = max_x; self.velocidad_x = -self.velocidad_base
            elif x < min_x: x = min_x; self.velocidad_x = self.velocidad_base
            if self.velocidad_x: self.direccion = 1 if self.velocidad_x > 0 else -1

        if y < suelo:
            self.velocidad_y += 2
            y = min(y + int(self.velocidad_y), suelo)
            if y >= suelo: self.velocidad_y = 0
        elif y > suelo: y = suelo; self.velocidad_y = 0

        self.move(x, y)
        
        # Rastro de partículas al moverse
        if estado == "patrulla" and time.time() - self.tiempo_ultima_particula > 0.1:
            self._generar_particula()
            self.tiempo_ultima_particula = time.time()

        if y < suelo: self.sombra_suelo.factor_escala = max(0.3, 1.0 - (suelo - y) / 200.0)
        else: self.sombra_suelo.factor_escala = 1.0
        self.sombra_suelo.update()
        
        if estado == "caer" and y >= suelo:
            self.squash_active = True
            self.timer_squash.start(150)
            self.volver_a_patrullar()

    def _generar_particula(self):
        color = random.choice([COLOR_PRIMARIO, COLOR_SECUNDARIO])
        x_pos = self.x() + SPRITE_X + random.randint(20, TAMANO_SPRITE - 20)
        y_pos = self.y() + SPRITE_Y + random.randint(20, TAMANO_SPRITE - 20)
        self.overlay_particulas.agregar_particula(x_pos, y_pos, color)

    def volver_a_patrullar(self):
        self._cancelar_pendientes()
        self.arrastrando = False
        self.velocidad_x = random.choice([-self.velocidad_base, self.velocidad_base])
        self.direccion = 1 if self.velocidad_x > 0 else -1
        self.cambiar_estado("patrulla")

    def _vigilar_estado(self):
        if self.arrastrando or self.estado_actual in ESTADOS_LIBRES: return
        if self.estado_actual.startswith("trepar"): return # Excluir trepar de la vigilancia
        if self.estado_actual == "pensando" and self.hilo_ia is not None and self.hilo_ia.isRunning(): return
        if time.time() - self.tiempo_estado > 45: self.volver_a_patrullar()

    def _elegir_comportamiento(self):
        if self.estado_actual not in ESTADOS_LIBRES or self.arrastrando: return
        if obtener_pico_audio() > 15: self._ejecutar_accion("bailar"); return
        if random.random() < 0.15: self._saltito(); return

        if random.random() < 0.55:
            opciones = ["dormir", "bailar", "hipnosis", "bola_fantasma", "humo", "ventana"]
            pesos = [0.2, 0.4, 0.3, 0.25, 0.15, 0.35]
            accion = random.choices(opciones, weights=pesos, k=1)[0]
            self._ejecutar_accion(accion)
        elif random.random() < 0.15: self._trepar_pared()

    def _saltito(self):
        self._cancelar_pendientes()
        self.velocidad_y = -15
        self.cambiar_estado("caer")
        self.decir("¡BOING!")

    def _ejecutar_accion(self, accion):
        if accion == "ventana": self._ir_a_ventana(); return
        self._cancelar_pendientes()
        if accion == "dormir": self.cambiar_estado("dormir"); self.decir("SLEEP_MODE_ON."); self._tras(5000, self.volver_a_patrullar)
        elif accion == "bailar": self.cambiar_estado("bailar"); self.decir("OVERRIDE_DANCE."); self._tras(4000, self.volver_a_patrullar)
        elif accion == "hipnosis": self.cambiar_estado("hipnosis"); self.decir("HYPNOSIS."); self._tras(4000, self.volver_a_patrullar)
        elif accion == "bola_fantasma": self._rodar_bola()
        elif accion == "humo": self._desaparecer_con_humo()

    def _soltar_pensamiento(self):
        if self.estado_actual in ESTADOS_LIBRES and not self.arrastrando:
            hora = datetime.datetime.now().hour
            if 0 <= hora < 6: frase = f"Tío, son las {hora} de la mañana. ¿No duermes?"
            elif 12 <= hora < 15: frase = "¿Ya has comido o qué?"
            else: frase = random.choice(FRASES_PENSAMIENTOS)
            self.decir(frase)

    def _rodar_bola(self):
        self.cambiar_estado("bola_fantasma")
        self.velocidad_x = random.choice([-6, 6])
        self.velocidad_y = -10
        self.decir("GHOST_ROLL.", 2500)
        self.timer_bola = QTimer(self)
        self.timer_bola.timeout.connect(self._mover_bola)
        self.timer_bola.start(25)
        self._tras(3500, lambda: (self.timer_bola.stop(), self.volver_a_patrullar()))

    def _mover_bola(self):
        min_x, max_x, suelo = self._obtener_limites(SINK_DE_PIE)
        x = self.x() + int(self.velocidad_x)
        if x > max_x: x = max_x; self.velocidad_x *= -1
        elif x < min_x: x = min_x; self.velocidad_x *= -1
        self.direccion = 1 if self.velocidad_x > 0 else -1
        self.velocidad_y += 2
        y = self.y() + int(self.velocidad_y)
        if y > suelo: y = suelo; self.velocidad_y = -12
        self.move(x, y)

    def _desaparecer_con_humo(self):
        self.cambiar_estado("humo")
        self._tras(800, lambda: self.setWindowOpacity(0.0))
        self._tras(1600, self._reaparecer)

    def _reaparecer(self):
        area = self._obtener_area()
        x = random.randint(area.left() + 50, max(area.left() + 51, area.right() - ANCHO_VENTANA_PET - 50))
        self.move(x, area.bottom() - ALTO_VENTANA_PET + SINK_DE_PIE)
        self.setWindowOpacity(1.0)
        self.cambiar_estado("travesura")
        self._tras(1000, self.volver_a_patrullar)

    def _trepar_pared(self):
        if self.estado_actual not in ESTADOS_LIBRES or self.arrastrando: return
        self._cancelar_pendientes()
        area = self._obtener_area()
        min_x, max_x, suelo = self._obtener_limites(SINK_DE_PIE)
        es_izquierda = self.x() + ANCHO_VENTANA_PET // 2 < area.center().x()
        self.lado_trepa = "izq" if es_izquierda else "der"
        self.pared_x = min_x if es_izquierda else max_x
        self.velocidad_x = -5 if es_izquierda else 5
        self.direccion = 1 if self.velocidad_x > 0 else -1
        self.fase_trepa = "ir"
        self.cambiar_estado("trepar_ir")
        self.decir("CLIMBING_WALL.")

    def _mover_trepar(self):
        area = self._obtener_area()
        min_x, max_x, suelo = self._obtener_limites(SINK_DE_PIE)
        
        if self.estado_actual == "trepar_ir":
            x = self.x() + int(self.velocidad_x)
            if (self.velocidad_x < 0 and x <= self.pared_x) or (self.velocidad_x > 0 and x >= self.pared_x):
                x = self.pared_x
                self.velocidad_x = 0 # CRUCIAL: Detener el movimiento horizontal al tocar la pared
                self.fase_trepa = "subir"
                self.cambiar_estado("trepar_izq" if self.lado_trepa == "izq" else "trepar_der")
            self.move(x, suelo)
            
        elif self.fase_trepa == "subir":
            y = self.y() - 5
            if y <= area.top() - SPRITE_Y:
                y = area.top() - SPRITE_Y
                self.fase_trepa = "pausa"
                self.decir("HIGH_ALTITUDE.")
                self._tras(1000, lambda: setattr(self, 'fase_trepa', 'bajar'))
            self.move(self.x(), y)
            
        elif self.fase_trepa == "bajar":
            y = self.y() + 5
            if y >= suelo:
                self.move(self.x(), suelo)
                self.fase_trepa = None
                self.volver_a_patrullar()
                return
            self.move(self.x(), y)

    def _obtener_ventanas_candidatas(self):
        if sys.platform != "win32": return []
        user32 = ctypes.windll.user32
        dpr = self._obtener_dpr()
        resultado = []
        hwnd_self, hwnd_chat = int(self.winId()), int(self.ventana_chat.winId())
        def callback(hwnd, lParam):
            if hwnd in (hwnd_self, hwnd_chat) or not user32.IsWindowVisible(hwnd): return True
            if user32.IsIconic(hwnd) or user32.IsZoomed(hwnd): return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0: return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if buf.value in TITULOS_IGNORADOS: return True
            rect = obtener_rectangulo_visible(hwnd)
            l, t, r, b = rect.left/dpr, rect.top/dpr, rect.right/dpr, rect.bottom/dpr
            if (r - l) > 200 and (b - t) > 100: resultado.append((hwnd, l, t, r, buf.value))
            return True
        user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(callback), 0)
        return resultado

    def _ir_a_ventana(self):
        candidatas = self._obtener_ventanas_candidatas()
        if not candidatas: self.decir("NO_WINDOWS_FOUND."); return False
        hwnd, l, t, r, titulo = random.choice(candidatas)
        self._cancelar_pendientes()
        self.cambiar_estado("humo")
        self.decir(f"INFILTRATING: '{titulo[:15]}...'")
        self._tras(700, lambda: self.setWindowOpacity(0.0))
        self._tras(1400, lambda: self._aparecer_en_ventana(hwnd, l, t, r))
        return True

    def _aparecer_en_ventana(self, hwnd, l, t, r):
        area = self._obtener_area()
        x = random.randint(max(area.left(), int(l)), min(area.right() - ANCHO_VENTANA_PET, int(r) - ANCHO_VENTANA_PET))
        y = max(area.top() + 10, int(t) - ALTO_VENTANA_PET + 10)
        self.setWindowOpacity(1.0)
        self.move(x, y)
        self.referencia_ventana = (hwnd, t)
        self.cambiar_estado("en_ventana")
        self.decir("TACTICAL_POSITION.")
        self._tras(random.randint(12000, 25000), self._bajar_de_ventana)

    def _bajar_de_ventana(self):
        if self.estado_actual != "en_ventana": return
        self.referencia_ventana = None
        self.velocidad_y = 0
        self.cambiar_estado("caer")
        self.decir("FALLING_BACK.")

    def _comprobar_raton(self):
        posicion = QCursor.pos()
        ahora = time.time()
        
        delta_pos = (posicion - self.ultima_pos_raton).manhattanLength()
        delta_t = ahora - self.tiempo_movimiento_raton
        if delta_t > 0:
            velocidad = delta_pos / delta_t
            if velocidad > 2000 and self.estado_actual in ESTADOS_LIBRES:
                self._iniciar_caza(posicion)
                self.tiempo_movimiento_raton = ahora
                self.ultima_pos_raton = posicion
                return
        
        if posicion != self.ultima_pos_raton:
            self.ultima_pos_raton = posicion
            self.tiempo_movimiento_raton = ahora
            self.tiempo_ultimo_movimiento_global = ahora
            if self.sueno_profundo: self._despertar_sueno_profundo()
            return
            
        if not self.sueno_profundo and self.estado_actual in ESTADOS_LIBRES:
            if ahora - self.tiempo_ultimo_movimiento_global > TIEMPO_SUENO_PROFUNDO:
                self._entrar_sueno_profundo(); return
                
        if ahora - self.tiempo_movimiento_raton > TIEMPO_ASOMARSE and self.estado_actual in ESTADOS_LIBRES:
            self._desaparecer_con_humo()

    def _iniciar_caza(self, pos_raton):
        self._cancelar_pendientes()
        self.cambiar_estado("patrulla")
        self.velocidad_x = 8 if pos_raton.x() > self.x() else -8
        self.direccion = 1 if self.velocidad_x > 0 else -1
        self.decir("TARGET_ACQUIRED.", 2000)
        self._tras(3000, self.volver_a_patrullar)

    def _entrar_sueno_profundo(self):
        self._cancelar_pendientes()
        self.sueno_profundo = True
        self.hide()
        self.decir("DEEP_SLEEP.")

    def _despertar_sueno_profundo(self):
        self.sueno_profundo = False
        self.show()
        self._saltito()
        self.decir("SYSTEM_WAKE.")

    def _programar_travesura(self):
        self.timer_travesura.start(random.randint(45000, 90000))

    def _hacer_travesura(self):
        self._programar_travesura()
        if not self.modo_travesura or self.estado_actual not in ESTADOS_LIBRES or self.arrastrando or not self.isVisible(): return
        random.choice([self._glitch_pantalla, self._nota_hackeo])()

    def _glitch_pantalla(self):
        self._cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("SYSTEM_GLITCH!")
        self.glitch.lanzar_glitch(self._obtener_pantalla().geometry())
        self._tras(1800, self.volver_a_patrullar)

    def _nota_hackeo(self):
        self._cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("DATA_BREACH.")
        self.glitch.lanzar_glitch(self._obtener_pantalla().geometry())
        self._tras(1800, self.volver_a_patrullar)

    def _activar_cyberpsychosis(self):
        self._cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("CYBERPSYCHOSIS_DETECTED.", 3000)
        self.glitch.lanzar_glitch(self._obtener_pantalla().geometry())
        reproducir_sonido("error")
        self._tras(3000, self.volver_a_patrullar)

    def poseer_ventana_activa(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd == int(self.winId()) or hwnd == int(self.ventana_chat.winId()):
            self.decir("CANNOT_TARGET_SELF."); return
        self.decir("WINDOW_HIJACKED.")
        self.posesion.poseer_ventana(hwnd)
        self._tras(5000, self.posesion.hide)

    def secuencia_satelite(self):
        self._cancelar_pendientes()
        self.cambiar_estado("travesura")
        self.decir("UPLINK_ESTABLISHED.")
        self.glitch.lanzar_glitch(self._obtener_pantalla().geometry())
        for i in range(5): self._tras(i * 300, lambda: self.glitch.lanzar_glitch(self._obtener_pantalla().geometry()))
        self._tras(2500, self.volver_a_patrullar)

    def iniciar_estudio(self, min_estudio=25, min_descanso=5):
        self.min_estudio = min_estudio
        self.min_descanso = min_descanso
        self.fase_estudio = "estudio"
        self.fin_estudio = time.time() + min_estudio * 60
        self.timer_estudio.start()
        self.decir(f"FOCUS_MODE: {min_estudio} min.", 5000)

    def parar_estudio(self):
        self.fase_estudio = None
        self.timer_estudio.stop()
        self.actualizar_tooltip.emit("Gengar")
        self.decir("FOCUS_MODE: OFF.")

    def _tick_estudio(self):
        if not self.fase_estudio: self.timer_estudio.stop(); return
        resta = int(self.fin_estudio - time.time())
        if resta <= 0:
            if self.fase_estudio == "estudio":
                self.fase_estudio = "descanso"
                self.fin_estudio = time.time() + self.min_descanso * 60
                self._avisar(f"DESCANSO: {self.min_descanso} min.")
            else:
                self.fase_estudio = "estudio"
                self.fin_estudio = time.time() + self.min_estudio * 60
                self._avisar("VUELTA AL TRABAJO.")
            return
        m, s = divmod(resta, 60)
        self.actualizar_tooltip.emit(f"Gengar - {self.fase_estudio}: {m:02d}:{s:02d}")

    def _avisar(self, texto):
        self.notificacion_sistema.emit("Gengar", texto)
        reproducir_sonido("success")
        self.decir(texto, 12000)
        if self.arrastrando: return
        self._cancelar_pendientes()
        self.cambiar_estado("bailar")
        self._tras(6000, self.volver_a_patrullar)

    def recibir_mensaje(self, prompt):
        self._cancelar_pendientes()
        self.cambiar_estado("pensando")
        self.decir("PROCESSING_DATA...", 3000)
        self.tiempo_inicio_hilo = time.time()
        self.hilo_ia = HiloIA(prompt)
        self.hilo_ia.respuesta_lista.connect(self._mostrar_respuesta)
        self.hilo_ia.start()

    def _mostrar_respuesta(self, texto):
        tiempo_total = time.time() - self.tiempo_inicio_hilo
        self.respuesta_para_chat.emit("Gengar", texto)
        self._cancelar_pendientes()
        es_error = texto.startswith("Error:")
        
        if es_error:
            self.decir("SYSTEM_FAILURE!")
            self.cambiar_estado("caer")
            self.glitch.lanzar_glitch(self._obtener_pantalla().geometry())
            reproducir_sonido("error")
            self._tras(3000, self.volver_a_patrullar)
        else:
            self.cambiar_estado("bailar")
            self.decir(texto, max(6000, len(texto) * 70))
            reproducir_sonido("success")
            self._tras(3000, self.volver_a_patrullar)
            
        geometria = self.frameGeometry()
        x = geometria.x() - 460
        y = geometria.y() - 50
        if x < 0: x = geometria.x() + geometria.width() + 10
        self.panel_mision.move(x, y)
        self.panel_mision.mostrar_mision(titulo="Respuesta", descripcion=texto, exito=not es_error, tiempo_total=tiempo_total)

    def accion_rapida(self, tipo):
        self._ejecutar_accion(tipo)
        self.decir(f"OVERRIDE: {tipo.upper()}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.decir("FILE_DETECTED.")

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f: contenido = f.read(2000)
                    self.recibir_mensaje(f"Analiza este archivo {os.path.basename(path)}:\n\n{contenido}")
                    self.decir(f"READING {os.path.basename(path)}...")
                except Exception: self.decir("READ_ERROR.")
                break

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f"background-color: #000; color: {COLOR_PRIMARIO}; border: 1px solid {COLOR_SECUNDARIO}; font-family: 'Consolas';")
        accion_chat = menu.addAction(">> OPEN_COMMS")
        accion_jugar = menu.addAction(">> OVERRIDE_PROTOCOL")
        accion_ocultar = menu.addAction(">> CLOAKING_DEVICE")
        accion_dormir = menu.addAction(">> SLEEP_MODE")
        accion = menu.exec(event.globalPos())
        if accion == accion_chat: self.solicitar_abrir_chat.emit()
        elif accion == accion_jugar: self._ejecutar_accion(random.choice(["bailar", "hipnosis", "bola_fantasma"]))
        elif accion == accion_ocultar: self._desaparecer_con_humo()
        elif accion == accion_dormir: self._ejecutar_accion("dormir")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.presionado = True
            self.arrastrando = False
            self.posicion_presion = event.globalPosition().toPoint()
            self.offset_arrastre = self.posicion_presion - self.pos()
            
            ahora = time.time()
            self.clics_recientes.append(ahora)
            self.clics_recientes = [t for t in self.clics_recientes if ahora - t < 2.0]
            if len(self.clics_recientes) >= 5:
                self._activar_cyberpsychosis()
                self.clics_recientes.clear()
            event.accept()

    def mouseMoveEvent(self, event):
        if not self.presionado: return
        pos_global = event.globalPosition().toPoint()
        if not self.arrastrando and (pos_global - self.posicion_presion).manhattanLength() > 5:
            self.arrastrando = True
            self._cancelar_pendientes()
            self.velocidad_y = 0
            self.cambiar_estado("arrastrado")
            self.decir("RELEASE_ME!")
        if self.arrastrando:
            self.move(pos_global - self.offset_arrastre)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton: return
        self.presionado = False
        if self.arrastrando:
            self.arrastrando = False
            self.velocidad_y = 2
            self.cambiar_estado("caer")
            self.decir("RECOVERING.")
        else:
            self._procesar_clic(event.position().y())
        event.accept()

    def _procesar_clic(self, y_local):
        if self.estado_actual in ("bola_fantasma", "humo", "trepar_ir"): return
        if SPRITE_Y <= y_local <= SPRITE_Y + 55:
            self._cancelar_pendientes()
            self.cambiar_estado("caricia")
            self.decir(random.choice(FRASES_CARICIA), 3000)
            self._tras(2500, self.volver_a_patrullar)
        else:
            self.decir("TICKLES_DETECTED.")

    def mouseDoubleClickEvent(self, event):
        self.solicitar_abrir_chat.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2: self.iniciar_estudio()
        elif event.key() == Qt.Key_F3: self._glitch_pantalla()
        elif event.key() == Qt.Key_F4:
            global MODO_DND
            MODO_DND = not MODO_DND
            self.decir(f"DND {'ACTIVADO' if MODO_DND else 'DESACTIVADO'}.", 3000)
        else: super().keyPressEvent(event)

# ==============================================================================
# SECCIÓN 10.5: PANTALLA DE LLAMADA ENTRANTE
# ==============================================================================

class PantallaLlamada(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(480, 220)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 20, screen.top() + 20)
        self.parpadeo = 0
        self.timer_parpadeo = QTimer(self)
        self.timer_parpadeo.timeout.connect(self._trigger_parpadeo)
        self.timer_parpadeo.start(500)
        self.setFocusPolicy(Qt.StrongFocus)

    def _trigger_parpadeo(self):
        self.parpadeo = (self.parpadeo + 1) % 2
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_T: self.accept()
        elif event.key() in (Qt.Key_R, Qt.Key_Escape): self.reject()
        else: super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.position().x(), event.position().y()
            if 170 < x < 260 and 150 < y < 190: self.accept()
            elif 310 < x < 400 and 150 < y < 190: self.reject()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(QPen(QColor(255, 0, 50), 1.5))
        painter.drawLine(20, 20, 20, 60); painter.drawLine(20, 20, 35, 20); painter.drawLine(20, 60, 35, 60)
        painter.setPen(Qt.NoPen); painter.setBrush(QColor(255, 0, 50, 200))
        painter.drawRect(35, 35, 10, 20)
        painter.setPen(QPen(QColor(0, 0, 0), 1)); painter.drawLine(38, 40, 42, 40); painter.drawLine(38, 50, 42, 50)
        painter.setPen(Qt.NoPen)
        for i in range(4):
            h = 4 + i * 3
            painter.setBrush(QColor(255, 0, 50, 100 + i * 50))
            painter.drawRect(50 + i * 4, 55 - h, 2, h)
        painter.setPen(QColor(255, 0, 50))
        painter.setFont(QFont("Consolas", 5, QFont.Bold))
        painter.drawText(25, 15, "STRENGTH"); painter.drawText(25, 9, "SIGNAL"); painter.drawText(25, 3, "100%")
        
        painter.save(); painter.translate(100, 120); painter.rotate(-12)
        for i in range(3):
            offset = i * 1.5
            color = QColor(255, 0, 50, 255 - i * 60)
            painter.setPen(QPen(color, 1.5))
            painter.drawRect(-35 - offset, -55 - offset, 70 + offset*2, 110 + offset*2)
        painter.setBrush(QColor(20, 0, 10, 200)); painter.setPen(Qt.NoPen); painter.drawRect(-35, -55, 70, 110)
        if os.path.exists(RUTA_CARA_GENGAR):
            pixmap = QPixmap(RUTA_CARA_GENGAR).scaled(70, 110, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            tint = QPixmap(pixmap.size()); tint.fill(QColor(255, 0, 50, 120))
            p = QPainter(pixmap); p.setCompositionMode(QPainter.CompositionMode_Multiply)
            p.drawPixmap(0, 0, tint); p.end(); painter.drawPixmap(-35, -55, pixmap)
        else:
            painter.setBrush(QColor(255, 0, 50, 150)); painter.drawEllipse(-20, -25, 40, 50)
            painter.drawPolygon(QPolygon([QPoint(-20, -25), QPoint(-30, -35), QPoint(-10, -30)]))
            painter.drawPolygon(QPolygon([QPoint(20, -25), QPoint(30, -35), QPoint(10, -30)]))
            painter.setBrush(QColor(0, 0, 0)); painter.drawEllipse(-10, -10, 8, 6); painter.drawEllipse(2, -10, 8, 6); painter.drawRect(-15, 10, 30, 5)
        painter.rotate(90); painter.setPen(QColor(255, 0, 50)); painter.setFont(QFont("Consolas", 6, QFont.Bold)); painter.drawText(-45, -30, "GENGAR_OS"); painter.restore()
        
        font_big = QFont("Consolas", 24, QFont.Bold); font_medium = QFont("Consolas", 12, QFont.Bold); font_small = QFont("Consolas", 6, QFont.Bold)
        painter.setFont(font_small); painter.setPen(QColor(0, 255, 255, 100)); painter.drawText(190, 85, "TRAN_TCLAS_000095")
        painter.setFont(font_big); x_pos, y_pos = 190, 115; text_gengar = "GENGAR"
        
        c40 = QColor(COLOR_PRIMARIO); c40.setAlpha(40); painter.setPen(c40)
        painter.drawText(x_pos - 2, y_pos, text_gengar); painter.drawText(x_pos + 2, y_pos, text_gengar)
        c80 = QColor(COLOR_PRIMARIO); c80.setAlpha(80); painter.setPen(c80)
        painter.drawText(x_pos - 1, y_pos, text_gengar); painter.drawText(x_pos + 1, y_pos, text_gengar)
        painter.setPen(QColor(255, 255, 255)); painter.drawText(x_pos, y_pos, text_gengar)
        
        painter.setClipRect(x_pos, y_pos - 12, 150, 3); painter.setPen(QColor(COLOR_PRIMARIO)); painter.drawText(x_pos + 5, y_pos, text_gengar); painter.setClipping(False)
        painter.setClipRect(x_pos, y_pos - 4, 150, 2); painter.setPen(QColor(COLOR_PRIMARIO)); painter.drawText(x_pos - 4, y_pos, text_gengar); painter.setClipping(False)
        
        painter.setFont(font_medium); text_call = "INCOMING CALL"; y_pos_call = y_pos + 20
        painter.setPen(QColor(255, 0, 50, 60)); painter.drawText(x_pos - 1, y_pos_call, text_call); painter.drawText(x_pos + 1, y_pos_call, text_call)
        if self.parpadeo == 0: painter.setPen(QColor(255, 0, 50))
        else: painter.setPen(QColor(150, 0, 30))
        painter.drawText(x_pos, y_pos_call, text_call)
        painter.setClipRect(x_pos, y_pos_call - 5, 150, 2); painter.setPen(QColor(255, 0, 50)); painter.drawText(x_pos + 3, y_pos_call, text_call); painter.setClipping(False)
        
        self._dibujar_boton(painter, 190, 155, "ANSWER", QColor(COLOR_PRIMARIO))
        self._dibujar_boton(painter, 330, 155, "REJECT", QColor(COLOR_PRIMARIO))
        
        painter.setPen(QPen(QColor(0, 255, 255, 15), 1))
        for y in range(0, self.height(), 2): painter.drawLine(0, y, self.width(), y)

    def _dibujar_boton(self, painter, x, y, texto, color_texto):
        painter.setPen(QPen(QColor(255, 0, 50), 1.5)); painter.setBrush(Qt.NoBrush); painter.drawRect(x, y, 20, 20)
        painter.setFont(QFont("Consolas", 12, QFont.Bold)); painter.setPen(QColor(255, 0, 50)); painter.drawText(QRect(x, y, 20, 20), Qt.AlignCenter, "T")
        painter.setBrush(QColor(255, 0, 50)); painter.setPen(Qt.NoPen); painter.drawPolygon(QPolygon([QPoint(x+10, y+22), QPoint(x+7, y+26), QPoint(x+13, y+26)]))
        painter.setFont(QFont("Consolas", 14, QFont.Bold)); painter.setPen(color_texto); painter.drawText(x + 28, y + 15, texto)
        painter.setFont(QFont("Consolas", 5)); painter.setPen(QColor(255, 255, 255, 120)); painter.drawText(x - 5, y + 35, "PRESS [T]")

# ==============================================================================
# SECCIÓN 11: BANDEJA DEL SISTEMA Y ARRANQUE
# ==============================================================================

def generar_icono_app():
    ruta = os.path.join(RUTA_IMAGENES, "shime1.png")
    pixmap = QPixmap(ruta) if os.path.exists(ruta) else QPixmap()
    if pixmap.isNull():
        pixmap = QPixmap(32, 32); pixmap.fill(QColor("#6a4c93"))
    return QIcon(pixmap)

def crear_bandeja_sistema(app, mascota, mostrar_chat, abrir_configuracion):
    if not QSystemTrayIcon.isSystemTrayAvailable(): return None
    bandeja = QSystemTrayIcon(generar_icono_app(), app)
    bandeja.setToolTip("Gengar Cyberdeck")
    menu = QMenu()
    menu.setStyleSheet(f"background-color: #000; color: {COLOR_PRIMARIO}; border: 1px solid {COLOR_SECUNDARIO}; font-family: 'Consolas';")
    
    def agregar_accion(texto, funcion, checkable=False, marcado=False):
        accion = QAction(texto, menu)
        if checkable: accion.setCheckable(True); accion.setChecked(marcado); accion.toggled.connect(funcion)
        else: accion.triggered.connect(lambda: funcion())
        menu.addAction(accion); return accion

    agregar_accion(">> TOGGLE_VISIBILITY", mascota.alternar_visibilidad)
    agregar_accion(">> OPEN_COMMS", mostrar_chat)
    agregar_accion(">> CONFIGURE", abrir_configuracion)
    menu.addSeparator()
    agregar_accion(">> HIJACK_WINDOW", mascota.poseer_ventana_activa)
    agregar_accion(">> UPLINK_SATELLITE", mascota.secuencia_satelite)
    menu.addSeparator()
    agregar_accion(">> MODO TRAVESURA", lambda v: setattr(mascota, "modo_travesura", v), True, False)
    agregar_accion(">> FOCUS_MODE (25m)", mascota.iniciar_estudio)
    agregar_accion(">> STOP_FOCUS", mascota.parar_estudio)
    menu.addSeparator()
    
    skin_menu = menu.addMenu(">> SKIN_SELECTOR")
    skin_menu.setStyleSheet(f"background-color: #000; color: {COLOR_PRIMARIO}; border: 1px solid {COLOR_SECUNDARIO};")
    def cambiar_skin(p, s):
        global COLOR_PRIMARIO, COLOR_SECUNDARIO
        COLOR_PRIMARIO = p; COLOR_SECUNDARIO = s
        QMessageBox.information(None, "Skin", "Reinicia la app para aplicar el skin.")
    skin_menu.addAction("Cian/Magenta", lambda: cambiar_skin("#00ffff", "#ff00ff"))
    skin_menu.addAction("Amarillo/Rojo", lambda: cambiar_skin("#ffff00", "#ff0000"))
    skin_menu.addAction("Verde/Blanco", lambda: cambiar_skin("#00ff00", "#ffffff"))
    skin_menu.addAction("Naranja/Azul", lambda: cambiar_skin("#ff8800", "#0088ff"))
    
    global MODO_DND
    agregar_accion(">> MODO DND (Silenciar Voz)", lambda v: globals().update(MODO_DND=v), True, MODO_DND)
    
    menu.addSeparator()
    if sys.platform == "win32":
        agregar_accion(">> START_WITH_WINDOWS", lambda: configurar_inicio_automatico(not comprobar_inicio_automatico()), True, comprobar_inicio_automatico())
        menu.addSeparator()
        
    agregar_accion(">> TERMINATE", app.quit)
    bandeja.setContextMenu(menu)
    bandeja._menu = menu
    bandeja.activated.connect(lambda r: mascota.alternar_visibilidad() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
    mascota.actualizar_tooltip.connect(bandeja.setToolTip)
    mascota.notificacion_sistema.connect(lambda t, m: bandeja.showMessage(t, m, QSystemTrayIcon.MessageIcon.Information, 5000))
    bandeja.show()
    return bandeja

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pantalla_llamada = PantallaLlamada()
    
    if pantalla_llamada.exec() == QDialog.Accepted:
        app.setQuitOnLastWindowClosed(False)
        ventana_chat = VentanaChatCyberdeck()
        mascota = MascotaGengar(ventana_chat)

        def mostrar_ventana_chat():
            ventana_chat.show()
            ventana_chat.raise_()
            ventana_chat.activateWindow()
            
        def abrir_ventana_configuracion():
            dialogo = VentanaConfiguracion(mascota)
            dialogo.exec()

        ventana_chat.mensaje_enviado.connect(mascota.recibir_mensaje)
        ventana_chat.accion_rapida.connect(mascota.accion_rapida)
        mascota.respuesta_para_chat.connect(lambda q, t: ventana_chat.agregar_mensaje(q, t))
        mascota.respuesta_para_chat.connect(lambda q, t: ventana_chat.detener_typing())
        mascota.solicitar_abrir_chat.connect(mostrar_ventana_chat)

        bandeja = crear_bandeja_sistema(app, mascota, mostrar_ventana_chat, abrir_ventana_configuracion)
        mascota.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)