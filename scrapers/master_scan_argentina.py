"""
🇦🇷 MASTER SCAN ARGENTINA — El Gran Hermano de los Precios
Orquestador total de Fravega, On City, Cetrogar, Megatone, Newsan y Casa del Audio.
"""

import logging
import time
import sqlite3
import sys
import os

# Agregar el root del proyecto al path para que encuentre 'targets' y 'core'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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
    
    # Directorio central de DBs
    db_dir = os.path.join(PROJECT_ROOT, "data", "databases")
    os.makedirs(db_dir, exist_ok=True)

    # Instanciar sniffers con sus paths de DB específicos en data/databases
    sniffers = {
        "Fravega": FravegaSniffer(db_path=os.path.join(db_dir, "fravega_monitor.db")),
        "OnCity": OnCitySniffer(db_path=os.path.join(db_dir, "oncity_monitor.db")),
        "Cetrogar": CetrogarSniffer(db_path=os.path.join(db_dir, "cetrogar_monitor.db")),
        "Megatone": MegatoneSniffer(db_path=os.path.join(db_dir, "megatone_monitor.db")),
        "Newsan": NewsanSniffer(db_path=os.path.join(db_dir, "newsan_monitor.db")),
        "CasaDelAudio": CasaDelAudioSniffer(db_path=os.path.join(db_dir, "casadelaudio_monitor.db"))
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
