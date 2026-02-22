---
description: Debugging sistemático cuando un scraper falla
---

# Debug Scraper

## Steps

1. **Identificar el error**: Correr el scraper y capturar el error completo
```bash
python targets/fravega/sniffer_fravega.py 2>&1 | head -50
```

2. **Verificar fingerprint TLS**: Confirmar que curl_cffi impersona correctamente
```bash
python -c "from core import HttpClient; c = HttpClient(); fp = c.verify_fingerprint(); print(f'JA3: {fp.get(\"ja3n_hash\")}\nUA: {fp.get(\"user_agent\")}')"
```

3. **Probar variantes de browser**: Testear distintas versiones de Chrome
```bash
python -c "
import curl_cffi
url = 'https://www.fravega.com'
for v in ['chrome', 'chrome119', 'chrome120', 'chrome124']:
    try:
        r = curl_cffi.get(url, impersonate=v)
        print(f'{v}: {r.status_code}')
    except Exception as e:
        print(f'{v}: ERROR {e}')
"
```

4. **Probar HTTP versions**: HTTP/3 tiene menos detección WAF
```bash
python -c "
import curl_cffi
url = 'https://www.fravega.com'
for hv in ['v1', 'v2', 'v3']:
    try:
        r = curl_cffi.get(url, impersonate='chrome', http_version=hv)
        print(f'HTTP/{hv}: {r.status_code}')
    except Exception as e:
        print(f'HTTP/{hv}: ERROR {e}')
"
```

5. **Probar con session + cookies**: Simular navegación real
```bash
python -c "
import curl_cffi
with curl_cffi.Session(impersonate='chrome') as s:
    r1 = s.get('https://www.fravega.com')
    print(f'Homepage: {r1.status_code}')
    print(f'Cookies: {s.cookies}')
    r2 = s.get('https://www.fravega.com/api/v1')
    print(f'API: {r2.status_code}')
"
```

6. **Aplicar fix según diagnóstico** y verificar que funciona
