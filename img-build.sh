#!/bin/bash

docker compose -f ./deployment/docker-compose.yml down -v
docker image prune -af
docker volume prune -af
docker image build -t storage:latest ./storage/
docker image build -t receiver:latest ./receiver/
docker image build -t dashboard:latest ./dashboard-ui/
docker image build -t audit_log:latest ./audit/
docker image build -t processing:latest ./processing/
docker compose -f ./deployment/docker-compose.yml up -d
docker ps --format "ID: {{.ID}}\tName: {{.Names}}"
