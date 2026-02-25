import subprocess
import time
import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler("sniffer_resilience.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RESILIENCE")

def run_sniffer(script_path, max_fails=5):
    fails = 0
    while fails < max_fails:
        logger.info(f"🚀 Iniciando sniffer: {script_path} (Intento {fails + 1}/{max_fails})")
        
        try:
            # Ejecutar el script y esperar a que termine
            process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Monitorear salida en tiempo real (opcional)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Sniffer finalizó normalmente. Reiniciando ciclo en 60s...")
                time.sleep(60)
                fails = 0 # Reset fails on success
            else:
                fails += 1
                logger.error(f"❌ Sniffer crash con código {process.returncode}")
                if stderr:
                    logger.error(f"Error Detallado: {stderr}")
                
                wait_time = 30 * fails
                logger.info(f"⏳ Esperando {wait_time}s antes de reintentar...")
                time.sleep(wait_time)
                
        except Exception as e:
            fails += 1
            logger.error(f"💥 Error crítico ejecutando sniffer: {e}")
            time.sleep(30)

    logger.critical("🚨 MAX_FAILS alcanzado. El sniffer no pudo recuperarse automáticamente.")
    # Aquí se podría llamar a una alerta de telegram admin si estuviera configurada en python
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python error_resilience.py <path_al_sniffer>")
        sys.exit(1)
    
    sniffer_script = sys.argv[1]
    run_sniffer(sniffer_script)
