#!/bin/bash
docker compose -f ./deployment/docker-compose.yml down
docker image prune -af
#docker volume prune -af
docker image build -t storage:latest ./storage/
docker image build -t receiver:latest ./receiver/
docker image build -t dashboard:latest ./dashboard-ui/
docker image build -t audit_log:latest ./audit/
docker image build -t processing:latest ./processing/
#docker compose -f ./deployment/docker-compose.yml up -d
#docker ps --format "ID: {{.ID}}\tName: {{.Names}}"
docker push storage:latest
docker push receiver:latest
docker push dashboard:latest
docker push audit_log:latest
docker push processing:latest
