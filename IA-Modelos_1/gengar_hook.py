"""
Hook de Claude Code para Gengar.

Claude Code ejecuta este script en cada evento (SessionStart, PreToolUse, Stop...)
y le pasa el evento como JSON por la entrada estandar. Aqui solo nos quedamos con
lo imprescindible (nombre de la herramienta, ruta o comando recortados, inicio del
prompt y del ultimo mensaje) y se lo mandamos a Gengar en 127.0.0.1.

- Solo libreria estandar: arranca rapido y no ralentiza a Claude.
- Si Gengar no esta abierto, no hace nada (y sale con codigo 0).
- NUNCA se envia el contenido de tus archivos: de un Write solo viaja el tamano.
"""
import sys
import os
import re
import json
import urllib.request

PUERTO = int(os.environ.get("GENGAR_PORT", "47831"))
RE_ERROR = re.compile(r"(error|fail|exception|traceback|cannot|not found|denied|fatal)", re.I)


def cortar(txt, n):
    txt = " ".join(str(txt or "").split())
    return txt if len(txt) <= n else txt[: n - 1] + "…"


def base(ruta):
    ruta = str(ruta or "")
    return os.path.basename(ruta.replace("\\", "/")) or ruta


def detalle_herramienta(nombre, ti):
    """Texto corto que aparece en el ticker sobre la cabeza de Gengar."""
    if not isinstance(ti, dict):
        return ""
    if nombre in ("Read", "Edit", "MultiEdit", "Write"):
        return base(ti.get("file_path"))
    if nombre == "NotebookEdit":
        return base(ti.get("notebook_path"))
    if nombre == "Bash":
        return cortar((ti.get("command") or "").splitlines()[0] if ti.get("command") else "", 60)
    if nombre == "Grep":
        return cortar('"%s"' % ti.get("pattern", ""), 40)
    if nombre == "Glob":
        return cortar(ti.get("pattern", ""), 40)
    if nombre == "WebFetch":
        url = str(ti.get("url", ""))
        return cortar(re.sub(r"^https?://", "", url), 50)
    if nombre == "WebSearch":
        return cortar(ti.get("query", ""), 50)
    if nombre in ("Task", "Agent"):
        return cortar(ti.get("description", ""), 50)
    return ""


def linea_de_error(resp):
    """La linea del error que de verdad importa (no todo el volcado)."""
    texto = ""
    if isinstance(resp, dict):
        texto = "\n".join(str(resp.get(k, "")) for k in ("stderr", "error", "stdout") if resp.get(k))
    elif resp:
        texto = str(resp)
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    if not lineas:
        return ""
    for l in reversed(lineas):
        if RE_ERROR.search(l):
            return cortar(l, 110)
    return cortar(lineas[-1], 110)


def hay_error(resp):
    if not isinstance(resp, dict):
        return False
    if resp.get("is_error") or resp.get("interrupted"):
        return True
    for k in ("exit_code", "exitCode", "returncode"):
        v = resp.get(k)
        if isinstance(v, int) and v != 0:
            return True
    return False


def ultimo_mensaje(datos):
    """Ultima frase de Claude: primero el campo directo, si no la cola del transcript."""
    directo = datos.get("last_assistant_message")
    if isinstance(directo, str) and directo.strip():
        return cortar(directo, 160)
    ruta = datos.get("transcript_path")
    if not ruta or not os.path.exists(ruta):
        return ""
    try:
        with open(ruta, "rb") as f:
            f.seek(0, os.SEEK_END)
            tam = f.tell()
            f.seek(max(0, tam - 200_000))
            cola = f.read().decode("utf-8", "ignore").splitlines()
        for linea in reversed(cola):
            try:
                o = json.loads(linea)
            except Exception:
                continue
            if o.get("type") != "assistant":
                continue
            cont = (o.get("message") or {}).get("content")
            if isinstance(cont, list):
                textos = [b.get("text", "") for b in cont if isinstance(b, dict) and b.get("type") == "text"]
                t = " ".join(x for x in textos if x).strip()
                if t:
                    return cortar(t, 160)
            elif isinstance(cont, str) and cont.strip():
                return cortar(cont, 160)
    except Exception:
        pass
    return ""


def main():
    try:
        crudo = sys.stdin.read() if sys.stdin else ""
        datos = json.loads(crudo or "{}")
    except Exception:
        return 0
    if not isinstance(datos, dict):
        return 0

    ev = datos.get("hook_event_name", "")
    herr = datos.get("tool_name", "") or ""
    ti = datos.get("tool_input") or {}
    resp = datos.get("tool_response")

    envio = {"ev": ev, "herr": herr, "sesion": str(datos.get("session_id", ""))[:12]}

    if herr:
        envio["detalle"] = detalle_herramienta(herr, ti)
        ruta = ""
        if isinstance(ti, dict):
            ruta = ti.get("file_path") or ti.get("notebook_path") or ""
        if ruta:
            envio["archivo"] = str(ruta)[:200]
        if herr == "Write" and isinstance(ti, dict):
            envio["bytes"] = len(str(ti.get("content", "")))   # solo el tamano, jamas el contenido

    if ev == "PostToolUse":
        if hay_error(resp):
            envio["error"] = True
            envio["err_linea"] = linea_de_error(resp)
    elif ev == "PostToolUseFailure":
        envio["error"] = True
        envio["err_linea"] = linea_de_error(datos.get("error") or resp)
    elif ev == "UserPromptSubmit":
        envio["prompt"] = cortar(datos.get("prompt", ""), 90)
    elif ev == "Notification":
        envio["msg"] = cortar(datos.get("message", ""), 140)
        envio["tipo"] = datos.get("notification_type", "")
    elif ev == "Stop":
        envio["ultimo"] = ultimo_mensaje(datos)

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:%d/evento" % PUERTO,
            data=json.dumps(envio).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-Gengar": "1"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=0.6).read()
    except Exception:
        pass   # Gengar no esta abierto: no pasa nada
    return 0


if __name__ == "__main__":
    sys.exit(main())