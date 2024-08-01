#!/bin/bash
docker login -u "ogpeter" -p "FatPassword32" docker.io
docker compose -f ./deployment/docker-compose.yml down
docker image prune -af
#docker volume prune -af
docker image build --tag ogpeter/storage:latest ./storage/
docker image build --tag ogpeter/receiver:latest ./receiver/
docker image build --tag ogpeter/dashboard:latest ./dashboard/
docker image build --tag ogpeter/audit:latest ./audit/
docker image build --tag ogpeter/processing:latest ./processing/
#docker compose -f ./deployment/docker-compose.yml up -d
#docker ps --format "ID: {{.ID}}\tName: {{.Names}}"
docker push ogpeter/storage:latest
docker push ogpeter/receiver:latest
docker push ogpeter/dashboard:latest
docker push ogpeter/audit:latest
docker push ogpeter/processing:latest
