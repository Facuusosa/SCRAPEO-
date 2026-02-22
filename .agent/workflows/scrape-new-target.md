---
description: Scrapear un nuevo target e-commerce desde cero
---

# Scrape New Target

// turbo-all

## Steps

1. **Reconocimiento**: Abrir el sitio del target, inspeccionar Network en DevTools, identificar si usa GraphQL o REST
```bash
python -c "from core import HttpClient; c = HttpClient(); r = c.get('URL_TARGET'); print(r.status_code, len(r.text))"
```

2. **Probar endpoints comunes**:
```bash
python -c "
from core import HttpClient
c = HttpClient()
for path in ['/api/graphql', '/graphql', '/api/v1/products', '/api/catalog']:
    try:
        r = c.get(f'URL_TARGET{path}')
        print(f'{path}: {r.status_code}')
    except Exception as e:
        print(f'{path}: ERROR')
"
```

3. **Crear directorio del target**:
```bash
mkdir -p targets/NOMBRE_TARGET
```

4. **Crear el scraper** heredando de BaseSniffer (ver `.claude/skills/scrape-target/SKILL.md` para template)

5. **Test con 1 categoría**:
```bash
python targets/NOMBRE_TARGET/sniffer_NOMBRE.py
```

6. **Verificar datos en DB**:
```bash
python -c "from core import Database; db = Database('targets/NOMBRE_TARGET/NOMBRE_monitor.db'); print(db.get_stats())"
```
