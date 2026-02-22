# AGENTS.md — Instrucciones para AI Agents
# Compatible con: OpenAI Codex, Google Jules, GitHub Copilot, Cursor, VS Code,
# Windsurf, Aider, RooCode, Gemini CLI, Devin, y 10+ herramientas más.
# Ref: https://agents.md

## Project Overview
FRAVEGA es un sistema de monitoreo de precios de e-commerce argentino.
Scrapea múltiples tiendas (Frávega, Garbarino, MercadoLibre, etc.),
detecta glitches de precios, compara entre competidores, e identifica
oportunidades de reventa con margen positivo.

## Tech Stack
- **Language:** Python 3.10+
- **HTTP Client:** curl_cffi (con impersonación de browser para bypass WAF)
- **Async:** asyncio + curl_cffi.AsyncSession
- **Database:** SQLite (local) con posible migración a PostgreSQL
- **Data Processing:** pandas + openpyxl
- **Browser Automation:** Playwright (fallback cuando curl_cffi no alcanza)

## Project Structure
```
FRAVEGA/
├── core/                    # Código compartido y reutilizable
│   ├── http_client.py       # Wrapper curl_cffi con retry + circuit breaker
│   ├── error_handling.py    # Excepciones custom + patterns de resiliencia
│   ├── async_engine.py      # Motor async con semaphore + rate limiting
│   ├── base_sniffer.py      # Clase abstracta para scrapers
│   └── database.py          # SQLite wrapper compartido
├── targets/                 # Un subdirectorio por e-commerce
│   ├── fravega/
│   ├── garbarino/
│   └── mercadolibre/
├── tools/                   # Generadores de reportes y dashboards
├── data/                    # JSONs de categorías, schemas, mapeos
├── lab/                     # Experimentos y pruebas
└── output/                  # HTML, Excel, reportes generados
```

## Setup Commands
```bash
# Crear virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# Instalar dependencias
pip install curl_cffi pandas openpyxl playwright

# Correr el sniffer de Frávega
python targets/fravega/sniffer_fravega.py
```

## Code Style
- Python 3.10+ con type hints obligatorios
- async/await por defecto para I/O (red, disco, DB)
- curl_cffi en vez de requests (NUNCA usar requests directo)
- Docstrings en español para funciones de negocio
- Nombres de variables en inglés, comentarios en español
- Max line length: 100 caracteres
- Imports ordenados: stdlib → third-party → local

## Testing
```bash
python -m pytest tests/ -v
python -m pytest tests/test_sniffer.py -k "test_glitch_detection"
```

## Key Conventions
1. **SIEMPRE usar Session** de curl_cffi, nunca requests sueltos
2. **SIEMPRE impersonate="chrome"** para requests a e-commerce
3. **SIEMPRE retry con backoff** para requests HTTP
4. **NUNCA hardcodear precios** en Excel — usar fórmulas
5. **Circuit Breaker** para todas las APIs externas
6. **Semaphore(3-5)** para rate limiting de requests paralelos
7. **Cada target** hereda de `core.base_sniffer.BaseSniffer`

## Security
- No commitear credenciales, API keys, ni tokens
- Usar `.env` para configuración sensible
- Rate limiting obligatorio: max 3-5 requests/segundo por dominio
- Respetar robots.txt cuando sea posible
- No hacer requests durante horarios de alta carga del target
