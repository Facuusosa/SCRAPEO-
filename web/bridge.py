import subprocess
import requests
import json
import threading
import os
import time

API_URL = "http://localhost:3001/api/events"

def monitor_stdout(process, provider):
    """Lector de stdout que envía cada línea al dashboard vía Webhook/SSE."""
    for line in iter(process.stdout.readline, b''):
        # Usar latin-1 para evitar errores de decode en Windows
        message = line.decode('latin-1', errors='replace').strip()
        if not message: continue
        
        print(f"[{provider}] {message}")
        
        # Determinar nivel de log basado en contenido
        level = "info"
        upper_msg = message.upper()
        if "ERROR" in upper_msg or "403" in upper_msg or "FAIL" in upper_msg:
            level = "error"
        elif "ANOMALY" in upper_msg or "GLITCH" in upper_msg or "ALERT" in upper_msg:
            level = "warn"
        elif "SUCCESS" in upper_msg or "CONFIRMED" in upper_msg or "LOADED" in upper_msg:
            level = "success"
            
        try:
            payload = {
                "type": "log",
                "id": str(time.time()),
                "timestamp": time.strftime("%H:%M:%S"),
                "level": level,
                "source": provider,
                "message": message
            }
            
            # Si el mensaje indica un glitch verificado, enviar actualización de UI
            if any(k in upper_msg for k in ["CONFIRMED", "GLITCH", "ALERT", "BAJÓ"]):
                payload["type"] = "update"
                payload["refreshProducts"] = True
                
            requests.post(API_URL, json=payload, timeout=2)
        except Exception:
            pass

import sys

def run_sniffer(script_path, provider):
    # Resolver el root del proyecto relativo a bridge.py
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_script = os.path.join(ROOT_DIR, script_path)
    
    if not os.path.exists(abs_script):
        print(f"Script not found: {abs_script}")
        return

    # IMPORTANTE: Correr desde el root (CWD) para que los imports relativos funcionen
    # Agregamos --daemon para que no terminen
    process = subprocess.Popen(
        [sys.executable, abs_script, "--daemon", "--interval", "120"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=ROOT_DIR
    )
    
    monitor_stdout(process, provider)

if __name__ == "__main__":
    sniffers = [
        ("targets/fravega/sniffer_fravega.py", "FRAVEGA"),
        ("targets/megatone/sniffer_megatone.py", "MEGATONE"),
        ("targets/cetrogar/sniffer_cetrogar.py", "CETROGAR"),
        ("targets/oncity/sniffer_oncity.py", "ONCITY")
    ]
    
    threads = []
    for path, provider in sniffers:
        t = threading.Thread(target=run_sniffer, args=(path, provider))
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join()
