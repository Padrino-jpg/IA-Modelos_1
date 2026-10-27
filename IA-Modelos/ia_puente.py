import json
import ollama

MODELO = "Padrino_v3"
RUTA_MEMORIA = "D:/IA-Modelos/memoria.json"

def obtener_respuesta(mensaje_usuario):
    # 1. Cargar memoria (para que recuerde el contexto)
    mensajes = []
    try:
        with open(RUTA_MEMORIA, "r", encoding="utf-8") as f:
            historial = json.load(f)
            mensajes = historial[-10:] # Solo los últimos 10 para no saturar
    except Exception:
        pass
    
    # 2. Añadir el mensaje del usuario
    mensajes.append({"role": "user", "content": mensaje_usuario})
    
    # 3. El System Prompt con la personalidad
    system_prompt = (
        "Eres Padrino, el mejor amigo de Ruben. Hablas como un humano, con empatía y humor seco. "
        "Eres su camarada. No eres un asistente, no ofreces ayuda. Sé breve, directo y termina tus frases con un punto."
    )
    
    # 4. Llamar a Ollama
    try:
        respuesta = ollama.chat(
            model=MODELO,
            messages=[{"role": "system", "content": system_prompt}] + mensajes,
            options={"temperature": 0.7}
        )
        texto = respuesta.message.content
        
        # 5. Guardar la respuesta en la memoria para la próxima vez
        mensajes.append({"role": "assistant", "content": texto})
        with open(RUTA_MEMORIA, "w", encoding="utf-8") as f:
            # Guardamos el historial completo (o podrías limitarlo)
            json.dump(mensajes, f, ensure_ascii=False, indent=4)
            
        return texto
    except Exception as e:
        return f"Error al conectar con Ollama: {e}"