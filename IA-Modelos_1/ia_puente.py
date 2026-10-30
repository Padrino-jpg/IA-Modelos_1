import os
import sys
import json
import time  # --- FIX: necesario para los reintentos de _lupa
import threading
import contextlib
import http.client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODELO_GENGAR = os.environ.get("GENGAR_MODELO", "Padrino_v3")
PERMITIR_TODO = os.environ.get("GENGAR_PERMITIR_TODO", "1") == "1"
_lock = threading.Lock()
_cb = None

def _accion():
    if _cb:
        try:
            _cb()
        except Exception:
            pass

def _ok(r):
    _accion()
    return r

PUERTO_GENGAR = int(os.environ.get("GENGAR_PORT", "47831"))
HERRAMIENTAS_LUPA = ("leer_archivo", "listar_directorio", "buscar_archivos", "buscar_web", "describir_pantalla")

def _lupa(activa=True, seg=None):
    datos = {"ev": "Lupa", "on": bool(activa)}
    if seg:
        datos["seg"] = seg
    for intento in range(1, 4):  # --- FIX: 3 reintentos por si el servidor aún no está listo (BUG 4)
        try:
            c = http.client.HTTPConnection("127.0.0.1", PUERTO_GENGAR, timeout=1.0)
            c.request("POST", "/", body=json.dumps(datos),
                      headers={"Content-Type": "application/json", "X-Gengar": "1"})
            resp = c.getresponse()  # --- FIX: guardamos la respuesta para comprobar el estado
            resp.read()
            c.close()
            if resp.status in (200, 204):  # --- FIX: comprobar estado HTTP
                print(f"[ia_puente] _lupa OK: {datos} -> HTTP {resp.status} (intento {intento})")  # --- FIX: diagnóstico éxito
                return True
            print(f"[ia_puente] _lupa: HTTP {resp.status} inesperado (intento {intento}/3)")  # --- FIX: diagnóstico fallo
        except Exception as e:
            print(f"[ia_puente] _lupa FALLO intento {intento}/3 en 127.0.0.1:{PUERTO_GENGAR}: {e}")  # --- FIX: diagnóstico fallo
        if intento < 3:
            time.sleep(0.3)  # --- FIX: espera entre reintentos
    print(f"[ia_puente] _lupa: no se pudo avisar a la GUI tras 3 intentos ({datos})")  # --- FIX: diagnóstico fallo final
    return False

@contextlib.contextmanager
def _con_lupa(nombre):
    activa = nombre in HERRAMIENTAS_LUPA
    if activa:
        _lupa(True)
    try:
        yield
    finally:
        if activa:
            _lupa(False)

@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

with suppress_stdout():
    import agente_padrino as padrino

padrino.MODELO_PADRINO = MODELO_GENGAR
padrino._pedir_confirmacion = lambda nombre, argumentos: PERMITIR_TODO
padrino._safe_print = lambda texto, color="", end="": None
padrino.maquina_de_escribir = lambda texto, color="": None

def _tool(nombre, desc, props, req):
    return {"type": "function", "function": {"name": nombre, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": req}}}

if not hasattr(padrino, "ESQUEMA_HERRAMIENTAS"):
    _s = {"type": "string"}
    padrino.ESQUEMA_HERRAMIENTAS = [
        _tool("abrir_aplicacion_sistema", "Abre una aplicación o archivo en el PC.", {"nombre_programa": _s}, ["nombre_programa"]),
        _tool("leer_archivo", "Lee el contenido de un archivo de texto.", {"ruta": _s}, ["ruta"]),
        _tool("describir_pantalla", "Captura la pantalla y responde una pregunta sobre ella.", {"pregunta": _s}, []),
        _tool("estado_sistema", "Devuelve CPU, RAM y procesos del PC.", {}, []),
        _tool("escribir_archivo", "Crea o sobrescribe un archivo con el contenido dado.", {"ruta": _s, "contenido": _s}, ["ruta", "contenido"]),
        _tool("listar_directorio", "Lista el contenido de una carpeta.", {"ruta": _s}, []),
        _tool("buscar_archivos", "Busca archivos por patrón glob dentro de una carpeta.", {"patron": _s, "ruta": _s}, ["patron"]),
        _tool("buscar_web", "Busca información actual en internet.", {"consulta": _s, "max_resultados": {"type": "integer"}}, ["consulta"]),
        _tool("cerrar_proceso", "Cierra un proceso por nombre.", {"nombre_proceso": _s}, ["nombre_proceso"]),
        _tool("volumen_sistema", "Ajusta el volumen del sistema de 0 a 100.", {"nivel": {"type": "integer"}}, ["nivel"]),
    ]

with suppress_stdout():
    padrino._cargar_emociones()
    padrino._cargar_lecciones()
    try:
        padrino.mensajes = padrino.cargar_memoria_historica()
    except Exception:
        pass

def _interceptores_simples(user_input):
    for nombre in (
        "interceptar_web_multimedia", "interceptar_hora_fecha", "interceptar_control_sistema",
        "interceptar_multimedia_global", "interceptar_captura_pantalla",
        "interceptar_utilidades_archivo", "interceptar_explorador_ruta",
    ):
        f = getattr(padrino, nombre, None)
        if f is None:
            continue
        pide, resultado = f(user_input)
        if pide:
            if nombre != "interceptar_hora_fecha":
                _accion()
            return resultado
    return None

def obtener_respuesta(user_input, on_accion=None):
    global _cb
    with _lock:
        _cb = on_accion
        return _obtener_respuesta(user_input)

def _obtener_respuesta(user_input):
    low = user_input.lower()

    # --- FIX/NUEVO: Pregunta sobre la canción actual ---
    pide_cancion, respuesta_cancion = padrino.interceptar_pregunta_musica(user_input)  # --- FIX/NUEVO
    if pide_cancion:  # --- FIX/NUEVO
        return respuesta_cancion  # --- FIX/NUEVO
    # ----------------------------------------

    pide_arch_code, peticion_code, ruta_code, lenguaje_code = padrino.interceptar_crear_archivo_codigo(user_input)
    if pide_arch_code:
        prompt_para_coder = (
            f"Genera un script en {lenguaje_code} que haga lo siguiente:\n"
            f"{peticion_code}\n\n"
            f"Responde SOLO con el código, sin explicaciones, sin markdown."
        )
        codigo_generado = padrino.llamar_subagente_coder(prompt_para_coder)
        codigo_limpio = padrino.re.sub(r'^```\w*\s*\n?|\n?```\s*$', '', codigo_generado, flags=padrino.re.MULTILINE).strip()
        try:
            ruta_abs = ruta_code
            if not os.path.isabs(ruta_abs):
                ruta_abs = os.path.join(padrino.RUTA_BASE, ruta_abs)
            padrino.Path(ruta_abs).parent.mkdir(parents=True, exist_ok=True)
            with open(ruta_abs, "w", encoding="utf-8") as f:
                f.write(codigo_limpio)
            return _ok(f"Hecho, tío. {os.path.basename(ruta_abs)} creado.")
        except Exception as e:
            return f"Fallo al escribir el archivo: {e}"
    elif peticion_code == "SENSIBLE":
        return "No, tío. Eso no lo hago."

    pide_codigo, prompt_codigo = padrino.interceptar_peticion_codigo(user_input)
    if pide_codigo:
        contexto = "\n".join(
            f"{m['role']}: {m['content'][:200]}"
            for m in padrino.mensajes[-4:]
            if m.get("role") in ("user", "assistant")
        )
        respuesta_coder = padrino.llamar_subagente_coder(prompt_codigo, contexto)
        return _ok(padrino.presentar_codigo_con_padrino(respuesta_coder, user_input))
    elif prompt_codigo == "SENSIBLE":
        return "No, tío. Eso no lo hago."

    if low.startswith("navega ") or low.startswith("busca en youtube "):
        orden = user_input[7:].strip() if low.startswith("navega ") else user_input
        return _ok(padrino.computer_use_navegador(orden))

    if low.startswith("padrino ve ") or low.startswith("padrino busca "):
        orden = user_input.split(" ", 2)[2].strip()
        return _ok(padrino.interactuar_con_pantalla(orden))

    if low in {"/hardware", "/rendimiento", "/tareas", "/rt"}:
        return "Panel de rendimiento activado en la consola."

    pide_vol, nivel = padrino.interceptar_volumen(user_input)
    if pide_vol and nivel is not None:
        return _ok(padrino._tool_volumen_sistema(nivel))

    pide_buscar_arch, patron_arch, ruta_arch = padrino.interceptar_buscar_archivos(user_input)
    if pide_buscar_arch:
        with _con_lupa("buscar_archivos"):
            res_busqueda = padrino._tool_buscar_archivos(patron_arch, ruta_arch)
        return _ok(res_busqueda)

    pide_escribir, ruta_esc, contenido_esc = padrino.interceptar_escritura_archivo(user_input)
    if pide_escribir:
        return _ok(padrino._tool_escribir_archivo(ruta_esc, contenido_esc))

    pide_cerrar, nombre_proc = padrino.interceptar_cierre_proceso(user_input)
    if pide_cerrar:
        return _ok(padrino._tool_cerrar_proceso(nombre_proc))

    pide_abrir, exito_abrir, objetivo_abrir = padrino.interceptar_apertura_directa(user_input)
    if pide_abrir:
        return _ok(f"Ejecutado '{objetivo_abrir}'." if exito_abrir else f"No pude abrir '{objetivo_abrir}'.")

    pide_leer, ruta_doc, contenido_doc = padrino.interceptar_y_leer_archivo(user_input)
    if pide_leer:
        _lupa(True, 2.5)
        return _ok(f"Contenido de '{ruta_doc}':\n\n{contenido_doc[:3000]}")

    pide_listar, listado = padrino.interceptar_listado_directorio(user_input)
    if pide_listar:
        _lupa(True, 2.5)
        return _ok(listado)

    resultado = _interceptores_simples(user_input)
    if resultado is not None:
        return resultado

    padrino._extraer_hechos(user_input)
    padrino.procesar_y_aprender_vocabulario(user_input)
    padrino.analizar_emociones_de_texto(user_input)

    padrino.mensajes.append({"role": "user", "content": user_input})
    historial_ctx = padrino.preparar_historial_ollama(padrino.mensajes)

    nota = ""
    if padrino.lexico_aprendido:
        nota += f" Vocabulario reciente: {', '.join(padrino.lexico_aprendido[-15:])}."
    if padrino.hechos_aprendidos:
        hechos_txt = "\n".join(f"- {k}: {v}" for k, v in padrino.hechos_aprendidos.items())
        nota += f"\n\nHECHOS QUE SABES SOBRE RUBEN:\n{hechos_txt}"
    if padrino._resumenes_previos:
        resumenes_txt = "\n".join(f"[{r['fecha']}] {r['resumen']}" for r in padrino._resumenes_previos)
        nota += f"\n\nMEMORIA DE SESIONES ANTERIORES:\n{resumenes_txt}"
    nota += padrino._bloque_emocional_para_prompt()

    bloque = [{"role": "system", "content": padrino.BASE_SYSTEM_PROMPT + nota}] + historial_ctx
    opciones = {"temperature": 0.85, "num_ctx": 4096}

    try:
        respuesta = padrino.ollama.chat(
            model=MODELO_GENGAR, messages=bloque,
            tools=padrino.ESQUEMA_HERRAMIENTAS, options=opciones, keep_alive="30m",
        )
    except Exception:
        try:
            respuesta = padrino.ollama.chat(model=MODELO_GENGAR, messages=bloque, options=opciones, keep_alive="30m")
        except Exception as e2:
            return f"Ollama no responde ({MODELO_GENGAR}): {e2}"

    llamadas = getattr(respuesta.message, "tool_calls", None)
    if not llamadas:
        llamadas = padrino._parsear_tool_call_en_texto(respuesta.message.content or "")

    if llamadas:
        bloque.append({"role": "assistant", "content": respuesta.message.content or ""})
        for llamada in llamadas:
            nombre = llamada.function.name
            args = llamada.function.arguments or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            _accion()
            with _con_lupa(nombre):
                res = padrino.ejecutar_herramienta(nombre, args)
            bloque.append({"role": "tool", "name": nombre, "content": json.dumps(res, ensure_ascii=False)})
        try:
            rfinal = padrino.ollama.chat(model=MODELO_GENGAR, messages=bloque, options=opciones, keep_alive="30m")
            texto_final = rfinal.message.content or ""
        except Exception as e:
            texto_final = f"[ERROR tras tools]: {e}"
    else:
        texto_final = respuesta.message.content or ""

    if not texto_final:
        texto_final = "Vale."

    padrino.mensajes.append({"role": "assistant", "content": texto_final})
    padrino.guardar_memoria_en_disco(padrino.mensajes)
    return texto_final

def iniciar_conciencia_musical(callback=None, intervalo=2.0):
    return padrino.iniciar_conciencia_musical(callback, intervalo)