import os
import subprocess
import sys
import time

# Resolve absolute paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(ROOT_DIR, 'core', 'dashboard', 'dashboard_server.py')
GENERATOR_PATH = os.path.join(ROOT_DIR, 'tools', 'generate_dashboard_v5.py')

def main():
    print("="*60)
    print("🚀 ODISEO STRATEGIC COMMANDER - INICIALIZANDO")
    print("="*60)
    
    # 1. Update static report
    print("\n[1/2] Actualizando reporte maestro V5...")
    try:
        subprocess.run([sys.executable, GENERATOR_PATH], check=True)
    except Exception as e:
        print(f"⚠️ Error actualizando reporte: {e}")

    # 2. Start Dashboard Server
    print("\n[2/2] Iniciando servidor dinámico...")
    print(f"🔗 URL Local: http://127.0.0.1:8000")
    print(f"🔗 URL Red:   http://0.0.0.0:8000")
    print("\nPresione CTRL+C para detener.")
    
    try:
        # Run the server in its directory to handle local imports/assets
        subprocess.run([sys.executable, SERVER_PATH], cwd=os.path.dirname(SERVER_PATH))
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")

if __name__ == "__main__":
    main()
