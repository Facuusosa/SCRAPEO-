---
name: debug-scraper
description: Debugging sistemático cuando un scraper falla (403, timeout, datos vacíos)
---

# Debug Scraper: $ARGUMENTS

## IRON LAW: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

## Fase 1 — Identificar el Síntoma
¿Qué está pasando exactamente?

| Síntoma | Causa Probable | Acción |
|---------|---------------|--------|
| 403 Forbidden | WAF detectó el bot | Verificar impersonación curl_cffi |
| 429 Too Many Requests | Rate limit excedido | Reducir Semaphore, agregar delays |
| Timeout | Server lento o bloqueando | Aumentar timeout, probar HTTP/3 |
| JSON vacío | Endpoint cambió | Re-descubrir API con /hunt-apis |
| Datos parciales | Paginación rota | Verificar cursor/offset |
| SSL Error | Certificado o proxy | `verify=False` o cambiar proxy |

## Fase 2 — Multi-Layer Diagnostic
Agregar logs en CADA frontera:

```python
# Frontera 1: HTTP Request
print(f"[HTTP] URL: {url}")
print(f"[HTTP] Status: {response.status_code}")
print(f"[HTTP] Headers: {dict(response.headers)}")
print(f"[HTTP] Body preview: {response.text[:500]}")

# Frontera 2: Parsing
print(f"[PARSE] Raw products count: {len(raw_products)}")
print(f"[PARSE] First product keys: {raw_products[0].keys() if raw_products else 'EMPTY'}")

# Frontera 3: Data
print(f"[DATA] Parsed products: {len(products)}")
print(f"[DATA] Products with price: {sum(1 for p in products if p.current_price > 0)}")
```

## Fase 3 — Verificar Fingerprint
```python
from core import HttpClient
client = HttpClient()

# ¿La impersonación funciona?
fp = client.verify_fingerprint()
print(f"JA3: {fp.get('ja3n_hash')}")
print(f"UA: {fp.get('user_agent')}")

# Comparar con tu Chrome real visitando:
# https://tls.browserleaks.com/json
```

## Fase 4 — Probar Variantes
```python
# Test 1: Cambiar versión de Chrome
for version in ["chrome", "chrome119", "chrome120", "chrome124"]:
    try:
        r = curl_cffi.get(url, impersonate=version)
        print(f"  {version}: {r.status_code}")
    except Exception as e:
        print(f"  {version}: ERROR {e}")

# Test 2: Cambiar HTTP version
for hv in ["v1", "v2", "v3"]:
    try:
        r = curl_cffi.get(url, impersonate="chrome", http_version=hv)
        print(f"  HTTP/{hv}: {r.status_code}")
    except:
        print(f"  HTTP/{hv}: ERROR")

# Test 3: Con/sin cookies
with curl_cffi.Session(impersonate="chrome") as s:
    s.get(base_url)  # Obtener cookies primero
    r = s.get(api_url)  # Luego el API
    print(f"  Con cookies: {r.status_code}")
```

## Fase 5 — Regla de 3
Si 3 fixes fallan: 
- ¿El sitio cambió su estructura?
- ¿Necesitamos Playwright en vez de curl_cffi?
- ¿Es mejor atacar otro endpoint/API?
