---
name: hunt-apis
description: Descubrir APIs ocultas de un sitio e-commerce (GraphQL, REST, endpoints internos)
---

# Hunt APIs: $ARGUMENTS

## Objetivo
Investigar exhaustivamente un sitio e-commerce para descubrir todas las APIs disponibles.

## Pasos

### 1. Inspección Inicial
- Abrir el sitio en browser con DevTools → Network
- Filtrar por XHR/Fetch
- Navegar por: home, categorías, producto individual, carrito, búsqueda
- Documentar CADA request que haga el frontend

### 2. Buscar GraphQL
```python
from core import HttpClient

client = HttpClient()

# Endpoints GraphQL comunes
graphql_paths = [
    "/api/graphql",
    "/graphql",
    "/api/v1/graphql",
    "/gql",
    "/_next/data",
    "/api/catalog",
]

for path in graphql_paths:
    try:
        url = f"https://TARGET_URL{path}"
        r = client.get(url)
        print(f"  {path} → {r.status_code} ({len(r.text)} bytes)")
    except Exception as e:
        print(f"  {path} → ERROR: {e}")
```

### 3. Introspección GraphQL
```python
# Si encontramos un endpoint GraphQL, obtener el schema completo
introspection_query = {
    "query": """
    {
        __schema {
            types { name kind fields { name type { name } } }
            queryType { fields { name args { name type { name } } } }
            mutationType { fields { name } }
        }
    }
    """
}
r = client.post("https://TARGET/api/graphql", json=introspection_query)
schema = r.json()
# Guardar en data/schema_TARGET.json
```

### 4. Buscar REST APIs
```python
# Endpoints REST comunes en e-commerce
rest_paths = [
    "/api/v1/products",
    "/api/v1/categories",
    "/api/v1/search?q=iphone",
    "/api/catalog/products",
    "/api/pricing",
    "/_api/catalog-api-proxy",
]
```

### 5. Buscar en el Código Fuente
```python
import re

r = client.get("https://TARGET_URL")
html = r.text

# Buscar URLs de API en el HTML/JS
api_patterns = [
    r'https?://[^"\s]+/api/[^"\s]+',
    r'https?://[^"\s]+/graphql[^"\s]*',
    r'"baseURL":\s*"([^"]+)"',
    r'endpoint["\s:]+["\']([^"\']+)',
]

for pattern in api_patterns:
    matches = re.findall(pattern, html)
    for m in matches:
        print(f"  Encontrado: {m}")
```

### 6. Buscar Tokens/Keys en JS Bundles
```python
# Extraer URLs de scripts JS
scripts = re.findall(r'src="([^"]+\.js)"', html)
for script_url in scripts[:10]:  # Limitar a 10
    js = client.get(script_url).text
    # Buscar API keys, tokens, endpoints
    tokens = re.findall(r'["\']([A-Za-z0-9_-]{20,})["\']', js)
    endpoints = re.findall(r'["\']/(api|graphql|v[0-9])[^"\']*["\']', js)
```

### 7. Documentar Hallazgos
Guardar en `data/api_discovery_TARGET.json`:
```json
{
    "target": "nombre",
    "base_url": "https://...",
    "api_type": "graphql|rest|hybrid",
    "endpoints": [...],
    "auth_required": false,
    "rate_limits": "unknown",
    "notes": "..."
}
```
