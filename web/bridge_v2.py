"""
🌉 BRIDGE V2 — Orquestador Mejorado para Sniffer V2

Cambios vs V1:
- Soporta tanto V1 (glitch detection) como V2 (oportunidades confirmadas)
- Mejor logging y telemetría
- SSE actualizado para opportunities
- Health check para cada sniffer

Uso:
    python web/bridge_v2.py --sniffers fravega
    python web/bridge_v2.py --sniffers fravega,megatone,cetrogar
"""

import subprocess
import requests
import json
import threading
import os
import time
import sys
from datetime import datetime
from typing import Optional, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("bridge-v2")

API_URL = "http://localhost:3001/api/events"
HEALTH_CHECK_INTERVAL = 30  # segundos


class SnifferProcess:
    """Gestiona un proceso de sniffer (V1 o V2)."""
    
    def __init__(self, script_path: str, provider: str, version: str = "v1"):
        self.script_path = script_path
        self.provider = provider
        self.version = version
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.last_heartbeat = None
        self.error_count = 0
        self.max_errors = 5
    
    def start(self):
        """Iniciar proceso sniffer."""
        if self.is_running:
            logger.warning(f"{self.provider}: Ya está corriendo")
            return
        
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_script = os.path.join(ROOT_DIR, self.script_path)
        
        if not os.path.exists(abs_script):
            logger.error(f"{self.provider}: Script no encontrado: {abs_script}")
            return
        
        try:
            self.process = subprocess.Popen(
                [sys.executable, abs_script, "--daemon"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=ROOT_DIR,
                text=True,
                bufsize=1,
            )
            
            self.is_running = True
            self.error_count = 0
            self.last_heartbeat = datetime.now()
            
            logger.info(f"{self.provider}: Iniciado (PID {self.process.pid})")
            
            # Thread para leer stdout
            reader_thread = threading.Thread(
                target=self._read_stdout,
                daemon=True,
            )
            reader_thread.start()
            
        except Exception as e:
            logger.error(f"{self.provider}: Error al iniciar: {e}")
            self.is_running = False
    
    def _read_stdout(self):
        """Leer stdout línea por línea y enviar a API."""
        if not self.process:
            return
        
        for line in iter(self.process.stdout.readline, ''):
            if not line:
                break
            
            message = line.strip()
            if not message:
                continue
            
            # Log local
            logger.info(f"{self.provider}: {message}")
            
            # Determinar tipo y nivel
            level = "info"
            is_opportunity = False
            
            upper_msg = message.upper()
            
            if "🚀" in message or "OPORTUNIDAD" in upper_msg:
                level = "success"
                is_opportunity = True
            elif "ERROR" in upper_msg or "403" in upper_msg or "FAIL" in upper_msg:
                level = "error"
                self.error_count += 1
            elif "❌" in message or "RECHAZADO" in upper_msg:
                level = "warn"
            elif "✅" in message or "VALIDADO" in upper_msg:
                level = "success"
            
            # Enviar al API
            self._send_event(message, level, is_opportunity)
            
            # Health check
            if self.error_count >= self.max_errors:
                logger.error(f"{self.provider}: Demasiados errores, reiniciando...")
                self.restart()
                return
    
    def _send_event(self, message: str, level: str, is_opportunity: bool = False):
        """Enviar evento a API via POST."""
        try:
            payload = {
                "type": "opportunity" if is_opportunity else "log",
                "id": str(time.time()),
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "source": self.provider,
                "version": self.version,
                "message": message,
            }
            
            # Si es oportunidad, pedir refresh del dashboard
            if is_opportunity:
                payload["refreshProducts"] = True
            
            requests.post(API_URL, json=payload, timeout=2)
            
        except Exception as e:
            logger.debug(f"{self.provider}: Error enviando evento: {e}")
    
    def restart(self):
        """Reiniciar proceso."""
        logger.warning(f"{self.provider}: Reiniciando...")
        self.stop()
        time.sleep(2)
        self.start()
    
    def stop(self):
        """Detener proceso."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            
            self.is_running = False
            logger.info(f"{self.provider}: Detenido")
    
    def health_check(self) -> bool:
        """Verificar si el proceso sigue corriendo."""
        if not self.process:
            return False
        
        poll = self.process.poll()
        
        if poll is not None:
            # Proceso terminó inesperadamente
            logger.warning(f"{self.provider}: Proceso terminó (exit code {poll})")
            self.is_running = False
            self.restart()
            return False
        
        # OK
        self.last_heartbeat = datetime.now()
        return True


class Bridge:
    """Orquestador principal."""
    
    def __init__(self):
        self.sniffers: dict[str, SnifferProcess] = {}
        self.running = False
    
    def add_sniffer(self, name: str, script_path: str, version: str = "v1"):
        """Agregar sniffer al pool."""
        sniffer = SnifferProcess(script_path, name, version)
        self.sniffers[name] = sniffer
        logger.info(f"✅ Sniffer registrado: {name} ({version})")
    
    def start_all(self):
        """Iniciar todos los sniffers."""
        logger.info(f"🚀 Iniciando {len(self.sniffers)} sniffers...")
        
        for sniffer in self.sniffers.values():
            sniffer.start()
            time.sleep(1)  # Delay para evitar race conditions
        
        self.running = True
        
        # Thread de health checks
        health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        health_thread.start()
        
        logger.info("✅ Todos los sniffers iniciados")
    
    def _health_check_loop(self):
        """Loop de health checks periódicos."""
        while self.running:
            time.sleep(HEALTH_CHECK_INTERVAL)
            
            for name, sniffer in self.sniffers.items():
                if not sniffer.health_check():
                    logger.warning(f"Health check falló para {name}")
    
    def stop_all(self):
        """Detener todos los sniffers."""
        logger.info("⛔ Deteniendo sniffers...")
        
        for sniffer in self.sniffers.values():
            sniffer.stop()
        
        self.running = False
        logger.info("✅ Todos detenidos")
    
    def status(self) -> dict:
        """Obtener estado de todos los sniffers."""
        return {
            name: {
                "running": sniffer.is_running,
                "version": sniffer.version,
                "pid": sniffer.process.pid if sniffer.process else None,
                "last_heartbeat": sniffer.last_heartbeat.isoformat() if sniffer.last_heartbeat else None,
                "error_count": sniffer.error_count,
            }
            for name, sniffer in self.sniffers.items()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Bridge V2 — Orquestador de Sniffers")
    parser.add_argument(
        "--sniffers",
        type=str,
        default="fravega",
        help="Sniffers a ejecutar (ej: fravega,megatone,cetrogar)"
    )
    parser.add_argument(
        "--versions",
        type=str,
        default="v2,v2,v2",
        help="Versión de cada sniffer (v1 o v2)"
    )
    
    args = parser.parse_args()
    
    # Parsear sniffers y versiones
    sniffer_names = [s.strip() for s in args.sniffers.split(",")]
    sniffer_versions = [v.strip() for v in args.versions.split(",")]
    
    # Asegurar que tenemos versión para cada sniffer
    while len(sniffer_versions) < len(sniffer_names):
        sniffer_versions.append("v2")
    
    # Configuración de sniffers
    SNIFFER_CONFIG = {
        "fravega": {
            "v1": "targets/fravega/sniffer_fravega.py",
            "v2": "targets/fravega/sniffer_fravega_v2.py",
        },
        "megatone": {
            "v1": "targets/megatone/sniffer_megatone.py",
            "v2": "targets/megatone/sniffer_megatone_v2.py",  # futuro
        },
        "cetrogar": {
            "v1": "targets/cetrogar/sniffer_cetrogar.py",
            "v2": "targets/cetrogar/sniffer_cetrogar_v2.py",  # futuro
        },
        "oncity": {
            "v1": "targets/oncity/sniffer_oncity.py",
            "v2": "targets/oncity/sniffer_oncity_v2.py",  # futuro
        },
    }
    
    # Crear bridge
    bridge = Bridge()
    
    # Registrar sniffers
    for name, version in zip(sniffer_names, sniffer_versions):
        if name not in SNIFFER_CONFIG:
            logger.warning(f"Sniffer desconocido: {name}")
            continue
        
        if version not in SNIFFER_CONFIG[name]:
            logger.warning(f"Versión desconocida: {name}/{version}")
            version = "v1"  # Fallback
        
        script_path = SNIFFER_CONFIG[name][version]
        bridge.add_sniffer(name, script_path, version)
    
    # Iniciar
    bridge.start_all()
    
    # Mantener vivo
    try:
        while True:
            time.sleep(10)
            
            # Imprimir status cada minuto
            if int(time.time()) % 60 == 0:
                status = bridge.status()
                logger.info(f"Status: {json.dumps(status, indent=2)}")
    
    except KeyboardInterrupt:
        logger.info("\n⛔ Interrupt recibido")
        bridge.stop_all()


if __name__ == "__main__":
    main()
