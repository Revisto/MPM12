#!/bin/sh

if [ "$DATABASE" = "sqlite" ]
then
    echo "Using SQLite database..."

    # Apply database migrations
    python manage.py migrate

    # Collect static files
    python manage.py collectstatic --noinput
fi

exec "$@"