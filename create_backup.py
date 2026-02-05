import sqlite3
import shutil
import datetime
import os

# Configuration
DB_PATH = 'bitacora.db'
TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
BACKUP_DIR = 'backups'
BACKUP_DB_NAME = f'bitacora_backup_{TIMESTAMP}.db'
BACKUP_SQL_NAME = f'bitacora_backup_{TIMESTAMP}.sql'

# Create backup directory if it doesn't exist
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Paths
backup_db_path = os.path.join(BACKUP_DIR, BACKUP_DB_NAME)
backup_sql_path = os.path.join(BACKUP_DIR, BACKUP_SQL_NAME)

print(f"Creating backup of {DB_PATH}...")

# 1. File Copy Backup
try:
    shutil.copy2(DB_PATH, backup_db_path)
    print(f"Database file copied to: {backup_db_path}")
except Exception as e:
    print(f"Error copying database file: {e}")

# 2. SQL Dump Backup
try:
    conn = sqlite3.connect(DB_PATH)
    with open(backup_sql_path, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    conn.close()
    print(f"SQL dump created at: {backup_sql_path}")
except Exception as e:
    print(f"Error creating SQL dump: {e}")

print("Backup process completed.")
