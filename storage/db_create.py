import mysql.connector
import yaml
with open('creds.yml', 'r') as f:
    creds = yaml.safe_load(f.read())
    creds = creds['datastore']
    
conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = creds['password']
)

c = conn.cursor()
c.execute("CREATE DATABASE acmestocks")
c.execute("USE acmestocks")