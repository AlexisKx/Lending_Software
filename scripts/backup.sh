#!/usr/bin/env bash
# Nightly SQLite backup. Run as a cron job (e.g. Railway scheduled service).
#
# Env vars:
#   SQLITE_PATH      Path to the live DB (default: ./db.sqlite3)
#   BACKUP_DIR       Where to drop the backup (default: ./backups)
#   BACKUP_KEEP_DAYS Prune backups older than this (default: 14)
#
# Optional: pipe the output to S3/B2/GDrive by editing the upload block below.
# For continuous replication, use litestream instead of this script.

set -euo pipefail

DB="${SQLITE_PATH:-./db.sqlite3}"
DEST="${BACKUP_DIR:-./backups}"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-14}"

if [[ ! -f "$DB" ]]; then
  echo "backup: source DB not found at $DB" >&2
  exit 1
fi

mkdir -p "$DEST"
TS="$(date +%Y%m%d-%H%M%S)"
OUT="$DEST/loandesk-$TS.sqlite3"

sqlite3 "$DB" ".backup '$OUT'"
gzip -9 "$OUT"
echo "backup: wrote $OUT.gz ($(du -h "$OUT.gz" | cut -f1))"

# --- Optional remote upload --------------------------------------------------
# aws s3 cp "$OUT.gz" "s3://my-loandesk-backups/" --storage-class STANDARD_IA
# rclone copy "$OUT.gz" b2:loandesk-backups/
# -----------------------------------------------------------------------------

find "$DEST" -name "loandesk-*.sqlite3.gz" -mtime "+$KEEP_DAYS" -delete
echo "backup: pruned files older than $KEEP_DAYS days"
