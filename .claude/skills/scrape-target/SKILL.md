---
name: scrape-target
description: Crear un scraper completo para un nuevo e-commerce target
---

# Scrape Target: $ARGUMENTS

## Objetivo
Crear un scraper completo para el target indicado, integrado con la arquitectura core del proyecto.

## Pasos

### 1. Reconocimiento del Target
- Abrir el sitio web del target en el browser
- Identificar la estructura de URLs (categorías, productos, paginación)
- Abrir DevTools → Network → buscar requests XHR/Fetch
- Identificar si usa GraphQL, REST API, o server-side rendering
- Documentar los endpoints encontrados

### 2. Probar el API con curl_cffi
```python
from core import HttpClient

client = HttpClient()
# Probar que no da 403
r = client.get("URL_DEL_TARGET")
print(r.status_code, len(r.text))

# Si tiene API, probar endpoint
r = client.get_json("URL_DEL_API")
print(r)
```

### 3. Crear el Scraper
- Crear directorio: `targets/<nombre_target>/`
- Crear archivo: `targets/<nombre_target>/sniffer_<nombre>.py`
- La clase DEBE heredar de `core.BaseSniffer`
- Implementar los 3 métodos obligatorios:
  - `fetch_products(category)` → Obtener data raw
  - `parse_product(raw)` → Convertir a `Product`
  - `detect_glitch(product)` → (opcional, hay default)

### 4. Template del Scraper
```python
from core import BaseSniffer, HttpClient, Product, Database

class NuevoSniffer(BaseSniffer):
    TARGET_NAME = "nombre_target"
    BASE_URL = "https://www.target.com"
    API_URL = "https://www.target.com/api"
    
    def __init__(self):
        super().__init__()
        self.client = HttpClient()
        self.db = Database(self.db_path)
    
    def fetch_products(self, category, **kwargs):
        r = self.client.get_json(f"{self.API_URL}/category/{category}")
        return r.get("products", [])
    
    def parse_product(self, raw):
        return Product(
            id=str(raw["id"]),
            name=raw["name"],
            current_price=float(raw.get("price", 0)),
            list_price=float(raw.get("listPrice", 0)),
            url=f"{self.BASE_URL}/p/{raw['id']}",
        )
    
    def save_products(self, products):
        self.db.save_products(products)

if __name__ == "__main__":
    sniffer = NuevoSniffer()
    sniffer.run_cycle(["celulares", "notebooks"])
```

### 5. Testing
- Correr el scraper con 1 categoría pequeña
- Verificar que no da 403/WAF blocks
- Verificar que parsea productos correctamente
- Verificar que guarda en DB

### 6. Integrar
- Agregar categorías al JSON de configuración
- Documentar el target en README.md
- Commit con mensaje descriptivo
