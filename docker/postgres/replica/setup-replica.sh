#!/bin/bash

# Wait for primary to be ready
until pg_isready -h postgres-primary -p 5432 -U admin
do
  echo "Waiting for primary database..."
  sleep 2
done

# Stop PostgreSQL service
pg_ctl stop -D "$PGDATA" || true

# Clean up existing data directory
rm -rf "$PGDATA"/*

# Create replica using pg_basebackup
pg_basebackup -h postgres-primary -D "$PGDATA" -U replicator -v -P -W -R

# Create recovery configuration
cat >> "$PGDATA/postgresql.auto.conf" <<EOF
primary_conninfo = 'host=postgres-primary port=5432 user=replicator password=repl123'
recovery_target_timeline = 'latest'
standby_mode = 'on'
EOF

# Create standby signal
touch "$PGDATA/standby.signal"

# Set proper permissions
chown -R postgres:postgres "$PGDATA"
chmod 700 "$PGDATA"

echo "Replica setup complete"
