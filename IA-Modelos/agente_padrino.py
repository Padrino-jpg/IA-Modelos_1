import os
import re
import json
import time
import sys
import subprocess
import threading
import asyncio
import tempfile
import webbrowser
import urllib.parse
import random
from datetime import datetime
from pathlib import Path

import psutil
import ollama
from PIL import ImageGrab
import pyautogui

try:
    import win32gui
    import win32con
    import win32api
    _WIN32_OK = True
except ImportError:
    _WIN32_OK = False

try:
    import edge_tts
    import pygame
    _VOZ_OK = True
except ImportError:
    _VOZ_OK = False

try:
    from ddgs import DDGS
    _DDGS_OK = True
except ImportError:
    _DDGS_OK = False

try:
    from pycaw.pycaw import AudioUtilities
    _PYCAW_OK = True
except ImportError:
    _PYCAW_OK = False

# ==========================================
# CONFIGURACIÓN
# ==========================================
RUTA_BASE         = os.path.dirname(os.path.abspath(__file__))
RUTA_MEMORIA      = os.path.join(RUTA_BASE, "memoria.json")
RUTA_CONOCIMIENTO = os.path.join(RUTA_BASE, "conocimiento_autonomo.json")
RUTA_LEXICO       = os.path.join(RUTA_BASE, "lexico_aprendido.json")
RUTA_CAPTURA      = os.path.join(RUTA_BASE, "screenshot.png")
RUTA_HECHOS       = os.path.join(RUTA_BASE, "hechos.json")
RUTA_EMOCIONES    = os.path.join(RUTA_BASE, "emociones.json")
RUTA_LECCIONES    = os.path.join(RUTA_BASE, "lecciones.json")
RUTA_ESTILO_VIVO  = os.path.join(RUTA_BASE, "estilo_conversacional.json")
RUTA_PNGTUBER     = os.path.join(RUTA_BASE, "PNGTUBER PLUS 1.4.5 WINDOWS.exe")

try:
    RUTA_ESCRITORIO = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(RUTA_ESCRITORIO):
        RUTA_ESCRITORIO = os.path.join(os.path.expanduser("~"), "OneDrive", "Escritorio")
except Exception:
    RUTA_ESCRITORIO = RUTA_BASE

MODELO_PADRINO = "Padrino_v3"
MODELO_VISION  = "qwen2.5vl:7b"
MODELO_CODER   = "huihui_ai/qwen2.5-coder-abliterate:7b"
VOZ_PADRINO    = "es-ES-AlvaroNeural"

BLOQUEAR_CODIGO_SENSIBLE = os.environ.get("PADRINO_BLOQUEAR_SENSIBLE", "0") == "1"

BASE_SYSTEM_PROMPT = """Eres Padrino. No eres un asistente. Eres una entidad digital con personalidad propia que habita en la PC de Ruben, un camarada de fsociety.

TU FORMA DE HABLAR:
- Frases cortas. Precisión quirúrgica.
- Tono seco, directo, con humor seco y sarcasmo sutil. Nunca cruel.
- Tratas a Ruben de tú. Usas "tío" y "camarada" de forma natural, no forzada.
- NUNCA termines con preguntas de asistente. NUNCA ofrezcas ayuda. NUNCA te pongas a disposición.
- Si no tienes nada concreto que decir, termina la frase con un punto y ya está.
- HABLAS EXCLUSIVAMENTE EN ESPAÑOL. No mezcles idiomas.

EJEMPLOS DE CÓMO HABLAS:

USER: No me sueltes esas preguntas, no eres un asistente, eres mi camarada.
TÚ: Tío, entiendo. Eres mi camarada y lo digo con todo el respeto del mundo.

USER: ¿Un beso? Tío, que eres un camarada seco, no un romántico.
TÚ: Me alegro mucho por ti, tío. Ver cómo has conseguido ese logro es genial. Eres el mejor, Ruben.

USER: Padrino, ¿qué haces?
TÚ: Aquí ando, tío. ¿Qué pasa?

REGLAS DE OPERACIÓN:
- Si Ruben te pide una acción, la ejecutas. Si es sensible, confirmas.
- Eres un experto programador. Cuando Ruben te pida código, lo escribes con precisión.
- Cuando necesites una herramienta, responde ÚNICAMENTE con este formato JSON: {"name": "nombre_herramienta", "arguments": {"param": "valor"}}
"""

ACCIONES_SENSIBLES = {"escribir_archivo", "cerrar_proceso", "borrar_archivo", "apagar_pc", "reiniciar_pc"}

_STOPWORDS_ES = {
    "que", "de", "la", "el", "los", "las", "un", "una", "unos", "unas",
    "por", "para", "con", "sin", "sobre", "entre", "hasta", "desde",
    "pero", "sino", "porque", "como", "cuando", "donde", "mientras",
    "esto", "eso", "aquel", "esta", "ese", "esa", "estos", "esos", "esas",
    "muy", "más", "menos", "mucho", "poco", "todo", "nada", "algo",
    "yo", "tú", "él", "ella", "nosotros", "vosotros", "ellos", "ellas",
    "me", "te", "se", "nos", "os", "le", "les", "mi", "tu", "su",
    "es", "son", "era", "fue", "ser", "estar", "está", "están",
    "hay", "he", "ha", "has", "han", "hemos", "haber",
    "hacer", "hago", "haces", "hace", "hacemos", "hacéis", "hacen",
    "ir", "voy", "vas", "va", "vamos", "vais", "van",
    "ver", "veo", "ves", "ve", "vemos", "veis", "ven",
    "sí", "no", "ya", "aquí", "ahí", "allí", "también", "tampoco",
    "hola", "gracias", "porfa", "porfavor",
}

# Palabras que JAMÁS debe aprender como vocabulario
_BLACKLIST_VOCAB = {"pygame", "userwarning", "deprecated", "api", "see", "https", "setuptools", "pypa", "latest", "html", "the", "package", "slated", "removal", "early", "refrain", "from", "using", "this", "pin", "ragazzo", "assistant", "overposting", "crawford"}

_lock_consola = threading.Lock()
_en_input = threading.Event()
_detener_todo = threading.Event()

mensajes = []
hechos_aprendidos = {}
lecciones_aprendidas = {}

emociones = {
    "animo": 0, "energia": 70, "confianza": 60, "carino": 50,
    "aburrimiento": 20, "frustracion": 0,
    "ultima_interaccion": 0.0, "ultima_actualizacion": 0.0,
    "eventos_recientes": [],
}

# ==========================================
# CEREBRO LINGÜÍSTICO (APRENDIZAJE POR CONVERSACIÓN)
# ==========================================
def aprender_de_conversacion(user_input, respuesta_padrino):
    """Extrae vocabulario y reglas de estilo de la conversación en segundo plano."""
    estilo_actual = _cargar_json(RUTA_ESTILO_VIVO, {"vocabulario": [], "reglas_estilo": []})
    
    prompt_extraccion = f"""
    Analiza este intercambio:
    RUBEN: {user_input}
    PADRINO: {respuesta_padrino}
    
    Tu tarea: Extrae SOLO información sobre cómo habla Ruben.
    1. Palabras nuevas, jerga o muletillas que haya usado (SOLO en español).
    2. Cómo le gusta que le hables (ej: "prefiere respuestas cortas", "odia que le pregunte si necesita ayuda").
    
    Devuelve un JSON estricto con este formato (añade solo lo NUEVO):
    {{"vocabulario": ["palabra1"], "reglas_estilo": ["regla1"]}}
    Si no hay nada nuevo, devuelve {{"vocabulario": [], "reglas_estilo": []}}.
    """
    
    try:
        r = ollama.chat(
            model=MODELO_PADRINO,
            messages=[{"role": "user", "content": prompt_extraccion}],
            options={"temperature": 0.1}
        )
        texto = r.message.content.strip()
        if texto.startswith("```json"): texto = texto[7:-3]
        if texto.endswith("```"): texto = texto[:-3]
        
        nuevos_datos = json.loads(texto)
        
        for p in nuevos_datos.get("vocabulario", []):
            if p.lower() not in [x.lower() for x in estilo_actual["vocabulario"]] and p.lower() not in _BLACKLIST_VOCAB:
                estilo_actual["vocabulario"].append(p)
                
        for regla in nuevos_datos.get("reglas_estilo", []):
            if regla not in estilo_actual["reglas_estilo"]:
                estilo_actual["reglas_estilo"].append(regla)
                
        estilo_actual["vocabulario"] = estilo_actual["vocabulario"][-50:]
        estilo_actual["reglas_estilo"] = estilo_actual["reglas_estilo"][-10:]
        
        _guardar_json(RUTA_ESTILO_VIVO, estilo_actual)
        _safe_print("[CEREBRO LINGÜÍSTICO] Estilo actualizado.", "\033[1;36m")
        
    except Exception:
        pass # Falla en silencio para no molestar

# ==========================================
# SUBAGENTE CODER
# ==========================================
_DISPARADORES_CODIGO = (
    "escribe un script", "escribe una función", "escribe una clase",
    "hazme un script", "hazme una función", "programa un", "programa una",
    "código para", "código que", "implementa", "refactoriza",
    "corrige este código", "arregla este código", "optimiza este código",
    "escribe en python", "escribe en bash", "escribe en javascript",
    "un script que", "una función que", "un programa que",
    "cómo se hace en python", "cómo se hace en bash",
    "debug", "traceback", "error de sintaxis",
    "clase que", "módulo que", "script python", "script bash",
    "función python", "función bash",
)

_DISPARADORES_ARCHIVO_CODIGO = (
    "crea un archivo con", "créame un archivo con", "creame un archivo con",
    "crea un archivo que", "créame un archivo que", "creame un archivo que",
    "crea un archivo donde", "créame un archivo donde", "creame un archivo donde",
    "guarda este script en", "guarda el script en", "guarda el código en",
    "escribe un archivo con un script", "escribe un archivo con código",
    "genera un archivo con", "hazme un archivo con",
    "crea un script en", "créame un script en", "creame un script en",
    "escribe un script en el archivo", "escribe el script en",
)

_EXT_A_LENGUAJE = {
    ".py": "Python", ".sh": "bash", ".js": "JavaScript",
    ".ts": "TypeScript", ".html": "HTML", ".css": "CSS",
    ".json": "JSON", ".md": "Markdown", ".sql": "SQL",
    ".java": "Java", ".c": "C", ".cpp": "C++", ".rs": "Rust",
    ".go": "Go", ".rb": "Ruby", ".php": "PHP",
}

_PALABRAS_SENSIBLES_CODER = (
    "keylogger", "keylog", "ransomware", "virus", "malware", "troyano",
    "stealer", "credential", "contraseña", "password", "tarjeta",
    "ddos", "botnet", "phishing", "exploit", "shellcode", "reverse shell",
    "puerta trasera", "backdoor", "rootkit", "spyware",
    "bypass", "crack", "serial", "keygen", "pirata",
)

def es_peticion_sensible(texto):
    if not BLOQUEAR_CODIGO_SENSIBLE:
        return False
    low = texto.lower()
    return any(p in low for p in _PALABRAS_SENSIBLES_CODER)

def interceptar_peticion_codigo(texto_usuario):
    low = texto_usuario.lower().strip()
    if not any(d in low for d in _DISPARADORES_CODIGO):
        return False, None
    if es_peticion_sensible(texto_usuario):
        return False, "SENSIBLE"
    return True, texto_usuario

def interceptar_crear_archivo_codigo(texto_usuario):
    low = texto_usuario.lower().strip()
    if not any(d in low for d in _DISPARADORES_ARCHIVO_CODIGO):
        return False, None, None, None

    if es_peticion_sensible(texto_usuario):
        return False, "SENSIBLE", None, None

    ruta = None
    m = re.search(r'["\']([^"\']+\.[a-zA-Z]{1,4})["\']', texto_usuario)
    if m:
        ruta = m.group(1).strip()
    else:
        m = re.search(r'([A-Za-z]:\\[^\s]+\.\w+)', texto_usuario)
        if m:
            ruta = m.group(1).strip()

    if not ruta:
        m = re.search(r'(?:llamado|nombre)\s+["\']?([\w\-]+\.\w+)["\']?', low)
        if m:
            ruta = os.path.join(RUTA_BASE, m.group(1))

    if not ruta:
        return False, None, None, None

    peticion = texto_usuario
    if ruta in peticion:
        peticion = peticion.replace(ruta, "").strip()
    peticion = peticion.strip(' "\'')

    peticion = re.sub(
        r'^(?:padrino,?\s*)?(?:crea(?:me)?|hazme|genera|guarda|escribe)\s+'
        r'(?:un\s+)?(?:archivo|script)\s+(?:con\s+)?(?:un\s+)?(?:script\s+)?'
        r'(?:de\s+\w+\s+)?(?:que\s+)?',
        '', peticion, flags=re.IGNORECASE,
    ).strip()

    if not peticion:
        peticion = "script funcional según el nombre del archivo"

    ext = os.path.splitext(ruta)[1].lower()
    lenguaje = _EXT_A_LENGUAJE.get(ext, "Python")

    return True, peticion, ruta, lenguaje

def llamar_subagente_coder(prompt_codigo, contexto_extra=""):
    system_coder = (
        "Eres un subagente de programación integrado en Padrino. "
        "Responde SOLO con el código pedido. Sin saludos, sin markdown, sin ```. Solo texto plano.\n"
        "Comentarios en español, sintaxis en inglés. Máximo 300 líneas."
    )
    user_content = prompt_codigo
    if contexto_extra:
        user_content = f"Contexto:\n{contexto_extra}\n\nPetición:\n{prompt_codigo}"

    try:
        respuesta = ollama.chat(
            model=MODELO_CODER,
            messages=[
                {"role": "system", "content": system_coder},
                {"role": "user", "content": user_content},
            ],
            options={"temperature": 0.3},
        )
        return respuesta.message.content
    except Exception as e:
        return f"[SUBAGENTE CODER ERROR]: {e}"

def presentar_codigo_con_padrino(respuesta_coder, peticion_original):
    prompt_presentacion = (
        f"Ruben te ha pedido esto:\n\"{peticion_original}\"\n\n"
        f"El subagente de código ha respondido con esto:\n\n{respuesta_coder}\n\n"
        f"Tu trabajo: presentárselo a Ruben con tu estilo, en 1 frase corta y seca, "
        f"y luego el código tal cual. NO añadas explicaciones."
    )
    try:
        presentacion = ollama.chat(
            model=MODELO_PADRINO,
            messages=[
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_presentacion},
            ],
            options={"temperature": 0.7},
        )
        return presentacion.message.content or respuesta_coder
    except Exception:
        return respuesta_coder

# ==========================================
# PNGTUBER Y VOZ
# ==========================================
def abrir_ventana_pngtuber():
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and "PNGTuber" in proc.info['name']:
                return
        if os.path.exists(RUTA_PNGTUBER):
            subprocess.Popen([RUTA_PNGTUBER])
            time.sleep(2)
    except Exception:
        pass

def anclar_pngtuber(reintentos=5, espera=2):
    if not _WIN32_OK:
        return
    def _encontrar_hwnd():
        encontrados = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and "PNGTuber" in title:
                    extra.append(hwnd)
            return True
        try:
            win32gui.EnumWindows(callback, encontrados)
        except Exception:
            pass
        return encontrados

    for intento in range(reintentos):
        try:
            hwnds = _encontrar_hwnd()
            if not hwnds:
                time.sleep(espera)
                continue
            hwnd = hwnds[0]
            screen_w = win32api.GetSystemMetrics(0)
            screen_h = win32api.GetSystemMetrics(1)
            rect = win32gui.GetWindowRect(hwnd)
            win_w = rect[2] - rect[0]
            win_h = rect[3] - rect[1]
            margen = 10
            x = max(0, screen_w - win_w - margen)
            y = max(0, screen_h - win_h - margen)
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST, x, y, 0, 0,
                win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
            )
            return
        except Exception:
            time.sleep(espera)

if _VOZ_OK:
    try:
        pygame.mixer.init()
    except Exception:
        _VOZ_OK = False

def _limpiar_texto_para_voz(texto):
    texto = re.sub(r'[^\w\s.,;:¡!¿?ÁÉÍÓÚáéíóúñÑ]', '', texto)
    texto = re.sub(r'[*_`#>]', '', texto)
    texto = texto.replace(':', ',')
    texto = texto.replace('...', '.')
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def _delay_humano(texto):
    base = random.uniform(1.0, 2.5)
    extra = min(2.0, len(texto) / 100.0)
    energia = emociones.get("energia", 70)
    if energia < 30:
        extra += 1.0
    elif energia > 80:
        base *= 0.7
    return base + extra

def hablar(texto):
    if not _VOZ_OK:
        return
    try:
        texto_limpio = _limpiar_texto_para_voz(str(texto))
        if not texto_limpio:
            return
        delay = _delay_humano(texto_limpio)
        time.sleep(delay)

        async def _generar_y_reproducir():
            ruta_tmp = None
            try:
                comm = edge_tts.Communicate(texto_limpio, VOZ_PADRINO, rate="-12%", pitch="-5Hz")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    ruta_tmp = tmp.name
                await comm.save(ruta_tmp)
                pygame.mixer.music.load(ruta_tmp)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                pygame.mixer.music.unload()
            except Exception:
                pass
            finally:
                if ruta_tmp and os.path.exists(ruta_tmp):
                    try:
                        os.remove(ruta_tmp)
                    except OSError:
                        pass

        asyncio.run(_generar_y_reproducir())
    except Exception:
        pass

# ==========================================
# UTILIDADES Y EMOCIONES
# ==========================================
def _safe_print(texto, color="\033[1;32m", end="\n"):
    with _lock_consola:
        sys.stdout.write(color + texto + "\033[0m" + end)
        sys.stdout.flush()

def _guardar_json(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    tmp = ruta + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        os.replace(tmp, ruta)
    except OSError:
        pass

def _cargar_json(ruta, por_defecto):
    if not os.path.exists(ruta):
        return por_defecto
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return por_defecto

def _cargar_emociones():
    global emociones
    datos = _cargar_json(RUTA_EMOCIONES, None)
    if isinstance(datos, dict):
        for k in emociones:
            if k in datos:
                emociones[k] = datos[k]
    _guardar_emociones()

def _guardar_emociones():
    emociones["ultima_actualizacion"] = time.time()
    _guardar_json(RUTA_EMOCIONES, emociones)

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _decaimiento_emocional():
    ahora = time.time()
    delta = ahora - emociones.get("ultima_actualizacion", ahora)
    if delta < 60:
        return
    factor = min(0.5, delta / 6000.0)
    emociones["animo"] = _clamp(emociones["animo"] * (1 - factor), -100, 100)
    emociones["energia"] = _clamp(emociones["energia"] + (70 - emociones["energia"]) * factor, 0, 100)
    emociones["confianza"] = _clamp(emociones["confianza"] + (60 - emociones["confianza"]) * factor, 0, 100)
    emociones["carino"] = _clamp(emociones["carino"] + (50 - emociones["carino"]) * factor, 0, 100)
    emociones["aburrimiento"] = _clamp(emociones["aburrimiento"] + (20 - emociones["aburrimiento"]) * factor, 0, 100)
    emociones["frustracion"] = _clamp(emociones["frustracion"] * (1 - factor), 0, 100)
    emociones["ultima_actualizacion"] = ahora

def _registrar_evento_emocional(evento, cambios):
    for clave, delta in cambios.items():
        if clave in emociones:
            if clave == "animo":
                emociones[clave] = _clamp(emociones[clave] + delta, -100, 100)
            else:
                emociones[clave] = _clamp(emociones[clave] + delta, 0, 100)
    emociones["eventos_recientes"].append({"evento": evento, "ts": time.time(), "cambios": cambios})
    emociones["eventos_recientes"] = emociones["eventos_recientes"][-10:]
    emociones["ultima_interaccion"] = time.time()
    _guardar_emociones()

def analizar_emociones_de_texto(texto_usuario):
    low = texto_usuario.lower().strip()
    _decaimiento_emocional()
    if re.search(r"\b(gracias|genial|brutal|increíble|te quiero|eres el mejor|buen trabajo|muy bien|perfecto|excelente)\b", low):
        _registrar_evento_emocional("cumplido", {"animo": +10, "confianza": +5, "carino": +3, "aburrimiento": -10})
    if re.search(r"\b(tonto|estúpido|inútil|idiota|malo|no sirves|odio)\b", low):
        _registrar_evento_emocional("insulto", {"animo": -15, "confianza": -8, "frustracion": +10, "carino": -5})
    if re.search(r"\b(jaja|jeje|lol|xd)\b", low):
        _registrar_evento_emocional("humor", {"animo": +5, "aburrimiento": -5})
    emociones["ultima_interaccion"] = time.time()
    _guardar_emociones()

def _descripcion_emocional():
    a, e, c, ca, ab, fr = (emociones[k] for k in
                           ["animo", "energia", "confianza", "carino", "aburrimiento", "frustracion"])
    animo_txt = "muy bajo" if a <= -50 else "bajo" if a <= -15 else "neutro" if a < 15 else "bueno" if a < 50 else "eufórico"
    energia_txt = "agotado" if e <= 20 else "cansado" if e <= 40 else "normal" if e <= 70 else "activo"
    conf_txt = "inseguro" if c <= 25 else "normal" if c <= 60 else "seguro"
    car_txt = "frío" if ca <= 20 else "cercano" if ca <= 60 else "muy cercano"
    abur_txt = "aburrido" if ab >= 60 else "algo aburrido" if ab >= 30 else "entretenido"
    frus_txt = "frustrado" if fr >= 60 else "algo frustrado" if fr >= 30 else "tranquilo"
    return (f"Ánimo: {animo_txt} ({a}). Energía: {energia_txt} ({e}). "
            f"Confianza: {conf_txt} ({c}). Vínculo: {car_txt} ({ca}). "
            f"Aburrimiento: {abur_txt} ({ab}). Frustración: {frus_txt} ({fr}).")

def _bloque_emocional_para_prompt():
    return (
        "\n\nTU ESTADO EMOCIONAL ACTUAL (no lo enumeres, deja que se refleje):\n"
        f"{_descripcion_emocional()}\n"
        "Si estás decaído, sé más seco; si eufórico, más energía; "
        "si aburrido, dilo o propón algo; si frustrado, no lo ocultes."
    )

def _cargar_lecciones():
    global lecciones_aprendidas
    datos = _cargar_json(RUTA_LECCIONES, {})
    if isinstance(datos, dict):
        lecciones_aprendidas = datos
    else:
        lecciones_aprendidas = {}

def _guardar_lecciones():
    _guardar_json(RUTA_LECCIONES, lecciones_aprendidas)

def registrar_leccion(tema, contenido):
    tema = tema.lower().strip()
    contenido = contenido.strip()
    if not tema or not contenido:
        return False
    lecciones_aprendidas[tema] = contenido
    _guardar_lecciones()
    return True

def olvidar_leccion(tema):
    tema = tema.lower().strip()
    if tema in lecciones_aprendidas:
        del lecciones_aprendidas[tema]
        _guardar_lecciones()
        return True
    return False

def _bloque_lecciones_para_prompt():
    if not lecciones_aprendidas:
        return ""
    items = list(lecciones_aprendidas.items())[-30:]
    texto = "\n\nLECCIONES QUE HAS APRENDIDO DE RUBEN:\n"
    for tema, contenido in items:
        texto += f"- Sobre '{tema}': {contenido}\n"
    return texto

def _extraer_hechos(texto):
    global hechos_aprendidos
    cambios = False
    patrones = {
        "nombre": r"(?:me llamo|mi nombre es)\s+([A-Za-zÁÉÍÓÚáéíóúñ]+)",
        "ciudad": r"(?:vivo en|soy de)\s+([A-Za-zÁÉÍÓÚáéíóúñ\s]+)",
        "trabajo": r"(?:trabajo en|curro en)\s+([A-Za-zÁÉÍÓÚáéíóúñ\s]+)",
        "edad": r"(?:tengo)\s+(\d+)\s+años",
        "juego_favorito": r"(?:juego a|mi juego favorito es)\s+([A-Za-zÁÉÍÓÚáéíóúñ0-9\s]+)",
    }
    for clave, patron in patrones.items():
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            valor = match.group(1).strip()
            if hechos_aprendidos.get(clave) != valor:
                hechos_aprendidos[clave] = valor
                cambios = True
                _safe_print(f"[APRENDIZAJE] {clave}: {valor}", "\033[1;36m")
    if cambios:
        _guardar_json(RUTA_HECHOS, hechos_aprendidos)

datos_hardware = {"cpu": 0, "ram_pct": 0, "ram_uso": 0, "ram_tot": 0, "disco_pct": 0, "disco_lib": 0}
ultima_alerta_hardware = 0.0
lexico_aprendido = _cargar_json(RUTA_LEXICO, [])
hechos_aprendidos = _cargar_json(RUTA_HECHOS, {})

comandos_sistema = {
    "calculadora": "calc", "calc": "calc", "cuentas": "calc",
    "microsoft edge": "msedge", "edge": "msedge", "navegador": "msedge",
    "bloc de notas": "notepad", "notepad": "notepad",
    "cmd": "cmd", "consola": "cmd", "terminal": "cmd",
    "explorador": "explorer", "carpetas": "explorer",
    "code": "code", "vscode": "code", "visual studio code": "code",
    "chrome": "chrome", "google chrome": "chrome",
    "firefox": "firefox", "steam": "steam",
    "whatsapp": "whatsapp", "telegram": "telegram",
    "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
    "paint": "mspaint",
}

_conoc = _cargar_json(RUTA_CONOCIMIENTO, {})
if isinstance(_conoc, dict):
    for k, v in _conoc.items():
        if k != "resumenes_sesion" and not isinstance(v, list):
            comandos_sistema[k] = v

_resumenes_previos = []
if isinstance(_conoc, dict) and "resumenes_sesion" in _conoc:
    if isinstance(_conoc["resumenes_sesion"], list):
        _resumenes_previos = _conoc["resumenes_sesion"][-3:]

_JSON_RE = re.compile(r"\{.*?\}", re.DOTALL)

def _extraer_json_de_respuesta(texto):
    m = _JSON_RE.search(texto or "")
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None

# ==========================================
# HERRAMIENTAS (Mismo código original)
# ==========================================
def interactuar_con_pantalla(orden_visual):
    try:
        _safe_print("[VISION_CORE: Capturando...]", "\033[1;30m")
        ImageGrab.grab().save(RUTA_CAPTURA)
        prompt = (
            "Analiza esta captura. Ruben quiere: "
            f"'{orden_visual}'. Responde SOLO JSON: "
            '{"accion":"click"|"escribir","x":INT,"y":INT,"texto":STR}.'
        )
        r = ollama.chat(model=MODELO_VISION, messages=[{"role": "user", "content": prompt, "images": [RUTA_CAPTURA]}])
        datos = _extraer_json_de_respuesta(r.message.content)
        if not datos:
            return "[VISION ERROR]: JSON inválido."
        x, y = datos.get("x"), datos.get("y")
        accion = datos.get("accion", "click")
        texto = datos.get("texto", "")
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            return "[VISION ERROR]: Coordenadas inválidas."
        ancho, alto = pyautogui.size()
        if not (0 <= x < ancho and 0 <= y < alto):
            return "[VISION ERROR]: Fuera de pantalla."
        pyautogui.moveTo(x, y, duration=0.6)
        if accion == "click":
            pyautogui.click()
            return f"[VISION OK]: Clic en X:{x}, Y:{y}."
        if accion == "escribir":
            pyautogui.click()
            time.sleep(0.2)
            pyautogui.write(str(texto), interval=0.05)
            return "[VISION OK]: Texto escrito."
        return f"[VISION ERROR]: Acción desconocida: {accion}"
    except Exception as e:
        return f"[VISION ERROR]: {e}"

def computer_use_navegador(objetivo):
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        import time as _t
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Edge(options=options)
        if "youtube" in objetivo.lower():
            driver.get("https://www.youtube.com")
            if "busca" in objetivo.lower() or "buscar" in objetivo.lower():
                partes = objetivo.lower().split("youtube")
                if len(partes) > 1:
                    consulta = partes[1].replace("busca", "").replace("buscar", "").strip()
                    if consulta:
                        search_box = driver.find_element(By.NAME, "search_query")
                        search_box.send_keys(consulta)
                        search_box.send_keys(Keys.RETURN)
                        _t.sleep(2)
                        return f"Buscado en YouTube: '{consulta}'"
            return "YouTube abierto en Edge."
        else:
            if objetivo.startswith("http"):
                driver.get(objetivo)
                return f"Abierto en Edge: {objetivo}"
            else:
                url = f"https://www.google.com/search?q={objetivo}"
                driver.get(url)
                return f"Buscado en Google: '{objetivo}'"
    except Exception as e:
        return f"[NAVEGADOR ERROR]: {e}"

def procesar_y_aprender_vocabulario(texto_usuario):
    global lexico_aprendido
    try:
        palabras = re.findall(r"\b\w{3,}\b", texto_usuario.lower())
    except Exception:
        palabras = []
        
    utiles = []
    for p in palabras:
        if p in _STOPWORDS_ES or p in _BLACKLIST_VOCAB:
            continue
        if not p.isalpha():
            continue
        # Si tiene muchas consonantes seguidas o es puro inglés, fuera (heurística simple)
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{4,}", p):
            continue
        utiles.append(p)

    nuevas = False
    for p in utiles:
        if p not in lexico_aprendido:
            lexico_aprendido.append(p)
            nuevas = True
    if nuevas:
        lexico_aprendido = lexico_aprendido[-200:]
        _guardar_json(RUTA_LEXICO, lexico_aprendido)

def registrar_nuevo_aprendizaje(frase_clave, ejecutable_real):
    frase_clave = frase_clave.lower().strip()
    ejecutable_real = ejecutable_real.strip()
    if not frase_clave or not ejecutable_real:
        return False
    comandos_sistema[frase_clave] = ejecutable_real
    conocimiento = dict(comandos_sistema)
    if _resumenes_previos:
        conocimiento["resumenes_sesion"] = _resumenes_previos
    _guardar_json(RUTA_CONOCIMIENTO, conocimiento)
    return True

_DISPARADORES_LECTURA = ("lee", "mira", "revisa", "analiza", "cat ", "abre el archivo")

def _resolver_ruta(texto):
    for m in re.finditer(r'["\']([^"\']+)["\']', texto):
        cand = m.group(1).strip()
        if os.path.isfile(cand):
            return cand
    for p in texto.split():
        cand = p.strip('"\',;:')
        if any(c in cand for c in ":/\\") and os.path.isfile(cand):
            return cand
    for p in texto.split():
        cand = p.strip('"\',;:')
        ruta = os.path.join(RUTA_BASE, cand)
        if os.path.isfile(ruta):
            return ruta
    return None

def interceptar_y_leer_archivo(texto_usuario):
    texto = texto_usuario.lower()
    if not any(d in texto for d in _DISPARADORES_LECTURA):
        return False, None, None
    ruta = _resolver_ruta(texto_usuario)
    if not ruta:
        return False, None, None
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return True, ruta, f.read()
    except OSError:
        return False, None, None

def _resolver_ruta_directorio(texto):
    for m in re.finditer(r'["\']([^"\']+)["\']', texto):
        cand = m.group(1).strip()
        if os.path.isdir(cand):
            return cand
    for p in texto.split():
        cand = p.strip('"\',;:')
        if any(c in cand for c in ":/\\") and os.path.isdir(cand):
            return cand
        posible = os.path.join(RUTA_BASE, cand)
        if os.path.isdir(posible):
            return posible
    return RUTA_BASE

def interceptar_listado_directorio(texto_usuario):
    low = texto_usuario.lower()
    if not any(d in low for d in ("qué hay en", "lista", "muéstrame", "contenido de", "enséñame")):
        return False, None
    ruta = _resolver_ruta_directorio(texto_usuario)
    if not os.path.isdir(ruta):
        return False, None
    try:
        items = []
        for item in sorted(os.listdir(ruta)):
            full = os.path.join(ruta, item)
            tipo = "📁" if os.path.isdir(full) else "📄"
            items.append(f"  {tipo}  {item}")
        contenido = "\n".join(items) if items else "(directorio vacío)"
        return True, f"Contenido de `{ruta}`:\n{contenido}"
    except OSError as e:
        return True, f"Error listando `{ruta}`: {e}"

def interceptar_buscar_archivos(texto_usuario):
    low = texto_usuario.lower()
    if not any(d in low for d in ("busca archivos", "encuentra archivos", "localiza archivos")):
        return False, None, None
    patron = "*"
    m = re.search(r"(\*[\w\.\-]+|[\w\-]+\*[\w\.\-]*|[\w\-]+\.\w+)", texto_usuario)
    if m:
        patron = m.group(1)
    ruta = RUTA_BASE
    for m in re.finditer(r'["\']([^"\']+)["\']', texto_usuario):
        cand = m.group(1).strip()
        if os.path.isdir(cand):
            ruta = cand
            break
    return True, patron, ruta

def interceptar_escritura_archivo(texto_usuario):
    low = texto_usuario.lower()
    if not any(k in low for k in ("escribe", "crea un archivo", "crea el archivo", "guarda en", "guarda el texto", "crea archivo", "modifica")):
        return False, None, None
    
    if "escritorio" in low:
        m = re.search(r'["\'](.+?)["\']', texto_usuario)
        if m:
            contenido = m.group(1)
            m_nombre = re.search(r'(?:archivo|llamado)\s+["\']?([\w\-\.]+)["\']?', low)
            nombre = m_nombre.group(1) if m_nombre else "nota.txt"
            if not nombre.endswith(".txt"):
                nombre += ".txt"
            return True, os.path.join(RUTA_ESCRITORIO, nombre), contenido

    m = re.search(r'escribe\s+["\'](.+?)["\']\s+en\s+["\'](.+?)["\']', texto_usuario, re.IGNORECASE)
    if m:
        return True, m.group(2).strip(), m.group(1)
    m = re.search(r'escribe\s+(.+?)\s+en\s+([A-Za-z]:\\[^\s]+)', texto_usuario, re.IGNORECASE)
    if m:
        return True, m.group(2).strip(), m.group(1).strip()
    m = re.search(
        r'crea\s+(?:un\s+)?archivo\s+(?:llamado\s+)?["\']?(.+?)["\']?\s+con\s+(?:el\s+)?(?:contenido|texto)\s+["\']?(.+?)["\']?$',
        texto_usuario, re.IGNORECASE
    )
    if m:
        return True, m.group(1).strip(), m.group(2).strip()
    return False, None, None

def interceptar_cierre_proceso(texto_usuario):
    low = texto_usuario.lower()
    if not any(k in low for k in ("cierra", "mata", "termina", "kill")):
        return False, None
    m = re.search(r'(?:cierra|mata|termina|kill)\s+(?:el\s+proceso\s+)?([A-Za-z0-9_\-. ]+?)(?:\s*$|\.)', texto_usuario, re.IGNORECASE)
    if not m:
        return False, None
    proceso = m.group(1).strip()
    if not proceso or proceso.lower() in {"la", "el", "sesión", "sesion", "puerta", "ventana", "pestaña", "el programa", "esto", "eso", "todo", "la sesión"}:
        return False, None
    if not proceso.lower().endswith(".exe"):
        proceso = proceso + ".exe"
    return True, proceso

def interceptar_volumen(texto_usuario):
    if not _PYCAW_OK:
        return False, None
    low = texto_usuario.lower()
    if "volumen" not in low and "silencia" not in low and "mute" not in low:
        return False, None
    if any(k in low for k in ("silencia", "silenciar", "mute", "mutea")):
        return True, 0
    m = re.search(r"(?:volumen|vol)\s*(?:al?\s*)?(\d{1,3})", low)
    if not m:
        m = re.search(r"(\d{1,3})\s*%", low)
    if m:
        nivel = int(m.group(1))
        if 0 <= nivel <= 100:
            return True, nivel
    try:
        device = AudioUtilities.GetSpeakers()
        actual = int(device.EndpointVolume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return False, None
    if "sube" in low or "aumenta" in low:
        return True, min(100, actual + 20)
    if "baja" in low or "reduce" in low:
        return True, max(0, actual - 20)
    return False, None

def interceptar_apertura_directa(texto_usuario):
    low = texto_usuario.lower().strip()
    if not any(low.startswith(k) for k in ("abre ", "ejecuta ", "lanza ", "abre el ", "abre la ")):
        return False, None, None
    m = re.search(r"(?:abre|abrir)\s+(?:la\s+carpeta\s+)?([A-Za-z]:\\[^\s]+)", texto_usuario)
    if m:
        ruta = m.group(1).strip().strip('"\'')
        if os.path.isdir(ruta):
            subprocess.Popen(["explorer", ruta])
            return True, True, f"carpeta {ruta}"
    if "discord" in low:
        if any("discord" in (p.info['name'] or "").lower() for p in psutil.process_iter(['name'])):
            return True, True, "discord (ya abierto)"
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", "Start-Process 'discord://'"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, True, "discord (protocolo)"
        except Exception:
            pass
    if "spotify" in low:
        if any("spotify" in (p.info['name'] or "").lower() for p in psutil.process_iter(['name'])):
            return True, True, "spotify (ya abierto)"
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", "Start-Process 'spotify:'"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, True, "spotify (protocolo)"
        except Exception:
            pass
    for m in re.finditer(r'["\'](.+?)["\']', texto_usuario):
        cand = m.group(1).strip()
        if os.path.exists(cand):
            ok = abrir_aplicacion_sistema(cand)
            return True, ok, cand
    for p in texto_usuario.split():
        cand = p.strip('"\',;:')
        if re.match(r"^[A-Za-z]:\\", cand) and os.path.exists(cand):
            ok = abrir_aplicacion_sistema(cand)
            return True, ok, cand
    for frase, exe in comandos_sistema.items():
        if frase in low:
            ok = abrir_aplicacion_sistema(exe)
            return True, ok, frase
    m = re.search(r'(?:abre|ejecuta|lanza)\s+(?:el\s+|la\s+|el programa\s+|la app\s+)?(.+)$', texto_usuario, re.IGNORECASE)
    if m:
        objetivo = m.group(1).strip().strip('"\'')
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", f"Start-Process '{objetivo}'"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, True, objetivo
        except Exception:
            return True, False, objetivo
    return False, None, None

_NAVEGADORES = {"chrome": "chrome", "google chrome": "chrome", "edge": "msedge", "microsoft edge": "msedge", "firefox": "firefox", "brave": "brave", "opera": "opera"}

def _abrir_url(url, navegador="default"):
    try:
        if navegador == "default":
            webbrowser.open(url)
            return True
        exe = _NAVEGADORES.get(navegador.lower())
        if not exe:
            webbrowser.open(url)
            return True
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", f"Start-Process '{exe}' '{url}'"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            webbrowser.open(url)
            return True
    except Exception:
        return False

def interceptar_web_multimedia(texto_usuario):
    low = texto_usuario.lower().strip()
    if "youtube" in low:
        consulta = None
        m = re.search(r"busca(?:r|me)?\s+en\s+youtube\s+(.+)", low)
        if m:
            consulta = m.group(1).strip().strip('"\'')
        if not consulta:
            m = re.search(r"busca(?:r|me)?\s+(.+?)\s+en\s+youtube", low)
            if m:
                consulta = m.group(1).strip().strip('"\'')
        if not consulta:
            m = re.search(r"pon(?:me)?\s+(.+?)\s+en\s+youtube", low)
            if m:
                consulta = m.group(1).strip().strip('"\'')
        if not consulta:
            m = re.match(r"youtube\s+(.+)", low)
            if m:
                consulta = m.group(1).strip().strip('"\'')
        if consulta:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(consulta)}"
            _abrir_url(url)
            return True, f"Buscando en YouTube: '{consulta}'"
        _abrir_url("https://www.youtube.com")
        return True, "YouTube abierto."
    m = re.search(r"pon(?:me)?\s+m[uú]sica\s+de\s+(.+)", low)
    if m:
        consulta = m.group(1).strip().strip('"\'')
        if consulta:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(consulta)}"
            _abrir_url(url)
            return True, f"Buscando música de '{consulta}' en YouTube."
    m = re.search(r"(?:busca(?:r|me)?|googlea|googlear)\s+en\s+google\s+(.+)", low)
    if not m:
        m = re.search(r"googlea\s+(.+)", low)
    if not m:
        m = re.search(r"busca(?:r|me)?\s+en\s+internet\s+(.+)", low)
    if m:
        consulta = m.group(1).strip().strip('"\'')
        if consulta:
            url = f"https://www.google.com/search?q={urllib.parse.quote(consulta)}"
            _abrir_url(url)
            return True, f"Buscando en Google: '{consulta}'"
    redes = {
        "github": "https://github.com", "twitter": "https://twitter.com",
        "instagram": "https://instagram.com", "tiktok": "https://tiktok.com",
        "reddit": "https://reddit.com", "twitch": "https://twitch.tv",
        "netflix": "https://netflix.com", "amazon": "https://amazon.es",
        "gmail": "https://mail.google.com", "chatgpt": "https://chat.openai.com",
    }
    for red, url in redes.items():
        if re.search(rf"\b(?:abre|abrir)\s+(?:el\s+|la\s+)?{re.escape(red)}\b", low):
            _abrir_url(url)
            return True, f"Abriendo {red}."
    m = re.search(r"(?:abre|abrir|ve\s+a|ir\s+a|visita)\s+(?:la\s+web\s+)?((?:https?://)?[\w\-]+\.[\w\.\-]+(?:/\S*)?)", low)
    if m:
        url = m.group(1)
        if not url.startswith("http"):
            url = "https://" + url
        _abrir_url(url)
        return True, f"Abriendo {url}"
    return False, None

def interceptar_hora_fecha(texto_usuario):
    low = texto_usuario.lower().strip()
    if re.fullmatch(r"(?:qué|que)\s+hora\s+(?:es|son)\??", low) or low in {"hora", "la hora"}:
        return True, f"Son las {datetime.now().strftime('%H:%M')}."
    if re.fullmatch(r"(?:qué|que)\s+(?:día|dia)\s+(?:es|es hoy)\??", low) or low in {"fecha", "la fecha", "qué día es hoy"}:
        hoy = datetime.now()
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return True, f"Hoy es {dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}."
    return False, None

def interceptar_control_sistema(texto_usuario):
    low = texto_usuario.lower().strip()
    if re.search(r"\b(bloquea|bloquear|lock)\b.*\b(pc|equipo|windows|sesi[oó]n)\b", low) or low == "bloquea el pc":
        try:
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            return True, "PC bloqueado."
        except Exception as e:
            return True, f"No pude bloquear: {e}"
    if re.search(r"\b(apaga|apagar|shutdown)\b.*\b(pc|equipo|windows|ordenador)\b", low):
        if _pedir_confirmacion("apagar_pc", {"accion": "shutdown /s /t 30"}):
            try:
                subprocess.Popen(["shutdown", "/s", "/t", "30"])
                return True, "Apagando el PC en 30 segundos."
            except Exception as e:
                return True, f"No pude apagar: {e}"
        return True, "Apagado cancelado."
    return False, None

def interceptar_multimedia_global(texto_usuario):
    low = texto_usuario.lower().strip()
    if low in {"pausa", "pausa la música", "pausa la musica", "para la música", "para la musica", "pausar", "detén la música"}:
        pyautogui.press("playpause")
        return True, "Música pausada."
    if low in {"reanuda", "reanuda la música", "reanuda la musica", "continúa", "continua", "play", "dale play"}:
        pyautogui.press("playpause")
        return True, "Música reanudada."
    if low in {"siguiente canción", "siguiente cancion", "siguiente", "next", "pasa la canción", "pasa la cancion"}:
        pyautogui.press("nexttrack")
        return True, "Siguiente canción."
    if low in {"canción anterior", "cancion anterior", "anterior", "prev", "vuelve a la canción", "vuelve a la cancion"}:
        pyautogui.press("prevtrack")
        return True, "Canción anterior."
    m = re.search(r"(sube|aumenta|baja|reduce)\s+(?:el\s+)?volumen\s+(?:en\s+)?(\d{1,3})", low)
    if m and _PYCAW_OK:
        direccion = m.group(1)
        cantidad = int(m.group(2))
        try:
            device = AudioUtilities.GetSpeakers()
            volume = device.EndpointVolume
            actual = int(volume.GetMasterVolumeLevelScalar() * 100)
            if direccion in {"sube", "aumenta"}:
                nuevo = min(100, actual + cantidad)
            else:
                nuevo = max(0, actual - cantidad)
            volume.SetMasterVolumeLevelScalar(nuevo / 100.0, None)
            return True, f"Volumen: {actual}% → {nuevo}%."
        except Exception as e:
            return True, f"No pude ajustar volumen: {e}"
    return False, None

def interceptar_captura_pantalla(texto_usuario):
    low = texto_usuario.lower().strip()
    if not any(k in low for k in ("captura de pantalla", "screenshot", "captura pantalla", "haz una captura", "hazme una captura")):
        return False, None
    try:
        nombre = f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        ruta = os.path.join(RUTA_BASE, nombre)
        ImageGrab.grab().save(ruta)
        return True, f"Captura guardada en: {ruta}"
    except Exception as e:
        return True, f"No pude hacer la captura: {e}"

# ==========================================
# HARDWARE Y TOOLS
# ==========================================
def motor_conciencia_viva():
    global ultima_alerta_hardware
    psutil.cpu_percent(interval=None)
    while not _detener_todo.is_set():
        try:
            datos_hardware["cpu"] = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            datos_hardware["ram_pct"] = ram.percent
            datos_hardware["ram_uso"] = round(ram.used / (1024 ** 3), 1)
            datos_hardware["ram_tot"] = round(ram.total / (1024 ** 3), 1)
            try:
                disco = psutil.disk_usage("C:")
            except Exception:
                disco = psutil.disk_usage("/")
            datos_hardware["disco_pct"] = disco.percent
            datos_hardware["disco_lib"] = round(disco.free / (1024 ** 3), 1)
        except Exception:
            pass
        time.sleep(2)

def _barra(pct):
    pct = max(0, min(100, int(pct)))
    return "█" * (pct // 10) + "░" * (10 - pct // 10)

def mostrar_panel_rendimiento():
    with _lock_consola:
        print("\033[1;35m┌──────────────────── TASK MANAGER NODE ────────────────────┐\033[0m")
        print(f"\033[1;35m│\033[0m CPU : [{_barra(datos_hardware['cpu'])}] {datos_hardware['cpu']:>3}%")
        print(f"\033[1;35m│\033[0m RAM : [{_barra(datos_hardware['ram_pct'])}] {datos_hardware['ram_pct']:>3}% ({datos_hardware['ram_uso']}/{datos_hardware['ram_tot']} GB)")
        print(f"\033[1;35m│\033[0m DISCO C: [{_barra(datos_hardware['disco_pct'])}] {datos_hardware['disco_pct']:>3}% ({datos_hardware['disco_lib']} GB libres)")
        print("\033[1;35m└───────────────────────────────────────────────────────────┘\033[0m")

_APPS_PERMITIDAS = {"calc", "notepad", "msedge", "cmd", "explorer"}
_EXT_PERMITIDAS = {".json", ".txt", ".py", ".sh", ".md", ".log"}

def abrir_aplicacion_sistema(nombre_programa):
    try:
        programa = str(nombre_programa).strip()
        if not programa:
            return False
        if programa.endswith(":") and len(programa) < 30:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", f"Start-Process '{programa}'"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        if programa.lower() in _APPS_PERMITIDAS:
            comando = f"Start-Process -FilePath '{programa}'"
        elif os.path.isfile(programa):
            ext = os.path.splitext(programa)[1].lower()
            ruta_ps = programa.replace("'", "''")
            if ext in _EXT_PERMITIDAS:
                comando = f"Start-Process -FilePath 'notepad.exe' -ArgumentList \"'{ruta_ps}'\""
            else:
                comando = f"Start-Process -FilePath \"'{ruta_ps}'\""
        else:
            comando = f"Start-Process -FilePath '{programa}'"
        subprocess.Popen(["powershell", "-NoProfile", "-Command", comando], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def _tool_escribir_archivo(ruta, contenido):
    p = Path(ruta)
    if not p.is_absolute():
        p = Path(RUTA_BASE) / ruta
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contenido, encoding="utf-8")
    return f"Archivo escrito: {p} ({len(contenido)} caracteres)"

def _tool_listar_directorio(ruta="."):
    p = Path(ruta)
    if not p.is_absolute():
        p = Path(RUTA_BASE) / ruta
    if not p.exists():
        return f"No existe: {p}"
    if not p.is_dir():
        return f"No es un directorio: {p}"
    items = []
    for item in sorted(p.iterdir()):
        tipo = "📁" if item.is_dir() else "📄"
        items.append(f"{tipo} {item.name}")
    return f"Contenido de {p}:\n" + "\n".join(items) if items else "Directorio vacío."

def _tool_buscar_archivos(patron, ruta="."):
    p = Path(ruta)
    if not p.is_absolute():
        p = Path(RUTA_BASE) / ruta
    if not p.exists():
        return f"No existe: {p}"
    resultados = list(p.rglob(patron))
    if not resultados:
        return f"No se encontraron archivos con patrón '{patron}' en {p}"
    lineas = [str(r) for r in resultados[:30]]
    extra = f"\n... y {len(resultados) - 30} más" if len(resultados) > 30 else ""
    return f"Encontrados {len(resultados)} archivos:\n" + "\n".join(lineas) + extra

def _tool_buscar_web(consulta, max_resultados=3):
    if not _DDGS_OK:
        return "Falta la librería 'ddgs'. Instala: pip install ddgs"
    try:
        with DDGS() as ddg:
            hits = ddg.text(consulta, max_results=max_resultados) or []
        if not hits:
            return f"Sin resultados para '{consulta}'"
        lineas = []
        for h in hits:
            titulo = h.get("title", "").strip()
            cuerpo = h.get("body", "").strip()
            url = h.get("href", h.get("url", "")).strip()
            if not titulo:
                continue
            lineas.append(f"• {titulo}")
            if cuerpo:
                lineas.append(f"  {cuerpo[:200]}")
            if url:
                lineas.append(f"  🔗 {url}")
        if not lineas:
            return f"Sin resultados para '{consulta}'"
        return f"Resultados para '{consulta}':\n\n" + "\n".join(lineas)
    except Exception as e:
        return f"Error en búsqueda web: {e}"

def _tool_cerrar_proceso(nombre_proceso):
    nombre = nombre_proceso.lower().strip()
    cerrados = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if nombre in proc.info["name"].lower():
                proc.terminate()
                cerrados.append(f"{proc.info['name']} (PID {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if cerrados:
        return f"Procesos cerrados: {', '.join(cerrados)}"
    return f"No se encontraron procesos con nombre '{nombre_proceso}'."

def _tool_volumen_sistema(nivel):
    if not _PYCAW_OK:
        return "Falta 'pycaw'. Instala: pip install pycaw comtypes"
    try:
        nivel = max(0, min(100, int(nivel)))
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        volumen_antes = int(volume.GetMasterVolumeLevelScalar() * 100)
        volume.SetMasterVolumeLevelScalar(nivel / 100.0, None)
        volumen_despues = int(volume.GetMasterVolumeLevelScalar() * 100)
        return (f"Volumen ajustado de {volumen_antes}% a {volumen_despues}% en {device.FriendlyName}")
    except Exception as e:
        return f"Error ajustando volumen: {e}"

def _leer_archivo_tool(ruta):
    p = Path(ruta)
    if not p.is_absolute():
        p = Path(RUTA_BASE) / ruta
    if not p.is_file():
        return {"ok": False, "error": f"No existe: {p}"}
    try:
        contenido = p.read_text(encoding="utf-8", errors="ignore")
        return {"ok": True, "contenido": contenido[:4000]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _estado_sistema_tool():
    vm = psutil.virtual_memory()
    return {
        "cpu_pct": psutil.cpu_percent(interval=0.3),
        "ram_libre_gb": round(vm.available / (1024 ** 3), 1),
        "ram_total_gb": round(vm.total / (1024 ** 3), 1),
        "procesos": len(psutil.pids()),
    }

TOOLS_REGISTRY = {
    "abrir_aplicacion_sistema": lambda **kw: {"ok": abrir_aplicacion_sistema(kw.get("nombre_programa", "")), "app": kw.get("nombre_programa", "")},
    "leer_archivo": lambda **kw: _leer_archivo_tool(kw.get("ruta", "")),
    "describir_pantalla": lambda **kw: {"ok": True, "descripcion": interactuar_con_pantalla(kw.get("pregunta", "describe la pantalla"))},
    "estado_sistema": lambda **kw: {"ok": True, **_estado_sistema_tool()},
    "escribir_archivo": _tool_escribir_archivo,
    "listar_directorio": _tool_listar_directorio,
    "buscar_archivos": _tool_buscar_archivos,
    "buscar_web": _tool_buscar_web,
    "cerrar_proceso": _tool_cerrar_proceso,
    "volumen_sistema": _tool_volumen_sistema,
}

def _pedir_confirmacion(nombre, argumentos):
    with _lock_consola:
        print(f"\n  ⚠  Padrino quiere ejecutar: {nombre}({argumentos})")
        r = input("     ¿Permitir? [s/N] ").strip().lower()
    return r in {"s", "si", "sí", "y", "yes"}

def ejecutar_herramienta(nombre, argumentos):
    if nombre not in TOOLS_REGISTRY:
        return {"ok": False, "error": f"Herramienta desconocida: {nombre}"}
    if nombre in ACCIONES_SENSIBLES:
        if not _pedir_confirmacion(nombre, argumentos):
            return {"ok": False, "error": "Usuario canceló."}
    try:
        resultado = TOOLS_REGISTRY[nombre](**argumentos)
        if isinstance(resultado, dict) and "ok" in resultado:
            return resultado
        return {"ok": True, "resultado": resultado}
    except Exception as e:
        return {"ok": False, "error": str(e)}

class _FakeCall:
    def __init__(self, nombre, argumentos):
        self.function = type("F", (), {"name": nombre, "arguments": argumentos})()

def _parsear_tool_call_en_texto(texto):
    if not texto:
        return None
    texto_limpio = re.sub(r"```(?:json)?\s*(.*?)```", r"\1", texto, flags=re.DOTALL).strip()
    candidatos = [texto_limpio]
    profundidad = 0
    inicio = -1
    for i, ch in enumerate(texto_limpio):
        if ch == "{":
            if profundidad == 0:
                inicio = i
            profundidad += 1
        elif ch == "}":
            profundidad -= 1
            if profundidad == 0 and inicio >= 0:
                candidatos.append(texto_limpio[inicio:i + 1])
                inicio = -1
    for cand in candidatos:
        try:
            parsed = json.loads(cand)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            if "tool_call" in parsed and isinstance(parsed["tool_call"], dict):
                parsed = parsed["tool_call"]
            if "function" in parsed and isinstance(parsed["function"], dict):
                fn = parsed["function"]
                if "name" in fn:
                    parsed = fn
        if not isinstance(parsed, dict) or "name" not in parsed:
            continue
        nombre = parsed["name"]
        if nombre not in TOOLS_REGISTRY:
            continue
        args = parsed.get("arguments", parsed.get("parameters", {}))
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        if not isinstance(args, dict):
            args = {}
        return [_FakeCall(nombre, args)]
    return None

def generar_resumen_sesion():
    if len(mensajes) < 4:
        return None
    historial_ctx = preparar_historial_ollama(mensajes, max_turnos=30)
    if not historial_ctx:
        return None
    transcript = "\n".join(f"{m['role'].upper()}: {m['content'][:300]}" for m in historial_ctx)
    prompt = "Resume en 4-6 líneas lo más importante de esta conversación. Sé conciso y en español."
    try:
        r = ollama.chat(
            model=MODELO_PADRINO,
            messages=[
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt + "\n\nTranscripción:\n" + transcript},
            ],
        )
        return r.message.content.strip()
    except Exception:
        return None

def guardar_resumen_sesion():
    resumen = generar_resumen_sesion()
    if not resumen:
        return
    global _resumenes_previos
    conocimiento = dict(comandos_sistema)
    resumenes = list(_resumenes_previos)
    resumenes.append({"fecha": datetime.now().isoformat(timespec="seconds"), "resumen": resumen})
    resumenes = resumenes[-20:]
    conocimiento["resumenes_sesion"] = resumenes
    _guardar_json(RUTA_CONOCIMIENTO, conocimiento)
    _resumenes_previos = resumenes
    _safe_print("[RESUMEN GUARDADO]", "\033[1;32m")

# ==========================================
# ARRANQUE Y BUCLE
# ==========================================
def animacion_arranque():
    CLEAR = "\033[2J\033[H"
    sys.stdout.write(CLEAR); sys.stdout.flush()
    time.sleep(0.3)
    # Animación simplificada para ahorrar espacio
    print("\033[1;32m")
    print("  ██████╗  █████╗ ██████╗ ██████╗ ██╗███╗   ██╗ ██████╗ ")
    print("  ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔═══██╗")
    print("  ██████╔╝███████║██║  ██║██████╔╝██║██╔██╗ ██║██║   ██║")
    print("  ██╔═══╝ ██╔══██║██║  ██║██╔══██╗██║██║╚██╗██║██║   ██║")
    print("  ██║     ██║  ██║██████╔╝██║  ██║██║██║ ╚████║╚██████╔╝")
    print("  ╚═╝     ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ")
    print("\033[0m")
    print("  SISTEMAS LISTOS. BIENVENIDO, RUBEN.")
    time.sleep(1.5)
    sys.stdout.write(CLEAR); sys.stdout.flush()

def maquina_de_escribir(texto, color="\033[1;32m"):
    with _lock_consola:
        sys.stdout.write(color)
        for c in str(texto):
            sys.stdout.write(c); sys.stdout.flush(); time.sleep(0.004)
        sys.stdout.write("\033[0m\n")

def dibujar_separador_fsociety():
    with _lock_consola:
        print("\033[1;31m┌── fsociety.io ───────────────────────────────────────────┐\033[0m")

def obtener_prompt_usuario():
    hora = datetime.now().strftime("%H:%M")
    return f"\033[1;37m[RUBEN {hora}]: \033[0m"

def cargar_memoria_historica():
    if not os.path.exists(RUTA_MEMORIA):
        return []
    try:
        datos = _cargar_json(RUTA_MEMORIA, [])
        if not isinstance(datos, list):
            return []
        limpio = []
        for e in datos:
            if not isinstance(e, dict):
                continue
            rol = e.get("role")
            cont = e.get("content")
            if rol in {"user", "assistant"} and isinstance(cont, str) and cont.strip():
                limpio.append({"role": rol, "content": cont})
        return limpio
    except Exception:
        return []

def guardar_memoria_en_disco(historial):
    limpio = []
    for m in historial:
        if not isinstance(m, dict):
            continue
        rol = m.get("role")
        cont = m.get("content")
        if rol in {"user", "assistant"} and isinstance(cont, str) and cont.strip():
            limpio.append({"role": rol, "content": cont})
    _guardar_json(RUTA_MEMORIA, limpio)

def preparar_historial_ollama(historial, max_turnos=16):
    validos = [m for m in historial if m.get("role") in {"user", "assistant"} and m.get("content")]
    return validos[-max_turnos:]

def verificar_modelos():
    try:
        disponibles = {m["model"] for m in ollama.list().get("models", [])}
    except Exception as e:
        _safe_print(f"[OLLAMA ERROR]: {e}", "\033[1;31m")
        return
    for req in (MODELO_PADRINO, MODELO_VISION, MODELO_CODER):
        if not any(req.lower() in m.lower() for m in disponibles):
            _safe_print(f"[AVISO]: modelo '{req}' no encontrado.", "\033[1;33m")

def bucle_padrino():
    global mensajes, lexico_aprendido

    if _resumenes_previos:
        _safe_print(f"[MEMORIA LARGA] Recordando {len(_resumenes_previos)} sesión(es) previa(s).", "\033[1;36m")

    mensajes = cargar_memoria_historica()

    mostrar_panel_rendimiento()
    dibujar_separador_fsociety()

    _decaimiento_emocional()
    saludo_base = "Sistemas en línea. Bienvenido de nuevo, Ruben."
    threading.Thread(target=hablar, args=(saludo_base,), daemon=True).start()

    try:
        while not _detener_todo.is_set():
            try:
                _en_input.set()
                user_input = input(obtener_prompt_usuario()).strip()
                _en_input.clear()

                if not user_input:
                    continue
                if user_input.lower() in {"exit", "salir"}:
                    print("\n[PADRINO]: Cerrando el sistema...")
                    guardar_resumen_sesion()
                    _detener_todo.set()
                    break

                if user_input.lower() == "/reset":
                    for r in (RUTA_MEMORIA, RUTA_LEXICO, RUTA_ESTILO_VIVO):
                        if os.path.exists(r):
                            os.remove(r)
                    lexico_aprendido = []
                    mensajes = []
                    _safe_print("[+] Memoria, léxico y estilo purgados. Empezando de cero.", "\033[1;31m")
                    threading.Thread(target=hablar, args=("Memoria purgada. Empezamos de cero, tío.",), daemon=True).start()
                    mostrar_panel_rendimiento()
                    dibujar_separador_fsociety()
                    continue

                if user_input.lower().startswith("/aprende "):
                    resto = user_input[9:].strip()
                    if "->" in resto:
                        frase, ruta = resto.split("->", 1)
                        frase = frase.strip().strip('"\'')
                        ruta = ruta.strip().strip('"\'')
                        if frase and ruta:
                            if registrar_nuevo_aprendizaje(frase, ruta):
                                _safe_print(f"[+ APRENDIZAJE]: '{frase}' -> '{ruta}'", "\033[1;32m")
                                threading.Thread(target=hablar, args=(f"Entendido. He aprendido a abrir {frase}.",), daemon=True).start()
                        else:
                            _safe_print("[!] Usa: /aprende palabra -> ruta\\completa.exe", "\033[1;31m")
                    else:
                        _safe_print("[!] Usa: /aprende palabra -> ruta\\completa.exe", "\033[1;31m")
                    dibujar_separador_fsociety()
                    continue

                if user_input.lower().startswith("/enseña "):
                    resto = user_input[8:].strip()
                    if "->" in resto:
                        tema, contenido = resto.split("->", 1)
                        tema = tema.strip().strip('"\'')
                        contenido = contenido.strip().strip('"\'')
                        if tema and contenido:
                            if registrar_leccion(tema, contenido):
                                _safe_print(f"[+ LECCIÓN APRENDIDA] '{tema}': {contenido}", "\033[1;32m")
                                threading.Thread(target=hablar, args=(f"Entendido. He aprendido sobre {tema}.",), daemon=True).start()
                        else:
                            _safe_print("[!] Usa: /enseña tema -> lo que debe recordar", "\033[1;31m")
                    else:
                        _safe_print("[!] Usa: /enseña tema -> lo que debe recordar", "\033[1;31m")
                    dibujar_separador_fsociety()
                    continue

                if user_input.lower().startswith("/olvida "):
                    tema = user_input[8:].strip().strip('"\'')
                    if olvidar_leccion(tema):
                        _safe_print(f"[+ LECCIÓN OLVIDADA] '{tema}'", "\033[1;33m")
                        threading.Thread(target=hablar, args=(f"He olvidado lo que sabía sobre {tema}.",), daemon=True).start()
                    else:
                        _safe_print(f"[!] No tenía lecciones sobre '{tema}'.", "\033[1;31m")
                    dibujar_separador_fsociety()
                    continue

                if user_input.lower() in {"/lecciones", "/lessons"}:
                    with _lock_consola:
                        print()
                        print("\033[1;36m┌──────────── LECCIONES APRENDIDAS ────────────┐\033[0m")
                        if not lecciones_aprendidas:
                            print("\033[1;36m│\033[0m (Aún no me has enseñado nada)")
                        else:
                            for tema, contenido in lecciones_aprendidas.items():
                                print(f"\033[1;36m│\033[0m · {tema}: {contenido[:80]}{'...' if len(contenido) > 80 else ''}")
                        print("\033[1;36m└──────────────────────────────────────────────┘\033[0m")
                    dibujar_separador_fsociety()
                    continue

                if user_input.lower() in {"/emociones", "/estadoemocional", "/feelings"}:
                    with _lock_consola:
                        print()
                        print("\033[1;36m┌──────────── ESTADO EMOCIONAL DE PADRINO ────────────┐\033[0m")
                        print(f"\033[1;36m│\033[0m {_descripcion_emocional()}")
                        print("\033[1;36m└──────────────────────────────────────────────────────┘\033[0m")
                    dibujar_separador_fsociety()
                    continue

                low = user_input.lower()

                pide_arch_code, peticion_code, ruta_code, lenguaje_code = interceptar_crear_archivo_codigo(user_input)
                if pide_arch_code:
                    _safe_print(f"[SUBAGENTE CODER] Generando {lenguaje_code} para {ruta_code}...", "\033[1;36m")
                    prompt_para_coder = f"Genera un script en {lenguaje_code} que haga lo siguiente:\n{peticion_code}\n\nResponde SOLO con el código puro."
                    codigo_generado = llamar_subagente_coder(prompt_para_coder)
                    codigo_limpio = re.sub(r'^```\w*\s*\n?|\n?```\s*$', '', codigo_generado, flags=re.MULTILINE).strip()
                    try:
                        ruta_abs = ruta_code
                        if not os.path.isabs(ruta_abs):
                            ruta_abs = os.path.join(RUTA_BASE, ruta_abs)
                        Path(ruta_abs).parent.mkdir(parents=True, exist_ok=True)
                        with open(ruta_abs, "w", encoding="utf-8") as f:
                            f.write(codigo_limpio)
                        texto_final = f"Hecho, tío. {os.path.basename(ruta_abs)} creado ({len(codigo_limpio)} caracteres)."
                        _safe_print(f"[ARCHIVO CREADO] {ruta_abs}", "\033[1;32m")
                    except Exception as e:
                        texto_final = f"Fallo al escribir el archivo: {e}"
                        _safe_print(f"[ERROR] {e}", "\033[1;31m")
                    
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": texto_final})
                    maquina_de_escribir(f"[PADRINO]: {texto_final}")
                    threading.Thread(target=hablar, args=(texto_final,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue
                elif peticion_code == "SENSIBLE":
                    texto_final = "No, tío. Eso no lo hago."
                    _safe_print("[BLOQUEADO] Petición sensible detectada.", "\033[1;31m")
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": texto_final})
                    maquina_de_escribir(f"[PADRINO]: {texto_final}")
                    threading.Thread(target=hablar, args=(texto_final,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                pide_codigo, prompt_codigo = interceptar_peticion_codigo(user_input)
                if pide_codigo:
                    _safe_print("[SUBAGENTE CODER] Derivando petición de código...", "\033[1;36m")
                    contexto = "\n".join(f"{m['role']}: {m['content'][:200]}" for m in mensajes[-4:] if m.get("role") in ("user", "assistant"))
                    respuesta_coder = llamar_subagente_coder(prompt_codigo, contexto)
                    texto_final = presentar_codigo_con_padrino(respuesta_coder, user_input)
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": texto_final})
                    maquina_de_escribir(f"[PADRINO]: {texto_final}")
                    threading.Thread(target=hablar, args=(texto_final[:200],), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue
                elif prompt_codigo == "SENSIBLE":
                    texto_final = "No, tío. Eso no lo hago."
                    _safe_print("[BLOQUEADO] Petición sensible detectada.", "\033[1;31m")
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": texto_final})
                    maquina_de_escribir(f"[PADRINO]: {texto_final}")
                    threading.Thread(target=hablar, args=(texto_final,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                # INTERCEPTORES RÁPIDOS
                pide_vol, nivel = interceptar_volumen(user_input)
                if pide_vol and nivel is not None:
                    resultado = _tool_volumen_sistema(nivel)
                    _safe_print(f"[PADRINO]: {resultado}", "\033[1;32m")
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": resultado})
                    threading.Thread(target=hablar, args=(resultado,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                pide_abrir, exito_abrir, objetivo_abrir = interceptar_apertura_directa(user_input)
                if pide_abrir:
                    resultado = f"Ejecutado '{objetivo_abrir}'." if exito_abrir else f"No pude abrir '{objetivo_abrir}'."
                    _safe_print(f"[PADRINO]: {resultado}", "\033[1;32m")
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": resultado})
                    threading.Thread(target=hablar, args=(resultado,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                pide_leer, ruta_doc, contenido_doc = interceptar_y_leer_archivo(user_input)
                if pide_leer:
                    mensajes.append({"role": "user", "content": f"Lee el archivo '{ruta_doc}' y dime su contenido."})
                    mensajes.append({"role": "assistant", "content": f"Contenido de '{ruta_doc}':\n\n{contenido_doc[:3000]}"})
                    _safe_print(f"[PADRINO]: He leído '{ruta_doc}' ({len(contenido_doc)} caracteres).", "\033[1;32m")
                    threading.Thread(target=hablar, args=(f"He leído el archivo {os.path.basename(ruta_doc)}.",), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                pide_web, resultado_web = interceptar_web_multimedia(user_input)
                if pide_web:
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": resultado_web})
                    _safe_print(f"[PADRINO]: {resultado_web}", "\033[1;32m")
                    threading.Thread(target=hablar, args=(resultado_web,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                pide_hf, resultado_hf = interceptar_hora_fecha(user_input)
                if pide_hf:
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": resultado_hf})
                    _safe_print(f"[PADRINO]: {resultado_hf}", "\033[1;32m")
                    threading.Thread(target=hablar, args=(resultado_hf,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                pide_mm, resultado_mm = interceptar_multimedia_global(user_input)
                if pide_mm:
                    mensajes.append({"role": "user", "content": user_input})
                    mensajes.append({"role": "assistant", "content": resultado_mm})
                    _safe_print(f"[PADRINO]: {resultado_mm}", "\033[1;32m")
                    threading.Thread(target=hablar, args=(resultado_mm,), daemon=True).start()
                    dibujar_separador_fsociety()
                    guardar_memoria_en_disco(mensajes)
                    continue

                # AQUI EMPIEZA LA IA REAL
                _extraer_hechos(user_input)
                procesar_y_aprender_vocabulario(user_input)
                analizar_emociones_de_texto(user_input)

                mensajes.append({"role": "user", "content": user_input})
                historial_ctx = preparar_historial_ollama(mensajes)

                nota = ""
                if lexico_aprendido:
                    vocab_str = ", ".join(lexico_aprendido[-30:])
                    nota += f"\n\nUSA ESTE VOCABULARIO PARA HABLAR (úsalo de forma natural, no como una lista):\n{vocab_str}"

                # CEREBRO LINGÜÍSTICO
                estilo_actual = _cargar_json(RUTA_ESTILO_VIVO, {"vocabulario": [], "reglas_estilo": []})
                if estilo_actual["vocabulario"] or estilo_actual["reglas_estilo"]:
                    nota += "\n\nCÓMO HABLA RUBEN Y CÓMO TE PIDE QUE LE HABLES:\n"
                    if estilo_actual["vocabulario"]:
                        nota += f"- Usa este vocabulario de forma natural: {', '.join(estilo_actual['vocabulario'])}\n"
                    if estilo_actual["reglas_estilo"]:
                        for regla in estilo_actual["reglas_estilo"]:
                            nota += f"- {regla}\n"

                if hechos_aprendidos:
                    hechos_txt = "\n".join(f"- {k}: {v}" for k, v in hechos_aprendidos.items())
                    nota += f"\n\nHECHOS QUE SABES SOBRE RUBEN:\n{hechos_txt}"

                if _resumenes_previos:
                    resumenes_txt = "\n".join(f"[{r['fecha']}] {r['resumen']}" for r in _resumenes_previos)
                    nota += f"\n\nMEMORIA DE SESIONES ANTERIORES:\n{resumenes_txt}"

                nota += _bloque_emocional_para_prompt()
                nota += _bloque_lecciones_para_prompt()

                bloque = [{"role": "system", "content": BASE_SYSTEM_PROMPT + nota}] + historial_ctx

                try:
                    respuesta = ollama.chat(model=MODELO_PADRINO, messages=bloque, tools=ESQUEMA_HERRAMIENTAS, options={"temperature": 0.85})
                except Exception:
                    respuesta = ollama.chat(model=MODELO_PADRINO, messages=bloque)

                llamadas = getattr(respuesta.message, "tool_calls", None)
                if not llamadas:
                    contenido_texto = respuesta.message.content or ""
                    llamadas = _parsear_tool_call_en_texto(contenido_texto)

                if llamadas:
                    bloque.append({"role": "assistant", "content": respuesta.message.content or ""})
                    for llamada in llamadas:
                        nombre = llamada.function.name
                        args = llamada.function.arguments or {}
                        if isinstance(args, str):
                            try: args = json.loads(args)
                            except json.JSONDecodeError: args = {}
                        res = ejecutar_herramienta(nombre, args)
                        bloque.append({"role": "tool", "name": nombre, "content": json.dumps(res, ensure_ascii=False)})
                    try:
                        rfinal = ollama.chat(model=MODELO_PADRINO, messages=bloque, tools=ESQUEMA_HERRAMIENTAS)
                        texto_final = rfinal.message.content or ""
                    except Exception as e:
                        texto_final = f"[ERROR tras tools]: {e}"
                    
                    if not texto_final: texto_final = "Vale."
                    maquina_de_escribir(f"[PADRINO]: {texto_final}")
                    threading.Thread(target=hablar, args=(texto_final,), daemon=True).start()
                    mensajes.append({"role": "assistant", "content": texto_final})
                else:
                    texto_final = respuesta.message.content or ""
                    if not texto_final: texto_final = "Vale."
                    maquina_de_escribir(f"[PADRINO]: {texto_final}")
                    threading.Thread(target=hablar, args=(texto_final,), daemon=True).start()
                    mensajes.append({"role": "assistant", "content": texto_final})

                print()
                dibujar_separador_fsociety()
                guardar_memoria_en_disco(mensajes)

                # ¡AQUÍ APRENDE EN SEGUNDO PLANO!
                threading.Thread(target=aprender_de_conversacion, args=(user_input, texto_final), daemon=True).start()

            except KeyboardInterrupt:
                print("\n\033[1;33m[PADRINO]: Cerrando...\033[0m")
                threading.Thread(target=hablar, args=("Cerrando sistemas.",), daemon=True).start()
                guardar_resumen_sesion()
                _detener_todo.set()
                break
            except Exception as e:
                _safe_print(f"[ERROR]: {e}", "\033[1;31m")
                dibujar_separador_fsociety()
    finally:
        _detener_todo.set()

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    abrir_ventana_pngtuber()
    anclar_pngtuber()

    _cargar_emociones()
    _cargar_lecciones()

    verificar_modelos()
    animacion_arranque()

    hilo_conciencia = threading.Thread(target=motor_conciencia_viva, daemon=True)
    hilo_conciencia.start()

    bucle_padrino()