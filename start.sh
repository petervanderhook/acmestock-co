bash ./bigbash.sh
bash ./img-build.sh

docker compose -f ./deployment/docker-compose.yml up -d --scale receiver=3

docker ps --format "ID: {{.ID}}\tName: {{.Names}}"
