import mysql.connector
import yaml
with open('creds.yml', 'r') as f:
    creds = yaml.safe_load(f.read())
    creds = creds['datastore']
   
conn = mysql.connector.connect(
    host = creds['host'],
    user = creds['user'],
    password = creds['password']
)

c = conn.cursor()
try:
    c.execute("USE acmestocks")
except:
    pass
try:
    c.execute("DROP TABLE stock")
except:
    pass
try:
    c.execute("DROP TABLE sell_order")
except:
    pass
try:
    c.execute("DROP DATABASE acmestocks")
except:
    pass
print("Tables Dropped")