
docker compose -f deployment/docker-compose.yml down -v
rm -rf /home/azureuser/logs
rm -rf /home/azureuser/zookeeper
rm -rf /home/azureuser/kafka
rm -rf /home/azureuser/config

mkdir /home/azureuser/zookeeper
mkdir /home/azureuser/zookeeper/data
mkdir /home/azureuser/kafka
mkdir /home/azureuser/config
mkdir /home/azureuser/config/receiver
mkdir /home/azureuser/config/storage
mkdir /home/azureuser/config/audit_log
mkdir /home/azureuser/config/processing
mkdir /home/azureuser/config/health
cp /home/azureuser/acmestock-co/health/log_conf.yml /home/azureuser/acmestock-co/health/app_conf.yml /home/azureuser/config/health/
cp /home/azureuser/acmestock-co/storage/log_conf.yml /home/azureuser/acmestock-co/storage/app_conf.yml /home/azureuser/config/storage/

cp /home/azureuser/acmestock-co/receiver/log_conf.yml /home/azureuser/acmestock-co/receiver/app_conf.yml /home/azureuser/config/receiver/

cp /home/azureuser/acmestock-co/audit/log_conf.yml /home/azureuser/acmestock-co/audit/app_conf.yml /home/azureuser/config/audit_log/

cp /home/azureuser/acmestock-co/processing/log_conf.yml /home/azureuser/acmestock-co/processing/app_conf.yml /home/azureuser/config/processing/
