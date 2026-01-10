#!/bin/sh
set -e
BACKUP_DIR=/backup
DB_FILE=/app/database.db
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
cp "$DB_FILE" "$BACKUP_DIR/database-$TIMESTAMP.db"
echo "Database backed up to $BACKUP_DIR/database-$TIMESTAMP.db"
