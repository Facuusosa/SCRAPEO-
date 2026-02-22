
import requests
import json
import sqlite3
import time

# --- CONFIGURACIÓN DE ATAQUE ---
TARGET_URL_TEMPLATE = "https://www.fravega.com/chk-api/api/v1/checkout/{checkout_id}/item"
CHECKOUT_ID = "354b50474a524442b25ecdf9f747186f" # Capturado de tu cURL
COOKIE_FVG_CHECKOUT = "354b50474a524442b25ecdf9f747186f" # Cookie maestra

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://www.fravega.com',
    'referer': 'https://www.fravega.com/',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
    'cookie': f'fvg-checkout={COOKIE_FVG_CHECKOUT}; checkout-type=headless'
}

def probe_cart(sku_code, seller_id="1"):
    """
    Inyecta un producto en el carrito fantasma para ver su PRECIO REAL FINAL.
    """
    url = TARGET_URL_TEMPLATE.format(checkout_id=CHECKOUT_ID)
    
    # Try different seller IDs if the default one fails
    potential_sellers = [seller_id, "1", "fravega", "fravegasellerprod1221"]
    
    for seller in potential_sellers:
        payload = {
            "orderItems": [
                {
                    "id": sku_code,
                    "quantity": 1,
                    "seller": seller
                }
            ]
        }
        
        try:
            #print(f"[*] Probando SKU {sku_code} con vendedor {seller}...")
            response = requests.put(url, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    if str(item.get('id')) == str(sku_code):
                        selling_price = item.get('sellingPrice') / 100 
                        list_price = item.get('listPrice') / 100
                        return selling_price, list_price
            else:
                pass # Try next seller
                # print(f"[!] Fallo {seller}: Status {response.status_code}")
                
        except Exception as e:
            print(f"[!] Error de red con {seller}: {e}")
            
    return None, None

def scan_database_for_hidden_discounts():
    """
    Recorre los productos en la DB y busca discrepancias entre el 'precio visible' y el 'precio carrito'.
    """
    print("🚀 Iniciando Cart Sniper (Buscador de Descuentos Ocultos)...")
    path = "fravega_monitor.db"
    
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        products = conn.execute("SELECT * FROM products WHERE sku_code IS NOT NULL ORDER BY last_seen DESC LIMIT 50").fetchall()
        
    for p in products:
        sku = p['sku_code']
        visible_price = p['last_price']
        seller = p['seller_name'] if p['seller_name'] else "fravega" # Default to 'fravega' if unknown
        
        # Si el vendedor es marketplace, a veces el ID del vendedor es distinto.
        # Por ahora probamos con 'fravega' o extraemos del campo seller_name si lo tuviéramos mapeado.
        
        cart_price, list_price = probe_cart(sku, seller)
        
        if cart_price:
            if cart_price < visible_price:
                diff = visible_price - cart_price
                percent = (diff / visible_price) * 100
                print(f"[💎 JOYITA ENCONTRADA] {p['title']}")
                print(f"   Precio Web: ${visible_price:,.0f} | Precio Carrito: ${cart_price:,.0f}")
                print(f"   AHORRO OCULTO: ${diff:,.0f} ({percent:.1f}%) 📉")
            elif cart_price > visible_price:
                 print(f"[Request Check] {p['title']} - Web: ${visible_price} / Cart: ${cart_price} (Subió en carrito?)")
            else:
                pass # Precio igual, aburrido
                # print(f"[=] {p['title']} sin cambios.")
        
        time.sleep(1.5) # Rate limit para no quemar el checkout

if __name__ == "__main__":
    scan_database_for_hidden_discounts()
