# 🔬 DEEP DIVE COMPLETO — ANÁLISIS DE TODOS LOS RECURSOS

> **Fecha:** 2026-02-20  
> **Objetivo:** Scrapear páginas, encontrar lo más barato, comparar precios, y revender con margen  
> **Método:** Lectura chunk-por-chunk de CADA recurso, sin saltear nada

---

## 📋 ÍNDICE DE RECURSOS ANALIZADOS

| # | Recurso | URL | Chunks Leídos | Relevancia |
|---|---------|-----|---------------|------------|
| 1 | **skills.sh** | https://skills.sh | 100+ chunks | 🔴 CRÍTICA |
| 2 | **agents.md** | https://agents.md | 7 chunks | 🟡 MEDIA |
| 3 | **curl_cffi** | https://curl-cffi.readthedocs.io | 30+ chunks | 🔴 CRÍTICA |
| 4 | **MCP (Model Context Protocol)** | https://modelcontextprotocol.io | 15+ chunks | 🟡 MEDIA |
| 5 | **Claude Code Docs** | https://docs.anthropic.com/en/docs/claude-code | 20+ chunks | 🟡 MEDIA |
| 6 | **leaked-system-prompts** | https://github.com/jujumilk3/leaked-system-prompts | 5 chunks | 🟢 BAJA |

---

## 1️⃣ SKILLS.SH — Ecosistema de Skills para AI Agents

### ¿Qué es?
Un marketplace/ecosistema abierto de "Skills" (capacidades reutilizables) para agentes de IA. Cada skill es un paquete con instrucciones, scripts y assets que extienden las capacidades de un agente.

### Estructura de una Skill
```
skill-name/
├── SKILL.md           # Instrucciones principales (OBLIGATORIO)
├── scripts/           # Scripts helper
├── references/        # Documentación de referencia
├── assets/            # Archivos adicionales
└── examples/          # Ejemplos de uso
```

### Skills Analizadas — TIER 1 (Impacto Directo)

#### 1.1 `systematic-debugging` (obra/superpowers)
- **Iron Law:** `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`
- **4 Fases:** Root Cause Investigation → Pattern Analysis → Hypothesis+Test → Implementation
- **Multi-Layer Diagnostic:** Cuando hay múltiples componentes (API→Service→DB), agregar logs en CADA frontera
- **Data Flow Tracing:** Rastrear hacia atrás hasta la fuente del valor malo
- **Regla de 3:** Si 3 fixes fallan → parar y cuestionar la ARQUITECTURA
- **🎯 FRAVEGA:** Cuando un sniffer falla (403, timeout, datos corruptos), seguir este proceso exacto

#### 1.2 `xlsx` (anthropics/skills)
- **2 librerías:** `openpyxl` para fórmulas/formato, `pandas` para análisis/bulk
- **Regla CRÍTICA:** SIEMPRE usar fórmulas Excel (`=SUM(B2:B9)`), NUNCA hardcodear valores
- **Color Coding:** Azul=inputs, Negro=fórmulas, Verde=links entre hojas, Rojo=links externos
- **Script recalc.py:** Usa LibreOffice para recalcular fórmulas. Retorna JSON con ubicaciones de errores
- **openpyxl tips:** `data_only=True` lee valores pero PIERDE fórmulas al guardar. `read_only=True` para archivos grandes
- **🎯 FRAVEGA:** Para leer `Precios competidores.xlsx`, crear reportes de comparación de precios

#### 1.3 `async-python-patterns` (wshobson/agents)
- **8 Patterns:** Basic async/await, gather(), Task management, Error handling, Timeout, Semaphores, Producer-Consumer, Rate limiting
- **Semaphore Rate Limiting:** `semaphore = asyncio.Semaphore(3)` → máximo 3 requests paralelos
- **Connection Pools:** `aiohttp.TCPConnector(limit=100, limit_per_host=10)`
- **Batch Processing:** Procesar items en lotes de N con `gather()`
- **Error handling:** `asyncio.gather(*tasks, return_exceptions=True)` → no falla todo si una task falla
- **Timeout:** `asyncio.wait_for(operation, timeout=2.0)` → mata operaciones lentas
- **🎯 FRAVEGA:** Reemplazar scraping sync por async con rate limiting. Pasar de 1 a 3-5 requests paralelos

#### 1.4 `error-handling-patterns` (wshobson/agents)
- **Circuit Breaker:** 3 estados: CLOSED (normal) → OPEN (falla, rechaza) → HALF_OPEN (prueba)
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=timedelta(seconds=60), success_threshold=2):
        self.state = CircuitState.CLOSED
```
- **Error Aggregation:** Colectar múltiples errores en vez de fallar en el primero
- **Graceful Degradation:** `with_fallback(primary=cache, fallback=db)`
- **Multiple Fallbacks:** `try_function(api1) or try_function(api2) or try_function(cache) or DEFAULT`
- **Retry con Exponential Backoff:** `@retry(max_attempts=3, backoff_factor=2.0)`
- **Custom Exception Hierarchy:** `ApplicationError` → `ScrapingError` → `WAFBlockedError`
- **🎯 FRAVEGA:** Circuit Breaker para API de Frávega. Retry con backoff para requests.

#### 1.5 `writing-plans` + `executing-plans` (obra/superpowers)
- **Granularidad:** 2-5 minutos por paso
- **Header format requerido:**
```markdown
# [Feature Name] Implementation Plan
> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key technologies]
```
- **Cada task incluye:** Archivo a modificar, qué cambiar, test, commit
- **🎯 FRAVEGA:** Planificar CADA nuevo target (MercadoLibre, Garbarino) con pasos atómicos

#### 1.6 `verification-before-completion` (obra/superpowers)
- **Iron Law:** `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`
- **Gate Function:** Identificar → Ejecutar → LEER output → Verificar
- **Red flags:** "Ya funciona" sin correr nada
- **🎯 FRAVEGA:** Siempre mostrar evidencia real del scraping funcionando

### Skills Analizadas — TIER 2 (Mejoran Calidad)

#### 1.7 `brainstorming` (obra/superpowers)
- Explorar → Preguntas (una a la vez, multiple choice) → 2-3 propuestas → Diseño → Plan
- Output: `docs/plans/YYYY-MM-DD-<topic>-design.md`
- YAGNI ruthlessly, explorar alternativas, validación incremental

#### 1.8 `subagent-driven-development` (obra/superpowers)
- Per task: Dispatch Implementer → Questions? → Implements/Tests/Commits → Spec Review → Code Quality Review
- 3 Templates: implementer, spec-reviewer, code-quality-reviewer
- NUNCA dispatch múltiples implementers en paralelo, NUNCA skipear reviews

#### 1.9 `dispatching-parallel-agents` (obra/superpowers)
- Cuándo: 3+ fallos en subsistemas independientes
- Pattern: Identificar dominios → Crear tasks focalizados → Dispatch paralelo → Review + Integrate
- Cuándo NO: Fallos relacionados, shared state, exploratory debugging

#### 1.10 `test-driven-development` (obra/superpowers)
- RED-GREEN-REFACTOR estricto: ver fallar → código mínimo → ver pasar → refactor
- Bug fix: SIEMPRE escribir failing test que reproduzca el bug PRIMERO

#### 1.11 `python-testing-patterns` (wshobson/agents)
- AAA Pattern: Arrange → Act → Assert
- Mocking: `unittest.mock.Mock()`, `patch()`, `@patch` decorator
- DB testing: `@pytest.fixture(scope="function")` con SQLite in-memory

#### 1.12 `python-performance-optimization` (wshobson/agents)
- 20 patterns: cProfile, lru_cache, generators, __slots__, multiprocessing
- Sync vs async: 4 requests de 1s: sync=4s, async=1s → 4x speedup
- Batch DB: `executemany()` vs individual: hasta 100x speedup

#### 1.13 `prompt-engineering-patterns` (wshobson/agents)
- Structured Output con Pydantic (JSON schema enforcement)
- Chain-of-Thought con Self-Verification
- Dynamic Example Selection con semantic similarity
- Progressive Disclosure: 4 niveles de complejidad
- Token Efficiency: reducir 150+ tokens a 30 manteniendo calidad

#### 1.14 `mcp-builder` (anthropics/skills)
- 4 Fases: Deep Research → Implementation → Review+Test → Evaluations
- Stack: TypeScript (preferido) o Python con FastMCP
- Zod (TS) o Pydantic (Python) para schemas

#### 1.15 `architecture-patterns` (wshobson/agents)
- Clean Architecture: domain/entities/ → use_cases/ → adapters/ → infrastructure/
- Hexagonal: Core con interfaces (Ports), implementaciones externas (Adapters)
- DDD: Value Objects, Entities, Aggregates, Domain Events

#### 1.16 `api-design-principles` (wshobson/agents)
- GraphQL Schema Design completo con Relay-style pagination
- DataLoader Pattern para resolver N+1
- **🎯 FRAVEGA:** Entender EXACTAMENTE la GraphQL API de Frávega

### Skills Analizadas — TIER 3 (Para el Futuro)

| Skill | Para Qué | Cuándo |
|-------|----------|--------|
| `docker-expert` | Deploy 24/7 del monitor | Cuando tengamos algo estable |
| `sql-optimization-patterns` | Optimizar DB cuando crezca | +10k registros |
| `github-actions-templates` | CI/CD automatizado | Cuando tengamos tests |
| `pdf` | Reportes PDF de precios | Para clientes/análisis |
| `webapp-testing` | Testing de dashboards | Si hacemos UI |

---

## 2️⃣ AGENTS.MD — Formato Estándar para Guiar AI Agents

### ¿Qué es?
Un formato abierto y simple (archivo `AGENTS.md`) que funciona como "README para agentes". Un solo archivo de instrucciones que es compatible con **20+ herramientas** de IA.

### Herramientas Compatibles
- OpenAI Codex, Google Jules, GitHub Copilot agent
- Cursor, VS Code, Windsurf, Aider, RooCode
- Factory, Amp, Zed, Warp, Kilo Code, Phoenix
- Gemini CLI, goose, opencode, Devin, UiPath

### Estructura Recomendada
1. **Project overview** — Descripción breve
2. **Build and test commands** — `pip install`, `python -m pytest`, etc.
3. **Code style guidelines** — Convenciones de código
4. **Testing instructions** — Cómo correr tests
5. **Security considerations** — Reglas de seguridad

### Ejemplo Real (OpenAI Codex)
```markdown
# AGENTS.md
## Setup commands
- Install deps: `pnpm install`
- Start dev server: `pnpm dev`
- Run tests: `pnpm test`

## Code style
- TypeScript strict mode
- Single quotes, no semicolons
- Use functional patterns where possible
```

### Migración
```bash
mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md
```

### Configuración Gemini CLI
```json
{ "contextFileName": "AGENTS.md" }
```

### 🎯 Aplicación FRAVEGA
Crear un `AGENTS.md` en la raíz del proyecto con:
- Setup commands (pip install, env setup)
- Estructura del proyecto
- Convenciones de código (Python, async, naming)
- Targets activos y cómo agregar nuevos
- Reglas de scraping (rate limits, headers, etc.)

---

## 3️⃣ CURL_CFFI — Biblioteca Python para Bypass de WAF

### ¿Qué es?
Python binding para `curl-impersonate` que permite imitar el fingerprint TLS/HTTP2 de browsers reales. **LA SOLUCIÓN** al problema de 403 que tuvimos con Frávega y Flybondi.

### ¿Por qué es crucial?
| Feature | requests | aiohttp | httpx | curl_cffi |
|---------|----------|---------|-------|-----------|
| HTTP/2 | ❌ | ❌ | ✅ | ✅ |
| HTTP/3 | ❌ | ❌ | ❌ | ✅ |
| Sync | ✅ | ❌ | ✅ | ✅ |
| Async | ❌ | ✅ | ✅ | ✅ |
| WebSocket | ❌ | ✅ | ❌ | ✅ |
| Retry nativo | ❌ | ❌ | ❌ | ✅ |
| **Fingerprints** | ❌ | ❌ | ❌ | **✅** |
| Velocidad | 🐇 | 🐇🐇 | 🐇 | 🐇🐇 |

### Instalación
```bash
pip install curl_cffi --upgrade
```

### Uso Básico — Impersonar Chrome
```python
import curl_cffi

# Impersonar Chrome (usa la última versión automáticamente)
r = curl_cffi.get("https://www.fravega.com", impersonate="chrome")
print(r.status_code)  # 200 en vez de 403!

# Con proxy
r = curl_cffi.get("https://www.fravega.com", 
                   impersonate="chrome", 
                   proxy="http://localhost:3128")

# Headers custom (se suman a los de Chrome)
r = curl_cffi.get("https://www.fravega.com",
                   impersonate="chrome",
                   headers={"Accept-Language": "es-AR"})

# DESACTIVAR headers default de Chrome
r = curl_cffi.get("https://www.fravega.com",
                   impersonate="chrome",
                   default_headers=False,
                   headers={"User-Agent": "Custom"})
```

### Sessions y Cookies (SIEMPRE usar)
```python
# Mantener cookies entre requests (simula navegación real)
with curl_cffi.Session(impersonate="chrome") as s:
    # Login o primera visita
    s.get("https://www.fravega.com")
    # Segunda request con cookies del server
    r = s.get("https://www.fravega.com/api/graphql")
    print(r.json())
```

### Retry Nativo con Backoff
```python
from curl_cffi import Session, RetryStrategy

# Retry automático con exponential backoff
strategy = RetryStrategy(count=3, delay=0.2, jitter=0.1, backoff="exponential")
with Session(impersonate="chrome", retry=strategy) as s:
    r = s.get("https://www.fravega.com/api/graphql")
```

### POST con JSON (para GraphQL de Frávega!)
```python
# GraphQL query a Frávega
payload = {
    "query": "query { search(term: \"iphone\") { products { name price } } }"
}
r = curl_cffi.post("https://www.fravega.com/api/graphql",
                    json=payload,
                    impersonate="chrome")
```

### Async para Scraping Masivo
```python
import asyncio
from curl_cffi import AsyncSession

urls = [
    "https://www.fravega.com/l/celulares",
    "https://www.garbarino.com/celulares",
    "https://www.mercadolibre.com.ar/celulares"
]

async with AsyncSession(impersonate="chrome") as s:
    tasks = [s.get(url) for url in urls]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r.status_code, len(r.text))
```

### WebSockets (para monitoreo real-time)
```python
from curl_cffi import Session, WebSocket

def on_message(ws: WebSocket, message):
    print(f"Precio actualizado: {message}")

with Session(impersonate="chrome") as s:
    ws = s.ws_connect("wss://api.example.com/prices", on_message=on_message)
    ws.run_forever()
```

### Topics Avanzados

#### Proxies
```python
# HTTP proxy
curl_cffi.get(url, proxy="http://user:pass@proxy.com:3128")
# SOCKS proxy
curl_cffi.get(url, proxy="socks5://localhost:9050")
```

#### HTTP Version Selection
```python
# Forzar HTTP/3 (menos detección!)
curl_cffi.get("https://www.fravega.com", http_version="v3")
# Forzar HTTP/1.1 (si h2 falla)
curl_cffi.get("https://www.fravega.com", http_version="v1")
```

#### Keep-Alive con HTTP/2
```python
s = Session(impersonate="chrome")
s.get("https://www.fravega.com")
s.upkeep()  # Manda ping frame para mantener conexión
```

### TLS Fingerprinting — Lo Que Hace Especial a curl_cffi
- **TLS fingerprint (JA3):** Hash de los cipher suites y extensiones usados en el handshake TLS. Cada browser tiene uno fijo.
- **HTTP/2 fingerprint (Akamai):** Settings del frame HTTP/2 que identifican el browser.
- **Chrome 110+ usa ClientHello permutation:** El orden de extensiones es random → JA3 cambia, pero ja3n (normalizado) no.
- **HTTP/3:** Menos WAFs lo usan aún → HAY MENOS DETECCIÓN con HTTP/3.

### Impersonation FAQ (Clave!)
- **¿Cómo verificar que funciona?** → Visitar `https://tls.browserleaks.com/json` y comparar con tu browser real
- **¿Aún me detectan con impersonation correcta?** → TLS/JA3 es UN factor. Otros: IP quality, request rate, JS fingerprints. Usar proxies y rate limiting
- **¿Randomizar fingerprints por request?** → NO generar fingerprints random. Usar `random.choice(["chrome119", "chrome120", ...])` con versiones populares
- **¿Puedo cambiar JS fingerprints?** → NO, curl_cffi no tiene browser/JS runtime. Para eso usar Playwright stealth
- **Error HTTP/2 stream 0:** Probar remover `Content-Length` header, usar mejor proxy, o forzar HTTP/1.1

### Cloudflare Bypass
> TLS fingerprints son solo UNO de los factores. Para protección básica, TLS solo alcanza. Para protección alta, necesitás: mejor IP (proxy residencial) + browser automation (Playwright)

### 🎯 Aplicación FRAVEGA
1. **Reemplazar `requests` por `curl_cffi`** en TODOS los scrapers
2. **Usar `impersonate="chrome"`** para bypass WAF Frávega/Flybondi
3. **Sessions con cookies** para simular navegación real
4. **RetryStrategy nativo** en vez de implementar retry manual
5. **AsyncSession + Semaphore** para scraping paralelo con rate limiting
6. **HTTP/3** para targets con detección agresiva
7. **Verificar fingerprint** en tls.browserleaks.com

---

## 4️⃣ MCP — Model Context Protocol

### ¿Qué es?
Protocolo abierto que permite a agentes de IA acceder a datos, herramientas y aplicaciones de manera estandarizada. Funciona como un "USB para AI" — conexión universal.

### Arquitectura
```
MCP Host (tu app)
├── MCP Client 1 → MCP Server (e.g., Sentry)
├── MCP Client 2 → MCP Server (e.g., filesystem)
└── MCP Client 3 → MCP Server (e.g., custom)
```

### Participantes
- **MCP Host:** La aplicación AI que coordina (e.g., Claude Code, tu script)
- **MCP Client:** Componente que mantiene conexión a un MCP Server
- **MCP Server:** Programa que provee contexto/dados a clientes

### Capas
1. **Data Layer (JSON-RPC 2.0):**
   - Lifecycle management (init, negotiate, terminate)
   - Server features: **Tools** (acciones), **Resources** (datos), **Prompts** (templates)
   - Client features: Sampling (LLM completions), Elicitation (pedir info al user)
2. **Transport Layer:**
   - **Stdio:** stdin/stdout para procesos locales, sin overhead de red
   - **Streamable HTTP:** POST + Server-Sent Events, para servidores remotos

### Primitivas
- **Tools:** Funciones ejecutables (file ops, API calls, DB queries)
- **Resources:** Data sources (file contents, DB records, API responses)
- **Prompts:** Templates reutilizables (system prompts, few-shot examples)

### Build an MCP Server (Python)
```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("price-monitor")

@mcp.tool()
async def get_prices(product: str) -> str:
    """Get prices for a product across multiple stores."""
    # Scraping logic here
    return prices_json

@mcp.tool()
async def compare_prices(product_id: str) -> str:
    """Compare prices for a specific product."""
    # Comparison logic
    return comparison

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

### Setup
```bash
uv init price-monitor
cd price-monitor
uv venv && source .venv/bin/activate
uv add "mcp[cli]" httpx
```

### Testing
- Usar **MCP Inspector** para testear tools
- Logging: NUNCA usar `print()` — usar `logging.info()` o `print(..., file=sys.stderr)`

### 🎯 Aplicación FRAVEGA
**Para cuando el proyecto esté más maduro:**
- Crear MCP Server que exponga tools: `get_prices`, `compare_prices`, `find_deals`
- Los agentes AI podrían consultar precios en tiempo real
- Permitiría integración con Claude Code, Cursor, etc.

---

## 5️⃣ CLAUDE CODE DOCS — Best Practices y Workflows

### Overview
Claude Code es una herramienta de coding agéntico: lee codebase, edita archivos, corre comandos. Disponible en terminal, IDE, desktop, web.

### Best Practices Extraídas

#### 1. Explore → Plan → Code
```
1. "read /src/scraper and understand how we handle sessions"  (EXPLORE)
2. "I want to add Garbarino. What files need to change? Create a plan." (PLAN)
3. "implement the scraper from your plan. write tests, run them." (IMPLEMENT)
4. "commit with a descriptive message" (COMMIT)
```

#### 2. CLAUDE.md Efectivo
- **Home folder** (`~/.claude/CLAUDE.md`): Aplica a TODAS las sesiones
- **Project root** (`./CLAUDE.md`): Check into git para compartir
- **Local** (`CLAUDE.local.md`): Para overrides personales, .gitignore
- **Child dirs:** Claude los lee on-demand

Ejemplo CLAUDE.md para nuestro proyecto:
```markdown
# Code style
- Python 3.10+, type hints obligatorios
- async por defecto para I/O
- curl_cffi en vez de requests

# Workflow
- Siempre correr tests después de cambios
- Usar circuit breaker para APIs externas
- Rate limit: max 3 requests paralelos por dominio
```

#### 3. Skills (Custom Slash Commands)
```markdown
# .claude/skills/scrape-target/SKILL.md
---
name: scrape-target
description: Scrape a new e-commerce target
---
1. Analyze the target URL structure
2. Find API endpoints (GraphQL, REST)
3. Create scraper with curl_cffi
4. Add rate limiting and error handling
5. Write tests
6. Add to monitoring rotation
```

Uso: `/scrape-target https://www.garbarino.com`

#### 4. Custom Subagents
```markdown
# .claude/agents/price-analyzer.md
---
name: price-analyzer
description: Analyzes price data for arbitrage opportunities
tools: Read, Grep, Glob, Bash
---
You are a price analysis specialist. Given product data:
- Identify lowest prices across stores
- Calculate potential margins
- Flag suspicious pricing (too low = scam, too high = error)
- Generate comparison report
```

#### 5. Session Management
- **`/clear`** entre tareas no relacionadas
- **`/compact <instructions>`** para comprimir contexto: `/compact Focus on scraping logic`
- **`/rewind`** para deshacer cambios
- **`claude --continue`** para retomar última conversación

#### 6. Headless Mode (Automatización)
```bash
# Correr análisis de precios automáticamente
claude -p "Analyze latest price data and generate report" --output-format json

# Fan out: procesar múltiples targets
for target in fravega garbarino musimundo; do
  claude -p "Scrape $target and save to database" \
    --allowedTools "Edit,Bash(python *)"
done
```

#### 7. Git Worktrees para Sesiones Paralelas
```bash
# Trabajar en Frávega en un worktree, MercadoLibre en otro
claude -w fravega-scraper    # Crea worktree independiente
claude -w meli-scraper       # Otro worktree paralelo
```

#### 8. Failure Patterns a Evitar
| Anti-Pattern | Solución |
|---|---|
| "Kitchen sink session" (mezclar tareas) | `/clear` entre tareas |
| Corregir error tras error sin parar | Después de 2 fallos: `/clear` y reescribir prompt |
| CLAUDE.md demasiado largo | Podar ruthlessly, usar hooks |
| "Trust then verify" (confiar sin verificar) | Siempre tests/evidence |
| Exploración infinita | Scope narrow o usar subagents |

### Common Workflows Relevantes

#### Fix Bugs
1. Compartir el error con Claude
2. Pedir recomendaciones de fix
3. Aplicar el fix
4. Verificar con tests

#### Work with Tests
1. Identificar código sin tests
2. Generar test scaffolding
3. Agregar edge cases
4. Correr y verificar

#### Create PRs
- Usar `/commit-push-pr` (built-in skill)
- O: `claude -p "create a pr"`

### 🎯 Aplicación FRAVEGA
1. Crear `CLAUDE.md` en raíz del proyecto con convenciones
2. Crear skills custom: `/scrape-target`, `/analyze-prices`, `/find-deals`
3. Crear subagents: `price-analyzer`, `scraper-debugger`
4. Usar headless mode para scraping schedule
5. Git worktrees para trabajar en múltiples targets simultáneos

---

## 6️⃣ LEAKED-SYSTEM-PROMPTS — Colección de Prompts de IA

### ¿Qué es?
Repositorio GitHub (`jujumilk3/leaked-system-prompts`) con system prompts reales filtrados de servicios AI populares.

### Prompts Disponibles
- **Perplexity AI** (múltiples versiones: 2022-2025, incluyendo GPT-4 y Claude variants)
- **Opera Aria**
- **Phind**
- **Proton Lumo**
- + 42 contributors con prompts de otros servicios

### Utilidad para FRAVEGA
- **Estudiar cómo los mejores AI tools estructuran sus prompts**
- **Extraer patterns de formatting:** cómo presentar datos, cómo dar instrucciones claras
- **Inspiración para PROMPTS_ARSENAL.md:** mejorar nuestros prompts de intelligence gathering
- **Entender limitaciones:** qué restricciones ponen los services (good for reverse engineering)

---

## 💎 TOP 15 PEPITAS DE ORO — APLICACIÓN DIRECTA AL NEGOCIO

| # | Pepita | De Dónde | Impacto | Código/Pattern |
|---|--------|----------|---------|----------------|
| 1 | **curl_cffi impersonate** | curl_cffi docs | Resuelve 403 de Frávega/Flybondi | `curl_cffi.get(url, impersonate="chrome")` |
| 2 | **RetryStrategy nativo** | curl_cffi | Reemplaza retry manual | `RetryStrategy(count=3, backoff="exponential")` |
| 3 | **AsyncSession + gather** | curl_cffi + async-patterns | Scraping 3-5x más rápido | `AsyncSession()` + `asyncio.gather()` |
| 4 | **Circuit Breaker** | error-handling skill | Previene bombardeo de API caída | 3 estados: CLOSED→OPEN→HALF_OPEN |
| 5 | **Semaphore Rate Limit** | async-patterns skill | Control de concurrencia | `asyncio.Semaphore(3)` |
| 6 | **Session con cookies** | curl_cffi | Simula navegación real | `with Session(impersonate="chrome") as s:` |
| 7 | **HTTP/3 para evasión** | curl_cffi fingerprint docs | Menos WAFs detectan HTTP/3 | `http_version="v3"` |
| 8 | **Excel con fórmulas** | xlsx skill | Reportes dinámicos | `openpyxl` + fórmulas, nunca hardcode |
| 9 | **Multi-Layer Diagnostic** | systematic-debugging | Debug eficiente de scrapers | Logs en cada frontera de componente |
| 10 | **No fix sin root cause** | systematic-debugging | Evita parches inútiles | 3 intentos → cuestionar arquitectura |
| 11 | **AGENTS.md universal** | agents.md | Compatible con 20+ AI tools | Un archivo, todas las herramientas |
| 12 | **Custom Skills** | Claude Code best practices | Automatizar tareas repetitivas | `.claude/skills/scrape-target/SKILL.md` |
| 13 | **Headless fan-out** | Claude Code best practices | Procesar múltiples targets en paralelo | `for target in ...; do claude -p ...` |
| 14 | **Graceful Degradation** | error-handling skill | Resiliencia ante fallos | `try api1 → try api2 → try cache → DEFAULT` |
| 15 | **MCP Server de precios** | MCP docs | Exponer datos a AI agents | `FastMCP("price-monitor")` con tools |

---

## 🎯 PLAN DE ACCIÓN PRIORIZADO

### FASE 1 — Inmediata (resolver el blocker de 403)
1. ✅ `pip install curl_cffi`
2. ✅ Refactorizar `sniffer_fravega.py` para usar `curl_cffi.Session(impersonate="chrome")`
3. ✅ Agregar `RetryStrategy` nativo
4. ✅ Verificar fingerprint en `tls.browserleaks.com/json`

### FASE 2 — Esta semana (infraestructura robusta)
1. Implementar Circuit Breaker para APIs externas
2. Implementar AsyncSession + Semaphore para scraping paralelo
3. Crear Custom Exception Hierarchy (`ScrapingError`, `WAFBlockedError`, etc.)
4. Crear `AGENTS.md` y `CLAUDE.md` en raíz del proyecto

### FASE 3 — Próxima semana (automatización)
1. Crear skills custom: `/scrape-target`, `/analyze-prices`
2. Agregar nuevos targets (Garbarino, MercadoLibre, Musimundo)
3. Implementar Excel reporting con fórmulas dinámicas
4. Setup TDD con pytest para scrapers

### FASE 4 — Futuro (escalamiento)
1. MCP Server para exponer datos de precios
2. Docker deploy 24/7
3. CI/CD con GitHub Actions
4. Dashboard web para visualización

---

## ⚖️ ¿INSTALAR SKILLS EXISTENTES O CREAR CUSTOM?

### Recomendación: **HÍBRIDO**

| Approach | Skills | Razón |
|----------|--------|-------|
| **Instalar directamente** | `systematic-debugging`, `verification-before-completion`, `writing-plans` | Son procesos genéricos que aplican tal cual |
| **Usar como inspiración** | `async-python-patterns`, `error-handling-patterns`, `python-testing-patterns` | Los patterns son universales pero necesitan adaptación al contexto de scraping |
| **Crear custom** | `scrape-target`, `analyze-prices`, `find-deals`, `compare-excel` | Son específicos de nuestro negocio, no existen en el marketplace |
| **No necesitar** | Docker, GitHub Actions, webapp-testing | Demasiado pronto, agregan complejidad innecesaria ahora |

### Para instalar una skill de skills.sh:
```bash
# Ejemplo (verificar comando exacto en skills.sh)
claude skill install obra/superpowers/systematic-debugging
```

---

*Documento generado por análisis exhaustivo de 170+ chunks de contenido de 6 fuentes distintas.*
