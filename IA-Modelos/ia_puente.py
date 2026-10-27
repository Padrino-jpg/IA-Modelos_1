import os
import sys
import json
import contextlib

# Suprimimos los prints de agente_padrino para que no ensucien la consola de la GUI
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
    # Importamos el cerebro de Padrino (asegúrate de que agente_padrino.py esté en la misma carpeta)
    import agente_padrino as padrino

# Parcheamos la función de confirmación para que no bloquee la GUI esperando un input()
def _gui_confirmacion(nombre, argumentos):
    # En la GUI permitimos todo automáticamente para no congelar la ventana
    print(f"[GUI] Permitiendo acción automática: {nombre}")
    return True

padrino._pedir_confirmacion = _gui_confirmacion

# Parcheamos las funciones de impresión para que no ensucien la consola
padrino._safe_print = lambda texto, color="", end="": None
padrino.maquina_de_escribir = lambda texto, color="": None

# Inicializamos los módulos de Padrino (emociones, lecciones, modelos)
with suppress_stdout():
    padrino._cargar_emociones()
    padrino._cargar_lecciones()

def obtener_respuesta(user_input):
    """
    Función principal que llama Gengar.
    Pasa el texto por todos los interceptores (código, web, archivos, etc.)
    y si no es nada de eso, se lo manda al modelo de Ollama.
    """
    low = user_input.lower()

    # ═══ 1. INTERCEPTORES (Bypasses) ═══
    
    # Crear archivo con código
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
            return f"Hecho, tío. {os.path.basename(ruta_abs)} creado."
        except Exception as e:
            return f"Fallo al escribir el archivo: {e}"
    elif peticion_code == "SENSIBLE":
        return "No, tío. Eso no lo hago."

    # Subagente Coder (solo código)
    pide_codigo, prompt_codigo = padrino.interceptar_peticion_codigo(user_input)
    if pide_codigo:
        contexto = "\n".join(
            f"{m['role']}: {m['content'][:200]}"
            for m in padrino.mensajes[-4:]
            if m.get("role") in ("user", "assistant")
        )
        respuesta_coder = padrino.llamar_subagente_coder(prompt_codigo, contexto)
        return padrino.presentar_codigo_con_padrino(respuesta_coder, user_input)
    elif prompt_codigo == "SENSIBLE":
        return "No, tío. Eso no lo hago."

    # Navegador autónomo
    if low.startswith("navega ") or low.startswith("busca en youtube "):
        orden = user_input[7:].strip() if low.startswith("navega ") else user_input
        return padrino.computer_use_navegador(orden)

    # Visión artificial
    if low.startswith("padrino ve ") or low.startswith("padrino busca "):
        orden = user_input.split(" ", 2)[2].strip()
        return padrino.interactuar_con_pantalla(orden)

    # Control de hardware
    if low in {"/hardware", "/rendimiento", "/tareas", "/rt"}:
        return "Panel de rendimiento activado en la consola."

    # Volumen
    pide_vol, nivel = padrino.interceptar_volumen(user_input)
    if pide_vol and nivel is not None:
        return padrino._tool_volumen_sistema(nivel)

    # Buscar archivos
    pide_buscar_arch, patron_arch, ruta_arch = padrino.interceptar_buscar_archivos(user_input)
    if pide_buscar_arch:
        return padrino._tool_buscar_archivos(patron_arch, ruta_arch)

    # Escribir archivo
    pide_escribir, ruta_esc, contenido_esc = padrino.interceptar_escritura_archivo(user_input)
    if pide_escribir:
        return padrino._tool_escribir_archivo(ruta_esc, contenido_esc)

    # Cerrar proceso
    pide_cerrar, nombre_proc = padrino.interceptar_cierre_proceso(user_input)
    if pide_cerrar:
        return padrino._tool_cerrar_proceso(nombre_proc)

    # Abrir aplicaciones
    pide_abrir, exito_abrir, objetivo_abrir = padrino.interceptar_apertura_directa(user_input)
    if pide_abrir:
        return f"Ejecutado '{objetivo_abrir}'." if exito_abrir else f"No pude abrir '{objetivo_abrir}'."

    # Leer archivo
    pide_leer, ruta_doc, contenido_doc = padrino.interceptar_y_leer_archivo(user_input)
    if pide_leer:
        return f"Contenido de '{ruta_doc}':\n\n{contenido_doc[:3000]}"

    # Listar directorio
    pide_listar, listado = padrino.interceptar_listado_directorio(user_input)
    if pide_listar:
        return listado

    # Web y multimedia
    pide_web, resultado_web = padrino.interceptar_web_multimedia(user_input)
    if pide_web:
        return resultado_web

    # Hora y fecha
    pide_hf, resultado_hf = padrino.interceptar_hora_fecha(user_input)
    if pide_hf:
        return resultado_hf

    # Control de sistema
    pide_sys, resultado_sys = padrino.interceptar_control_sistema(user_input)
    if pide_sys:
        return resultado_sys

    # Multimedia global
    pide_mm, resultado_mm = padrino.interceptar_multimedia_global(user_input)
    if pide_mm:
        return resultado_mm

    # Captura de pantalla
    pide_cap, resultado_cap = padrino.interceptar_captura_pantalla(user_input)
    if pide_cap:
        return resultado_cap

    # Utilidades de archivos
    pide_util, resultado_util = padrino.interceptar_utilidades_archivo(user_input)
    if pide_util:
        return resultado_util

    # Explorador de rutas
    pide_expl, resultado_expl = padrino.interceptar_explorador_ruta(user_input)
    if pide_expl:
        return resultado_expl

    # ═══ 2. LLAMADA A OLLAMA CON HERRAMIENTAS ═══
    
    # Analizar emociones y aprender del texto
    padrino._extraer_hechos(user_input)
    padrino.procesar_y_aprender_vocabulario(user_input)
    padrino.analizar_emociones_de_texto(user_input)

    padrino.mensajes.append({"role": "user", "content": user_input})
    historial_ctx = padrino.preparar_historial_ollama(padrino.mensajes)

    # Construir el prompt del sistema
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

    try:
        respuesta = padrino.ollama.chat(
            model=padrino.MODELO_PADRINO,
            messages=bloque,
            tools=padrino.ESQUEMA_HERRAMIENTAS,
            options={"temperature": 0.85},
        )
    except Exception as e:
        # Fallback si Ollama falla con las herramientas
        try:
            respuesta = padrino.ollama.chat(model=padrino.MODELO_PADRINO, messages=bloque)
        except Exception as e2:
            return f"Error de conexión con Ollama: {e2}"

    llamadas = getattr(respuesta.message, "tool_calls", None)

    if not llamadas:
        contenido_texto = respuesta.message.content or ""
        llamadas = padrino._parsear_tool_call_en_texto(contenido_texto)

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
            res = padrino.ejecutar_herramienta(nombre, args)
            bloque.append({
                "role": "tool",
                "name": nombre,
                "content": json.dumps(res, ensure_ascii=False),
            })
        try:
            rfinal = padrino.ollama.chat(model=padrino.MODELO_PADRINO, messages=bloque, tools=padrino.ESQUEMA_HERRAMIENTAS)
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