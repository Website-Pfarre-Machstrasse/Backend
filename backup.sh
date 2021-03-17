#!/bin/bash

#Temp-Ordner Quelle: https://code-maven.com/create-temporary-directory-on-linux-using-bash
tmp_dir=$(mktemp -d -t backup-XXXXXXXXXX)

#Backup erstellen Quelle: https://www.postgresql.org/docs/9.3/app-pgdump.html
pg_dump -Fc "$DB_NAME" > "$tmp_dir/db_dump"
cp "$MEDIA_FOLDER" "$tmp_dir"

#Zip
tar -cvfx "./backup/Backup-$(date +%Y-%m-%d).tar.gz" "$tmp_dir/*"

#Temp-Ordner entfernen
rm -rf "$tmp_dir"
