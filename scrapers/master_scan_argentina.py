"""
🇦🇷 MASTER SCAN ARGENTINA — El Gran Hermano de los Precios
Orquestador total de Fravega, On City, Cetrogar, Megatone, Newsan y Casa del Audio.
"""

import logging
import time
import sqlite3
import os
from datetime import datetime

# Importar sniffers
from targets.fravega.sniffer_fravega import FravegaSniffer
from targets.oncity.sniffer_oncity import OnCitySniffer
from targets.cetrogar.sniffer_cetrogar import CetrogarSniffer
from targets.megatone.sniffer_megatone import MegatoneSniffer
from targets.newsan.sniffer_newsan import NewsanSniffer
from targets.casadelaudio.sniffer_casadelaudio import CasaDelAudioSniffer

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('master_scan.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MASTER")

CATEGORIES = [
    'celulares', 'notebooks', 'smart-tv', 'heladeras', 
    'lavarropas', 'aires', 'audio', 'cocinas'
]

def run_master():
    start_time = time.time()
    logger.info("🚀 INICIANDO ESCANEO MAESTRO NACIONAL")
    
    # Instanciar sniffers
    sniffers = {
        "Fravega": FravegaSniffer(),
        "OnCity": OnCitySniffer(),
        "Cetrogar": CetrogarSniffer(),
        "Megatone": MegatoneSniffer(),
        "Newsan": NewsanSniffer(),
        "CasaDelAudio": CasaDelAudioSniffer()
    }
    
    stats = {}

    for name, sniffer in sniffers.items():
        logger.info(f"\n >>> ATACANDO TARGET: {name.upper()} <<<")
        try:
            # Newsan y Casa del Audio son mas lentos por ser HTML parsing, les pedimos menos por ahora
            limit = 300 if name in ["Newsan", "CasaDelAudio"] else 1000
            
            # Ejecutar ciclo
            results = sniffer.run_cycle(CATEGORIES, size=limit)
            
            # Guardar stats
            total_prods = sum(r.products_found for r in results)
            stats[name] = total_prods
            logger.info(f"✅ {name} terminado: {total_prods} productos encontrados.")
            
        except Exception as e:
            logger.error(f"❌ Error en sniffer {name}: {e}")
            stats[name] = 0
        finally:
            if hasattr(sniffer, 'close'):
                sniffer.close()

    end_time = time.time()
    duration = (end_time - start_time) / 60
    
    # RESUMEN FINAL
    logger.info("\n" + "="*50)
    logger.info("🏆 RESUMEN DEL ESCANEO MAESTRO")
    logger.info("="*50)
    total_general = 0
    for name, count in stats.items():
        logger.info(f"- {name:15s}: {count:5d} productos")
        total_general += count
    
    logger.info(f"\n✨ TOTAL PRODUCTOS EN BASE: {total_general}")
    logger.info(f"⏱️ DURACIÓN TOTAL: {duration:.1f} minutos")
    logger.info("="*50)

if __name__ == "__main__":
    run_master()
