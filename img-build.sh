#!/bin/bash
docker compose -f ./deployment/docker-compose.yml down
docker image prune -af
#docker volume prune -af
docker image build --tag ogpeter/ogpeter:storage ./storage/
docker image build --tag ogpeter/ogpeter:receiver ./receiver/
docker image build --tag ogpeter/ogpeter:dashboard ./dashboard-ui/
docker image build --tag ogpeter/ogpeter:audit ./audit/
docker image build --tag ogpeter/ogpeter:processing ./processing/
#docker compose -f ./deployment/docker-compose.yml up -d
#docker ps --format "ID: {{.ID}}\tName: {{.Names}}"
docker push storage:latest
docker push receiver:latest
docker push dashboard:latest
docker push audit:latest
docker push processing:latest
