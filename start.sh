bash ./img-build.sh

docker compose -f ./deployment/docker-compose.yml up -d

docker ps --format "ID: {{.ID}}\tName: {{.Names}}"
