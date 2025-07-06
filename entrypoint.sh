#!/bin/sh
set -e

# Fix permissions for static and media
chown -R appuser:appuser /app/staticfiles /app/media || true

exec "$@" 