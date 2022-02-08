echo building docker containers
COMPOSE_HTTP_TIMEOUT=600 docker-compose up --build -d --force-recreate --remove-orphans