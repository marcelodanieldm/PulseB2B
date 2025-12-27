# OSINT Lead Scorer API Endpoints

Estos endpoints permiten acceder a scraping de noticias, análisis de sentimiento y scoring de leads usando OSINT.

## Endpoints

### 1. Scraping de noticias
- **GET /osint-leads/news**
  - Parámetros:
    - `query` (str): Consulta de búsqueda (default: "tech startup funding OR hiring")
    - `region` (str): Región (default: "US")
    - `period` (str): Periodo (default: "7d")
    - `max_results` (int): Máximo de resultados (default: 20)
  - Respuesta: Lista de artículos de noticias.

### 2. Análisis de sentimiento
- **GET /osint-leads/sentiment**
  - Parámetros:
    - `text` (str): Texto a analizar (obligatorio)
  - Respuesta: Diccionario con polaridad y método.

### 3. Scoring de un lead
- **POST /osint-leads/score-lead**
  - Body: Artículo de noticia (dict con `title`, `description`, etc.)
  - Respuesta: Scoring y señales detectadas.

### 4. Scoring batch de leads
- **GET /osint-leads/score-batch**
  - Parámetros:
    - `query` (str): Consulta de búsqueda
    - `regions` (List[str]): Lista de regiones
    - `period` (str): Periodo
    - `max_results_per_region` (int): Máximo por región
    - `min_score` (int): Score mínimo
  - Respuesta: Lista de leads calificados.

## Ejemplo de uso con curl

```bash
curl "http://localhost:8000/osint-leads/news?query=tech+startup&region=US&period=7d&max_results=5"
curl "http://localhost:8000/osint-leads/sentiment?text=This+startup+is+growing+fast"
curl -X POST "http://localhost:8000/osint-leads/score-lead" -H "Content-Type: application/json" -d '{"title": "Startup X raises funding", "description": "Series A round"}'
curl "http://localhost:8000/osint-leads/score-batch?query=tech+startup&regions=US&period=7d&max_results_per_region=5&min_score=20"
```

## Notas
- Todos los endpoints devuelven JSON.
- El scraping depende de GoogleNews y puede requerir VPN para ciertos países.
- El scoring es heurístico y puede personalizarse.
