#!/bin/sh

export FLASK_APP=server/app:create_app()
export FLASK_ENV=PRODUCTION
cd /usr/srv/
exec flask run --host '0.0.0.0' --port 6060