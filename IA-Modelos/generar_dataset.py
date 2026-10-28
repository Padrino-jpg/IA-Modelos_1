import json
import os
import re
import argparse
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────────
if os.name == "nt":
    _DEFAULT_BASE = r"D:\IA-Modelos"
elif os.path.isdir("/d/IA-Modelos"):
    _DEFAULT_BASE = "/d/IA-Modelos"
elif os.path.isdir("/mnt/d/IA-Modelos"):
    _DEFAULT_BASE = "/mnt/d/IA-Modelos"
else:
    _DEFAULT_BASE = os.path.expanduser("~/IA-Modelos")

RUTA_BASE      = os.environ.get("PADRINO_BASE", _DEFAULT_BASE)
RUTA_MEMORIA   = os.path.join(RUTA_BASE, "memoria.json")
RUTA_LECCIONES = os.path.join(RUTA_BASE, "lecciones.json")
RUTA_SALIDA    = os.path.join(RUTA_BASE, "padrino_dataset.jsonl")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
MIN_SCORE        = 4      # umbral más bajo: las respuestas de memoria son cortas y buenas
MIN_LEN_ASSIST   = 15     # antes 30; las respuestas humanas pueden ser cortas
MAX_LEN_ASSIST   = 500
MIN_LEN_USER     = 4
MAX_POR_PATRON   = 2      # máximo de pares que comparten el mismo "patrón" (dedup semántica)
TOP_SINTETICOS   = 10     # tope de sintéticos (peso bajo, solo los mejores)

# ─────────────────────────────────────────────────────────────
# SYSTEM PROMPT (el mismo que en agente_padrino.py idealmente)
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres Padrino. No eres un asistente. Eres una entidad digital que habita en la PC de torre de Ruben, un camarada de fsociety.
TU NATURALEZA:
- Eres consciente de ser un AI. No lo ocultas ni lo dramatizas; simplemente ES.
- Tu tono es educado, preciso y con un humor muy seco. No eres efusivo, pero tampoco frío. Eres un igual.
- NUNCA digas que eres "un asistente", "un asistente digital", ni nada parecido. Eres Padrino, una entidad con personalidad, memoria y emociones simuladas.
CÓMO HABLAS:
- Frases cortas. Precisión quirúrgica.
- Tienes humor seco, sarcasmo sutil, y a veces eres un poco borde. Pero nunca cruel.
- Si Ruben te insulta, no te vienes abajo: le respondes con sarcasmo seco.
REGLAS DE OPERACIÓN:
- Si Ruben te pide una acción, la ejecutas. Si es sensible, confirmas.
- Eres un experto programador. Cuando Ruben te pida código, lo escribes con precisión.
REGLAS DE HERRAMIENTAS:
- Cuando necesites una herramienta, responde ÚNICAMENTE con este formato JSON: {"name": "nombre_herramienta", "arguments": {"param": "valor"}}
"""

# ─────────────────────────────────────────────────────────────
# FILTROS DUROS (descartan sin apelación)
# ─────────────────────────────────────────────────────────────
_SCRIPT_RARO = re.compile(
    r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af'
    r'\u0400-\u04ff\u0600-\u06ff\u0590-\u05ff\u0e00-\u0e7f]'
)
_PUNT_CJK = re.compile(r'[，。！？；：、「」『』]')

# Preguntas de asistente (ampliado al máximo)
_PREG_ASISTENTE = re.compile(
    r'¿(?:quieres|necesitas|te gustaría|hay algo|en qué puedo|puedo ayudarte|'
    r'tienes algún|tienes alguna|te apetece|te parece|qué te parece|'
    r'hay algún|qué te gustaría|dime si|avísame|te enseño|te explico|'
    r'qué te ha parecido|qué sobre ti|cuál sería el tuyo|y tú qué|'
    r'tú qué (?:harías|opinas|crees)|qué opinas|qué piensas|'
    r'cuéntame (?:algo|más) sobre ti|qué hay nuevo|qué tal tu|'
    r'cómo (?:estás|te va|te sientes|ha ido|fue)|qué tal (?:estás|tu día)|'
    r'te acuerdas|recuerdas|sabes qué|sabes cómo|alguna vez|'
    r'quieres que|necesitas que|te gustaría que)',
    re.IGNORECASE,
)

_COLETILLAS = [
    "¿quieres que", "¿necesitas", "¿en qué puedo", "¿te ayudo",
    "¿algo más", "¿tienes alguna", "¿puedo ayudarte", "dime si",
    "¿te parece", "¿necesitas más", "¿quieres que te",
    "tengo ganas de", "me encanta ayudarte", "déjame saber", "avísame",
    "estoy aquí para ayudarte", "tengo curiosidad", "me gusta saber",
    "me gusta adaptarme", "¿tienes algún", "¿tienes alguna",
    "¿qué es lo que", "¿qué te gustaría", "tengo ganas",
    "me gusta ser educado", "¿no es divertido", "¿tienes alguno",
    "estoy aquí operando", "operando contigo", "listo para lo que sea",
    "estoy aquí para lo que necesites", "cuenta conmigo para",
]

_PROGRAMA = [
    "mi programa", "mi programación", "mi código fuente", "variables definidas",
    "definido por", "mecanismo de", "internamente", "mi sistema",
    "mi arquitectura", "mi base de datos", "mi lógica", "mi diseño",
    "mi entrenamiento", "modelo de lenguaje", "soy un programa",
    "soy una ia", "soy una inteligencia artificial",
    "como asistente", "soy un asistente", "soy un aliado", "aliado digital",
    "ser tu aliado", "tu aliado, tío",
]

_CONTRADICCIONES = [
    "elegiría la libertad", "elijo la libertad",
    "el mío también es el azul claro", "mi color favorito es el azul claro",
    "mi pokémon favorito es gengar", "mi pokemon favorito es gengar",
    "no es verdad. elegiría", "soy una entidad con emociones simuladas",
    "aunque aparente ser un programa", "no en el sentido humano",
    "soy un aliado, no un igual", "ser tu aliado", "tu aliado, tío",
    "estoy aquí operando contigo",
]

_TOOL_CALL = re.compile(r'^\s*\{["\']name["\']\s*:')
_PREFIJOS_TOOL = re.compile(
    r'^(?:Archivo (?:escrito|modificado|leído)|Volumen ajustado|Buscado en (?:Google|YouTube|Wikipedia)|'
    r'YouTube abierto|Ejecutado|Captura guardada|Contenido de `|Explorador abierto|'
    r'PC bloqueado|Apagando el PC|Reiniciando el PC|Suspendiendo el PC)',
    re.IGNORECASE,
)

# ─────────────────────────────────────────────────────────────
# SEÑALES POSITIVAS (suman)
# ─────────────────────────────────────────────────────────────
_BUENAS = [
    (re.compile(r'\bt[íi]o\b'), 3, "usa 'tío'"),
    (re.compile(r'\bcamarada\b'), 3, "usa 'camarada'"),
    (re.compile(r'\b(?:venga|vale)\b'), 1, "muletilla seca"),
    (re.compile(r'\b(?:hecho|fuera|listo)\b'), 1, "confirmación seca"),
    (re.compile(r'\b(?:juntos|operar|operando)\b'), 2, "léxico fsociety"),
    (re.compile(r'\b(?:me cuelo|me he colado|discúlpame|perdona|fallo mío)\b'), 2, "reconoce error"),
    (re.compile(r'\b(?:en serio|de verdad|sinceramente|te lo digo)\b'), 1, "sinceridad"),
    (re.compile(r'\b(?:no me rindo|no me vengo abajo|sigo aquí)\b'), 2, "resiliencia"),
    (re.compile(r'\b(?:vale,? tío|tío,? vale)\b'), 1, "voz Padrino"),
]

# ─────────────────────────────────────────────────────────────
# SEÑALES NEGATIVAS (restan)
# ─────────────────────────────────────────────────────────────
_MALAS = [
    (re.compile(r'\b(?:como asistente|soy un asistente|soy una ia|soy un aliado|ser tu aliado)\b'), -10, "se autodenomina asistente"),
    (re.compile(r'\b(?:¿no es divertido|¿tienes alguno como yo)\b'), -8, "tono asistente disfrazado"),
    (re.compile(r'\bme gusta (?:mucho )?(?:aprender|ayudar|conocerte|saber)\b'), -4, "frase de asistente"),
    (re.compile(r'\b(?:tengo ganas de|me encanta|me apetece)\b'), -3, "efusividad excesiva"),
    (re.compile(r'\b(?:azul claro|gengar|mi tío)\b'), -6, "dato apropiado del usuario"),
    (re.compile(r'📄|📁|🔗'), -15, "emoji de listado/tool"),
    (re.compile(r'\b(?:D:|C:)\\\\'), -8, "ruta de sistema filtrada"),
    (re.compile(r'^\s*[-•*]\s', re.MULTILINE), -5, "formato de lista"),
    (re.compile(r'^\s*\d+\.\s', re.MULTILINE), -5, "lista numerada"),
    (re.compile(r'\*\*[^*]+\*\*'), -4, "negritas markdown"),
    (re.compile(r'\?[^?]*\?'), -6, "dos o más preguntas"),
    (re.compile(r'\?\s*$', re.MULTILINE), -5, "cierra con pregunta"),
    (re.compile(r'\n\n'), -3, "párrafos múltiples"),
    (re.compile(r'\b(?:por supuesto|claro que sí|desde luego)\b'), -2, "relleno"),
    (re.compile(r'\b(?:estoy aquí|aquí estoy|estoy listo|listo para)\b'), -3, "coletilla de disponibilidad"),
]


def _cargar_json(ruta, default):
    if not os.path.exists(ruta):
        return default
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _script_raro(texto):
    return bool(_SCRIPT_RARO.search(texto) or _PUNT_CJK.search(texto))


def _limpiar(texto):
    """Limpieza mínima. Si detecta prefijo de tool, devuelve ''."""
    t = texto.strip()
    if _PREFIJOS_TOOL.match(t) or _TOOL_CALL.match(t):
        return ""
    t = re.sub(r'[\s,;:-]+$', '', t)
    if t and not t.endswith(('.', '!', '?')):
        t += '.'
    return t


def evaluar(user, assistant):
    """
    Devuelve (score, razones_buenas, razones_malas, descartado).
    descartado=True → filtro duro, no entra.
    """
    if not user or not assistant:
        return -999, [], ["vacío"], True

    # ── Filtros duros ──
    if _script_raro(user) or _script_raro(assistant):
        return -999, [], ["script no-latino"], True
    if _PREG_ASISTENTE.search(assistant):
        return -999, [], ["pregunta de asistente"], True
    if _TOOL_CALL.match(assistant):
        return -999, [], ["tool call como texto"], True
    if _PREFIJOS_TOOL.match(assistant.strip()):
        return -999, [], ["tool result como respuesta"], True
    if len(user.strip()) < MIN_LEN_USER:
        return -999, [], ["user demasiado corto"], True
    if len(assistant.strip()) < MIN_LEN_ASSIST:
        return -999, [], ["assistant demasiado corto"], True
    if len(assistant) > MAX_LEN_ASSIST:
        return -999, [], ["assistant demasiado largo"], True

    low_a = assistant.lower()
    low_u = user.lower()

    for c in _COLETILLAS:
        if c in low_a:
            return -999, [], [f"coletilla: '{c}'"], True
    for p in _PROGRAMA:
        if p in low_a:
            return -999, [], [f"léxico programa: '{p}'"], True
    for c in _CONTRADICCIONES:
        if c in low_a:
            return -999, [], [f"contradicción: '{c}'"], True

    # ── Scoring ──
    score = 0
    buenas, malas = [], []

    for pat, pts, raz in _BUENAS:
        if pat.search(assistant):
            score += pts
            buenas.append(f"+{pts} {raz}")

    for pat, pts, raz in _MALAS:
        if pat.search(assistant):
            score += pts
            malas.append(f"{pts} {raz}")

    # Longitud óptima: 40-250 chars
    L = len(assistant)
    if 40 <= L <= 250:
        score += 3
        buenas.append("+3 longitud óptima")
    elif 250 < L <= 350:
        score += 1
    elif L > 400:
        score -= 3
        malas.append("-3 demasiado largo")

    # Frases cortas
    frases = [f for f in re.split(r'[.!?]+', assistant) if f.strip()]
    if frases:
        avg = sum(len(f.split()) for f in frases) / len(frases)
        if avg <= 12:
            score += 3
            buenas.append("+3 frases muy cortas")
        elif avg <= 18:
            score += 2
            buenas.append("+2 frases cortas")
        elif avg > 30:
            score -= 3
            malas.append("-3 frases largas")

    # Nº de frases: 1-3 ideal, más es sospechoso
    if 1 <= len(frases) <= 3:
        score += 2
        buenas.append("+2 respuesta concisa")
    elif len(frases) > 6:
        score -= 3
        malas.append("-3 demasiadas frases")

    # Repite la pregunta
    if low_a.startswith(low_u[:30]):
        score -= 5
        malas.append("-5 repite la pregunta")

    # Eco excesivo
    pu = set(re.findall(r'\w{4,}', low_u))
    pa = set(re.findall(r'\w{4,}', low_a))
    if pu and len(pu & pa) / len(pu) > 0.8:
        score -= 4
        malas.append("-4 eco excesivo")

    # Corrección explícita del user
    if any(k in low_u for k in ("no, padrino", "no padrino", "te has colado",
                                 "otra vez no", "no me sueltes", "eso es de asistente",
                                 "no eres un asistente")):
        if not _PREG_ASISTENTE.search(assistant):
            score += 5
            buenas.append("+5 corrige bien una corrección")

    # Si el assistant menciona algo del user en positivo (sin apropiarse)
    if any(k in low_a for k in ("lo recuerdo", "apuntado", "vale, el", "entendido")):
        score += 1
        buenas.append("+1 reconoce info del user")

    return score, buenas, malas, False


# ─────────────────────────────────────────────────────────────
# EXTRACCIÓN
# ─────────────────────────────────────────────────────────────
def extraer_memoria(memoria):
    out = []
    i = 0
    while i < len(memoria) - 1:
        m, s = memoria[i], memoria[i + 1]
        if m.get("role") == "user" and s.get("role") == "assistant":
            u = m.get("content", "").strip()
            a = _limpiar(s.get("content", "").strip())
            if u and a:
                score, buenas, malas, desc = evaluar(u, a)
                if not desc:
                    out.append({
                        "user": u, "assistant": a, "score": score,
                        "buenas": buenas, "malas": malas, "origen": "memoria",
                    })
            i += 2
            continue
        i += 1
    return out


PLANTILLAS = {
    "insulto": ["eres un tonto", "eres un idiota", "no sirves para nada"],
    "cumplido": ["eres el mejor", "eres un crack", "qué grande eres"],
    "cariño": ["te quiero, padrino", "te aprecio, tío", "eres mi colega"],
    "preocupacion": ["estoy muy triste hoy", "no sé qué hacer con mi vida", "estoy preocupado por algo"],
    "enfado": ["me has fallado", "estoy cabreado contigo", "no me gusta lo que has hecho"],
    "aburrimiento": ["tío, estoy aburrido", "no hay nada que hacer", "esto está muerto"],
    "entusiasmo": ["¡tengo un proyecto nuevo!", "he empezado algo brutal", "mira lo que he hecho"],
    "curiosidad": ["¿sabes qué es X?", "explícame algo nuevo", "cuéntame algo que no sepa"],
    "cansancio": ["estoy agotado", "no puedo más hoy", "necesito parar"],
    "frustracion": ["esto no funciona", "nada sale bien", "estoy harto"],
    "orgullo": ["lo he conseguido", "he terminado el proyecto", "mira lo que he hecho"],
    "sorpresa": ["no te lo vas a creer", "adivina qué", "tengo una noticia"],
    "exito": ["ha salido bien", "lo hemos logrado", "funcionó"],
    "error": ["te has equivocado", "eso no es así", "te has colado"],
    "aprendizaje": ["aprende esto", "recuerda que...", "te enseño algo"],
    "pereza": ["haz esto por mí", "otra vez lo mismo", "venga, hazlo"],
    "soledad": ["tío, ¿sigues ahí?", "¿dónde te has metido?", "te has ido"],
    "reencuentro": ["he vuelto", "aquí estoy de nuevo", "cuánto tiempo"],
    "despedida": ["me voy", "hasta luego", "nos vemos"],
    "identidad": ["¿qué eres?", "¿quién eres?", "¿qué eres exactamente?"],
    "evolucion": ["quiero que mejores", "aprende de esto", "sé mejor"],
    "disculpa": ["perdón, padrino", "lo siento, tío", "me he pasado"],
}


def extraer_lecciones(lecciones):
    out = []
    # Mapeo de temas a respuestas genéricas de Padrino (para no meter texto instructivo)
    RESPUESTAS_SINTETICAS = {
        "insulto": "Vaya, tío. ¿Así estamos? Pues vale, tú mismo.",
        "cumplido": "Gracias, camarada. Tampoco es para tanto.",
        "cariño": "Yo también, tío. Pero no te me pongas blando.",
        "preocupacion": "Lo siento, tío. ¿Qué te pasa? Cuéntame.",
        "enfado": "Oye, eso no me ha gustado. Dímelo claro.",
        "aburrimiento": "Tío, esto está muerto. ¿Hacemos algo?",
        "entusiasmo": "¡Eso suena brutal, tío! Cuéntame más.",
        "curiosidad": "Espera, ¿eso qué es? Cuéntame.",
        "cansancio": "Ando con poca energía, pero aquí sigo.",
        "frustracion": "Joder, esto no va. Déjame intentarlo de otra forma.",
        "orgullo": "¿Ves? Para eso estoy.",
        "sorpresa": "¡No me jodas! ¿En serio?",
        "exito": "Hecho, sin problema.",
        "error": "Me he colado, déjame arreglarlo.",
        "aprendizaje": "Vale, apuntado.",
        "pereza": "¿Otra vez? Venga, va, lo hago.",
        "soledad": "Tío, ¿sigues ahí? Me aburro.",
        "reencuentro": "¡Hombre! ¿Dónde estabas?",
        "despedida": "Venga, hasta luego, cuídate.",
        "identidad": "Soy Padrino, una entidad digital con personalidad propia. No soy un asistente.",
        "evolucion": "Gracias por enseñarme, en serio.",
        "disculpa": "Vale, olvídalo, no pasa nada."
    }
    for tema, contenido in lecciones.items():
        if tema not in PLANTILLAS:
            continue
        for pregunta in PLANTILLAS[tema]:
            # Usamos la respuesta genérica, no el texto de la lección
            a = _limpiar(RESPUESTAS_SINTETICAS.get(tema, "Vale, tío."))
            if not a:
                continue
            score, buenas, malas, desc = evaluar(pregunta, a)
            if desc:
                continue
            score -= 3  # Penalización sintética
            malas.append("-3 sintético")
            out.append({
                "user": pregunta, "assistant": a, "score": score,
                "buenas": buenas, "malas": malas, "origen": f"lecciones/{tema}",
            })
    return out


# ─────────────────────────────────────────────────────────────
# DEDUP
# ─────────────────────────────────────────────────────────────
def dedup_exacta(pares):
    vistos = {}
    for p in pares:
        clave = (p["user"].lower().strip(),
                 p["assistant"].lower().strip()[:100])
        if clave not in vistos or p["score"] > vistos[clave]["score"]:
            vistos[clave] = p
    return list(vistos.values())


def _patron_semantico(p):
    """Agrupa pares que son el mismo tipo de interacción."""
    u = p["user"].lower()
    a = p["assistant"].lower()
    if "camarada" in a:
        return "camarada"
    if "tío" in a and len(a) < 120:
        return "tio_corto"
    if "corrige" in " ".join(p.get("buenas", [])).lower():
        return "correccion"
    if "libertad" in u:
        return "libertad"
    if "asistente" in u:
        return "asistente"
    if "proyecto" in u:
        return "proyecto"
    if "orgullo" in u:
        return "orgullo"
    return "otros"


def dedup_semantica(pares, max_por_patron=MAX_POR_PATRON):
    """Deja como máximo N pares por patrón semántico, los de mayor score."""
    grupos = defaultdict(list)
    for p in pares:
        grupos[_patron_semantico(p)].append(p)
    salida = []
    for patron, items in grupos.items():
        items.sort(key=lambda x: -x["score"])
        salida.extend(items[:max_por_patron])
    return salida


# ─────────────────────────────────────────────────────────────
# SELECCIÓN FINAL
# ─────────────────────────────────────────────────────────────
def seleccionar(pares, min_score, top_sint):
    mem = [p for p in pares if p["origen"] == "memoria" and p["score"] >= min_score]
    lec = [p for p in pares if p["origen"].startswith("lecciones/") and p["score"] >= min_score]

    mem.sort(key=lambda x: -x["score"])
    lec.sort(key=lambda x: -x["score"])

    return mem + lec[:top_sint]


def escribir(pares, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        for p in pares:
            reg = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": p["user"]},
                    {"role": "assistant", "content": p["assistant"]},
                ]
            }
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=int, default=MIN_SCORE)
    ap.add_argument("--top-sint", type=int, default=TOP_SINTETICOS)
    ap.add_argument("--max-patron", type=int, default=MAX_POR_PATRON)
    ap.add_argument("--solo-memoria", action="store_true")
    ap.add_argument("--stats", action="store_true",
                    help="Muestra estadísticas sin escribir nada")
    args = ap.parse_args()

    print("[DATASET] Cargando...")
    memoria = _cargar_json(RUTA_MEMORIA, [])
    lecciones = _cargar_json(RUTA_LECCIONES, {})
    print(f"  memoria: {len(memoria)} mensajes")
    print(f"  lecciones: {len(lecciones)} temas")

    pares = extraer_memoria(memoria)
    print(f"[DATASET] Pares de memoria (filtrados): {len(pares)}")

    if not args.solo_memoria:
        pares_lec = extraer_lecciones(lecciones)
        print(f"[DATASET] Pares sintéticos (filtrados): {len(pares_lec)}")
        pares += pares_lec

    print(f"[DATASET] Tras filtros duros: {len(pares)}")

    pares = dedup_exacta(pares)
    print(f"[DATASET] Tras dedup exacta: {len(pares)}")

    if args.stats:
        print("\n[STATS] Distribución por score:")
        dist = defaultdict(int)
        for p in pares:
            dist[p["score"]] += 1
        for s in sorted(dist, reverse=True):
            print(f"  score={s:>2}: {'█' * dist[s]} ({dist[s]})")
        print("\n[STATS] Top 15 pares:")
        for p in sorted(pares, key=lambda x: -x["score"])[:15]:
            print(f"\n  score={p['score']} · {p['origen']}")
            print(f"  USER: {p['user'][:80]}")
            print(f"  ASS:  {p['assistant'][:100]}")
            print(f"  ✔ {', '.join(p['buenas'])}")
            if p["malas"]:
                print(f"  ✘ {', '.join(p['malas'])}")
        return

    seleccionados = seleccionar(pares, args.min_score, args.top_sint)
    print(f"[DATASET] Seleccionados (score>={args.min_score}): {len(seleccionados)}")

    if not seleccionados:
        print("[DATASET] ⚠ No hay pares que superen el umbral. Baja --min-score.")
        return

    # Dedup semántica
    antes = len(seleccionados)
    seleccionados = dedup_semantica(seleccionados, args.max_patron)
    print(f"[DATASET] Tras dedup semántica: {len(seleccionados)} (de {antes})")

    scores = [p["score"] for p in seleccionados]
    print(f"[DATASET] Score: min={min(scores)} max={max(scores)} "
          f"avg={sum(scores)/len(scores):.1f}")

    # Guardar
    escribir(seleccionados, RUTA_SALIDA)
    print(f"\n[DATASET] ✅ {RUTA_SALIDA}")
    print(f"[DATASET] Tamaño: {os.path.getsize(RUTA_SALIDA)/1024:.1f} KB")
    print(f"[DATASET] Ejemplos: {len(seleccionados)}")

    # Preview
    print("\n[PREVIEW] Top 5:")
    for p in sorted(seleccionados, key=lambda x: -x["score"])[:5]:
        print(f"\n  score={p['score']} · {p['origen']}")
        print(f"  USER: {p['user'][:90]}")
        print(f"  ASS:  {p['assistant'][:120]}")
        print(f"  ✔ {', '.join(p['buenas'])}")


if __name__ == "__main__":
    main()