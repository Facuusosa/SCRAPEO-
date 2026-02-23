import os
import shutil

ROOT = os.getcwd()
DB_DIR = os.path.join(ROOT, "data", "databases")
os.makedirs(DB_DIR, exist_ok=True)

potential_sources = [
    ROOT,
    os.path.join(ROOT, "targets", "fravega"),
    os.path.join(ROOT, "targets", "oncity"),
    os.path.join(ROOT, "targets", "cetrogar"),
    os.path.join(ROOT, "targets", "megatone"),
    os.path.join(ROOT, "targets", "newsan"),
    os.path.join(ROOT, "targets", "casadelaudio")
]

db_names = [
    "fravega_monitor.db",
    "oncity_monitor.db",
    "cetrogar_monitor.db",
    "megatone_monitor.db",
    "newsan_monitor.db",
    "casadelaudio_monitor.db"
]

for db_name in db_names:
    best_file = None
    max_size = -1
    
    # 1. Find the best version of this DB
    for src in potential_sources:
        path = os.path.join(src, db_name)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"Found {path} ({size} bytes)")
            if size > max_size:
                max_size = size
                best_file = path
    
    # 2. Move it to DB_DIR if it's not already there or if it's better
    dest = os.path.join(DB_DIR, db_name)
    if best_file:
        if best_file != dest:
            print(f"Moving {best_file} to {dest}")
            shutil.copy2(best_file, dest) # Copy instead of move for safety
        else:
            print(f"{dest} is already the best version.")
    
    # 3. (Optional) Remove other versions to avoid confusion
    for src in potential_sources:
        path = os.path.join(src, db_name)
        if os.path.exists(path) and path != dest:
             print(f"Cleaning up secondary file: {path}")
             os.remove(path)

print("DB Consolidation complete.")
