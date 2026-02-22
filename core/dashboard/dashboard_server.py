import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from intelligence_core import get_unified_data, get_all_alerts, get_product_history

_cache = {"data": None, "ts": 0}

def get_cached_data():
    now = time.time()
    if _cache["data"] and (now - _cache["ts"] < 30):
        return _cache["data"]
    
    print("\n[CORE] Iniciando escaneo profundo de bases de datos...")
    start = time.time()
    raw_prods, cats = get_unified_data()
    alerts = get_all_alerts()
    # Depuración de datos basura (precios erróneos en DB)
    clean_prods = [p for p in raw_prods if 500 < p['price'] < 40_000_000]
    _cache["data"] = (clean_prods, cats, alerts)
    _cache["ts"] = now
    end = time.time()
    print(f"[CORE] Sincronización exitosa: {len(clean_prods)} productos y {len(alerts)} alertas procesadas en {end-start:.2f}s")
    return _cache["data"]

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class StrategicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        root_path = self.path.split('?')[0]
        try:
            if root_path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                index_path = os.path.join(os.path.dirname(__file__), 'dashboard_index.html')
                with open(index_path, 'rb') as f:
                    self.wfile.write(f.read())
            
            elif root_path == '/api/data':
                prods, cats, alerts = get_cached_data()
                payload = json.dumps({"products": prods, "categories": cats, "alerts": alerts}).encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(payload)
                print(f"[API] Transmisión de {len(prods)} productos completada ({len(payload)/1024/1024:.2f} MB)")
                
            elif root_path == '/api/history':
                from urllib.parse import parse_qs, urlparse
                params = parse_qs(urlparse(self.path).query)
                store = params.get('store', [None])[0]
                pid = params.get('id', [None])[0]
                
                history = get_product_history(store, pid)
                payload = json.dumps(history).encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(payload)
                
            elif root_path == '/v5':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                # Navigate from core/dashboard/ to root/output/
                root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                v5_path = os.path.join(root_dir, 'output', 'dashboard_v5.html')
                if os.path.exists(v5_path):
                    with open(v5_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.wfile.write(b"Reporte V5 no encontrado. Ejecute el generador.")
            else:
                self.send_error(404)
        except Exception as e:
            print(f"[ERROR] Fallo en el servidor: {e}")
            self.send_error(500)

if __name__ == "__main__":
    # Escuchar en todas las interfaces para máxima compatibilidad
    server = ThreadedHTTPServer(('0.0.0.0', 8000), StrategicHandler)
    print("\n" + "!"*50)
    print("🚀 ODISEO COMMAND CENTER ONLINE")
    print("📡 LOCAL:  http://127.0.0.1:8000")
    print("📡 RED:    http://0.0.0.0:8000")
    print("!"*50 + "\n")
    server.serve_forever()
