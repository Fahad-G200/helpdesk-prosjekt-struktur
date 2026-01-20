#!/usr/bin/env python3
"""
Automatisk backup av helpdesk-database

Dette scriptet kopierer database.db til en backup-mappe med tidsstempel.
Scriptet kan kjøres manuelt eller automatiseres med cron/scheduled tasks.

Eksempel bruk:
    python backup.py
    
For automatisering (cron):
    0 2 * * * /usr/bin/python3 /path/to/backup.py
    (Kjører hver natt kl 02:00)
"""

import shutil
import logging
from datetime import datetime
from pathlib import Path

# Konfigurasjon
DB_PATH = Path(__file__).resolve().parent / "backend" / "database.db"
BACKUP_DIR = Path(__file__).resolve().parent / "backups"
MAX_BACKUPS = 7  # Behold kun siste 7 backups

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_backup() -> bool:
    """
    Opprett backup av database
    
    Returns:
        bool: True hvis backup lyktes, False ellers
    """
    try:
        # Sjekk at database eksisterer
        if not DB_PATH.exists():
            logger.error(f"Database ikke funnet: {DB_PATH}")
            return False
        
        # Opprett backup-mappe hvis den ikke finnes
        BACKUP_DIR.mkdir(exist_ok=True, parents=True)
        logger.info(f"Backup-mappe: {BACKUP_DIR}")
        
        # Generer filnavn med tidsstempel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"database_backup_{timestamp}.db"
        backup_path = BACKUP_DIR / backup_filename
        
        # Kopier database
        shutil.copy2(DB_PATH, backup_path)
        
        # Bekreft at backup ble opprettet
        if backup_path.exists():
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Backup opprettet: {backup_filename} ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("❌ Backup feilet: fil ble ikke opprettet")
            return False
            
    except Exception as e:
        logger.error(f"❌ Feil under backup: {e}")
        return False


def cleanup_old_backups() -> None:
    """
    Slett gamle backups og behold kun de nyeste
    """
    try:
        # Finn alle backup-filer
        backups = sorted(BACKUP_DIR.glob("database_backup_*.db"))
        
        # Slett eldre backups hvis vi har flere enn MAX_BACKUPS
        if len(backups) > MAX_BACKUPS:
            to_delete = backups[:-MAX_BACKUPS]  # Alle unntatt de siste
            for old_backup in to_delete:
                old_backup.unlink()
                logger.info(f"🗑️  Slettet gammel backup: {old_backup.name}")
            
            logger.info(f"Beholder {MAX_BACKUPS} nyeste backups")
        else:
            logger.info(f"Totalt {len(backups)} backups (maks {MAX_BACKUPS})")
            
    except Exception as e:
        logger.error(f"Feil ved opprydding av backups: {e}")


def list_backups() -> None:
    """
    Vis oversikt over alle backups
    """
    try:
        backups = sorted(BACKUP_DIR.glob("database_backup_*.db"), reverse=True)
        
        if not backups:
            logger.info("Ingen backups funnet")
            return
        
        logger.info(f"\n📦 Tilgjengelige backups ({len(backups)}):")
        logger.info("-" * 60)
        
        for backup in backups:
            size_mb = backup.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(backup.stat().st_mtime)
            logger.info(f"{backup.name:<40} {size_mb:>6.2f} MB  {modified}")
        
        logger.info("-" * 60)
        
    except Exception as e:
        logger.error(f"Feil ved visning av backups: {e}")


def restore_backup(backup_filename: str) -> bool:
    """
    Gjenopprett database fra backup
    
    Args:
        backup_filename: Navn på backup-fil som skal gjenopprettes
        
    Returns:
        bool: True hvis restore lyktes, False ellers
    """
    try:
        backup_path = BACKUP_DIR / backup_filename
        
        if not backup_path.exists():
            logger.error(f"Backup ikke funnet: {backup_filename}")
            return False
        
        # Lag sikkerhetskopi av eksisterende database før restore
        if DB_PATH.exists():
            emergency_backup = DB_PATH.parent / f"database_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(DB_PATH, emergency_backup)
            logger.info(f"Sikkerhetskopi opprettet: {emergency_backup.name}")
        
        # Gjenopprett fra backup
        shutil.copy2(backup_path, DB_PATH)
        logger.info(f"✅ Database gjenopprettet fra: {backup_filename}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Feil ved gjenoppretting: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    logger.info("=" * 60)
    logger.info("🔄 Helpdesk Database Backup System")
    logger.info("=" * 60)
    
    # Hvis argument er gitt, håndter restore
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_backups()
        elif sys.argv[1] == "restore" and len(sys.argv) > 2:
            restore_backup(sys.argv[2])
        else:
            print("\nBruk:")
            print("  python backup.py              - Opprett ny backup")
            print("  python backup.py list         - Vis alle backups")
            print("  python backup.py restore FILE - Gjenopprett fra backup")
            sys.exit(1)
    else:
        # Normal backup
        if create_backup():
            cleanup_old_backups()
            list_backups()
            logger.info("\n✅ Backup fullført")
        else:
            logger.error("\n❌ Backup feilet")
            sys.exit(1)