import mysql.connector
import yaml
with open('creds.yml', 'r') as f:
    creds = yaml.safe_load(f.read())
    creds = creds['datastore']

def make_db():
    conn = mysql.connector.connect(
        host = creds['host'],
        user = creds['user'],
        port = int(creds['port']),
        password = creds['password']
    )

    c = conn.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS acmestocks")
    c.execute("USE acmestocks")

if __name__ == '__main__':
    make_db()