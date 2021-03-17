#!/bin/bash

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        -h|--hard)
            HARD=YES
            shift
        ;;
        *)
            POSITIONAL+=("$1")
            shift
        ;;
    esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters
HARD="${HARD:-NO}"
file="./backup/Backup-$1.tar.gz"
tmp_dir=$(mktemp -d -t restore-XXXXXXXXXX)

# unzip to $tmp Quelle: https://linuxize.com/post/how-to-extract-unzip-tar-gz-file/
tar -xvf "$file" -C "$tmp_dir"

# pg_restore Quelle: https://www.postgresql.org/docs/9.2/app-pgrestore.html
if [[ "$HARD" == YES ]]; then
    dropdb "$DB_NAME"
    pg_restore -C -d "$DB_NAME" "$tmp_dir/db_dump"
    rm -r "$MEDIA_FOLDER"
else
    pg_restore -a -Fc --single-transaction -d "$DB_NAME" "$tmp_dir/db_dump"
fi

rm "$tmp_dir/db_dump"
mv "$tmp_dir/*" "$MEDIA_FOLDER/../"

rm -rf "$tmp_dir"
