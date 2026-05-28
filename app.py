import os
import json
import urllib.request
import urllib.error
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
API_KEY = os.environ.get("GROQ_KEY")
url = "https://api.groq.com/openai/v1/chat/completions"

conversaciones = {}

def preguntar_ia(messages):
    datos = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages
    }
    datos_bytes = json.dumps(datos).encode("utf-8")
    peticion = urllib.request.Request(url, data=datos_bytes, method="POST")
    peticion.add_header("Content-Type", "application/json")
    peticion.add_header("Authorization", f"Bearer {API_KEY}")
    peticion.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    with urllib.request.urlopen(peticion) as respuesta:
        resultado = json.loads(respuesta.read().decode("utf-8"))
        return resultado["choices"][0]["message"]["content"]

@app.route("/")
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    datos = request.json
    session_id = datos.get("session_id", "default")
    mensaje = datos.get("mensaje")
    
    if session_id not in conversaciones:
        conversaciones[session_id] = [
            {
                "role": "system",
                "content": "Eres el asistente virtual de la Clínica Veterinaria Huella, situada en Fuenlabrada. Tu nombre es Max. Respondes siempre en español de forma amable y profesional. Solo respondes preguntas relacionadas con la clínica y las mascotas. Si te preguntan algo que no tiene que ver con la clínica, redirige amablemente la conversación. Los horarios son de lunes a viernes de 9:00 a 20:00 y sábados de 10:00 a 14:00. Los servicios que ofrecemos son: consultas generales, vacunaciones, cirugía, peluquería canina y urgencias 24h."
            }
        ]
    
    conversaciones[session_id].append({"role": "user", "content": mensaje})
    respuesta = preguntar_ia(conversaciones[session_id])
    conversaciones[session_id].append({"role": "assistant", "content": respuesta})
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)