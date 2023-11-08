import mysql.connector
import yaml
with open('creds.yml', 'r') as f:
    creds = yaml.safe_load(f.read())
    creds = creds['datastore']
def make_tables():
    conn = mysql.connector.connect(
        host = creds['host'],
        user = creds['user'],
        password = creds['password'],
        database = creds['database']
    )
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS stock(
            id_db INTEGER PRIMARY KEY AUTO_INCREMENT,
            listing_id VARCHAR(50) NOT NULL,
            company VARCHAR(250) NOT NULL,
            share_price FLOAT NOT NULL,
            total_shares_available INTEGER NOT NULL,
            listing_date VARCHAR(100) NOT NULL,
            trace_id VARCHAR(250) NOT NULL)
            ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS sell_order(
            id_db INTEGER PRIMARY KEY AUTO_INCREMENT, 
            seller_id VARCHAR(50) NOT NULL,
            broker_id VARCHAR(50) NOT NULL,
            share_price FLOAT NOT NULL,
            amount INTEGER NOT NULL,
            sale_date VARCHAR(100) NOT NULL,
            trace_id VARCHAR(250) NOT NULL)
            ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    make_tables()