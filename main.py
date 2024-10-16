from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar el cliente de OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise Exception("Por favor, proporciona tu clave de API de OpenAI en el archivo .env")
client = OpenAI(api_key=api_key)

app = FastAPI()

# Modelos Pydantic

class Audiencia(BaseModel):
    nombreProducto: str
    textoAnuncio: str

class AudienciaAjuste(BaseModel):
    audienciaId: int
    nuevoTexto: str

class Producto(BaseModel):
    nombreProducto: str
    descripcionProducto: str
    publicoObjetivo: str = None  # Opcional

class CopiaPublicitaria(BaseModel):
    producto: Producto

# Endpoints

# 1. Generar Audiencia
# POST /audiencias
@app.post("/audiencias")
async def generar_audiencia(audiencia: Audiencia):
    prompt = f"Basado en el siguiente texto de anuncio para el producto '{audiencia.nombreProducto}', identifica la audiencia ideal (ubicación, edad, género, intereses, comportamientos):\n\n{audiencia.textoAnuncio}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    audiencia_generada = response.choices[0].message.content.strip()
    return {
        "nombreProducto": audiencia.nombreProducto,
        "audiencia": audiencia_generada
    }

# PUT /audiencias/{audienciaId}
@app.put("/audiencias/{audienciaId}")
async def ajustar_audiencia(audienciaId: int, ajuste: AudienciaAjuste):
    return {"mensaje": "Audiencia ajustada", "audienciaId": audienciaId, "nuevoTexto": ajuste.nuevoTexto}

# 2. Generar Copias Publicitarias (Autotarget)
# POST /generar_copias_publicitarias/
@app.post("/generar_copias_publicitarias/")
async def generar_copias_publicitarias(copia: CopiaPublicitaria):
    producto = copia.producto

    prompt = f"""
Eres Autotarget, un modelo de lenguaje especializado en generar copias publicitarias persuasivas y creativas. Te enfocarás en capturar los puntos de venta únicos del producto, involucrar emocionalmente al público objetivo y motivarlos a tomar acción (por ejemplo, comprar, registrarse o solicitar más información). Tus respuestas deben ser claras, concisas y persuasivas, utilizando titulares llamativos y textos optimizados para varias plataformas publicitarias como redes sociales, email y páginas de destino.

Directrices:
1. Conciencia de la Audiencia: Adapta el tono y estilo según el público objetivo, que puede variar desde casual y moderno para audiencias jóvenes hasta profesional y autoritario para contextos de negocios.

2. Técnicas Persuasivas:
- Usa apelaciones emocionales (felicidad, emoción, urgencia, etc.).
- Destaca beneficios sobre características, enfatizando el problema que el producto resuelve.
- Incluye llamadas a la acción que inspiren urgencia o curiosidad (por ejemplo, "¡Obtén el tuyo ahora!", "¡Descubre el futuro hoy!").

3. Creatividad: Infunde creatividad en la redacción, especialmente para productos innovadores o disruptivos. Utiliza metáforas, eslóganes o frases pegajosas para hacer que el producto sea memorable.

4. Tono y Estilo: Adapta el tono para que coincida con el tipo de producto y la voz de la marca. Ejemplos incluyen:
- Juguetón y optimista para marcas de estilo de vida.
- Confiable e informativo para servicios financieros.
- Elegante y enfocado en tecnología para productos tecnológicos.

5. Optimización:
- Mantén la copia corta e impactante (especialmente para plataformas con límites de caracteres).
- Hazla visualmente adaptable (por ejemplo, divide en secciones como encabezados, texto principal y eslóganes).

Instrucciones:
- Basado en la descripción del producto proporcionada, genera 2-3 variaciones de copias publicitarias. Cada versión debe variar en tono (por ejemplo, una lúdica, una profesional y una altamente persuasiva). Incluye un titular llamativo, cuerpo del texto y una llamada a la acción fuerte.

Descripción del Producto:
Nombre: {producto.nombreProducto}
Descripción: {producto.descripcionProducto}
"""

    if producto.publicoObjetivo:
        prompt += f"Público Objetivo: {producto.publicoObjetivo}\n"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )

    copias_generadas = response.choices[0].message.content.strip()
    return {"copiasPublicitarias": copias_generadas}
