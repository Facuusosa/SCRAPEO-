# CLAUDE.md — Configuración para Claude Code
# Ref: https://docs.anthropic.com/en/docs/claude-code/best-practices

# Proyecto FRAVEGA — Monitor de Precios E-commerce Argentina

## Contexto del Proyecto
Este proyecto scrapea tiendas de e-commerce argentinas para encontrar los precios
más bajos, detectar glitches de precios, y encontrar oportunidades de reventa.
El blocker principal ha sido WAF detection (403 errors) que se resuelve con curl_cffi.

## Archivos Clave
- `core/http_client.py` — Cliente HTTP con curl_cffi + impersonation
- `core/error_handling.py` — Circuit Breaker, retries, excepciones custom
- `core/async_engine.py` — Motor async para scraping paralelo
- `core/base_sniffer.py` — Clase base para todos los scrapers
- `targets/fravega/sniffer_fravega.py` — Scraper principal de Frávega
- `data/clean_categories.json` — Categorías descubiertas de Frávega
- `DEEP_DIVE_COMPLETO.md` — Análisis exhaustivo de todas las herramientas

## Code Style
- Python 3.10+, type hints obligatorios
- async por defecto para toda operación I/O
- curl_cffi en vez de requests (SIEMPRE)
- Docstrings en español para lógica de negocio

## Workflow
- Correr tests después de cada cambio: `python -m pytest tests/ -v`
- Verificar que el scraper no da 403 antes de commitear
- Usar Circuit Breaker para APIs externas
- Rate limit: max 3 requests paralelos por dominio (Semaphore)

## Reglas de Negocio
- Un "glitch" es cuando el precio baja >40% del precio lista
- Margen mínimo de reventa: 15%
- Categorías prioritarias: celulares, notebooks, TVs, consolas
- Moneda: ARS (pesos argentinos)

## Cuando Compactes (/compact)
Preservar siempre:
- Lista de archivos modificados
- Estado actual del scraper (funciona/no funciona)
- Último error encontrado
- Categorías activas de scraping

## Additional Instructions
- @README.md para overview del proyecto
- @PROTOCOL.md para metodología y hallazgos técnicos
- @DEEP_DIVE_COMPLETO.md para referencia de todas las herramientas analizadas
- @AGENTS.md para convenciones de código
